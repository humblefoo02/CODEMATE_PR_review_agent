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
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "demo/simple_streamlit_demo.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down PR Review Agent...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
