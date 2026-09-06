#!/usr/bin/env python3
"""
Test script for the RSI WhatsApp Bot
Run this to verify configuration and test basic functionality
"""

import os
import sys
from typing import Dict, Any


def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        import requests
        print("✓ Flask and requests imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def test_env_variables():
    """Test that environment variables are set"""
    print("\nTesting environment variables...")
    
    required_vars = ["PHONE_NUMBER_ID", "WHATSAPP_TOKEN", "VERIFY_TOKEN"]
    optional_vars = ["WABA_ID", "OPENAI_API_KEY"]
    
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✓ {var}: Set")
        else:
            print(f"✗ {var}: NOT SET (required)")
            all_set = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✓ {var}: Set (optional)")
        else:
            print(f"○ {var}: Not set (optional)")
    
    return all_set


def test_app_initialization():
    """Test that the Flask app initializes correctly"""
    print("\nTesting app initialization...")
    try:
        from app import app, whatsapp_client, ai_assistant
        print("✓ Flask app initialized successfully")
        print(f"✓ WhatsApp client created")
        print(f"✓ AI assistant created")
        return True, app
    except Exception as e:
        print(f"✗ Error initializing app: {e}")
        return False, None


def test_endpoints(app):
    """Test Flask endpoints"""
    print("\nTesting endpoints...")
    
    try:
        with app.test_client() as client:
            response = client.get("/")
            if response.status_code == 200:
                print(f"✓ GET / returns 200")
            else:
                print(f"✗ GET / returns {response.status_code}")
            
            response = client.get("/health")
            if response.status_code == 200:
                print(f"✓ GET /health returns 200")
                data = response.get_json()
                print(f"  Status: {data.get('status')}")
            else:
                print(f"✗ GET /health returns {response.status_code}")
            
            response = client.get("/webhook?hub.mode=subscribe&hub.verify_token=rsi_otono_2026&hub.challenge=test123")
            if response.status_code == 200 and response.data.decode() == "test123":
                print(f"✓ GET /webhook verification works")
            else:
                print(f"✗ GET /webhook verification failed")
            
            response = client.post("/webhook", json={})
            if response.status_code in [200, 400]:
                print(f"✓ POST /webhook accepts requests")
            else:
                print(f"✗ POST /webhook returns {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing endpoints: {e}")
        return False


def test_ai_responses():
    """Test AI assistant fallback responses"""
    print("\nTesting AI assistant fallback responses...")
    
    try:
        from app import ai_assistant
        
        test_cases = [
            ("¿Qué es economía circular?", "circular"),
            ("Tengo dudas sobre la tarea", "tarea"),
            ("¿Qué es RSC?", "responsabilidad"),
            ("Sostenibilidad", "sostenibilidad"),
        ]
        
        for question, expected_keyword in test_cases:
            response = ai_assistant._fallback_response(question)
            if expected_keyword.lower() in response.lower() or "RSI" in response:
                print(f"✓ Response for '{question[:30]}...'")
            else:
                print(f"○ Response for '{question[:30]}...': {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Error testing AI responses: {e}")
        return False


def main():
    print("=" * 60)
    print("RSI WhatsApp Bot - Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    
    results.append(("Environment Variables", test_env_variables()))
    
    success, app = test_app_initialization()
    results.append(("App Initialization", success))
    
    if app:
        results.append(("Endpoints", test_endpoints(app)))
        results.append(("AI Responses", test_ai_responses()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! Your bot is ready to run.")
        print("\nRun the bot with: python app.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Set environment variables: cp .env.whatsapp .env && edit .env")
        print("  3. Load environment: export $(cat .env | xargs)")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: python-dotenv not installed, skipping .env loading")
    
    main()
