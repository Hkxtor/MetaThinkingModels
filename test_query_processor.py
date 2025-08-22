#!/usr/bin/env python3
"""
Test script for the Query Processor
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.model_parser import ModelParser
from src.core.llm_client import LLMClient, LLMConfig
from src.core.query_processor import QueryProcessor

def test_query_processor():
    """Test the query processor functionality"""
    
    print("Testing Query Processor")
    print("=" * 50)
    
    # Initialize components
    try:
        # Load models
        print("1. Loading thinking models...")
        parser = ModelParser("models")
        models = parser.load_all_models()
        print(f"   ✓ Loaded {len(models)} thinking models")
        
        # Create LLM client
        print("2. Creating LLM client...")
        config = LLMConfig.from_env()
        client = LLMClient(config)
        print(f"   ✓ LLM client created with model: {config.model_name}")
        
        # Create query processor
        print("3. Creating query processor...")
        processor = QueryProcessor(parser, client)
        print(f"   ✓ Query processor initialized")
        
    except Exception as e:
        print(f"   ✗ Initialization failed: {e}")
        return
    
    # Test queries
    test_queries = [
        "How can I improve my startup's marketing strategy and customer acquisition?",
        "I need to solve a complex scheduling problem with multiple constraints.",
        "What's the best approach to analyze large datasets for patterns?",
        "Hello, how are you today?",  # Should select no models
        "Help me design a better user interface for my mobile app."
    ]
    
    print(f"\n4. Testing query processing...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        try:
            # Process the query
            result = processor.process_query(query)
            
            print(f"✓ Processing completed")
            print(f"  Selected models: {result.selected_models}")
            print(f"  Processing time: {result.processing_time:.2f}s")
            print(f"  Solution length: {len(result.solution)} characters")
            
            if result.error:
                print(f"  ⚠️  Error: {result.error}")
            
            # Show solution preview
            solution_preview = result.solution[:300] + "..." if len(result.solution) > 300 else result.solution
            print(f"  Solution preview: {solution_preview}")
            
        except Exception as e:
            print(f"  ✗ Query processing failed: {e}")
    
    # Test model summary
    print(f"\n5. Testing model summary...")
    try:
        summary = processor.get_available_models_summary()
        print(f"   ✓ Model summary retrieved")
        print(f"   Total models: {summary['total_models']}")
        print(f"   Types: {summary['types']}")
        print(f"   Fields: {summary['fields']}")
        print(f"   Type distribution: {summary['type_distribution']}")
    except Exception as e:
        print(f"   ✗ Model summary failed: {e}")
    
    print(f"\n✓ Query processor testing completed!")

if __name__ == "__main__":
    test_query_processor()
