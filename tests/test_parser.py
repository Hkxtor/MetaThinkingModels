#!/usr/bin/env python3
"""
Test script for the model parser
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.model_parser import ModelParser, load_models

def test_parser():
    """Test the model parser functionality"""
    
    print("Testing ThinkingModels Parser")
    print("=" * 50)
    
    # Create parser instance
    parser = ModelParser("models")
    
    # Load all models
    print("Loading all models...")
    models = parser.load_all_models()
    
    # Print summary
    summary = parser.get_model_summary()
    print(f"\nModel Summary:")
    print(f"Total models loaded: {summary['total_models']}")
    print(f"Types: {summary['types']}")
    print(f"Fields: {summary['fields']}")
    print(f"Type distribution: {summary['type_distribution']}")
    
    print(f"\nFirst 10 model IDs:")
    for i, model_id in enumerate(summary['model_ids'][:10]):
        print(f"  {i+1}. {model_id}")
    
    # Test individual model retrieval
    print(f"\nTesting individual model retrieval...")
    if models:
        first_model_id = list(models.keys())[0]
        model = parser.get_model(first_model_id)
        if model:
            print(f"\nModel Details for '{first_model_id}':")
            print(f"  ID: {model.id}")
            print(f"  Type: {model.type}")
            print(f"  Field: {model.field}")
            print(f"  Definition: {model.definition[:200]}...")
            print(f"  Examples: {len(model.examples)} examples")
            if model.examples:
                print(f"  First example: {model.examples[0][:100]}...")
    
    # Test filtering by type
    print(f"\nTesting filtering by type...")
    solve_models = parser.get_models_by_type("solve")
    explain_models = parser.get_models_by_type("explain")
    print(f"Solve models: {len(solve_models)}")
    print(f"Explain models: {len(explain_models)}")
    
    # Test filtering by field
    print(f"\nTesting filtering by field...")
    universal_models = parser.get_universal_models()
    print(f"Universal models (*): {len(universal_models)}")
    
    # Show some universal model IDs
    if universal_models:
        print("Universal model IDs:")
        for i, model in enumerate(universal_models[:5]):
            print(f"  {i+1}. {model.id}")
    
    print(f"\nTest completed successfully!")

if __name__ == "__main__":
    test_parser()
