#!/usr/bin/env python3
"""
OpenAI API Connection Test

This script tests the connection to the OpenAI API and checks for common issues:
- API key validation
- SSL certificate errors
- Network connectivity
- API endpoint accessibility

Usage:
    python openai_connection_test.py [--api-key KEY] [--no-verify-ssl] [--base-url URL] [--timeout SECONDS]

Options:
    --api-key KEY       OpenAI API key (defaults to environment variables)
    --no-verify-ssl     Disable SSL certificate verification
    --base-url URL      Custom API base URL (for proxies or alternative endpoints)
    --timeout SECONDS   Connection timeout in seconds (default: 30)
    --model MODEL       Model to use for testing (default: gpt-3.5-turbo)
    --verbose           Show detailed information and full stack traces
"""

import os
import sys
import ssl
import time
import traceback
import argparse
import requests
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Add parent directory to path so we can import the article_dryer module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from .env file
load_dotenv()


class ConnectionTester:
    def __init__(self, args):
        self.api_key = args.api_key or os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY')
        self.verify_ssl = not args.no_verify_ssl
        self.base_url = args.base_url
        self.timeout = args.timeout
        self.model = args.model
        self.verbose = args.verbose
        
        if not self.api_key:
            print("❌ ERROR: No API key provided. Please specify --api-key or set the API_KEY or OPENAI_API_KEY environment variable.")
            sys.exit(1)

    def run_tests(self):
        """Run a series of tests to check OpenAI API connectivity"""
        print("\n=== OpenAI API Connection Test ===\n")
        
        self.test_network_connectivity()
        self.test_ssl_configuration()
        self.test_api_authentication()
        self.test_api_model_availability()
        
        print("\n✅ All tests completed!\n")

    def test_network_connectivity(self):
        """Test basic network connectivity to the OpenAI domain"""
        print("🌐 Testing network connectivity...")
        
        try:
            url = self.base_url or "https://api.openai.com"
            hostname = url.split("//")[1].split("/")[0]
            
            print(f"   Connecting to {hostname}...")
            response = requests.get(
                f"{url}/v1/models",
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                print(f"✅ Network connectivity: OK (Status code: {response.status_code})")
            else:
                print(f"⚠️  Network connectivity: Responded with status code {response.status_code}")
                if self.verbose:
                    print(f"Response: {response.text}")
        except requests.exceptions.SSLError as e:
            print("❌ SSL Error: Certificate verification failed")
            print("   Try running with --no-verify-ssl to bypass certificate verification")
            if self.verbose:
                print(f"\nError details: {str(e)}")
                traceback.print_exc()
        except requests.exceptions.ConnectionError as e:
            print("❌ Connection Error: Unable to connect to the API endpoint")
            print("   This could be due to network issues, proxy configuration, or firewall settings")
            if self.verbose:
                print(f"\nError details: {str(e)}")
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            if self.verbose:
                traceback.print_exc()

    def test_ssl_configuration(self):
        """Test SSL configuration by examining available certificates"""
        print("\n🔒 Testing SSL configuration...")
        
        context = ssl.create_default_context()
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            print("   SSL certificate verification is DISABLED")
        else:
            print("   SSL certificate verification is ENABLED")
        
        try:
            # Check SSL version and available protocols
            print(f"   SSL version: {ssl.OPENSSL_VERSION}")
            
            # Check if the default certificate paths are accessible
            cafile = ssl.get_default_verify_paths().cafile
            capath = ssl.get_default_verify_paths().capath
            
            print(f"   Default certificate file: {cafile or 'Not set'}")
            print(f"   Default certificate path: {capath or 'Not set'}")
            
            if cafile and os.path.exists(cafile):
                print(f"✅ Certificate file exists and is accessible")
            elif cafile:
                print(f"❌ Certificate file does not exist: {cafile}")
            
            if capath and os.path.exists(capath):
                print(f"✅ Certificate path exists and is accessible")
            elif capath:
                print(f"❌ Certificate path does not exist: {capath}")
                
        except Exception as e:
            print(f"❌ SSL Configuration Error: {str(e)}")
            if self.verbose:
                traceback.print_exc()

    def test_api_authentication(self):
        """Test API authentication with the provided key"""
        print("\n🔑 Testing API authentication...")
        
        # Configure OpenAI client with appropriate SSL verification settings
        client_params = {
            'api_key': self.api_key,
            'base_url': self.base_url
        }
        
        # Add SSL verification options
        if not self.verify_ssl:
            # Create a custom SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            client_params['http_client'] = {
                'ssl_context': ssl_context
            }
        
        client = OpenAI(**client_params)
        
        try:
            # Try to list available models
            print("   Authenticating to OpenAI API...")
            start_time = time.time()
            models = client.models.list()
            elapsed_time = time.time() - start_time
            
            print(f"✅ Authentication successful! (Response time: {elapsed_time:.2f}s)")
            print(f"   Available models: {len(models.data)}")
            
        except APIError as e:
            if e.status == 401:
                print("❌ Authentication failed: Invalid API key")
            else:
                print(f"❌ API Error (Status {e.status}): {e.message}")
            if self.verbose:
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")
            if self.verbose:
                traceback.print_exc()

    def test_api_model_availability(self):
        """Test if the specified model is available"""
        print(f"\n🤖 Testing model availability for '{self.model}'...")
        
        # Configure OpenAI client
        client_params = {
            'api_key': self.api_key,
            'base_url': self.base_url
        }
        
        # Add SSL verification options
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            client_params['http_client'] = {
                'ssl_context': ssl_context
            }
            
        client = OpenAI(**client_params)
        
        try:
            # Try to send a simple completion request
            print(f"   Sending a test request to model '{self.model}'...")
            start_time = time.time()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello! This is a connection test."}
                ],
                max_tokens=10
            )
            elapsed_time = time.time() - start_time
            
            content = response.choices[0].message.content
            print(f"✅ Model response received! (Response time: {elapsed_time:.2f}s)")
            print(f"   Response: \"{content}\"")
            
        except APIError as e:
            if e.status == 404:
                print(f"❌ Model '{self.model}' not found. It may not exist or you don't have access to it.")
            else:
                print(f"❌ API Error (Status {e.status}): {e.message}")
            if self.verbose:
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if self.verbose:
                traceback.print_exc()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test OpenAI API connectivity")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--base-url", help="Custom API base URL")
    parser.add_argument("--timeout", type=int, default=30, help="Connection timeout in seconds")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to test with")
    parser.add_argument("--verbose", action="store_true", help="Show detailed information and stack traces")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    tester = ConnectionTester(args)
    tester.run_tests()