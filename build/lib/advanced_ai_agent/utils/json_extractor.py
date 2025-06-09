"""
JSON extraction utilities for parsing AI responses.
"""

import json
import re
from typing import Dict, Any, List


class JSONExtractor:
    """
    Utility class for extracting and parsing JSON from text responses.
    """
    
    def __init__(self):
        self.json_patterns = [
            # Standard JSON block
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            # JSON with nested objects (more complex)
            r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}',
        ]
    
    def extract_json_block(self, text: str) -> Dict[str, Any]:
        """
        Extract and parse the first valid JSON object from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValueError: If no valid JSON found
        """
        # First try to find JSON blocks using balanced bracket matching
        candidates = self._find_json_candidates(text)
        
        if not candidates:
            raise ValueError("No JSON object found in the text.")
        
        # Try parsing candidates with progressive cleanup
        for candidate in candidates:
            # Try direct parsing first
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
            
            # Try with cleanup
            cleaned = self._clean_json_string(candidate)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue
        
        # If all candidates failed, try extracting from code blocks
        code_block_json = self._extract_from_code_blocks(text)
        if code_block_json:
            try:
                return json.loads(code_block_json)
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Failed to parse any JSON block in the text:\n{text[:500]}...")
    
    def _find_json_candidates(self, text: str) -> List[str]:
        """Find potential JSON objects using balanced bracket matching."""
        candidates = []
        stack = []
        start_idx = None
        
        for i, ch in enumerate(text):
            if ch == '{':
                if not stack:
                    start_idx = i
                stack.append(ch)
            elif ch == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx is not None:
                        candidates.append(text[start_idx:i+1])
                        start_idx = None
        
        return candidates
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON formatting issues."""
        # Remove trailing commas before closing brackets/braces
        cleaned = re.sub(r',(\s*[\]}])', r'\1', json_str)
        
        # Fix triple quotes and similar issues
        cleaned = cleaned.replace('\n"""', '\n').replace('"""', '\n')
        cleaned = cleaned.replace("\n'''", '\n').replace("'''", '\n')
        
        # Remove comments (// and /* */)
        cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        # Fix unescaped quotes in strings (basic attempt)
        # This is a simple heuristic and may not work for all cases
        cleaned = re.sub(r'(?<!\\)"([^"]*)"([^"]*)"', r'"\1\"\2"', cleaned)
        
        return cleaned
    
    def _extract_from_code_blocks(self, text: str) -> str:
        """Extract JSON from markdown code blocks."""
        # Look for ```json or ``` code blocks
        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(\{.*?\})\s*\n```',
            r'`([^`]*\{[^`]*\}[^`]*)`'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                # Basic validation that it looks like JSON
                if '{' in match and '}' in match:
                    return match.strip()
        
        return ""
    
    def extract_multiple_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract multiple JSON objects from text.
        
        Args:
            text: Text containing multiple JSON objects
            
        Returns:
            List of parsed JSON objects
        """
        candidates = self._find_json_candidates(text)
        results = []
        
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                results.append(parsed)
            except json.JSONDecodeError:
                # Try with cleanup
                cleaned = self._clean_json_string(candidate)
                try:
                    parsed = json.loads(cleaned)
                    results.append(parsed)
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def validate_json_structure(self, json_obj: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that a JSON object has required fields.
        
        Args:
            json_obj: JSON object to validate
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
        """
        return all(field in json_obj for field in required_fields)
    
    def extract_with_fallback(self, text: str, fallback_pattern: str = None) -> Dict[str, Any]:
        """
        Extract JSON with fallback to regex pattern if JSON parsing fails.
        
        Args:
            text: Text to extract from
            fallback_pattern: Regex pattern to use as fallback
            
        Returns:
            Parsed JSON or constructed object from regex
        """
        try:
            return self.extract_json_block(text)
        except ValueError:
            if fallback_pattern:
                match = re.search(fallback_pattern, text, re.DOTALL)
                if match:
                    # Construct a basic JSON object from regex groups
                    groups = match.groups()
                    if len(groups) >= 3:
                        return {
                            "thought": groups[0].strip(),
                            "action": groups[1].strip(),
                            "args": {"query": groups[2].strip()} if groups[2] else {}
                        }
            
            # Last resort: try to extract key information manually
            return self._manual_extraction(text)
    
    def _manual_extraction(self, text: str) -> Dict[str, Any]:
        """Manual extraction as last resort."""
        # Look for common patterns
        thought_match = re.search(r'(?:thought|thinking)[:=]\s*["\']?([^"\'\n]+)', text, re.IGNORECASE)
        action_match = re.search(r'(?:action|tool)[:=]\s*["\']?([^"\'\n]+)', text, re.IGNORECASE)
        
        result = {
            "thought": thought_match.group(1).strip() if thought_match else "No clear thought found",
            "action": action_match.group(1).strip() if action_match else "finish",
            "args": {}
        }
        
        return result