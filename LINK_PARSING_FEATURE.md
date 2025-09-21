# 🔗 Link Parsing Feature

## ✅ **New Feature Added**

I've added a **PR/MR Link textbox** to the Streamlit dashboard that automatically extracts repository and PR number from GitHub, GitLab, and Bitbucket links.

## 🚀 **How It Works**

### **1. Paste Any PR/MR Link**
Simply paste a link in the "PR/MR Link" textbox in the sidebar:

- **GitHub**: `https://github.com/owner/repo/pull/123`
- **GitLab**: `https://gitlab.com/group/project/-/merge_requests/123`
- **Bitbucket**: `https://bitbucket.org/workspace/repo/pull-requests/456`

### **2. Auto-Detection**
The system automatically:
- ✅ Detects the platform (GitHub/GitLab/Bitbucket)
- ✅ Extracts repository name
- ✅ Extracts PR/MR number
- ✅ Auto-fills the form fields
- ✅ Sets the correct server type

### **3. Quick Analysis**
When a valid link is detected:
- ✅ Shows "⚡ Quick Analyze" button
- ✅ Displays extracted information
- ✅ One-click analysis

## 📊 **Supported Link Formats**

### **GitHub PR Links**
```
https://github.com/octocat/Hello-World/pull/1
https://github.com/microsoft/vscode/pull/12345
```
**Extracts**: `octocat/Hello-World`, PR #1

### **GitLab MR Links**
```
https://gitlab.com/group/project/-/merge_requests/123
https://gitlab.com/gitlab-org/gitlab/-/merge_requests/45678
```
**Extracts**: `group/project`, MR !123

### **Bitbucket PR Links**
```
https://bitbucket.org/workspace/repo/pull-requests/456
https://bitbucket.org/atlassian/bitbucket/pull-requests/789
```
**Extracts**: `workspace/repo`, PR #456

## 🎯 **User Experience**

### **Before (Manual Entry)**
1. Select server type
2. Enter repository manually
3. Enter PR number manually
4. Click analyze

### **After (Link Parsing)**
1. Paste PR/MR link
2. Click "⚡ Quick Analyze"
3. Done! 🎉

## 🔧 **Technical Implementation**

### **Link Parsing Logic**
```python
# GitHub
match = re.search(r'github\.com/([^/]+/[^/]+)/pull/(\d+)', link)

# GitLab  
match = re.search(r'gitlab\.com/([^/]+/[^/]+)/-/merge_requests/(\d+)', link)

# Bitbucket
match = re.search(r'bitbucket\.org/([^/]+/[^/]+)/pull-requests/(\d+)', link)
```

### **Auto-Detection Features**
- ✅ Platform detection
- ✅ Repository extraction
- ✅ PR/MR number extraction
- ✅ Form auto-filling
- ✅ Server type selection
- ✅ Error handling
- ✅ Success feedback

## 🏆 **Hackathon Advantages**

### **1. User-Friendly**
- ✅ One-click analysis from any PR/MR link
- ✅ No manual configuration needed
- ✅ Supports all major platforms

### **2. Time-Saving**
- ✅ Copy-paste from browser
- ✅ No manual data entry
- ✅ Instant analysis

### **3. Professional**
- ✅ Clean, intuitive interface
- ✅ Error handling and validation
- ✅ Success feedback

## 🚀 **Usage Examples**

### **Example 1: GitHub PR**
```
Input: https://github.com/octocat/Hello-World/pull/1
Output: ✅ GitHub: octocat/Hello-World PR #1
Action: Click "⚡ Quick Analyze"
```

### **Example 2: GitLab MR**
```
Input: https://gitlab.com/group/project/-/merge_requests/123
Output: ✅ GitLab: group/project MR !123
Action: Click "⚡ Quick Analyze"
```

### **Example 3: Bitbucket PR**
```
Input: https://bitbucket.org/workspace/repo/pull-requests/456
Output: ✅ Bitbucket: workspace/repo PR #456
Action: Click "⚡ Quick Analyze"
```

## 🎯 **Ready to Win!**

The PR Review Agent now has:
- ✅ **Link parsing** for all major platforms
- ✅ **One-click analysis** from any PR/MR link
- ✅ **Auto-detection** of platform and details
- ✅ **Professional UI** with error handling
- ✅ **Time-saving** workflow

**Perfect for hackathon demos! 🏆**
