## AI Venture Assessor & Idea MVP

An MVP that helps rapidly evaluate product ideas for market potential, pricing, and positioning, with runnable API endpoints you can extend into a full product. The goal: a credible path to a multi-million dollar business by accelerating validation and reducing time-to-market.

### Why this can be worth a couple million dollars
- **Speed-to-validation**: Shorten idea validation from weeks to hours. Faster cycles mean more shots on goal.
- **Monetizable workflow**: Package as B2B SaaS for founders, studios, incubators, agencies, and corp innovation teams.
- **Clear ROI**: Even modest penetration achieves $2M+ ARR (e.g., ~800 orgs x $200/mo).

### Capabilities (MVP)
- Store and list ideas
- Assess ideas for market potential (stubbed heuristic today, LLM-pluggable)
- Generate a concise summary and suggested pricing tiers

### Tech Stack
- FastAPI, Pydantic, Uvicorn
- In-memory store (swap with Postgres/Redis later)

### Run locally
```bash
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:
```bash
curl -s http://127.0.0.1:8000/health
```

### Example usage
- Create an idea:
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Compliance Copilot",
    "description": "Automate GDPR gap analysis and evidence collection for audits.",
    "target_customer": "B2B SaaS companies"
  }'
```

- Assess an idea:
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Compliance Copilot",
    "description": "Automate GDPR gap analysis and evidence collection for audits.",
    "market_size_estimate": 2000000000
  }'
```

Or run the helper script (requires `jq`):
```bash
chmod +x examples/curl_examples.sh
./examples/curl_examples.sh
```

### Pricing and ROI notes
- **Starter $99/mo**: individuals, solo founders
- **Team $199–$299/mo**: small teams or agencies
- **Pro $499–$999/mo**: venture studios, corp innovation
- **Path to $2M ARR**: e.g., 600 Team + 200 Pro at $200 blended ARPU ≈ $1.6M; upsell/annual plans and professional services bridge the rest.

### Next steps
- Swap in a real LLM provider via `app/services/llm_adapter.py`
- Add persistence (Postgres) and background jobs (Celery/RQ)
- Build an opinionated UI/Flows (Next.js, shadcn/ui)

# 🤖 Programming Agent

An intelligent assistant for software development tasks including code analysis, generation, debugging, and project management.

## 🚀 Features

### 📊 Project Analysis
- **Project Structure Analysis**: Automatically analyzes your project structure
- **Language Detection**: Supports 20+ programming languages
- **Code Metrics**: Lines of code, file types, and language distribution
- **Dependency Analysis**: Identifies project dependencies

### 🔍 Code Quality Analysis
- **Static Analysis**: Analyzes code quality and identifies issues
- **Language-Specific Checks**: Python, JavaScript, TypeScript, Java support
- **Best Practices**: Suggests improvements based on coding standards
- **Metrics**: Code complexity, line length, and structure analysis

### 💻 Code Generation
- **Multi-Language Support**: Python, JavaScript, Java
- **Template-Based**: Generates code based on requirements
- **Best Practices**: Follows language-specific conventions
- **Documentation**: Auto-generates comments and docstrings

### 🐛 Debugging Assistant
- **Error Analysis**: Analyzes error messages and provides solutions
- **Syntax Checking**: Identifies syntax errors and suggests fixes
- **Common Issues**: Detects common programming mistakes
- **Fix Suggestions**: Provides specific solutions for problems

### 🔧 Refactoring Support
- **Method Extraction**: Suggests when to extract methods
- **Variable Renaming**: Identifies unclear variable names
- **Conditional Simplification**: Suggests ways to simplify complex logic
- **Code Structure**: Recommends structural improvements

### 🧪 Testing Support
- **Test Discovery**: Automatically finds and runs tests
- **Multi-Framework**: Supports pytest, unittest, npm test, maven, gradle
- **Custom Commands**: Allows custom test commands
- **Result Analysis**: Provides detailed test results

### 📁 Project Creation
- **Project Templates**: Python, JavaScript, Web projects
- **Best Practices**: Follows language-specific project structures
- **Dependencies**: Includes appropriate dependency files
- **Documentation**: Auto-generates README and documentation

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Git (for version control)

### Quick Start
```bash
# Clone or download the agent files
# Make sure you have programming_agent.py and agent_cli.py in your workspace

# Run the agent directly
python programming_agent.py

# Or use the CLI interface
python agent_cli.py --help
```

## 📖 Usage

### Command Line Interface

The agent provides a comprehensive CLI for easy interaction:

```bash
# Analyze current project
python agent_cli.py analyze

# Analyze code quality of a specific file
python agent_cli.py quality programming_agent.py

# Generate Python code
python agent_cli.py generate python "data processor" "handle CSV,validate data"

# Debug a file
python agent_cli.py debug main.py "syntax error"

# Create a new Python project
python agent_cli.py create python my_project

# Run tests
python agent_cli.py test

# Get help
python agent_cli.py help
```

### Programmatic Usage

```python
from programming_agent import ProgrammingAgent

# Initialize the agent
agent = ProgrammingAgent()

# Analyze project structure
analysis = agent.analyze_project_structure()
print(f"Found {len(analysis['files'])} files")

# Generate code
code = agent.generate_code('python', 'Create a data processor', 
                          ['Handle CSV files', 'Validate data'])
print(code)

# Debug code
debug_info = agent.debug_code('main.py', 'SyntaxError: invalid syntax')
for suggestion in debug_info['suggestions']:
    print(f"- {suggestion}")

# Create a new project
result = agent.create_project_structure('python', 'my_new_project')
if result['success']:
    print(f"Created {len(result['created_files'])} files")
```

## 🔧 Supported Languages

### Primary Support
- **Python**: Full AST analysis, PEP 8 compliance, unittest/pytest support
- **JavaScript**: ES6+ features, npm/yarn support, common patterns
- **TypeScript**: Type checking suggestions, modern JS features
- **Java**: Maven/Gradle support, OOP patterns, testing frameworks

### File Type Recognition
- **Web**: HTML, CSS, SCSS, Sass
- **Data**: JSON, XML, YAML, TOML, CSV
- **Config**: INI, Shell scripts, Docker files
- **Documentation**: Markdown, Text files
- **Version Control**: Git files, Makefiles

## 📊 Output Formats

The agent supports multiple output formats:

### Text Output (Default)
```
📊 Project Analysis
Workspace: /path/to/workspace
Files: 15
Languages: Python, JavaScript, HTML
Total lines: 1,234
```

### JSON Output
```bash
python agent_cli.py analyze --output json
```
```json
{
  "workspace_path": "/path/to/workspace",
  "files": [...],
  "languages": ["Python", "JavaScript"],
  "total_lines": 1234
}
```

## 🎯 Use Cases

### For Developers
- **Code Review**: Analyze code quality before committing
- **Refactoring**: Get suggestions for improving code structure
- **Debugging**: Quick analysis of error messages and code issues
- **Project Setup**: Create new projects with best practices

### For Teams
- **Code Standards**: Enforce consistent coding practices
- **Onboarding**: Help new developers understand project structure
- **Documentation**: Auto-generate project documentation
- **Testing**: Ensure test coverage and quality

### For Projects
- **Maintenance**: Identify technical debt and improvement areas
- **Scalability**: Analyze code complexity and structure
- **Quality Assurance**: Automated code quality checks
- **Project Management**: Track project metrics and progress

## 🔍 Advanced Features

### Custom Analysis
```python
# Custom code analysis
agent = ProgrammingAgent('/custom/path')
analysis = agent.analyze_code_quality('complex_file.py')

# Custom test commands
test_results = agent.run_tests('python -m pytest --verbose')
```

### Integration
```python
# Integrate with CI/CD pipelines
def ci_check():
    agent = ProgrammingAgent()
    analysis = agent.analyze_project_structure()
    
    if analysis['total_lines'] > 10000:
        print("⚠️ Large codebase detected")
    
    quality = agent.analyze_code_quality('main.py')
    if quality['issues']:
        print("❌ Code quality issues found")
        return False
    
    return True
```

## 🚀 Examples

### Example 1: Project Analysis
```bash
$ python agent_cli.py analyze
📊 Project Analysis
Workspace: /workspace
Files: 8
Languages: Python, Markdown, Text
Total lines: 1,847
Analysis time: 2024-01-15T10:30:00
```

### Example 2: Code Generation
```bash
$ python agent_cli.py generate python "API client" "handle HTTP requests,JSON parsing,error handling"
```

Generated code:
```python
"""
API client

Requirements:
- handle HTTP requests
- JSON parsing
- error handling

Generated by Programming Agent
"""

import requests
import json
from typing import Dict, Any, Optional

class APIClient:
    """API client for handling HTTP requests"""
    
    def __init__(self, base_url: str):
        """Initialize the API client."""
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a GET request."""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making GET request: {e}")
            return None

def main():
    """Main function for API client"""
    client = APIClient("https://api.example.com")
    data = client.get("/users")
    print(data)

if __name__ == "__main__":
    main()
```

### Example 3: Debugging
```bash
$ python agent_cli.py debug broken_file.py "IndentationError: expected an indented block"
🐛 Debug Analysis: broken_file.py
Error: IndentationError: expected an indented block

💡 Suggestions:
  - Check for missing colons, parentheses, or indentation issues

🔧 Potential Fixes:
  - Check for missing colons, parentheses, or indentation issues
```

## 🔧 Configuration

### Environment Variables
```bash
# Set custom workspace path
export AGENT_WORKSPACE=/path/to/project

# Set log level
export AGENT_LOG_LEVEL=DEBUG
```

### Logging
The agent creates detailed logs in `agent.log`:
```
2024-01-15 10:30:00 - ProgrammingAgent - INFO - Analyzing project structure...
2024-01-15 10:30:01 - ProgrammingAgent - INFO - Found 15 files
2024-01-15 10:30:02 - ProgrammingAgent - INFO - Analysis complete
```

## 🤝 Contributing

### Adding New Languages
1. Extend the `_detect_language` method
2. Add language-specific analysis in `_analyze_*_code` methods
3. Implement code generation in `_generate_*_code` methods
4. Add test cases and documentation

### Adding New Features
1. Follow the existing code structure
2. Add comprehensive error handling
3. Include logging for debugging
4. Update documentation and help text

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

### Common Issues

**Q: The agent can't find my project files**
A: Make sure you're running the agent from the correct directory or specify the workspace path.

**Q: Code generation doesn't work for my language**
A: Currently supports Python, JavaScript, and Java. Other languages can be added by extending the code generation methods.

**Q: Tests aren't running**
A: The agent tries common test commands. Use `--command` to specify a custom test command.

### Getting Help
```bash
# Show all available commands
python agent_cli.py --help

# Show detailed help
python agent_cli.py help

# Show help for specific command
python agent_cli.py analyze --help
```

## 🔮 Future Features

- [ ] Support for more programming languages (Go, Rust, C++)
- [ ] Advanced code analysis with machine learning
- [ ] Integration with popular IDEs
- [ ] Real-time code monitoring
- [ ] Performance analysis and optimization suggestions
- [ ] Security vulnerability detection
- [ ] Code documentation generation
- [ ] Dependency vulnerability scanning

---

**Happy Coding! 🚀**

The Programming Agent is designed to make your development workflow more efficient and enjoyable. Whether you're a solo developer or part of a team, it provides the tools you need to write better code, faster.