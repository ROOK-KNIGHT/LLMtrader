"""
Position Tools - LLM position monitoring and management
"""

import sys
import os
import json
from typing import Dict, Any, List
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class PositionTools:
    """
    Tools for LLM-managed position monitoring with trigger-based reviews.
    Allows the LLM to register positions for monitoring and receive alerts when triggers fire.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize position tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
        self.managed_positions = {}  # In-memory storage (would use DB in production)
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'register_position',
                'description': 'Register a position for LLM monitoring with price triggers. The LLM will be alerted when triggers fire for review.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Underlying symbol (e.g., AAPL, TSLA)'
                        },
                        'position_type': {
                            'type': 'string',
                            'description': 'Position type: STOCK, OPTION, SPREAD'
                        },
                        'quantity': {
                            'type': 'number',
                            'description': 'Position size (shares or contracts)'
                        },
                        'entry_price': {
                            'type': 'number',
                            'description': 'Entry price'
                        },
                        'current_price': {
                            'type': 'number',
                            'description': 'Current market price'
                        },
                        'trade_thesis': {
                            'type': 'string',
                            'description': 'Why you entered this trade (2-3 sentences)'
                        },
                        'triggers': {
                            'type': 'array',
                            'description': 'Array of price triggers for review',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'trigger_price': {'type': 'number'},
                                    'direction': {'type': 'string', 'enum': ['above', 'below']},
                                    'trigger_type': {'type': 'string', 'enum': ['profit_target', 'stop_loss', 'thesis_check', 'price_level']},
                                    'notes': {'type': 'string'}
                                }
                            }
                        },
                        'option_details': {
                            'type': 'object',
                            'description': 'Option details if position_type is OPTION',
                            'properties': {
                                'option_symbol': {'type': 'string'},
                                'strike': {'type': 'number'},
                                'expiration': {'type': 'string'},
                                'option_type': {'type': 'string', 'enum': ['CALL', 'PUT']}
                            }
                        }
                    },
                    'required': ['symbol', 'position_type', 'quantity', 'entry_price', 'current_price', 'trade_thesis', 'triggers']
                }
            },
            {
                'name': 'update_triggers',
                'description': 'Update trigger levels on an existing monitored position.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'position_id': {
                            'type': 'string',
                            'description': 'Position ID to update'
                        },
                        'triggers': {
                            'type': 'array',
                            'description': 'New trigger array (replaces existing)',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'trigger_price': {'type': 'number'},
                                    'direction': {'type': 'string'},
                                    'trigger_type': {'type': 'string'},
                                    'notes': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'required': ['position_id', 'triggers']
                }
            },
            {
                'name': 'submit_decision',
                'description': 'Submit your decision after reviewing a position (HOLD, TAKE_PROFIT, CUT_LOSS, ADJUST_TRIGGERS).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'position_id': {
                            'type': 'string',
                            'description': 'Position ID being reviewed'
                        },
                        'decision': {
                            'type': 'string',
                            'enum': ['HOLD', 'TAKE_PROFIT', 'CUT_LOSS', 'ADJUST_TRIGGERS'],
                            'description': 'Your decision'
                        },
                        'rationale': {
                            'type': 'string',
                            'description': 'Brief explanation (2-3 sentences)'
                        },
                        'new_triggers': {
                            'type': 'array',
                            'description': 'New triggers if decision is ADJUST_TRIGGERS',
                            'items': {'type': 'object'}
                        }
                    },
                    'required': ['position_id', 'decision', 'rationale']
                }
            },
            {
                'name': 'get_managed_positions',
                'description': 'Get all positions currently being monitored by the LLM.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'description': 'Filter by status: ACTIVE, CLOSED, ALL (default: ACTIVE)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'close_position',
                'description': 'Mark a position as closed and stop monitoring.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'position_id': {
                            'type': 'string',
                            'description': 'Position ID to close'
                        },
                        'exit_price': {
                            'type': 'number',
                            'description': 'Exit price'
                        },
                        'exit_reason': {
                            'type': 'string',
                            'description': 'Reason for exit'
                        }
                    },
                    'required': ['position_id', 'exit_price', 'exit_reason']
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'register_position':
            return self._register_position(**args)
        elif tool_name == 'update_triggers':
            return self._update_triggers(**args)
        elif tool_name == 'submit_decision':
            return self._submit_decision(**args)
        elif tool_name == 'get_managed_positions':
            return self._get_managed_positions(**args)
        elif tool_name == 'close_position':
            return self._close_position(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _register_position(self, symbol: str, position_type: str, quantity: float,
                          entry_price: float, current_price: float, trade_thesis: str,
                          triggers: List[Dict], option_details: Dict = None) -> str:
        """Register position for monitoring"""
        try:
            # Generate position ID
            position_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store position
            self.managed_positions[position_id] = {
                'position_id': position_id,
                'symbol': symbol,
                'position_type': position_type,
                'quantity': quantity,
                'entry_price': entry_price,
                'current_price': current_price,
                'trade_thesis': trade_thesis,
                'triggers': triggers,
                'option_details': option_details,
                'status': 'ACTIVE',
                'registered_at': datetime.now().isoformat(),
                'last_review': None,
                'review_count': 0
            }
            
            # Calculate P&L
            pnl = (current_price - entry_price) * quantity
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            output = f"✅ POSITION REGISTERED FOR LLM MONITORING\n"
            output += "="*80 + "\n\n"
            output += f"Position ID: {position_id}\n"
            output += f"Symbol: {symbol}\n"
            output += f"Type: {position_type}\n"
            output += f"Quantity: {quantity}\n"
            output += f"Entry: ${entry_price:.2f}\n"
            output += f"Current: ${current_price:.2f}\n"
            output += f"P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n\n"
            
            if option_details:
                output += f"Option: {option_details.get('option_symbol', 'N/A')}\n"
                output += f"Strike: ${option_details.get('strike', 0):.2f}\n"
                output += f"Expiration: {option_details.get('expiration', 'N/A')}\n"
                output += f"Type: {option_details.get('option_type', 'N/A')}\n\n"
            
            output += f"TRADE THESIS:\n{trade_thesis}\n\n"
            
            output += f"TRIGGERS ({len(triggers)}):\n"
            for i, trigger in enumerate(triggers, 1):
                output += f"  {i}. ${trigger['trigger_price']:.2f} ({trigger['direction']}) - {trigger['trigger_type']}\n"
                if trigger.get('notes'):
                    output += f"     Notes: {trigger['notes']}\n"
            
            output += "\n🔔 You will be alerted when any trigger fires for position review.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error registering position: {str(e)}"
    
    def _update_triggers(self, position_id: str, triggers: List[Dict]) -> str:
        """Update position triggers"""
        try:
            if position_id not in self.managed_positions:
                return f"Error: Position {position_id} not found"
            
            self.managed_positions[position_id]['triggers'] = triggers
            
            output = f"✅ TRIGGERS UPDATED\n"
            output += "="*80 + "\n\n"
            output += f"Position: {position_id}\n\n"
            output += f"NEW TRIGGERS ({len(triggers)}):\n"
            for i, trigger in enumerate(triggers, 1):
                output += f"  {i}. ${trigger['trigger_price']:.2f} ({trigger['direction']}) - {trigger['trigger_type']}\n"
                if trigger.get('notes'):
                    output += f"     Notes: {trigger['notes']}\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error updating triggers: {str(e)}"
    
    def _submit_decision(self, position_id: str, decision: str, rationale: str,
                        new_triggers: List[Dict] = None) -> str:
        """Submit position review decision"""
        try:
            if position_id not in self.managed_positions:
                return f"Error: Position {position_id} not found"
            
            position = self.managed_positions[position_id]
            position['last_review'] = datetime.now().isoformat()
            position['review_count'] += 1
            
            output = f"✅ DECISION RECORDED\n"
            output += "="*80 + "\n\n"
            output += f"Position: {position_id}\n"
            output += f"Decision: {decision}\n"
            output += f"Rationale: {rationale}\n\n"
            
            if decision == 'ADJUST_TRIGGERS' and new_triggers:
                position['triggers'] = new_triggers
                output += f"NEW TRIGGERS ({len(new_triggers)}):\n"
                for i, trigger in enumerate(new_triggers, 1):
                    output += f"  {i}. ${trigger['trigger_price']:.2f} ({trigger['direction']}) - {trigger['trigger_type']}\n"
            elif decision == 'TAKE_PROFIT' or decision == 'CUT_LOSS':
                output += "⚠️  Remember to execute the exit order using place_order tool.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error submitting decision: {str(e)}"
    
    def _get_managed_positions(self, status: str = 'ACTIVE') -> str:
        """Get managed positions"""
        try:
            if not self.managed_positions:
                return "No positions being monitored"
            
            # Filter by status
            if status == 'ALL':
                positions = list(self.managed_positions.values())
            else:
                positions = [p for p in self.managed_positions.values() if p['status'] == status]
            
            if not positions:
                return f"No {status} positions"
            
            output = f"LLM-MANAGED POSITIONS ({len(positions)})\n"
            output += "="*80 + "\n\n"
            
            for pos in positions:
                pnl = (pos['current_price'] - pos['entry_price']) * pos['quantity']
                pnl_pct = ((pos['current_price'] - pos['entry_price']) / pos['entry_price']) * 100
                
                output += f"📊 {pos['position_id']}\n"
                output += f"   {pos['symbol']} | {pos['position_type']} | {pos['quantity']} units\n"
                output += f"   Entry: ${pos['entry_price']:.2f} | Current: ${pos['current_price']:.2f}\n"
                output += f"   P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n"
                output += f"   Triggers: {len(pos['triggers'])} active\n"
                output += f"   Reviews: {pos['review_count']}\n"
                output += f"   Status: {pos['status']}\n\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting positions: {str(e)}"
    
    def _close_position(self, position_id: str, exit_price: float, exit_reason: str) -> str:
        """Close position"""
        try:
            if position_id not in self.managed_positions:
                return f"Error: Position {position_id} not found"
            
            position = self.managed_positions[position_id]
            position['status'] = 'CLOSED'
            position['exit_price'] = exit_price
            position['exit_reason'] = exit_reason
            position['closed_at'] = datetime.now().isoformat()
            
            # Calculate final P&L
            pnl = (exit_price - position['entry_price']) * position['quantity']
            pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            
            output = f"✅ POSITION CLOSED\n"
            output += "="*80 + "\n\n"
            output += f"Position: {position_id}\n"
            output += f"Symbol: {position['symbol']}\n"
            output += f"Entry: ${position['entry_price']:.2f}\n"
            output += f"Exit: ${exit_price:.2f}\n"
            output += f"Final P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n"
            output += f"Reason: {exit_reason}\n"
            output += f"Reviews: {position['review_count']}\n\n"
            output += "Position monitoring stopped.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error closing position: {str(e)}"
