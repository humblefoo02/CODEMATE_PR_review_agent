#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import yaml
        print("✅ PyYAML imported")
        
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import plotly
        print("✅ Plotly imported")
        
        # Test core modules
        from core.analyzer import Analyzer
        print("✅ Analyzer imported")
        
        from core.feedback import FeedbackGenerator
        print("✅ FeedbackGenerator imported")
        
        from core.scorer import PRScorer
        print("✅ PRScorer imported")
        
        from core.fetcher import PRFetcher
        print("✅ PRFetcher imported")
        
        from utils.logger import get_logger
        print("✅ Logger imported")
        
        # Test integrations
        from integrations.github import GitHubIntegration
        print("✅ GitHub integration imported")
        
        from integrations.gitlab import GitLabIntegration
        print("✅ GitLab integration imported")
        
        from integrations.bitbucket import BitbucketIntegration
        print("✅ Bitbucket integration imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
