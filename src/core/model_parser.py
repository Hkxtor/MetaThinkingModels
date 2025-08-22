"""
Model Parser for ThinkingModels

This module handles loading, parsing, and indexing of thinking model files.
Supports the custom XML-like text format used by the thinking models.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ThinkingModel:
    """
    Data structure representing a thinking model
    """
    id: str
    type: str  # 'solve' or 'explain'
    field: str  # domain field (e.g., '*' for universal)
    definition: str
    examples: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate model data after initialization"""
        if not self.id:
            raise ValueError("Model ID is required")
        if not self.type:
            raise ValueError("Model type is required")
        if not self.field:
            raise ValueError("Model field is required")
        if not self.definition:
            raise ValueError("Model definition is required")
        if self.type not in ["solve", "explain"]:
            raise ValueError("Model type must be 'solve' or 'explain'")


class ModelParser:
    """
    Parser for loading and managing thinking models from XML-like text files
    """
    
    def __init__(self, models_directory: str = "models"):
        """
        Initialize the model parser
        
        Args:
            models_directory: Path to directory containing model files
        """
        self.models_directory = Path(models_directory)
        self.models: Dict[str, ThinkingModel] = {}
        
        # Ensure models directory exists
        self.models_directory.mkdir(exist_ok=True)
    
    def _extract_tag_content(self, lines: List[str], tag: str) -> str:
        """
        Extract content between XML-like tags from lines
        
        Args:
            lines: List of file lines
            tag: Tag name to extract (without < >)
            
        Returns:
            Content between the tags as a string
        """
        content_lines = []
        in_tag = False
        
        for line in lines:
            # Remove line numbers and '|' prefix
            if '|' in line:
                line_content = line.split('|', 1)[1] if '|' in line else line
            else:
                line_content = line
            
            if f'<{tag}>' in line_content:
                in_tag = True
                # Check if there's content after the opening tag
                after_tag = line_content.split(f'<{tag}>', 1)[1]
                if after_tag.strip():
                    content_lines.append(after_tag)
            elif f'</{tag}>' in line_content:
                in_tag = False
                # Check if there's content before the closing tag
                before_tag = line_content.split(f'</{tag}>', 1)[0]
                if before_tag.strip():
                    content_lines.append(before_tag)
                break
            elif in_tag:
                content_lines.append(line_content)
        
        return '\n'.join(content_lines).strip()
    
    def _extract_examples(self, lines: List[str]) -> List[str]:
        """
        Extract all example sections from the file
        
        Args:
            lines: List of file lines
            
        Returns:
            List of example content strings
        """
        examples = []
        current_example = []
        in_example = False
        
        for line in lines:
            # Remove line numbers and '|' prefix
            if '|' in line:
                line_content = line.split('|', 1)[1] if '|' in line else line
            else:
                line_content = line
            
            if '<example>' in line_content:
                in_example = True
                current_example = []
                # Check if there's content after the opening tag
                after_tag = line_content.split('<example>', 1)[1]
                if after_tag.strip():
                    current_example.append(after_tag)
            elif '</example>' in line_content:
                in_example = False
                # Check if there's content before the closing tag
                before_tag = line_content.split('</example>', 1)[0]
                if before_tag.strip():
                    current_example.append(before_tag)
                # Add the completed example
                if current_example:
                    examples.append('\n'.join(current_example).strip())
                current_example = []
            elif in_example:
                current_example.append(line_content)
        
        return examples
    
    def _parse_model_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single model file and extract structured data
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Dictionary with parsed model data
            
        Raises:
            ValueError: If file parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract required fields
            model_id = self._extract_tag_content(lines, 'id')
            model_type = self._extract_tag_content(lines, 'type')
            model_field = self._extract_tag_content(lines, 'field')
            definition = self._extract_tag_content(lines, 'define')
            examples = self._extract_examples(lines)
            
            return {
                'id': model_id,
                'type': model_type,
                'field': model_field,
                'definition': definition,
                'examples': examples
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse {file_path}: {str(e)}")
    
    def _validate_model_data(self, data: Dict[str, Any], file_path: Path) -> None:
        """
        Validate that model data contains required fields
        
        Args:
            data: Model data dictionary
            file_path: Path to source file (for error messages)
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['id', 'type', 'field', 'definition']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing or empty required field '{field}' in {file_path}")
    
    def _create_model_from_data(self, data: Dict[str, Any]) -> ThinkingModel:
        """
        Create a ThinkingModel instance from parsed data
        
        Args:
            data: Model data dictionary
            
        Returns:
            ThinkingModel instance
        """
        return ThinkingModel(
            id=data['id'],
            type=data['type'],
            field=data['field'],
            definition=data['definition'],
            examples=data.get('examples', [])
        )
    
    def load_single_model(self, file_path: Union[str, Path]) -> ThinkingModel:
        """
        Load a single model from a file
        
        Args:
            file_path: Path to the model file
            
        Returns:
            ThinkingModel instance
            
        Raises:
            ValueError: If file parsing or validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"Model file not found: {file_path}")
        
        # Parse file content
        data = self._parse_model_file(file_path)
        
        # Validate required fields
        self._validate_model_data(data, file_path)
        
        # Create model instance
        model = self._create_model_from_data(data)
        
        logger.info(f"Loaded model '{model.id}' from {file_path}")
        return model
    
    def load_all_models(self) -> Dict[str, ThinkingModel]:
        """
        Load all models from the models directory
        
        Returns:
            Dictionary mapping model IDs to ThinkingModel instances
        """
        self.models.clear()
        
        # Find all .txt model files
        model_files = list(self.models_directory.glob('*.txt'))
        
        if not model_files:
            logger.warning(f"No .txt model files found in {self.models_directory}")
            return self.models
        
        # Load each model file
        loaded_count = 0
        for file_path in model_files:
            try:
                model = self.load_single_model(file_path)
                
                # Check for duplicate IDs
                if model.id in self.models:
                    logger.warning(f"Duplicate model ID '{model.id}' found in {file_path}. Skipping.")
                    continue
                
                self.models[model.id] = model
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"Failed to load model from {file_path}: {str(e)}")
                continue
        
        logger.info(f"Successfully loaded {loaded_count} models from {len(model_files)} files")
        return self.models
    
    def get_model(self, model_id: str) -> Optional[ThinkingModel]:
        """
        Get a model by ID
        
        Args:
            model_id: Model identifier
            
        Returns:
            ThinkingModel instance or None if not found
        """
        return self.models.get(model_id)
    
    def get_models_by_type(self, model_type: str) -> List[ThinkingModel]:
        """
        Get all models of a specific type
        
        Args:
            model_type: Type name ('solve' or 'explain')
            
        Returns:
            List of ThinkingModel instances
        """
        return [model for model in self.models.values() if model.type == model_type]
    
    def get_models_by_field(self, field: str) -> List[ThinkingModel]:
        """
        Get all models for a specific field
        
        Args:
            field: Field name (e.g., '*' for universal)
            
        Returns:
            List of ThinkingModel instances
        """
        return [model for model in self.models.values() if model.field == field]
    
    def get_universal_models(self) -> List[ThinkingModel]:
        """
        Get all universal models (field = '*')
        
        Returns:
            List of ThinkingModel instances
        """
        return self.get_models_by_field('*')
    
    def get_model_ids(self) -> List[str]:
        """
        Get all available model IDs
        
        Returns:
            List of model IDs
        """
        return list(self.models.keys())
    
    def get_model_types(self) -> List[str]:
        """
        Get all unique types from loaded models
        
        Returns:
            List of unique type names
        """
        return list(set(model.type for model in self.models.values()))
    
    def get_model_fields(self) -> List[str]:
        """
        Get all unique fields from loaded models
        
        Returns:
            List of unique field names
        """
        return list(set(model.field for model in self.models.values()))
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all loaded models
        
        Returns:
            Dictionary with model statistics
        """
        if not self.models:
            return {"total_models": 0, "types": [], "fields": [], "type_distribution": {}}
        
        type_counts = {}
        for model in self.models.values():
            type_counts[model.type] = type_counts.get(model.type, 0) + 1
        
        return {
            "total_models": len(self.models),
            "types": self.get_model_types(),
            "fields": self.get_model_fields(),
            "type_distribution": type_counts,
            "model_ids": self.get_model_ids()
        }


# Convenience function for quick model loading
def load_models(models_directory: str = "models") -> Dict[str, ThinkingModel]:
    """
    Convenience function to load all models from a directory
    
    Args:
        models_directory: Path to models directory
        
    Returns:
        Dictionary mapping model IDs to ThinkingModel instances
    """
    parser = ModelParser(models_directory)
    return parser.load_all_models()
