"""
Conversation Manager - Context and conversation history management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class ConversationManager:
    """
    Manages conversation history and context for the LLM.
    Handles context window limits and conversation persistence.
    """
    
    def __init__(self, max_messages: int = 20):
        """
        Initialize conversation manager.
        
        Args:
            max_messages: Maximum number of messages to keep in history
        """
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            'started_at': datetime.now().isoformat(),
            'message_count': 0,
            'tool_calls': 0
        }
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata (tool calls, timestamps, etc.)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            message['metadata'] = metadata
        
        self.messages.append(message)
        self.metadata['message_count'] += 1
        
        # Trim if exceeds max
        if len(self.messages) > self.max_messages:
            # Keep system message if present
            system_msgs = [m for m in self.messages if m['role'] == 'system']
            other_msgs = [m for m in self.messages if m['role'] != 'system']
            
            # Keep most recent messages
            trimmed = other_msgs[-(self.max_messages - len(system_msgs)):]
            self.messages = system_msgs + trimmed
    
    def add_tool_call(self, tool_name: str, args: Dict[str, Any], result: str):
        """
        Record a tool call in metadata.
        
        Args:
            tool_name: Name of tool called
            args: Tool arguments
            result: Tool result
        """
        self.metadata['tool_calls'] += 1
        
        if 'tool_history' not in self.metadata:
            self.metadata['tool_history'] = []
        
        self.metadata['tool_history'].append({
            'tool': tool_name,
            'args': args,
            'result_length': len(result),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 tool calls
        if len(self.metadata['tool_history']) > 50:
            self.metadata['tool_history'] = self.metadata['tool_history'][-50:]
    
    def get_messages(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        Get conversation messages.
        
        Args:
            include_system: Whether to include system messages
        
        Returns:
            List of messages
        """
        if include_system:
            return self.messages.copy()
        else:
            return [m for m in self.messages if m['role'] != 'system']
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the conversation context.
        
        Returns:
            Context summary string
        """
        summary = f"CONVERSATION CONTEXT\n"
        summary += "="*50 + "\n"
        summary += f"Started: {self.metadata['started_at']}\n"
        summary += f"Messages: {self.metadata['message_count']}\n"
        summary += f"Tool Calls: {self.metadata['tool_calls']}\n"
        summary += f"Current History: {len(self.messages)} messages\n"
        
        if 'tool_history' in self.metadata:
            recent_tools = self.metadata['tool_history'][-5:]
            summary += f"\nRecent Tools:\n"
            for tool in recent_tools:
                summary += f"  - {tool['tool']} ({tool['timestamp']})\n"
        
        return summary
    
    def clear_history(self, keep_system: bool = True):
        """
        Clear conversation history.
        
        Args:
            keep_system: Whether to keep system messages
        """
        if keep_system:
            system_msgs = [m for m in self.messages if m['role'] == 'system']
            self.messages = system_msgs
        else:
            self.messages = []
        
        self.metadata['message_count'] = len(self.messages)
    
    def export_conversation(self) -> Dict[str, Any]:
        """
        Export conversation for persistence.
        
        Returns:
            Dictionary with conversation data
        """
        return {
            'messages': self.messages,
            'metadata': self.metadata,
            'exported_at': datetime.now().isoformat()
        }
    
    def import_conversation(self, data: Dict[str, Any]):
        """
        Import conversation from exported data.
        
        Args:
            data: Exported conversation data
        """
        self.messages = data.get('messages', [])
        self.metadata = data.get('metadata', {})
    
    def get_token_estimate(self) -> int:
        """
        Estimate token count for current conversation.
        Rough estimate: ~4 characters per token.
        
        Returns:
            Estimated token count
        """
        total_chars = sum(len(m['content']) for m in self.messages)
        return total_chars // 4
    
    def should_summarize(self, token_limit: int = 8000) -> bool:
        """
        Check if conversation should be summarized to save tokens.
        
        Args:
            token_limit: Token limit threshold
        
        Returns:
            True if should summarize
        """
        return self.get_token_estimate() > token_limit
