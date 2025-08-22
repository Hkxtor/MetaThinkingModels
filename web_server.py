#!/usr/bin/env python3
"""
ThinkingModels Web Server Launcher

Simple launcher script to start the ThinkingModels web application.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    # Import and run the web app
    from web.app import app
    import uvicorn
    
    # Configuration from environment variables or defaults
    host = os.getenv('WEB_HOST', '127.0.0.1')
    port = int(os.getenv('WEB_PORT', '8000'))
    debug = os.getenv('WEB_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting ThinkingModels Web Server on http://{host}:{port}")
    print("📝 Access the web UI at: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print("\n💡 Configure your LLM API:")
    print("   export LLM_API_URL=https://your-api-endpoint.com")
    print("   export LLM_API_KEY=your-api-key")
    print("\n⚡ Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "web.app:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 ThinkingModels Web Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
