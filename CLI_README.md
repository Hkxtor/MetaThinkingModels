# ThinkingModels CLI Interface

A powerful command-line interface for the ThinkingModels project that allows you to solve problems using AI and thinking models.

## Installation

Ensure you have the required dependencies installed:

```bash
pip install click colorama rich requests
```

## Quick Start

1. **Check available commands:**
   ```bash
   python thinking_models.py --help
   ```

2. **View available thinking models:**
   ```bash
   python thinking_models.py models
   ```

3. **Test your setup:**
   ```bash
   python thinking_models.py test
   ```

4. **Start interactive mode:**
   ```bash
   python thinking_models.py interactive
   ```

## Configuration

### Environment Variables

Set these environment variables for API access:

```bash
# Required
LLM_API_URL=https://your-llm-api-endpoint.com

# Optional
LLM_API_KEY=your-api-key-here
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
THINKING_MODELS_DIR=models
```

### Command Line Options

You can also configure settings via command-line options:

```bash
python thinking_models.py --api-url https://api.example.com --model gpt-4 --temperature 0.5 query "How can I improve productivity?"
```

## Commands

### 1. Interactive Mode

Start an interactive session where you can ask questions and get responses:

```bash
python thinking_models.py interactive
```

**Interactive Commands:**
- `help` - Show help information
- `models` - List available thinking models
- `config` - Show current configuration
- `quit` / `exit` / `q` - Exit interactive mode

### 2. Single Query Processing

Process a single query and get a response:

```bash
python thinking_models.py query "How can I improve my startup's marketing strategy?"
```

**Options:**
- `-o, --output-file FILE` - Save results to a file
- `--output-format [rich|json|plain]` - Output format

**Examples:**
```bash
# Basic query
python thinking_models.py query "What's the best approach to prioritize tasks?"

# Save to file
python thinking_models.py query "How to reduce costs?" -o results.txt

# JSON output
python thinking_models.py --output-format json query "Investment strategies?"
```

### 3. Batch Processing

Process multiple queries from a file:

```bash
python thinking_models.py query -f example_queries.txt
```

**Batch File Format:**
```text
# Comments start with #
How can I improve my startup's marketing strategy?

What's the best approach to analyze large datasets?

Help me prioritize my daily tasks more effectively.
```

**Options:**
- `-f, --batch-file FILE` - Input file with queries
- `-o, --output-file FILE` - Save results to a file

### 4. Model Information

List all available thinking models:

```bash
python thinking_models.py models
```

### 5. Configuration Check

View current configuration:

```bash
python thinking_models.py config
```

### 6. System Test

Test your ThinkingModels setup:

```bash
python thinking_models.py test
```

## Output Formats

### Rich Format (Default)
Beautiful, formatted output with tables, panels, and colors:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              Query Information        ┃
┠───────────────────────────────────────┨
┃ Query:   How to improve productivity? ┃
┃ Models:  eisenhower_matrix, agile     ┃
┃ Time:    2.34s                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### JSON Format
Structured JSON output for programmatic use:
```json
{
  "query": "How to improve productivity?",
  "selected_models": ["eisenhower_matrix", "agile"],
  "solution": "To improve productivity...",
  "processing_time": 2.34,
  "error": null
}
```

### Plain Format
Simple text output:
```
Query: How to improve productivity?
Selected Models: eisenhower_matrix, agile
Processing Time: 2.34s

Solution:
To improve productivity...
```

## Examples

### Example 1: Interactive Session
```bash
$ python thinking_models.py interactive
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        ThinkingModels Interactive      ┃
┃              Mode                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✓ 140 thinking models loaded

Your query: How can I manage my time better?

[Processing...]

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            Query Information           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Example 2: Batch Processing
```bash
python thinking_models.py query -f business_questions.txt -o business_analysis.json --output-format json
```

### Example 3: Different API Configuration
```bash
python thinking_models.py --api-url https://api.openrouter.ai/api/v1 --model anthropic/claude-3-haiku query "Explain machine learning"
```

## Tips

1. **Be Specific**: More specific queries lead to better model selection and solutions.

2. **Use Verbose Mode**: Add `-v` for detailed processing information:
   ```bash
   python thinking_models.py -v query "Your question here"
   ```

3. **Check Model Relevance**: Use `models` command to see what thinking models are available.

4. **Batch Processing**: Use batch files for processing multiple related queries efficiently.

5. **Output Formats**: Use JSON format when integrating with other tools or scripts.

## Troubleshooting

### Common Issues

1. **API Configuration Error**
   ```
   Error: LLM_API_URL environment variable must be set
   ```
   **Solution:** Set the LLM_API_URL environment variable or use `--api-url` option.

2. **Model Loading Error**
   ```
   Error loading models: [Errno 2] No such file or directory: 'models'
   ```
   **Solution:** Ensure the models directory exists or specify correct path with `--models-dir`.

3. **API Connection Error**
   ```
   LLM API request failed after 3 attempts
   ```
   **Solution:** Check your API URL, key, and internet connection.

### Debug Mode

Use verbose mode for detailed information:
```bash
python thinking_models.py -v test
```

### Test Setup

Always run the test command after configuration:
```bash
python thinking_models.py test
```

This will check:
- Model loading (140 models expected)
- API configuration
- API connection
- Full query processing pipeline

## Advanced Usage

### Custom Model Directory
```bash
python thinking_models.py --models-dir /path/to/custom/models query "Your question"
```

### Multiple Output Formats
```bash
# Save both rich and JSON outputs
python thinking_models.py query "Question" -o results.txt
python thinking_models.py --output-format json query "Question" -o results.json
```

### Environment-Specific Configuration

Create different environment files:

**.env.development**
```bash
LLM_API_URL=http://localhost:1234/v1
LLM_MODEL_NAME=local-model
```

**.env.production**
```bash
LLM_API_URL=https://api.openai.com/v1
LLM_API_KEY=your-production-key
LLM_MODEL_NAME=gpt-4
```

## Integration

The CLI can be easily integrated into scripts and workflows:

### Bash Script Example
```bash
#!/bin/bash
# Process business questions
python thinking_models.py query -f business_questions.txt -o business_results.json --output-format json

# Check if successful
if [ $? -eq 0 ]; then
    echo "Processing completed successfully"
    # Process results.json with other tools
else
    echo "Processing failed"
    exit 1
fi
```

### Python Integration
```python
import subprocess
import json

# Run CLI command
result = subprocess.run([
    'python', 'thinking_models.py', 
    '--output-format', 'json',
    'query', 'How to improve team productivity?'
], capture_output=True, text=True)

if result.returncode == 0:
    response = json.loads(result.stdout)
    print(f"Selected models: {response['selected_models']}")
    print(f"Solution: {response['solution']}")
```

## Support

For issues and questions:
1. Run `python thinking_models.py test` to diagnose problems
2. Check that all 140 thinking models are loaded
3. Verify API configuration with `python thinking_models.py config`
4. Use verbose mode (`-v`) for detailed error information
