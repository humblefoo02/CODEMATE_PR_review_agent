#!/usr/bin/env python3
"""
Simple startup script for PR Review Agent with Streamlit
"""

import subprocess
import sys
import os

def main():
    """Start the Streamlit application"""
    print("🤖 Starting PR Review Agent...")
    print("📊 Streamlit dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Check if config.yml exists
    if not os.path.exists("config.yml"):
        print("⚠️  config.yml not found. Creating a template...")
        with open("config.yml", "w") as f:
            f.write("""server: github
repo: "owner/repository"
pr_id: 1

github:
  token: "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"

gitlab:
  url: "https://gitlab.com"
  token: "your_gitlab_token_here"

bitbucket:
  username: "your_username"
  password: "your_password"
""")
        print("✅ Template config.yml created. Please update with your API keys.")
        print()
    
    try:
        # Run Streamlit with the simple demo
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "demo/simple_streamlit_demo.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down PR Review Agent...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Try running: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
