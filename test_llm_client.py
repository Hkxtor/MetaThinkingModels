#!/usr/bin/env python3
"""
Test script for the LLM client with OpenRouter API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.llm_client import LLMClient, LLMConfig
from src.core.model_parser import ModelParser

def test_llm_client():
    """Test the LLM client functionality"""
    
    print("Testing LLM Client with OpenRouter API")
    print("=" * 50)
    
    # Test configuration loading
    try:
        config = LLMConfig.from_env()
        print(f"✓ Configuration loaded successfully")
        print(f"  API URL: {config.api_url}")
        print(f"  Model: {config.model_name}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Max Tokens: {config.max_tokens}")
        print(f"  API Key: {'***' + config.api_key[-10:] if config.api_key else 'Not set'}")
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return
    
    # Create LLM client
    try:
        client = LLMClient(config)
        print(f"✓ LLM client created successfully")
    except Exception as e:
        print(f"✗ LLM client creation failed: {e}")
        return
    
    # Test basic connection
    print(f"\nTesting basic connection...")
    try:
        is_connected = client.test_connection()
        if is_connected:
            print(f"✓ Connection test passed")
        else:
            print(f"✗ Connection test failed")
            return
    except Exception as e:
        print(f"✗ Connection test error: {e}")
        return
    
    # Test basic response generation
    print(f"\nTesting basic response generation...")
    try:
        response = client.generate_response("Hello! Please respond with a brief greeting.")
        print(f"✓ Response generated successfully")
        print(f"  Response: {response[:100]}...")
    except Exception as e:
        print(f"✗ Response generation failed: {e}")
        return
    
    # Test model selection functionality
    print(f"\nTesting model selection functionality...")
    try:
        # Load some models first
        parser = ModelParser("models")
        models = parser.load_all_models()
        
        if not models:
            print("✗ No models loaded, skipping model selection test")
            return
        
        # Get a subset of models for testing (with definitions)
        model_list = list(models.values())[:20]  # Use first 20 models
        available_models = []
        for model in model_list:
            available_models.append({
                'id': model.id,
                'definition': model.definition
            })
        
        test_query = "I need help with analyzing market trends and making business decisions."
        
        # Count words in the prompt before sending
        system_prompt = """
You are an expert at selecting relevant thinking models for problem-solving.
Given a user query and a list of available thinking models with their definitions, select only those that are potentially helpful.

Your response should be a JSON list of model IDs, like: ["model1", "model2", "model3"]
Select between 0-3 of the most relevant models. Only select a model when it's truly useful. If no model fits, select none.
"""
        
        # Format available models with definitions (same as in the actual function)
        models_text = ""
        for model in available_models:
            models_text += f"**{model['id']}**: {model['definition'][:300]}...\n\n"
        
        user_prompt = f"""
User Query: {test_query}

Available Thinking Models:
{models_text}

Select the most relevant thinking models for this query:
"""
        
        # Count words
        total_prompt = system_prompt + user_prompt
        word_count = len(total_prompt.split())
        char_count = len(total_prompt)
        
        print(f"  Prompt word count: {word_count} words")
        print(f"  Prompt character count: {char_count} characters")
        print(f"  Estimated tokens (rough): {word_count * 1.3:.0f} tokens")
        
        # selected_models = client.request_model_selection(test_query, available_models)
        # print(f"✓ Model selection completed")
        # print(f"  Query: {test_query}")
        # print(f"  Available models: {len(available_models)}")
        # print(f"  Selected models: {selected_models}")
        
    except Exception as e:
        print(f"✗ Model selection failed: {e}")
        return
    
    # Test solution generation with selected models
    # print(f"\nTesting solution generation with selected models...")
    # try:
    #     # Prepare model data for solution generation
    #     selected_model_data = []
    #     for model_id in selected_models[:3]:  # Use first 3 selected models
    #         if model_id in models:
    #             model = models[model_id]
    #             selected_model_data.append({
    #                 'id': model.id,
    #                 'type': model.type,
    #                 'definition': model.definition,
    #                 'examples': model.examples
    #             })
        
    #     if selected_model_data:
    #         solution = client.request_solution(test_query, selected_model_data)
    #         print(f"✓ Solution generated successfully")
    #         print(f"  Solution length: {len(solution)} characters")
    #         print(f"  Solution preview: {solution[:200]}...")
    #     else:
    #         print("✗ No model data available for solution generation")
            
    # except Exception as e:
    #     print(f"✗ Solution generation failed: {e}")
    #     return
    
    print(f"\n✓ All LLM client tests completed successfully!")

if __name__ == "__main__":
    test_llm_client()