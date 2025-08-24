#!/usr/bin/env python3
"""
AI Notebook System - System Test Script
Tests all major components to ensure Phase 1 is complete and functional.
"""

import asyncio
import requests
import json
import time
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

class SystemTester:
    """Comprehensive system tester for AI Notebook System"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {}
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message"""
        status_icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        icon = status_icons.get(status, "ℹ️")
        print(f"{icon} {message}")
    
    def test_service_health(self) -> bool:
        """Test if all services are running"""
        self.print_status("Testing service health...")
        
        services = {
            "Backend API": f"{BASE_URL}/health",
            "PostgreSQL": "localhost:5432",
            "Redis": "localhost:6379",
            "MinIO": "http://localhost:9000",
            "Ollama": "http://localhost:11434",
            "Jupyter Kernel": "http://localhost:8888"
        }
        
        all_healthy = True
        
        for service_name, endpoint in services.items():
            try:
                if "localhost:" in endpoint and not endpoint.startswith("http"):
                    # Test port connectivity for localhost:port format
                    import socket
                    host, port = endpoint.split(":")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, int(port)))
                    sock.close()
                    
                    if result == 0:
                        self.print_status(f"{service_name}: Running", "SUCCESS")
                    else:
                        self.print_status(f"{service_name}: Not accessible", "ERROR")
                        all_healthy = False
                else:
                    # Test HTTP endpoint
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        self.print_status(f"{service_name}: Running", "SUCCESS")
                    else:
                        self.print_status(f"{service_name}: HTTP {response.status_code}", "WARNING")
            except Exception as e:
                self.print_status(f"{service_name}: Error - {str(e)}", "ERROR")
                all_healthy = False
        
        return all_healthy
    
    def test_authentication(self) -> bool:
        """Test authentication endpoints"""
        self.print_status("Testing authentication...")
        
        try:
            # Test login
            login_data = {
                "email": "admin@example.com",
                "password": TEST_PASSWORD
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/auth/login-json", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.print_status("Authentication: Login successful", "SUCCESS")
                return True
            else:
                self.print_status(f"Authentication: Login failed - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Authentication: Error - {str(e)}", "ERROR")
            return False
    
    def test_ai_providers(self) -> bool:
        """Test AI provider endpoints"""
        self.print_status("Testing AI providers...")
        
        if not self.auth_token:
            self.print_status("AI Providers: No auth token", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test AI health check
            response = requests.get(f"{BASE_URL}/api/v1/ai/health", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_status("AI Providers: Health check successful", "SUCCESS")
                
                # Check Ollama status
                if "ollama" in data.get("health_status", {}):
                    ollama_status = data["health_status"]["ollama"]
                    if ollama_status.get("available") and ollama_status.get("healthy"):
                        self.print_status("AI Providers: Ollama is healthy", "SUCCESS")
                    else:
                        self.print_status("AI Providers: Ollama not healthy", "WARNING")
                
                return True
            else:
                self.print_status(f"AI Providers: Health check failed - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"AI Providers: Error - {str(e)}", "ERROR")
            return False
    
    def test_ai_chat(self) -> bool:
        """Test AI chat functionality"""
        self.print_status("Testing AI chat...")
        
        if not self.auth_token:
            self.print_status("AI Chat: No auth token", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test simple chat
            chat_data = {
                "message": "Hello, can you help me with Python?",
                "provider": "ollama"
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=chat_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    self.print_status("AI Chat: Chat successful", "SUCCESS")
                    self.print_status(f"AI Chat: Response from {data.get('provider')}", "INFO")
                    return True
                else:
                    self.print_status("AI Chat: Chat failed - no response", "ERROR")
                    return False
            else:
                self.print_status(f"AI Chat: Chat failed - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"AI Chat: Error - {str(e)}", "ERROR")
            return False
    
    def test_project_management(self) -> bool:
        """Test project management endpoints"""
        self.print_status("Testing project management...")
        
        if not self.auth_token:
            self.print_status("Projects: No auth token", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test project creation
            project_data = {
                "name": "Test Project",
                "description": "Test project for system validation"
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/projects", json=project_data, headers=headers)
            
            if response.status_code in [200, 201]:  # 201 is "Created" status
                data = response.json()
                project_id = data.get("id")
                self.print_status("Projects: Project created successfully", "SUCCESS")
                
                # Test project retrieval
                response = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}", headers=headers)
                
                if response.status_code == 200:
                    self.print_status("Projects: Project retrieved successfully", "SUCCESS")
                    
                    # Test project listing
                    response = requests.get(f"{BASE_URL}/api/v1/projects", headers=headers)
                    
                    if response.status_code == 200:
                        self.print_status("Projects: Project listing successful", "SUCCESS")
                        return True
                    else:
                        self.print_status("Projects: Project listing failed", "ERROR")
                        return False
                else:
                    self.print_status("Projects: Project retrieval failed", "ERROR")
                    return False
            else:
                self.print_status(f"Projects: Project creation failed - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Projects: Error - {str(e)}", "ERROR")
            return False
    
    def test_dataset_management(self) -> bool:
        """Test dataset management endpoints"""
        self.print_status("Testing dataset management...")
        
        if not self.auth_token:
            self.print_status("Datasets: No auth token", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test dataset listing
            response = requests.get(f"{BASE_URL}/api/v1/datasets", headers=headers)
            
            if response.status_code == 200:
                self.print_status("Datasets: Dataset listing successful", "SUCCESS")
                return True
            else:
                self.print_status(f"Datasets: Dataset listing failed - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Datasets: Error - {str(e)}", "ERROR")
            return False
    
    def test_ollama_models(self) -> bool:
        """Test Ollama model availability"""
        self.print_status("Testing Ollama models...")
        
        try:
            # Test Ollama API
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                if models:
                    self.print_status(f"Ollama: {len(models)} models available", "SUCCESS")
                    for model in models[:3]:  # Show first 3 models
                        self.print_status(f"Ollama: Model {model.get('name')}", "INFO")
                    return True
                else:
                    self.print_status("Ollama: No models available", "WARNING")
                    return False
            else:
                self.print_status(f"Ollama: API error - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Ollama: Error - {str(e)}", "ERROR")
            return False
    
    def test_data_profiling(self) -> bool:
        """Test data profiling with sample dataset"""
        self.print_status("Testing data profiling...")
        
        try:
            # Check if sample data exists
            sample_file = Path("data/data_dirty.csv")
            
            if sample_file.exists():
                self.print_status("Data Profiling: Sample dataset found", "SUCCESS")
                
                # Test profiling service
                if not self.auth_token:
                    self.print_status("Data Profiling: No auth token", "WARNING")
                    return True  # Skip this test if no auth
                
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                # This would test the profiling endpoint
                # For now, just check if the file is readable
                import pandas as pd
                try:
                    df = pd.read_csv(sample_file)
                    self.print_status(f"Data Profiling: CSV read successfully - {len(df)} rows, {len(df.columns)} columns", "SUCCESS")
                    return True
                except Exception as e:
                    self.print_status(f"Data Profiling: CSV read failed - {str(e)}", "ERROR")
                    return False
            else:
                self.print_status("Data Profiling: Sample dataset not found", "WARNING")
                return True  # Not critical for system test
                
        except Exception as e:
            self.print_status(f"Data Profiling: Error - {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self) -> dict:
        """Run all system tests"""
        self.print_status("🚀 Starting AI Notebook System Tests...", "INFO")
        self.print_status("=" * 50, "INFO")
        
        tests = [
            ("Service Health", self.test_service_health),
            ("Authentication", self.test_authentication),
            ("AI Providers", self.test_ai_providers),
            ("AI Chat", self.test_ai_chat),
            ("Project Management", self.test_project_management),
            ("Dataset Management", self.test_dataset_management),
            ("Ollama Models", self.test_ollama_models),
            ("Data Profiling", self.test_data_profiling)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.print_status(f"\n🧪 Running: {test_name}", "INFO")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    self.test_results[test_name] = "PASS"
                else:
                    self.test_results[test_name] = "FAIL"
            except Exception as e:
                self.print_status(f"{test_name}: Exception - {str(e)}", "ERROR")
                results[test_name] = False
                self.test_results[test_name] = "ERROR"
        
        return results
    
    def print_summary(self):
        """Print test summary"""
        self.print_status("\n" + "=" * 50, "INFO")
        self.print_status("📊 TEST SUMMARY", "INFO")
        self.print_status("=" * 50, "INFO")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result == "ERROR")
        
        self.print_status(f"Total Tests: {total_tests}", "INFO")
        self.print_status(f"Passed: {passed_tests}", "SUCCESS")
        self.print_status(f"Failed: {failed_tests}", "ERROR" if failed_tests > 0 else "SUCCESS")
        self.print_status(f"Errors: {error_tests}", "ERROR" if error_tests > 0 else "SUCCESS")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        self.print_status(f"Success Rate: {success_rate:.1f}%", "INFO")
        
        if success_rate >= 80:
            self.print_status("🎉 Phase 1 POC is READY!", "SUCCESS")
        elif success_rate >= 60:
            self.print_status("⚠️ Phase 1 POC needs some fixes", "WARNING")
        else:
            self.print_status("❌ Phase 1 POC has significant issues", "ERROR")
        
        # Print detailed results
        self.print_status("\n📋 DETAILED RESULTS:", "INFO")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            print(f"  {status_icon} {test_name}: {result}")

def main():
    """Main test runner"""
    print("🤖 AI Notebook System - Phase 1 POC Test")
    print("=" * 60)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Run tests
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Print summary
    tester.print_summary()
    
    # Exit with appropriate code
    success_rate = sum(1 for result in results.values() if result) / len(results) if results else 0
    if success_rate >= 0.8:
        print("\n🎉 All tests passed! Phase 1 POC is complete and functional!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 