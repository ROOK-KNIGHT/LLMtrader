"""
Token Refresher - Standalone process managed by Supervisor.
Runs every 3 minutes, refreshes Schwab access tokens for all users
whose token expires within 15 minutes. Also detects stale refresh tokens.

This runs as a SEPARATE process (not inside uvicorn) so it is immune to
worker recycling and asyncio event-loop issues.
"""

import os
import sys
import time
import base64
import logging
import requests
from datetime import datetime, timedelta

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [token-refresher] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("token_refresher")

# ── Config ───────────────────────────────────────────────────────────────────
REFRESH_INTERVAL_SECONDS = 180          # run every 3 minutes
REFRESH_WINDOW_MINUTES   = 15           # refresh tokens expiring within 15 min
SCHWAB_TOKEN_URL         = "https://api.schwabapi.com/v1/oauth/token"
REQUEST_TIMEOUT          = 15           # seconds


def get_db_connection():
    """Return a raw psycopg2 connection (not pooled — single process)."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn_str = os.environ.get(
        "DATABASE_URL",
        "postgresql://localhost:5432/llmtrader"
    )
    conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
    conn.autocommit = False
    return conn


def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt app_secret using the ENCRYPTION_KEY env var."""
    from cryptography.fernet import Fernet
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY environment variable is not set")
    cipher = Fernet(key.encode() if isinstance(key, str) else key)
    return cipher.decrypt(encrypted_secret.encode()).decode()


def refresh_token_for_user(conn, row: dict) -> bool:
    """
    Attempt to refresh the access token for one user.
    Returns True on success, False on failure.
    """
    user_id = row["user_id"]
    try:
        app_secret = decrypt_secret(row["app_secret_encrypted"])
        credentials = f"{row['app_key']}:{app_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        resp = requests.post(
            SCHWAB_TOKEN_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": row["refresh_token"],
            },
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code == 200:
            tokens = resp.json()
            expires_in = tokens.get("expires_in", 1800)
            new_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            new_access_token = tokens["access_token"]
            new_refresh_token = tokens.get("refresh_token", row["refresh_token"])

            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE schwab_tokens
                    SET access_token  = %s,
                        refresh_token = %s,
                        expires_at    = %s,
                        updated_at    = NOW()
                    WHERE user_id = %s
                    """,
                    (new_access_token, new_refresh_token, new_expires_at, user_id),
                )
            conn.commit()
            logger.info(
                f"user_id={user_id} token refreshed — expires at {new_expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            return True

        else:
            conn.rollback()
            logger.warning(
                f"user_id={user_id} refresh FAILED — HTTP {resp.status_code}: {resp.text[:200]}"
            )
            if resp.status_code in (400, 401):
                logger.error(
                    f"user_id={user_id} refresh token may be EXPIRED — user must re-authenticate via Schwab OAuth"
                )
            return False

    except Exception as exc:
        conn.rollback()
        logger.error(f"user_id={user_id} refresh exception: {exc}")
        return False


def run_refresh_cycle(conn):
    """Find all tokens expiring soon and refresh them."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT st.user_id,
                       st.refresh_token,
                       st.expires_at,
                       sc.app_key,
                       sc.app_secret_encrypted
                FROM schwab_tokens st
                JOIN schwab_credentials sc ON sc.user_id = st.user_id
                WHERE st.expires_at <= NOW() + INTERVAL '%s minutes'
                """,
                (REFRESH_WINDOW_MINUTES,),
            )
            rows = cur.fetchall()

        if not rows:
            logger.debug("No tokens need refreshing right now.")
            return

        logger.info(f"Found {len(rows)} token(s) to refresh.")
        success = 0
        for row in rows:
            if refresh_token_for_user(conn, row):
                success += 1

        logger.info(f"Refresh cycle complete: {success}/{len(rows)} succeeded.")

    except Exception as exc:
        logger.error(f"Refresh cycle error: {exc}")
        try:
            conn.rollback()
        except Exception:
            pass


def main():
    logger.info("Schwab token refresher starting up...")
    logger.info(f"Refresh interval: {REFRESH_INTERVAL_SECONDS}s | Window: {REFRESH_WINDOW_MINUTES} min")

    conn = None
    while True:
        try:
            # Reconnect if needed
            if conn is None or conn.closed:
                logger.info("Connecting to database...")
                conn = get_db_connection()
                logger.info("Database connection established.")

            run_refresh_cycle(conn)

        except Exception as exc:
            logger.error(f"Unexpected error in main loop: {exc}")
            # Close broken connection so we reconnect next cycle
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
            conn = None

        time.sleep(REFRESH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
