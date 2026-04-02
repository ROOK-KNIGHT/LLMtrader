"""
LLM Handler - Multi-model LLM client with tool execution
Supports Claude (Anthropic), Grok (X.AI), and Gemini with proper tool formatting
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Tuple

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class LLMHandler:
    """
    Handles API interactions with various AI models (Claude, Grok, Gemini).
    Loads API keys per-user from the ai_api_keys database table.
    """

    def __init__(self, user_id: int = None, db_connection_string: str = None):
        """
        Initialize LLM handler.

        Args:
            user_id: User ID to load API keys for (from ai_api_keys table)
            db_connection_string: PostgreSQL connection string
        """
        self.user_id = user_id
        self.db_connection_string = db_connection_string or os.getenv('DATABASE_URL')
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from PostgreSQL for this user, fallback to env vars"""
        if PSYCOPG2_AVAILABLE and self.db_connection_string and self.user_id:
            try:
                keys = self._load_api_keys_from_postgres()
                if keys:
                    return keys
            except Exception as e:
                print(f"Warning: Failed to load API keys from PostgreSQL: {e}")

        return self._load_api_keys_from_env()

    def _load_api_keys_from_postgres(self) -> Dict[str, str]:
        """Load API keys from ai_api_keys table for this user"""
        conn = psycopg2.connect(self.db_connection_string)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT service_name, api_key
                FROM ai_api_keys
                WHERE user_id = %s AND is_active = true
                """,
                (self.user_id,)
            )
            results = cursor.fetchall()
            cursor.close()
            if results:
                keys = {row[0].lower(): row[1] for row in results}
                return keys
            return {}
        finally:
            conn.close()

    def _load_api_keys_from_env(self) -> Dict[str, str]:
        """Load API keys from environment variables (fallback)"""
        return {
            'claude': os.getenv('CLAUDE_API_KEY', ''),
            'grok': os.getenv('GROK_API_KEY', ''),
            'gemini': os.getenv('GEMINI_API_KEY', '')
        }

    async def call_model(
        self,
        model_name: str,
        prompt: str,
        system_prompt: str = None,
        tools_registry=None,
        conversation_history: List[Dict] = None
    ) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Unified method to call any supported model.

        Args:
            model_name: Model name ('claude', 'grok', 'gemini')
            prompt: User prompt
            system_prompt: System prompt (optional)
            tools_registry: ToolsRegistry instance for tool execution
            conversation_history: Prior messages for multi-turn context

        Returns:
            Tuple of (response_text, status, error_message)
        """
        model_name = model_name.lower()

        if model_name == 'claude':
            return await self._call_claude(prompt, system_prompt, tools_registry, conversation_history)
        elif model_name == 'grok':
            return await self._call_grok(prompt, system_prompt, tools_registry, conversation_history)
        elif model_name == 'gemini':
            return await self._call_gemini(prompt, system_prompt, tools_registry, conversation_history)
        else:
            return None, 'error', f"Unknown model: {model_name}"

    async def _call_claude(
        self,
        prompt: str,
        system_prompt: str,
        tools_registry,
        conversation_history: List[Dict] = None
    ) -> Tuple[Optional[str], str, Optional[str]]:
        """Call Claude (Anthropic) API — claude-opus-4-6"""
        try:
            api_key = self.api_keys.get('claude')
            if not api_key:
                return None, 'error', 'Claude API key not found. Please add it via Settings.'

            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            # Build messages — include conversation history for multi-turn context
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    if role in ('user', 'assistant') and content:
                        messages.append({'role': role, 'content': content})

            # Add current user message
            messages.append({'role': 'user', 'content': prompt})

            payload = {
                'model': 'claude-opus-4-6',
                'max_tokens': 4096,
                'messages': messages
            }
            if system_prompt:
                payload['system'] = system_prompt

            # Format tools for Claude (Anthropic tool_use format)
            if tools_registry:
                tools_def = []
                for tool in tools_registry.get_all_tools_definitions():
                    tools_def.append({
                        "name": tool['name'],
                        "description": tool['description'],
                        "input_schema": tool['parameters']
                    })
                if tools_def:
                    payload['tools'] = tools_def

            async with aiohttp.ClientSession() as session:
                # Multi-turn tool execution loop (up to 10 turns)
                for turn in range(10):
                    async with session.post(
                        'https://api.anthropic.com/v1/messages',
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            return None, 'error', f"Claude API error {response.status}: {error_text[:300]}"

                        data = await response.json()

                        # Tool use — execute tools and loop back
                        if data.get('stop_reason') == 'tool_use' and tools_registry:
                            messages.append({"role": "assistant", "content": data['content']})

                            tool_results = []
                            for block in data['content']:
                                if block['type'] == 'tool_use':
                                    tool_name = block['name']
                                    tool_input = block['input']
                                    try:
                                        result = tools_registry.execute_tool(tool_name, tool_input)
                                        tool_results.append({
                                            "type": "tool_result",
                                            "tool_use_id": block['id'],
                                            "content": str(result)
                                        })
                                    except Exception as e:
                                        tool_results.append({
                                            "type": "tool_result",
                                            "tool_use_id": block['id'],
                                            "content": f"Error executing {tool_name}: {e}",
                                            "is_error": True
                                        })

                            messages.append({"role": "user", "content": tool_results})
                            payload['messages'] = messages
                            continue  # Loop with tool results

                        # End of turn — extract text response
                        for block in data['content']:
                            if block['type'] == 'text':
                                return block['text'], 'success', None

                        return None, 'error', 'No text in Claude response'

                return None, 'error', 'Max tool iterations (10) reached'

        except Exception as e:
            return None, 'error', str(e)

    async def _call_grok(
        self,
        prompt: str,
        system_prompt: str,
        tools_registry,
        conversation_history: List[Dict] = None
    ) -> Tuple[Optional[str], str, Optional[str]]:
        """Call Grok (X.AI) API"""
        try:
            api_key = self.api_keys.get('grok')
            if not api_key:
                return None, 'error', 'Grok API key not found'

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})

            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    if role in ('user', 'assistant') and content:
                        messages.append({'role': role, 'content': content})

            messages.append({'role': 'user', 'content': prompt})

            # Format tools for Grok (OpenAI format)
            tools_def = []
            if tools_registry:
                for tool in tools_registry.get_all_tools_definitions():
                    tools_def.append({
                        "type": "function",
                        "function": tool
                    })

            payload = {
                'messages': messages,
                'model': 'grok-beta',
                'stream': False,
                'temperature': 0.7
            }
            if tools_def:
                payload['tools'] = tools_def

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.x.ai/v1/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return None, 'error', f"Grok API error {response.status}: {error_text[:300]}"

                    data = await response.json()
                    message = data['choices'][0]['message']

                    # Handle tool calls
                    if message.get('tool_calls') and tools_registry:
                        tool_calls = message['tool_calls']
                        messages.append(message)

                        for tool_call in tool_calls:
                            func_name = tool_call['function']['name']
                            try:
                                args = json.loads(tool_call['function']['arguments'])
                                result = tools_registry.execute_tool(func_name, args)
                            except Exception as e:
                                result = f"Error executing {func_name}: {e}"

                            messages.append({
                                "tool_call_id": tool_call['id'],
                                "role": "tool",
                                "name": func_name,
                                "content": str(result)
                            })

                        # Follow-up call without tools
                        payload['messages'] = messages
                        payload.pop('tools', None)

                        async with session.post(
                            'https://api.x.ai/v1/chat/completions',
                            headers=headers,
                            json=payload
                        ) as response2:
                            if response2.status != 200:
                                return None, 'error', f"Grok follow-up error {response2.status}"
                            data2 = await response2.json()
                            return data2['choices'][0]['message']['content'], 'success', None

                    return message['content'], 'success', None

        except Exception as e:
            return None, 'error', str(e)

    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: str,
        tools_registry,
        conversation_history: List[Dict] = None
    ) -> Tuple[Optional[str], str, Optional[str]]:
        """Call Gemini (Google) API"""
        try:
            api_key = self.api_keys.get('gemini')
            if not api_key:
                return None, 'error', 'Gemini API key not found'

            model = 'gemini-2.0-flash-exp'
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'

            # Format tools for Gemini
            tools_def = []
            if tools_registry:
                funcs = []
                for tool in tools_registry.get_all_tools_definitions():
                    props = {}
                    for k, v in tool['parameters']['properties'].items():
                        gemini_type = "STRING"
                        if v['type'] == 'integer':
                            gemini_type = "INTEGER"
                        elif v['type'] == 'number':
                            gemini_type = "NUMBER"
                        elif v['type'] == 'boolean':
                            gemini_type = "BOOLEAN"
                        elif v['type'] == 'array':
                            gemini_type = "ARRAY"
                        elif v['type'] == 'object':
                            gemini_type = "OBJECT"

                        props[k] = {
                            "type": gemini_type,
                            "description": v.get('description', '')
                        }

                    funcs.append({
                        "name": tool['name'],
                        "description": tool['description'],
                        "parameters": {
                            "type": "OBJECT",
                            "properties": props,
                            "required": tool['parameters'].get('required', [])
                        }
                    })
                tools_def = [{'function_declarations': funcs}]

            contents = []
            if system_prompt:
                contents.append({'role': 'user', 'parts': [{'text': f"System: {system_prompt}"}]})
                contents.append({'role': 'model', 'parts': [{'text': "Understood."}]})

            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    if role == 'user' and content:
                        contents.append({'role': 'user', 'parts': [{'text': content}]})
                    elif role == 'assistant' and content:
                        contents.append({'role': 'model', 'parts': [{'text': content}]})

            contents.append({'role': 'user', 'parts': [{'text': prompt}]})

            payload = {'contents': contents}
            if tools_def:
                payload['tools'] = tools_def

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return None, 'error', f"Gemini API error {response.status}: {error_text[:300]}"

                    data = await response.json()
                    candidate = data['candidates'][0]
                    parts = candidate['content']['parts']

                    func_call = next((p['functionCall'] for p in parts if 'functionCall' in p), None)

                    if func_call and tools_registry:
                        contents.append({'role': 'model', 'parts': [{'functionCall': func_call}]})

                        tool_name = func_call['name']
                        args = func_call['args']

                        try:
                            result = tools_registry.execute_tool(tool_name, args)
                        except Exception as e:
                            result = f"Error: {e}"

                        contents.append({
                            'role': 'function',
                            'parts': [{
                                'functionResponse': {
                                    'name': tool_name,
                                    'response': {'content': str(result)}
                                }
                            }]
                        })

                        payload['contents'] = contents

                        async with session.post(url, json=payload) as response2:
                            if response2.status != 200:
                                error_text2 = await response2.text()
                                return None, 'error', f"Gemini follow-up error {response2.status}: {error_text2[:200]}"
                            data2 = await response2.json()
                            parts2 = data2['candidates'][0]['content']['parts']
                            text2 = next((p['text'] for p in parts2 if 'text' in p), None)
                            return text2, 'success', None

                    text = next((p['text'] for p in parts if 'text' in p), None)
                    return text, 'success', None

        except Exception as e:
            return None, 'error', str(e)
