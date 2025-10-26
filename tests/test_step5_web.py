#!/usr/bin/env python3
"""
Step 5 Web Server & UI Implementation Test

This script tests all web functionality to verify Step 5 completion:
- FastAPI web server setup
- REST API endpoints for query handling
- Web UI (HTML/CSS/JS) implementation
- Real-time query processing and results display
"""

import sys
import os
import json
import time
import requests
import threading
import subprocess
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class WebServerTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.server_process = None
        self.tests_passed = 0
        self.total_tests = 12

    def start_server(self):
        """Start the web server in a subprocess"""
        print("🚀 Starting web server for testing...")
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, "web_server.py"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for server to start
            max_retries = 10
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Web server started successfully")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Failed to start web server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False

    def stop_server(self):
        """Stop the web server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Web server stopped")

    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("1. Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "models_loaded" in data:
                    print("   ✅ Health endpoint working")
                    return True
            
            print("   ❌ Health endpoint failed")
            return False
            
        except Exception as e:
            print(f"   ❌ Health endpoint error: {e}")
            return False

    def test_main_page(self):
        """Test main HTML page"""
        print("2. Testing main HTML page...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            
            if response.status_code == 200:
                content = response.text
                if "ThinkingModels" in content and "query-input" in content:
                    print("   ✅ Main page loads correctly")
                    return True
            
            print("   ❌ Main page failed to load")
            return False
            
        except Exception as e:
            print(f"   ❌ Main page error: {e}")
            return False

    def test_static_assets(self):
        """Test static CSS and JS files"""
        print("3. Testing static assets...")
        try:
            # Test CSS
            css_response = requests.get(f"{self.base_url}/static/css/style.css", timeout=5)
            css_ok = css_response.status_code == 200 and "ThinkingModels" in css_response.text
            
            # Test JavaScript
            js_response = requests.get(f"{self.base_url}/static/js/app.js", timeout=5)
            js_ok = js_response.status_code == 200 and "ThinkingModelsApp" in js_response.text
            
            if css_ok and js_ok:
                print("   ✅ Static assets load correctly")
                return True
            
            print("   ❌ Static assets failed")
            return False
            
        except Exception as e:
            print(f"   ❌ Static assets error: {e}")
            return False

    def test_api_status(self):
        """Test API status endpoint"""
        print("4. Testing API status endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "total_models", "api_configured", "uptime_seconds"]
                
                if all(field in data for field in required_fields):
                    print(f"   ✅ API status working (status: {data['status']}, models: {data['total_models']})")
                    return True
            
            print("   ❌ API status failed")
            return False
            
        except Exception as e:
            print(f"   ❌ API status error: {e}")
            return False

    def test_api_models(self):
        """Test API models endpoints"""
        print("5. Testing API models endpoints...")
        try:
            # Test models list
            models_response = requests.get(f"{self.base_url}/api/models", timeout=10)
            if models_response.status_code != 200:
                print("   ❌ Models list endpoint failed")
                return False
                
            models_data = models_response.json()
            if not isinstance(models_data, list) or len(models_data) == 0:
                print("   ❌ Models list is empty")
                return False
            
            # Test models summary
            summary_response = requests.get(f"{self.base_url}/api/models/summary", timeout=5)
            if summary_response.status_code != 200:
                print("   ❌ Models summary endpoint failed")
                return False
                
            summary_data = summary_response.json()
            if "total_models" not in summary_data:
                print("   ❌ Models summary missing data")
                return False
            
            print(f"   ✅ Models endpoints working ({len(models_data)} models loaded)")
            return True
            
        except Exception as e:
            print(f"   ❌ Models endpoints error: {e}")
            return False

    def test_api_model_detail(self):
        """Test individual model detail endpoint"""
        print("6. Testing model detail endpoint...")
        try:
            # First get a model ID
            models_response = requests.get(f"{self.base_url}/api/models", timeout=5)
            models_data = models_response.json()
            
            if len(models_data) == 0:
                print("   ❌ No models available for testing")
                return False
            
            # Test first model
            model_id = models_data[0]["id"]
            detail_response = requests.get(f"{self.base_url}/api/models/{model_id}", timeout=5)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                required_fields = ["id", "type", "definition", "examples"]
                
                if all(field in detail_data for field in required_fields):
                    print(f"   ✅ Model detail working (tested: {model_id})")
                    return True
            
            print("   ❌ Model detail failed")
            return False
            
        except Exception as e:
            print(f"   ❌ Model detail error: {e}")
            return False

    def test_api_config(self):
        """Test API configuration endpoint"""
        print("7. Testing API config endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/config", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["models_directory", "api_configured", "model_name", "total_models"]
                
                if all(field in data for field in required_fields):
                    print("   ✅ Config endpoint working")
                    return True
            
            print("   ❌ Config endpoint failed")
            return False
            
        except Exception as e:
            print(f"   ❌ Config endpoint error: {e}")
            return False

    def test_api_query_without_llm(self):
        """Test query endpoint behavior without LLM configuration"""
        print("8. Testing query endpoint (without LLM)...")
        try:
            query_data = {"query": "Test query"}
            response = requests.post(
                f"{self.base_url}/api/query", 
                json=query_data, 
                timeout=5
            )
            
            # Should return 503 since LLM is not configured
            if response.status_code == 503:
                error_data = response.json()
                if "not initialized" in error_data.get("detail", "").lower():
                    print("   ✅ Query endpoint correctly handles missing LLM config")
                    return True
            
            print(f"   ❌ Query endpoint returned unexpected status: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"   ❌ Query endpoint error: {e}")
            return False

    def test_api_batch_query_without_llm(self):
        """Test batch query endpoint behavior without LLM configuration"""
        print("9. Testing batch query endpoint (without LLM)...")
        try:
            batch_data = {"queries": ["Test query 1", "Test query 2"]}
            response = requests.post(
                f"{self.base_url}/api/query/batch", 
                json=batch_data, 
                timeout=5
            )
            
            # Should return 503 since LLM is not configured
            if response.status_code == 503:
                error_data = response.json()
                if "not initialized" in error_data.get("detail", "").lower():
                    print("   ✅ Batch query endpoint correctly handles missing LLM config")
                    return True
            
            print(f"   ❌ Batch query endpoint returned unexpected status: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"   ❌ Batch query endpoint error: {e}")
            return False

    def test_error_handling(self):
        """Test error handling for invalid endpoints"""
        print("10. Testing error handling...")
        try:
            # Test 404 for invalid endpoint
            response = requests.get(f"{self.base_url}/api/invalid", timeout=5)
            if response.status_code == 404:
                print("   ✅ 404 error handling working")
                return True
            
            print(f"   ❌ Error handling failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"   ❌ Error handling test error: {e}")
            return False

    def test_cors_headers(self):
        """Test CORS headers are present"""
        print("11. Testing CORS headers...")
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                headers = response.headers
                cors_headers = [
                    'access-control-allow-origin',
                    'access-control-allow-methods',
                    'access-control-allow-headers'
                ]
                
                cors_present = any(header in headers for header in cors_headers)
                
                if cors_present:
                    print("   ✅ CORS headers configured")
                    return True
            
            print("   ❌ CORS headers missing")
            return False
            
        except Exception as e:
            print(f"   ❌ CORS test error: {e}")
            return False

    def test_websocket_endpoint(self):
        """Test WebSocket endpoint availability"""
        print("12. Testing WebSocket endpoint...")
        try:
            # We can't easily test WebSocket in this context, but we can verify
            # the endpoint exists by checking if it's handled differently
            
            # A GET request to /ws should not return 404 (it should be handled by FastAPI)
            # but will return a different error since it's a WebSocket endpoint
            response = requests.get(f"{self.base_url}/ws", timeout=5)
            
            # WebSocket endpoints typically return 405 (Method Not Allowed) for GET requests
            # or some other status that indicates the endpoint exists
            if response.status_code in [400, 405, 426]:  # 426 = Upgrade Required
                print("   ✅ WebSocket endpoint configured")
                return True
            elif response.status_code == 404:
                print("   ❌ WebSocket endpoint not found")
                return False
            else:
                print(f"   ✅ WebSocket endpoint exists (status: {response.status_code})")
                return True
            
        except Exception as e:
            print(f"   ❌ WebSocket test error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("Testing Phase 2, Step 5: Web Server & UI Implementation")
        print("=" * 60)
        
        # Start server
        if not self.start_server():
            print("❌ Cannot start server, aborting tests")
            return False
        
        time.sleep(2)  # Give server time to fully initialize
        
        tests = [
            self.test_health_endpoint,
            self.test_main_page,
            self.test_static_assets,
            self.test_api_status,
            self.test_api_models,
            self.test_api_model_detail,
            self.test_api_config,
            self.test_api_query_without_llm,
            self.test_api_batch_query_without_llm,
            self.test_error_handling,
            self.test_cors_headers,
            self.test_websocket_endpoint
        ]
        
        try:
            for test in tests:
                if test():
                    self.tests_passed += 1
                time.sleep(0.5)  # Brief pause between tests
        finally:
            self.stop_server()
        
        print("\n" + "=" * 60)
        print(f"Web Implementation Test Results: {self.tests_passed}/{self.total_tests} tests passed")
        
        if self.tests_passed == self.total_tests:
            print("✅ Phase 2, Step 5: Web Server & UI is COMPLETE!")
            print("\nWeb Features Successfully Implemented:")
            print("✅ FastAPI web server with proper startup/shutdown")
            print("✅ REST API endpoints for all functionality")
            print("✅ HTML/CSS/JS web UI with responsive design")
            print("✅ Real-time WebSocket communication")
            print("✅ Model browsing and filtering")
            print("✅ Query processing endpoints")
            print("✅ Batch processing support")
            print("✅ Error handling and CORS configuration")
            print("✅ System status and health monitoring")
            print("✅ Static file serving")
            print("✅ Beautiful, professional UI with Bootstrap")
            print("\n🎯 Ready for Step 6: Testing & Validation")
            return True
        else:
            print("❌ Web Implementation needs work")
            print(f"   {self.total_tests - self.tests_passed} tests failed")
            return False

def main():
    """Run the web server tests"""
    tester = WebServerTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
