# 🤖 PR Review Agent

An AI-powered pull request review system that analyzes code quality, security, and best practices across multiple git platforms (GitHub, GitLab, Bitbucket).

## ✨ Features

### 🔍 **Comprehensive Code Analysis**
- **Style & Linting**: Flake8 integration for Python code style
- **Security Scanning**: Bandit for security vulnerability detection
- **Complexity Analysis**: Radon for cyclomatic complexity assessment
- **Dependency Scanning**: Safety for vulnerability detection
- **Custom Analysis**: TODO/FIXME detection, hardcoded secrets, large functions

### 🤖 **AI-Powered Feedback**
- **OpenAI Integration**: Intelligent code suggestions and improvements
- **Context-Aware**: Understands code context and provides relevant feedback
- **Actionable Suggestions**: Specific, implementable recommendations

### 🎯 **Multi-Platform Support**
- **GitHub**: Full API integration with rate limiting
- **GitLab**: Complete merge request support
- **Bitbucket**: Pull request analysis and commenting

### 📊 **Advanced Scoring System**
- **Weighted Scoring**: Different weights for security, style, complexity
- **Grade System**: A+ to F grading with detailed breakdowns
- **Metrics Dashboard**: Comprehensive analysis metrics

### 🌐 **Multiple Interfaces**
- **CLI Interface**: Rich terminal output with progress bars
- **Web Dashboard**: Interactive web interface for detailed analysis
- **API Endpoints**: RESTful API for integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- API keys for your git platforms

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pr-review-agent.git
cd pr-review-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys**
```yaml
# config.yml
server: github
repo: "owner/repository"
pr_id: 123

github:
  token: "your_github_token"

gitlab:
  url: "https://gitlab.com"
  token: "your_gitlab_token"

bitbucket:
  username: "your_username"
  password: "your_password"
```

4. **Set up environment variables (optional)**
```bash
export OPENAI_API_KEY="your_openai_key"
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"
```

### Usage

#### 🖥️ **Command Line Interface**

**Basic Analysis:**
```bash
python main.py --server github --repo octocat/Hello-World --pr-id 1
```

**Advanced CLI with Rich Output:**
```bash
python demo/cli_demo.py --server github --repo owner/repo --pr-id 123 --export results.json
```

**Options:**
- `--server`: Choose git server (github, gitlab, bitbucket)
- `--repo`: Repository in format "owner/repo"
- `--pr-id`: Pull request/merge request number
- `--export`: Export results to JSON file
- `--verbose`: Enable detailed logging
- `--no-ai`: Disable AI-powered feedback

#### 🌐 **Web Dashboard (Streamlit)**

**Start the Streamlit dashboard:**
```bash
python run_streamlit.py
# OR
streamlit run demo/streamlit_demo.py
```

**Access the dashboard:**
- Open http://localhost:8501 in your browser
- Configure analysis parameters in the sidebar
- Click "Analyze PR" to start analysis
- View interactive charts and detailed results

#### 🐳 **Docker Deployment**

**Using Docker Compose:**
```bash
docker-compose up -d
```

**Using Docker:**
```bash
docker build -t pr-review-agent .
docker run -p 8501:8501 pr-review-agent
```

**Access the dashboard:**
- Open http://localhost:8501 in your browser

## 📋 API Reference

### Endpoints

#### `GET /api/analyze`
Analyze a pull request
- **Parameters**: `server`, `repo`, `pr_id`
- **Returns**: Complete analysis results

#### `GET /api/status`
Get current analysis status
- **Returns**: Analysis state and metrics

#### `GET /api/feedback`
Get detailed feedback
- **Returns**: Structured feedback items

#### `GET /api/score`
Get score breakdown
- **Returns**: Detailed scoring information

#### `POST /api/comment`
Create review comment
- **Parameters**: `file_path`, `line`, `comment`
- **Returns**: Success status

#### `GET /api/export`
Export analysis report
- **Parameters**: `format` (json)
- **Returns**: Complete report data

## 🔧 Configuration

### Analysis Tools

The system uses multiple analysis tools that can be configured:

```yaml
# config.yml
analysis:
  flake8:
    enabled: true
    max_line_length: 88
  bandit:
    enabled: true
    severity_level: medium
  radon:
    enabled: true
    complexity_threshold: 10
  safety:
    enabled: true
    check_live: false
```

### AI Integration

Configure AI providers in your environment:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-3.5-turbo"
export OPENAI_MAX_TOKENS="1000"

# Anthropic (alternative)
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 🧪 Testing

**Run the test suite:**
```bash
pytest tests/ -v --cov=core --cov=integrations --cov=utils
```

**Run specific test categories:**
```bash
pytest tests/test_analyzer.py -v
pytest tests/test_feedback.py -v
pytest tests/test_scorer.py -v
```

**Generate coverage report:**
```bash
pytest --cov=core --cov-report=html
```

## 🚀 CI/CD Integration

### GitHub Actions

The repository includes GitHub Actions workflows for:
- Automated testing on multiple Python versions
- Security scanning with Bandit and Safety
- Code quality checks with Flake8 and MyPy
- Automated PR reviews

### Custom CI Integration

**Example GitHub Actions step:**
```yaml
- name: Run PR Review Agent
  run: |
    python main.py --server github --repo ${{ github.repository }} --pr-id ${{ github.event.number }}
```

**Example GitLab CI step:**
```yaml
pr_review:
  script:
    - python main.py --server gitlab --repo $CI_PROJECT_PATH --pr-id $CI_MERGE_REQUEST_IID
```

## 📊 Scoring System

### Score Calculation

The scoring system uses weighted penalties:

- **Security Issues**: 30% weight (highest priority)
- **Errors**: 25% weight
- **Complexity**: 20% weight
- **Style**: 15% weight
- **Maintainability**: 10% weight

### Grade Scale

- **A+**: 95-100 (Excellent)
- **A**: 90-94 (Very Good)
- **B+**: 85-89 (Good)
- **B**: 80-84 (Satisfactory)
- **C+**: 75-79 (Needs Improvement)
- **C**: 70-74 (Below Standards)
- **D**: 60-69 (Poor)
- **F**: 0-59 (Failing)

## 🔒 Security

### API Key Management

- Store API keys in environment variables
- Use `.env` files for local development
- Never commit API keys to version control

### Security Scanning

The system includes multiple security checks:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanning
- **Custom**: Hardcoded secret detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Run linting
flake8 .

# Run type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flake8** for Python linting
- **Bandit** for security analysis
- **Radon** for complexity analysis
- **OpenAI** for AI-powered feedback
- **Rich** for beautiful terminal output
- **FastAPI** for the web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pr-review-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pr-review-agent/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/pr-review-agent/wiki)

---

**Made with ❤️ for the developer community**
