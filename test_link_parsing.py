#!/usr/bin/env python3
"""
Test script to demonstrate link parsing functionality
"""

import re

def test_link_parsing():
    """Test the link parsing functionality"""
    print("🔗 Testing PR/MR Link Parsing")
    print("=" * 50)
    
    # Test cases
    test_links = [
        "https://github.com/octocat/Hello-World/pull/1",
        "https://gitlab.com/group/project/-/merge_requests/123",
        "https://bitbucket.org/workspace/repo/pull-requests/456",
        "https://github.com/microsoft/vscode/pull/12345",
        "https://gitlab.com/gitlab-org/gitlab/-/merge_requests/45678",
        "https://bitbucket.org/atlassian/bitbucket/pull-requests/789"
    ]
    
    for link in test_links:
        print(f"\n🔍 Testing: {link}")
        
        try:
            # GitHub PR link
            if "github.com" in link:
                match = re.search(r'github\.com/([^/]+/[^/]+)/pull/(\d+)', link)
                if match:
                    repo = match.group(1)
                    pr_id = int(match.group(2))
                    print(f"✅ GitHub: {repo} PR #{pr_id}")
                else:
                    print("❌ Invalid GitHub PR link format")
            
            # GitLab MR link
            elif "gitlab.com" in link or "gitlab" in link:
                match = re.search(r'gitlab\.com/([^/]+/[^/]+)/-/merge_requests/(\d+)', link)
                if match:
                    repo = match.group(1)
                    pr_id = int(match.group(2))
                    print(f"✅ GitLab: {repo} MR !{pr_id}")
                else:
                    print("❌ Invalid GitLab MR link format")
            
            # Bitbucket PR link
            elif "bitbucket.org" in link or "bitbucket" in link:
                match = re.search(r'bitbucket\.org/([^/]+/[^/]+)/pull-requests/(\d+)', link)
                if match:
                    repo = match.group(1)
                    pr_id = int(match.group(2))
                    print(f"✅ Bitbucket: {repo} PR #{pr_id}")
                else:
                    print("❌ Invalid Bitbucket PR link format")
            
            else:
                print("⚠️ Unsupported link format")
                
        except Exception as e:
            print(f"❌ Error parsing link: {e}")

def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    print("\n1. GitHub PR Link:")
    print("   https://github.com/octocat/Hello-World/pull/1")
    print("   → Extracts: octocat/Hello-World, PR #1")
    
    print("\n2. GitLab MR Link:")
    print("   https://gitlab.com/group/project/-/merge_requests/123")
    print("   → Extracts: group/project, MR !123")
    
    print("\n3. Bitbucket PR Link:")
    print("   https://bitbucket.org/workspace/repo/pull-requests/456")
    print("   → Extracts: workspace/repo, PR #456")
    
    print("\n4. Streamlit Usage:")
    print("   - Paste any of these links in the 'PR/MR Link' textbox")
    print("   - The system will auto-detect the platform and extract details")
    print("   - Click '⚡ Quick Analyze' to start analysis")

if __name__ == "__main__":
    test_link_parsing()
    show_usage_examples()
