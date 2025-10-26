#!/usr/bin/env python3
"""
Test script for refined system prompts
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.llm_client import LLMClient, LLMConfig
from src.core.model_parser import ModelParser

def test_refined_prompts():
    """Test the refined system prompts"""
    
    print("Testing Refined System Prompts")
    print("=" * 50)
    
    # Load models and client
    parser = ModelParser("models")
    models = parser.load_all_models()
    client = LLMClient()
    
    # Test queries with different relevance levels
    test_cases = [
        {
            "query": "Hello, how are you?",
            "expected": "No models should be selected (social greeting)",
            "models": list(models.keys())[:30]
        },
        {
            "query": "What's the weather like today?",
            "expected": "No models should be selected (weather query)",
            "models": list(models.keys())[:30]
        },
        {
            "query": "I need to analyze market trends for my startup and make strategic business decisions about product pricing.",
            "expected": "2-3 relevant business models should be selected",
            "models": list(models.keys())[:40]
        },
        {
            "query": "How can I solve this coding problem using dynamic programming?",
            "expected": "1-2 relevant programming models should be selected",
            "models": list(models.keys())[:40]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['expected']}")
        print(f"Query: {test_case['query']}")
        
        # Phase 1: Model Selection
        try:
            selected_models = client.request_model_selection(
                test_case['query'], 
                test_case['models']
            )
            
            print(f"Selected models ({len(selected_models)}): {selected_models}")
            
            if len(selected_models) > 3:
                print("  ⚠️  Warning: More than 3 models selected")
            elif len(selected_models) == 0:
                print("  ✓ No models selected - appropriate for irrelevant query")
            else:
                print(f"  ✓ {len(selected_models)} models selected")
            
        except Exception as e:
            print(f"  ✗ Model selection failed: {e}")
            continue
        
        # Phase 2: Solution Generation (only if models were selected)
        if selected_models:
            try:
                # Prepare model data
                selected_model_data = []
                for model_id in selected_models:
                    if model_id in models:
                        model = models[model_id]
                        selected_model_data.append({
                            'id': model.id,
                            'type': model.type,
                            'definition': model.definition,
                            'examples': model.examples[:2]  # Limit examples
                        })
                
                if selected_model_data:
                    solution = client.request_solution(test_case['query'], selected_model_data)
                    print(f"  ✓ Solution generated ({len(solution)} characters)")
                    
                    # Check if solution mentions the selected models
                    models_mentioned = 0
                    for model_data in selected_model_data:
                        if model_data['id'].lower() in solution.lower():
                            models_mentioned += 1
                    
                    print(f"  ✓ Models explicitly mentioned: {models_mentioned}/{len(selected_model_data)}")
                    
                    # Show a preview of the solution
                    preview = solution[:300] + "..." if len(solution) > 300 else solution
                    print(f"  Solution preview: {preview}")
                
            except Exception as e:
                print(f"  ✗ Solution generation failed: {e}")
        else:
            print("  ℹ️  Skipping solution generation (no models selected)")
    
    # Test edge case: Empty model list
    print(f"\nEdge Case: Empty model list")
    try:
        selected_models = client.request_model_selection("Test query", [])
        print(f"  ✓ Empty model list handled: {selected_models}")
    except Exception as e:
        print(f"  ✗ Empty model list failed: {e}")
    
    print(f"\n✓ Refined prompts testing completed!")

if __name__ == "__main__":
    test_refined_prompts()
