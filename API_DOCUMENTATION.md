# ThinkingModels REST API Documentation

**Status: ✅ PRODUCTION READY**

The ThinkingModels Web Application provides a comprehensive REST API for programmatic access to the thinking models system. This API supports both HTTP requests and WebSocket connections for real-time query processing.

## Current Implementation Status

✅ **Core API Endpoints** - Fully implemented and tested  
✅ **WebSocket Real-time Processing** - Complete with progress updates  
✅ **Model Library Access** - 140+ thinking models with filtering  
✅ **Query Processing Engine** - Two-phase orchestration system  
✅ **Error Handling & Validation** - Comprehensive error responses  
✅ **Health Monitoring** - Status and health check endpoints  
✅ **Documentation** - Complete API documentation with examples  
✅ **Docker Support** - Production-ready containerization  

**Latest Updates (August 2025):**
- All Phase 1 & 2 development completed
- Full web interface with Bootstrap UI
- Docker and Docker Compose configurations
- Production deployment scripts
- Comprehensive documentation suite

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints Overview](#endpoints-overview)
- [System Endpoints](#system-endpoints)
- [Model Endpoints](#model-endpoints)
- [Query Processing](#query-processing)
- [WebSocket API](#websocket-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Base URL

When running the web server locally:
```
http://127.0.0.1:8000
```

For deployed instances, replace with your domain:
```
https://your-domain.com
```

---

## Authentication

Currently, the API does not require authentication for basic operations. For production deployments, consider implementing authentication middleware.

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface (HTML) |
| `GET` | `/api/status` | System health and status |
| `GET` | `/api/health` | Simple health check |
| `GET` | `/api/models` | List all thinking models |
| `GET` | `/api/models/summary` | Models statistics |
| `GET` | `/api/models/{model_id}` | Get specific model details |
| `POST` | `/api/query` | Process a query |
| `POST` | `/api/query/batch` | Process multiple queries |
| `WebSocket` | `/ws` | Real-time query processing |

---

## System Endpoints

### GET /api/status

Get comprehensive system status information.

**Response:**
```json
{
  "status": "healthy",
  "api_configured": true,
  "total_models": 140,
  "model_distribution": {
    "solve": 85,
    "explain": 55
  },
  "fields": [
    "business",
    "psychology", 
    "decision-making",
    "creativity"
  ],
  "uptime": "2h 15m 30s",
  "version": "1.0.0"
}
```

**Status Values:**
- `healthy`: All systems operational
- `limited`: API not configured, models available
- `error`: Critical system failure

### GET /api/health

Simple health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Model Endpoints

### GET /api/models

Retrieve a list of all available thinking models.

**Query Parameters:**
- `type` (optional): Filter by model type (`solve` or `explain`)
- `field` (optional): Filter by field/category
- `search` (optional): Search in model IDs and definitions

**Example Request:**
```bash
curl "http://127.0.0.1:8000/api/models?type=solve&field=business"
```

**Response:**
```json
[
  {
    "id": "swot",
    "type": "solve",
    "field": "business",
    "definition": "A strategic planning tool that evaluates Strengths, Weaknesses, Opportunities, and Threats...",
    "examples": [
      "Analyze a new product launch",
      "Evaluate market position"
    ]
  },
  {
    "id": "porter_five_forces",
    "type": "solve", 
    "field": "business",
    "definition": "Framework for analyzing competitive forces in an industry...",
    "examples": [
      "Industry analysis",
      "Competitive strategy"
    ]
  }
]
```

### GET /api/models/summary

Get statistical summary of the thinking models library.

**Response:**
```json
{
  "total_models": 140,
  "type_distribution": {
    "solve": 85,
    "explain": 55
  },
  "fields": [
    "business",
    "psychology",
    "decision-making",
    "creativity",
    "systems-thinking"
  ],
  "field_distribution": {
    "business": 35,
    "psychology": 25,
    "decision-making": 30,
    "creativity": 20,
    "systems-thinking": 30
  }
}
```

### GET /api/models/{model_id}

Get detailed information about a specific thinking model.

**Path Parameters:**
- `model_id`: The ID of the thinking model

**Example Request:**
```bash
curl "http://127.0.0.1:8000/api/models/swot"
```

**Response:**
```json
{
  "id": "swot",
  "type": "solve",
  "field": "business",
  "definition": "SWOT Analysis is a strategic planning tool used to evaluate the Strengths, Weaknesses, Opportunities, and Threats involved in a project or business venture...",
  "examples": [
    "Analyzing a startup's market position",
    "Evaluating a new product launch",
    "Strategic planning for expansion"
  ],
  "usage_tips": [
    "Be honest about weaknesses",
    "Consider external factors",
    "Prioritize findings"
  ]
}
```

---

## Query Processing

### POST /api/query

Process a single query using the two-phase thinking models system.

**Request Body:**
```json
{
  "query": "How can I improve my startup's marketing strategy?",
  "model_id": null,
  "options": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Parameters:**
- `query` (required): The user's question or problem
- `model_id` (optional): Force use of specific model ID
- `options` (optional): LLM generation parameters

**Response:**
```json
{
  "query": "How can I improve my startup's marketing strategy?",
  "selected_models": ["swot", "porter_five_forces", "customer_persona"],
  "solution": "To improve your startup's marketing strategy, I'll apply several thinking models...\n\n**SWOT Analysis Perspective:**\nStrengths:\n- Innovative product...",
  "processing_time": 3.45,
  "model_selection_reasoning": "Selected SWOT for strategic analysis, Porter's Five Forces for competitive landscape, and Customer Persona for targeting",
  "timestamp": "2024-01-15T10:30:00Z",
  "tokens_used": 1543
}
```

**Error Response:**
```json
{
  "error": "API configuration error",
  "detail": "LLM_API_URL not configured",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### POST /api/query/batch

Process multiple queries in a single request.

**Request Body:**
```json
{
  "queries": [
    "What is design thinking?",
    "How to improve team collaboration?",
    "Explain the lean startup methodology"
  ],
  "options": {
    "parallel": true,
    "temperature": 0.7
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "query": "What is design thinking?",
      "selected_models": ["design_thinking", "creative_process"],
      "solution": "Design thinking is a human-centered approach...",
      "processing_time": 2.1
    },
    {
      "query": "How to improve team collaboration?",
      "selected_models": ["team_dynamics", "communication"],
      "solution": "To improve team collaboration...",
      "processing_time": 1.8
    }
  ],
  "total_processing_time": 5.2,
  "successful": 2,
  "failed": 0
}
```

---

## WebSocket API

### WebSocket /ws

Real-time query processing with live updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws');
```

**Client Messages:**

**Query Message:**
```json
{
  "type": "query",
  "query": "How to improve productivity?",
  "model_id": null
}
```

**Ping Message:**
```json
{
  "type": "ping"
}
```

**Server Messages:**

**Query Started:**
```json
{
  "type": "query_started",
  "query": "How to improve productivity?",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Model Selection:**
```json
{
  "type": "model_selected",
  "selected_models": ["eisenhower_matrix", "gtd", "pomodoro"],
  "reasoning": "Selected time management and productivity frameworks"
}
```

**Processing Update:**
```json
{
  "type": "processing_update",
  "message": "Generating solution using selected models...",
  "progress": 0.7
}
```

**Result:**
```json
{
  "type": "result",
  "query": "How to improve productivity?",
  "selected_models": ["eisenhower_matrix", "gtd", "pomodoro"],
  "solution": "To improve productivity, I'll apply several proven frameworks...",
  "processing_time": 4.2,
  "timestamp": "2024-01-15T10:30:15Z"
}
```

**Error:**
```json
{
  "type": "error",
  "error": "Processing failed",
  "detail": "API request timeout",
  "timestamp": "2024-01-15T10:30:30Z"
}
```

**Pong:**
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request (invalid parameters) |
| `404` | Not Found (model/endpoint not found) |
| `500` | Internal Server Error |
| `503` | Service Unavailable (API not configured) |

### Error Response Format

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/query"
}
```

### Common Errors

**API Not Configured:**
```json
{
  "error": "Configuration Error",
  "detail": "LLM_API_URL environment variable not set"
}
```

**Model Not Found:**
```json
{
  "error": "Model Not Found", 
  "detail": "Model 'invalid_model' does not exist"
}
```

**Query Processing Failed:**
```json
{
  "error": "Processing Error",
  "detail": "LLM API request failed after 3 retries"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployments, consider implementing rate limiting based on:

- IP address
- User authentication
- Query complexity
- Resource usage

---

## Configuration

### Environment Variables

The API supports the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LLM_API_URL` | Base URL for LLM API | Yes* | None |
| `LLM_API_KEY` | API key for LLM service | Yes* | None |
| `LLM_MODEL` | Default model name | No | `gpt-3.5-turbo` |
| `API_HOST` | Server bind address | No | `127.0.0.1` |
| `API_PORT` | Server port | No | `8000` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

*Required for full query processing functionality

### Docker Deployment

**Quick Start:**
```bash
# Build and run with Docker Compose
docker-compose up --build
```

**Production Deployment:**
```bash
# Using production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Start the Server:**
```bash
# Development
python run_web.py

# Production  
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Health Monitoring

The API includes built-in health monitoring endpoints:

- `/api/health` - Basic health check
- `/api/status` - Comprehensive system status
- WebSocket ping/pong for connection health

---

## Examples

### Python Example

```python
import requests
import json

base_url = "http://127.0.0.1:8000"

# Get system status
response = requests.get(f"{base_url}/api/status")
status = response.json()
print(f"System status: {status['status']}")

# List models
response = requests.get(f"{base_url}/api/models")
models = response.json()
print(f"Available models: {len(models)}")

# Process a query
query_data = {
    "query": "How can I improve my team's productivity?"
}
response = requests.post(f"{base_url}/api/query", json=query_data)
result = response.json()

print(f"Selected models: {result['selected_models']}")
print(f"Solution: {result['solution'][:100]}...")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const baseURL = 'http://127.0.0.1:8000';

async function queryThinkingModels() {
  try {
    // Get models summary
    const summary = await axios.get(`${baseURL}/api/models/summary`);
    console.log(`Total models: ${summary.data.total_models}`);
    
    // Process query
    const queryResponse = await axios.post(`${baseURL}/api/query`, {
      query: "What are the best practices for remote work?"
    });
    
    console.log('Selected models:', queryResponse.data.selected_models);
    console.log('Solution:', queryResponse.data.solution.substring(0, 200) + '...');
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

queryThinkingModels();
```

### WebSocket JavaScript Example

```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Send a query
  ws.send(JSON.stringify({
    type: 'query',
    query: 'How to make better decisions?'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'query_started':
      console.log('Query processing started');
      break;
    case 'model_selected':
      console.log('Models selected:', data.selected_models);
      break;
    case 'processing_update':
      console.log('Update:', data.message);
      break;
    case 'result':
      console.log('Solution received:', data.solution.substring(0, 100) + '...');
      break;
    case 'error':
      console.error('Error:', data.error);
      break;
  }
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### cURL Examples

**Get system status:**
```bash
curl -X GET "http://127.0.0.1:8000/api/status" \
     -H "Content-Type: application/json"
```

**Search models:**
```bash
curl -X GET "http://127.0.0.1:8000/api/models?search=decision&type=solve" \
     -H "Content-Type: application/json"
```

**Process query:**
```bash
curl -X POST "http://127.0.0.1:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "How to prioritize tasks effectively?",
       "options": {
         "temperature": 0.8
       }
     }'
```

**Batch processing:**
```bash
curl -X POST "http://127.0.0.1:8000/api/query/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "queries": [
         "What is systems thinking?",
         "How to improve creativity?"
       ]
     }'
```

---

For more information, visit the [main documentation](README.md) or [CLI documentation](CLI_README.md).
