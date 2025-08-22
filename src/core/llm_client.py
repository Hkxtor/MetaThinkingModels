"""
LLM Client for ThinkingModels

This module provides a client for interacting with OpenAI-compatible LLM APIs
with proper error handling, retry logic, and configuration support.
"""

import os
import time
import json
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """
    Configuration for LLM API client
    """
    api_url: str
    api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """
        Create config from environment variables
        
        Returns:
            LLMConfig instance with values from environment
        """
        api_url = os.getenv('LLM_API_URL')
        if not api_url:
            raise ValueError("LLM_API_URL environment variable must be set")
        
        return cls(
            api_url=api_url,
            api_key=os.getenv('LLM_API_KEY'),
            model_name=os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
            timeout=int(os.getenv('LLM_TIMEOUT', '30')),
            max_retries=int(os.getenv('LLM_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('LLM_RETRY_DELAY', '1.0'))
        )


class LLMClient:
    """
    Client for interacting with OpenAI-compatible LLM APIs
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LLM client
        
        Args:
            config: LLM configuration. If None, loads from environment
        """
        self.config = config or LLMConfig.from_env()
        self.session = requests.Session()
        
        # Set up headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ThinkingModels/1.0'
        })
        
        # Add API key if provided
        if self.config.api_key:
            self.session.headers['Authorization'] = f'Bearer {self.config.api_key}'
    
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Make a request to the LLM API with retry logic
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API call
            
        Returns:
            API response dictionary
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        payload = {
            'model': self.config.model_name,
            'messages': messages,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens,
            **kwargs
        }
        
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Making LLM API request (attempt {attempt + 1}/{self.config.max_retries})")
                
                # Determine the correct endpoint
                if self.config.api_url.endswith('/v1') or self.config.api_url.endswith('/v1/'):
                    endpoint = f"{self.config.api_url.rstrip('/')}/chat/completions"
                else:
                    endpoint = f"{self.config.api_url.rstrip('/')}/v1/chat/completions"
                
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=self.config.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info("LLM API request successful")
                return result
                
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"API request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                    
        raise RuntimeError(f"LLM API request failed after {self.config.max_retries} attempts. Last error: {last_error}")
    
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from LLM API response
        
        Args:
            response: API response dictionary
            
        Returns:
            Extracted content string
        """
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid API response format: {e}")
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt to set context
            
        Returns:
            Generated response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self._make_request(messages)
        return self._extract_content(response)
    
    def request_model_selection(self, query: str, available_models: List[Dict[str, Any]]) -> List[str]:
        """
        Request LLM to select relevant thinking models for a query
        
        Args:
            query: User's query
            available_models: List of available model data (with id and definition)
            
        Returns:
            List of selected model IDs
        """
        system_prompt = """
You are an expert at selecting relevant thinking models for problem-solving.
Given a user query and a list of available thinking models with their definitions, select only those that are potentially helpful.

Your response should be a JSON list of model IDs, like: ["model1", "model2", "model3"]
Select between 0-3 of the most relevant models. Only select a model when it's truly useful. If no model fits, select none.
"""
        
        # Format available models with definitions
        models_text = ""
        for model in available_models:
            models_text += f"**{model['id']}**: {model['definition'][:300]}...\n\n"
        
        user_prompt = f"""
User Query: {query}

Available Thinking Models:
{models_text}

Select the most relevant thinking models for this query:
"""
        
        response = self.generate_response(user_prompt, system_prompt)
        
        # Try to parse the JSON response
        try:
            # Clean up the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3].strip()
            elif response.startswith('```'):
                response = response[3:-3].strip()
            
            selected_models = json.loads(response)
            
            # Validate that selected models are in available models
            available_model_ids = [model['id'] for model in available_models]
            valid_models = [model for model in selected_models if model in available_model_ids]
            
            # Limit to maximum 3 models
            valid_models = valid_models[:3]
            
            if not valid_models:
                logger.warning("No valid models selected, returning empty list")
                return []
            
            return valid_models
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse model selection response: {response}")
            # Fallback: return empty list if parsing fails
            return []
    
    def request_solution(self, query: str, selected_models: List[Dict[str, Any]]) -> str:
        """
        Request LLM to solve a problem using selected thinking models
        
        Args:
            query: User's query
            selected_models: List of selected thinking model data
            
        Returns:
            Generated solution
        """
        system_prompt = """
You are an expert problem solver. You have been provided with thinking models that may assist in solving a user's query.
Only use these thinking models as guidance if they are helpful. Otherwise, feel free to ignore them.

For each thinking model provided, consider:
1. Its applicability to the problem
2. Whether using its methodology adds value
3. If so, explicitly reference it in your solution

Provide a clear, structured response that demonstrates thoughtful application when relevant, but don't force their use.
"""
        
        # Format the thinking models for the prompt
        models_text = ""
        for i, model in enumerate(selected_models, 1):
            models_text += f"""
{i}. **{model['id']}** ({model['type']})
   Definition: {model['definition']}
   
   Examples:
"""
            for j, example in enumerate(model['examples'], 1):
                models_text += f"   {j}. {example[:200]}...\n"
            models_text += "\n"
        
        user_prompt = f"""
User Query: {query}

Relevant Thinking Models:
{models_text}

Using these thinking models as guidance, provide a comprehensive solution to the user's query:
"""
        
        return self.generate_response(user_prompt, system_prompt)
    
    def test_connection(self) -> bool:
        """
        Test the connection to the LLM API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate_response("Hello, please respond with 'OK' if you can hear me.")
            return "OK" in response or "ok" in response.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

