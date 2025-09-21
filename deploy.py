#!/usr/bin/env python3
"""
Deployment script for PR Review Agent
This script will start the Streamlit app with the hardcoded GitHub token
"""

import subprocess
import sys
import os

def main():
    """Deploy the PR Review Agent"""
    print("🚀 Deploying PR Review Agent...")
    print("📊 Streamlit dashboard will be available at: http://localhost:8501")
    print("🔑 GitHub token is hardcoded and ready to use")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Verify config exists
    if not os.path.exists("config.yml"):
        print("❌ config.yml not found!")
        return False
    
    # Verify GitHub token is configured
    try:
        import yaml
        with open("config.yml", "r") as f:
            config = yaml.safe_load(f)
        
        token = config.get("github", {}).get("token")
        if not token or token == "your_github_token_here":
            print("❌ GitHub token not properly configured!")
            return False
        
        print(f"✅ GitHub token configured: {token[:10]}...")
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False
    
    try:
        # Start Streamlit app
        print("🌐 Starting Streamlit app...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down PR Review Agent...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure you have streamlit installed: pip install streamlit")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
