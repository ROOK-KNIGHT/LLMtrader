<template>
  <div class="prompt-library">
    <div class="prompt-category" v-for="category in promptCategories" :key="category.id">
      <div class="category-header">
        <span class="category-icon">{{ category.icon }}</span>
        <span class="category-title">{{ category.title }}</span>
      </div>
      
      <div class="prompt-cards">
        <div 
          v-for="prompt in category.prompts" 
          :key="prompt.id"
          class="prompt-card"
          @click="$emit('select-prompt', prompt)"
        >
          <div class="prompt-card-header">
            <span class="prompt-title">{{ prompt.title }}</span>
            <span v-if="prompt.autoExecute" class="badge badge-warning" style="font-size: 0.65rem;">
              AUTO
            </span>
          </div>
          <p class="prompt-description">{{ prompt.description }}</p>
          <div class="prompt-meta">
            <span class="meta-item">{{ prompt.timeframe }}</span>
            <span class="meta-item" :class="`risk-${prompt.risk}`">{{ prompt.risk }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['select-prompt'])

const promptCategories = [
  {
    id: 'quick',
    icon: '',
    title: 'Quick Plays',
    prompts: [
      {
        id: 'best_trade_now',
        title: 'Best Trade Right Now',
        description: 'Scan all setups and find the #1 highest-conviction trade',
        timeframe: '1-5 days',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Scan the market and find me the best options trade right now with the highest conviction. Analyze volatility, momentum, support/resistance, and sentiment. Give me one clear recommendation with entry, target, and stop.'
      },
      {
        id: 'momentum_scalp',
        title: 'Momentum Scalp',
        description: 'Volume spike + price acceleration for quick 1-3% plays',
        timeframe: '15min-2hrs',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Find intraday momentum scalp opportunities: stocks with volume spikes >200% and price acceleration >1% in the last 30 minutes. Target 1-3% moves.'
      },
      {
        id: 'opening_range',
        title: 'Opening Range Breakout',
        description: 'Trade the break of first 30-min range on gap stocks',
        timeframe: '30min-4hrs',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Identify Opening Range Breakout setups: stocks with gaps >1% and consolidation in first 30 minutes. Find the best breakout candidate for 2-5% move.'
      }
    ]
  },
  {
    id: 'market',
    icon: '',
    title: 'Market Overview',
    prompts: [
      {
        id: 'top_movers',
        title: 'Top Movers',
        description: 'Biggest gainers and losers with volume analysis',
        timeframe: 'Today',
        risk: 'info',
        autoExecute: false,
        prompt: 'Show me the top 10 movers today (both gainers and losers) with volume analysis. Explain what\'s driving each move and if there\'s a tradeable setup.'
      },
      {
        id: 'sector_rotation',
        title: 'Sector Rotation',
        description: 'Which sectors are leading and lagging today',
        timeframe: 'Today',
        risk: 'info',
        autoExecute: false,
        prompt: 'Analyze sector rotation today. Which sectors are leading and lagging? What\'s the macro narrative driving this rotation? Any sector pair trades?'
      },
      {
        id: 'market_regime',
        title: 'Market Regime',
        description: 'Current market environment and positioning strategy',
        timeframe: 'This Week',
        risk: 'info',
        autoExecute: false,
        prompt: 'What\'s the current market regime? (trending, ranging, volatile). Analyze SPY, QQQ, VIX. What\'s the best positioning strategy for this environment?'
      }
    ]
  },
  {
    id: 'news',
    icon: '',
    title: 'News & Events',
    prompts: [
      {
        id: 'breaking_news',
        title: 'Breaking News Impact',
        description: 'Latest market-moving news and trading implications',
        timeframe: 'Last Hour',
        risk: 'info',
        autoExecute: false,
        prompt: 'What are the most important market-moving news events in the last hour? Analyze the impact on specific stocks and sectors. Any immediate trading opportunities?'
      },
      {
        id: 'earnings_calendar',
        title: 'Earnings This Week',
        description: 'Upcoming earnings with volatility analysis',
        timeframe: 'This Week',
        risk: 'info',
        autoExecute: false,
        prompt: 'Show me the most important earnings reports this week. For each, analyze: historical earnings move, current IV vs HV, and whether options are priced correctly. Any straddle opportunities?'
      },
      {
        id: 'fed_events',
        title: 'Fed & Macro Events',
        description: 'Upcoming Fed meetings and economic data releases',
        timeframe: 'Next 2 Weeks',
        risk: 'info',
        autoExecute: false,
        prompt: 'What are the key Fed and macro events in the next 2 weeks? (FOMC, CPI, jobs report, etc.). How should I position ahead of these events?'
      }
    ]
  },
  {
    id: 'volatility',
    icon: '',
    title: 'Volatility & Options',
    prompts: [
      {
        id: 'vol_skew',
        title: 'Volatility Skew Anomalies',
        description: 'Options where IV is underpricing realized moves',
        timeframe: '1-2 weeks',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Scan for volatility skew anomalies where historical volatility significantly exceeds implied volatility. Find the top 3 underpriced options opportunities.'
      },
      {
        id: 'gamma_squeeze',
        title: 'Gamma Exposure Zones',
        description: 'Heavy options OI near price for potential squeeze',
        timeframe: '1-3 days',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Find stocks with extreme gamma exposure - heavy options open interest concentration near current price. Identify potential pinning zones or breakout acceleration areas.'
      },
      {
        id: 'earnings_straddle',
        title: 'Earnings Straddle Dislocation',
        description: 'Options priced too cheap vs historical earnings moves',
        timeframe: 'Pre-earnings',
        risk: 'moderate',
        autoExecute: true,
        prompt: 'Identify pre-earnings setups where the implied move (from ATM straddle pricing) differs significantly from historical earnings gap moves. Find underpriced volatility opportunities.'
      }
    ]
  },
  {
    id: 'portfolio',
    icon: '',
    title: 'Portfolio Management',
    prompts: [
      {
        id: 'portfolio_review',
        title: 'Full Portfolio Review',
        description: 'Analyze every position: hold, trim, or exit?',
        timeframe: 'Current',
        risk: 'info',
        autoExecute: false,
        prompt: 'Review my entire portfolio. For each position, analyze: current thesis validity, technical setup, risk/reward, and whether I should hold, trim, or exit. Be brutally honest.'
      },
      {
        id: 'risk_audit',
        title: 'Portfolio Risk Audit',
        description: 'Check for hidden sector/factor concentration',
        timeframe: 'Current',
        risk: 'info',
        autoExecute: false,
        prompt: 'Audit my portfolio for risk concentration. Check for hidden exposures to specific sectors, factors (momentum, value, growth), or correlated positions. Suggest hedges if needed.'
      },
      {
        id: 'tail_risk_hedge',
        title: 'Build Tail Risk Hedge',
        description: 'Cheap downside protection for current positions',
        timeframe: '45-day hedge',
        risk: 'limited',
        autoExecute: true,
        prompt: 'Design a cost-effective tail risk hedge for my portfolio using SPX puts or put spreads. Optimize for minimal theta decay while providing meaningful downside protection.'
      }
    ]
  }
]
</script>

<style scoped>
.prompt-library {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
  overflow-y: auto;
  height: 100%;
}

.prompt-category {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-primary);
}

.category-icon {
  font-size: 1.25rem;
}

.category-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.prompt-cards {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.prompt-card:hover {
  border-color: var(--accent-primary);
  background: var(--bg-hover);
  transform: translateX(2px);
}

.prompt-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.prompt-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.prompt-description {
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.prompt-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.65rem;
}

.meta-item {
  padding: 0.125rem 0.375rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.risk-moderate {
  background: rgba(245, 158, 11, 0.1);
  color: var(--accent-warning);
}

.risk-limited {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.risk-info {
  background: rgba(6, 182, 212, 0.1);
  color: var(--accent-info);
}
</style>
