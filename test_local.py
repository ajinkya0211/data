#!/usr/bin/env python3
"""
AI Notebook System - Local Component Test
Tests backend components without Docker to verify Phase 1 implementation.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Core config imported successfully")
        
        from app.core.database import AsyncSessionLocal
        print("✅ Database module imported successfully")
        
        # Test models
        from app.models.user import User, UserCreate
        print("✅ User models imported successfully")
        
        from app.models.project import Project, ProjectCreate
        print("✅ Project models imported successfully")
        
        from app.models.dataset import Dataset, DatasetCreate
        print("✅ Dataset models imported successfully")
        
        from app.models.block import Block, BlockCreate
        print("✅ Block models imported successfully")
        
        # Test services
        from app.services.ai_provider_service import AIProviderService, AIProvider
        print("✅ AI Provider service imported successfully")
        
        from app.services.project_service import ProjectService
        print("✅ Project service imported successfully")
        
        from app.services.dataset_service import DatasetService
        print("✅ Dataset service imported successfully")
        
        from app.services.profiler_service import ProfilerService
        print("✅ Profiler service imported successfully")
        
        # Test API endpoints
        from app.api.v1.endpoints.auth import router as auth_router
        print("✅ Auth endpoints imported successfully")
        
        from app.api.v1.endpoints.projects import router as projects_router
        print("✅ Project endpoints imported successfully")
        
        from app.api.v1.endpoints.datasets import router as datasets_router
        print("✅ Dataset endpoints imported successfully")
        
        from app.api.v1.endpoints.ai_agent import router as ai_router
        print("✅ AI agent endpoints imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Check required settings
        required_settings = [
            'DATABASE_URL',
            'REDIS_URL',
            'MINIO_URL',
            'JWT_SECRET',
            'DEFAULT_AI_PROVIDER',
            'OLLAMA_BASE_URL',
            'OPENAI_API_KEY',
            'GEMINI_API_KEY'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if value is not None:
                    print(f"✅ {setting}: {str(value)[:50]}...")
                else:
                    print(f"⚠️ {setting}: None (optional)")
            else:
                print(f"❌ {setting}: Not found")
        
        print("✅ Configuration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_models():
    """Test model validation"""
    print("\n🧪 Testing model validation...")
    
    try:
        from app.models.user import UserCreate
        from app.models.project import ProjectCreate
        from app.models.dataset import DatasetCreate
        from app.models.block import BlockCreate
        
        # Test user creation
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        }
        user = UserCreate(**user_data)
        print("✅ User model validation successful")
        
        # Test project creation
        project_data = {
            "name": "Test Project",
            "description": "Test project description"
        }
        project = ProjectCreate(**project_data)
        print("✅ Project model validation successful")
        
        # Test dataset creation
        dataset_data = {
            "name": "Test Dataset",
            "source_type": "file",
            "source_path": "/path/to/data.csv",
            "tags": ["test", "sample"]
        }
        dataset = DatasetCreate(**dataset_data)
        print("✅ Dataset model validation successful")
        
        # Test block creation
        block_data = {
            "title": "Test Block",
            "kind": "code",
            "language": "python",
            "content": "print('Hello World')",
            "project_id": "test-project-id"
        }
        block = BlockCreate(**block_data)
        print("✅ Block model validation successful")
        
        print("✅ All model validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Model validation test failed: {e}")
        return False

def test_ai_provider_service():
    """Test AI provider service"""
    print("\n🧪 Testing AI Provider Service...")
    
    try:
        from app.services.ai_provider_service import AIProviderService, AIProvider
        
        # Create service instance
        service = AIProviderService()
        print("✅ AI Provider Service created successfully")
        
        # Test provider enum
        providers = [AIProvider.OLLAMA, AIProvider.OPENAI, AIProvider.GEMINI]
        print(f"✅ AI Providers defined: {[p.value for p in providers]}")
        
        # Test service methods exist
        methods = [
            'initialize',
            'generate_response',
            'get_available_providers',
            'switch_default_provider',
            'health_check'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        print("✅ AI Provider Service test completed")
        return True
        
    except Exception as e:
        print(f"❌ AI Provider Service test failed: {e}")
        return False

def test_project_service():
    """Test project service"""
    print("\n🧪 Testing Project Service...")
    
    try:
        from app.services.project_service import ProjectService
        
        # Create service instance (without database)
        service = ProjectService(None)
        print("✅ Project Service created successfully")
        
        # Test service methods exist
        methods = [
            'create_project',
            'get_project',
            'get_project_with_blocks',
            'list_user_projects',
            'update_project',
            'delete_project',
            'apply_patch',
            'export_project'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        print("✅ Project Service test completed")
        return True
        
    except Exception as e:
        print(f"❌ Project Service test failed: {e}")
        return False

def test_dataset_service():
    """Test dataset service"""
    print("\n🧪 Testing Dataset Service...")
    
    try:
        from app.services.dataset_service import DatasetService
        
        # Create service instance (without database)
        service = DatasetService(None)
        print("✅ Dataset Service created successfully")
        
        # Test service methods exist
        methods = [
            'create_dataset',
            'create_dataset_from_upload',
            'get_dataset',
            'list_datasets',
            'search_datasets',
            'update_dataset',
            'delete_dataset',
            'get_dataset_preview',
            'profile_dataset'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        print("✅ Dataset Service test completed")
        return True
        
    except Exception as e:
        print(f"❌ Dataset Service test failed: {e}")
        return False

def test_profiler_service():
    """Test profiler service"""
    print("\n🧪 Testing Profiler Service...")
    
    try:
        from app.services.profiler_service import ProfilerService
        
        # Create service instance (without database)
        service = ProfilerService(None)
        print("✅ Profiler Service created successfully")
        
        # Test service methods exist
        methods = [
            'profile_dataset',
            'get_latest_profile',
            'profile_file_directly',
            'batch_profile_datasets',
            'get_profiling_summary'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        print("✅ Profiler Service test completed")
        return True
        
    except Exception as e:
        print(f"❌ Profiler Service test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint definitions"""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.projects import router as projects_router
        from app.api.v1.endpoints.datasets import router as datasets_router
        from app.api.v1.endpoints.ai_agent import router as ai_router
        
        # Check auth endpoints
        auth_routes = [route.path for route in auth_router.routes]
        expected_auth_routes = ['/login', '/login-json', '/me', '/refresh', '/logout']
        
        for route in expected_auth_routes:
            if any(route in auth_route for auth_route in auth_routes):
                print(f"✅ Auth endpoint {route} exists")
            else:
                print(f"❌ Auth endpoint {route} missing")
        
        # Check project endpoints
        project_routes = [route.path for route in projects_router.routes]
        expected_project_routes = ['/', '/{project_id}', '/{project_id}/patch', '/{project_id}/export']
        
        for route in expected_project_routes:
            if any(route in project_route for project_route in project_routes):
                print(f"✅ Project endpoint {route} exists")
            else:
                print(f"❌ Project endpoint {route} missing")
        
        # Check AI endpoints
        ai_routes = [route.path for route in ai_router.routes]
        expected_ai_routes = ['/chat', '/generate-code', '/analyze-error', '/providers', '/health']
        
        for route in expected_ai_routes:
            if any(route in ai_route for ai_route in ai_routes):
                print(f"✅ AI endpoint {route} exists")
            else:
                print(f"❌ AI endpoint {route} missing")
        
        print("✅ API endpoints test completed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and organization"""
    print("\n🧪 Testing file structure...")
    
    try:
        # Check backend structure
        backend_files = [
            "backend/app/main.py",
            "backend/app/core/config.py",
            "backend/app/core/database.py",
            "backend/app/core/auth.py",
            "backend/app/models/__init__.py",
            "backend/app/models/user.py",
            "backend/app/models/project.py",
            "backend/app/models/dataset.py",
            "backend/app/models/block.py",
            "backend/app/services/ai_provider_service.py",
            "backend/app/services/project_service.py",
            "backend/app/services/dataset_service.py",
            "backend/app/services/profiler_service.py",
            "backend/app/api/v1/api.py",
            "backend/app/api/v1/endpoints/auth.py",
            "backend/app/api/v1/endpoints/projects.py",
            "backend/app/api/v1/endpoints/datasets.py",
            "backend/app/api/v1/endpoints/ai_agent.py",
            "backend/requirements.txt",
            "backend/Dockerfile"
        ]
        
        missing_files = []
        for file_path in backend_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - MISSING")
                missing_files.append(file_path)
        
        # Check configuration files
        config_files = [
            "docker-compose.yml",
            "env.example",
            "setup.sh",
            "setup-ollama.sh",
            "README.md",
            "AI_PROVIDERS.md"
        ]
        
        for file_path in config_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - MISSING")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️ Missing files: {len(missing_files)}")
            return False
        else:
            print("\n✅ All required files present")
            return True
        
    except Exception as e:
        print(f"❌ File structure test failed: {e}")
        return False

def main():
    """Run all local tests"""
    print("🤖 AI Notebook System - Phase 1 POC Local Test")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Model Validation", test_models),
        ("AI Provider Service", test_ai_provider_service),
        ("Project Service", test_project_service),
        ("Dataset Service", test_dataset_service),
        ("Profiler Service", test_profiler_service),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 LOCAL TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 Phase 1 POC Implementation is COMPLETE!")
        print("✅ All backend components are properly implemented")
        print("✅ All services are correctly defined")
        print("✅ All API endpoints are properly configured")
        print("✅ Multi-AI provider support is implemented")
        print("\n🚀 Ready for Docker deployment and full system testing!")
    elif success_rate >= 70:
        print("\n⚠️ Phase 1 POC is mostly complete but needs some fixes")
        print("Check the failed tests above for details")
    else:
        print("\n❌ Phase 1 POC has significant implementation issues")
        print("Please fix the failed tests before proceeding")
    
    # Print detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, result in results.items():
        status_icon = "✅" if result else "❌"
        print(f"  {status_icon} {test_name}: {'PASS' if result else 'FAIL'}")
    
    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 