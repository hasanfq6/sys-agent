"""
AI interface abstraction for different AI providers.
"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class BaseAIInterface(ABC):
    """Abstract base class for AI interfaces."""
    
    @abstractmethod
    def ask(self, prompt: str) -> str:
        """Ask the AI a question and return the response."""
        pass


class AutoAIInterface(BaseAIInterface):
    """Interface using pytgpt.auto.AUTO."""
    
    def __init__(self):
        try:
            from pytgpt.auto import AUTO
            self.ai = AUTO()
        except ImportError:
            # Fallback to a mock interface for demonstration
            self.ai = None
            print("Warning: pytgpt not available. Using mock AI interface.")
    
    def ask(self, prompt: str) -> str:
        """Ask the AI using pytgpt AUTO with timeout handling."""
        if self.ai is None:
            # Mock response for demonstration
            return """
{
  "thought": "This is a mock response since pytgpt is not available.",
  "action": "finish",
  "args": {}
}
"""
        
        try:
            # Add timeout handling
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("AI request timed out")
            
            # Set timeout to 30 seconds
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                response = self.ai.ask(prompt)
            finally:
                signal.alarm(0)  # Cancel the alarm
            
            # Handle different response formats
            if isinstance(response, dict):
                # Try different paths for the response content
                text = (
                    response.get("choices", [{}])[0].get("delta", {}).get("content") or
                    response.get("choices", [{}])[0].get("message", {}).get("content") or
                    response.get("content") or
                    response.get("token") or  # Handle token-based responses
                    response.get("text") or   # Handle text-based responses
                    str(response)
                )
                
                # Special handling for token-based and text-based responses that contain JSON
                content_field = None
                if "token" in response and isinstance(response["token"], str):
                    content_field = response["token"]
                elif "text" in response and isinstance(response["text"], str):
                    content_field = response["text"]
                
                if content_field:
                    content = content_field.strip()
                    # If content contains what looks like JSON, extract it properly
                    if '{' in content and '}' in content:
                        # Find the first complete JSON object
                        stack = []
                        start_idx = None
                        
                        for i, ch in enumerate(content):
                            if ch == '{':
                                if not stack:
                                    start_idx = i
                                stack.append(ch)
                            elif ch == '}':
                                if stack:
                                    stack.pop()
                                    if not stack and start_idx is not None:
                                        # Found complete JSON object
                                        text = content[start_idx:i+1]
                                        break
                        
                        # If we didn't find a complete JSON, try simple extraction
                        if not text or text == str(response):
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            if start != -1 and end > start:
                                text = content[start:end]
            else:
                text = str(response)
            
            # Validate response is not empty
            if not text or text.strip() == "":
                return """
{
  "thought": "AI returned empty response, finishing task.",
  "action": "finish",
  "args": {}
}
"""
            
            return text.strip()
            
        except TimeoutError:
            return """
{
  "thought": "AI request timed out, finishing task.",
  "action": "finish",
  "args": {}
}
"""
        except Exception as e:
            return f"""
{{
  "thought": "Error communicating with AI: {str(e)}",
  "action": "finish",
  "args": {{}}
}}
"""


class OpenAIInterface(BaseAIInterface):
    """Interface for OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai is required for OpenAIInterface. Install with: pip install openai")
    
    def ask(self, prompt: str) -> str:
        """Ask OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"


class AnthropicInterface(BaseAIInterface):
    """Interface for Anthropic Claude API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("anthropic is required for AnthropicInterface. Install with: pip install anthropic")
    
    def ask(self, prompt: str) -> str:
        """Ask Anthropic Claude API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Anthropic API Error: {str(e)}"


class AIInterface:
    """
    Main AI interface that can use different providers.
    """
    
    def __init__(self, provider: str = "auto", **kwargs):
        self.provider = provider
        
        if provider == "auto":
            self.interface = AutoAIInterface()
        elif provider == "openai":
            self.interface = OpenAIInterface(**kwargs)
        elif provider == "anthropic":
            self.interface = AnthropicInterface(**kwargs)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
    
    def ask(self, prompt: str) -> str:
        """Ask the AI interface."""
        return self.interface.ask(prompt)
    
    def get_provider(self) -> str:
        """Get the current provider name."""
        return self.provider