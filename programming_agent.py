#!/usr/bin/env python3
"""
Programming Agent - An intelligent assistant for software development tasks
Author: AI Assistant
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import re
import ast
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import difflib
import shutil

class ProgrammingAgent:
    """
    An intelligent programming agent that can help with various software development tasks
    including code analysis, generation, debugging, and project management.
    """
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.project_config = {}
        self.code_analysis_cache = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration for the agent."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ProgrammingAgent')
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """
        Analyze the current project structure and return detailed information.
        
        Returns:
            Dict containing project structure analysis
        """
        self.logger.info("Analyzing project structure...")
        
        analysis = {
            'workspace_path': str(self.workspace_path),
            'files': [],
            'directories': [],
            'file_types': {},
            'total_lines': 0,
            'languages': set(),
            'dependencies': {},
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.workspace_path)
                
                # Determine file type and language
                file_ext = file_path.suffix.lower()
                language = self._detect_language(file_ext, file)
                
                if language:
                    analysis['languages'].add(language)
                    if language not in analysis['file_types']:
                        analysis['file_types'][language] = []
                    analysis['file_types'][language].append(str(relative_path))
                
                # Count lines for code files
                if language:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            analysis['total_lines'] += lines
                    except Exception as e:
                        self.logger.warning(f"Could not read {file_path}: {e}")
                
                analysis['files'].append({
                    'path': str(relative_path),
                    'language': language,
                    'extension': file_ext,
                    'size': file_path.stat().st_size
                })
        
        analysis['languages'] = list(analysis['languages'])
        return analysis
    
    def _detect_language(self, extension: str, filename: str) -> Optional[str]:
        """Detect programming language based on file extension and name."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Shell',
            '.sql': 'SQL',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.gitignore': 'Git',
            '.dockerfile': 'Docker',
            '.dockerignore': 'Docker',
            'dockerfile': 'Docker',
            'makefile': 'Makefile',
            'cmakelists.txt': 'CMake'
        }
        
        return language_map.get(extension.lower()) or language_map.get(filename.lower())
    
    def analyze_code_quality(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze code quality for a specific file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict containing code quality metrics
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        analysis = {
            'file_path': str(file_path),
            'language': self._detect_language(file_path.suffix, file_path.name),
            'metrics': {},
            'issues': [],
            'suggestions': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            analysis['metrics']['total_lines'] = len(lines)
            analysis['metrics']['non_empty_lines'] = len([l for l in lines if l.strip()])
            analysis['metrics']['comment_lines'] = len([l for l in lines if l.strip().startswith(('#', '//', '/*', '*'))])
            analysis['metrics']['code_lines'] = analysis['metrics']['non_empty_lines'] - analysis['metrics']['comment_lines']
            
            # Language-specific analysis
            if analysis['language'] == 'Python':
                analysis.update(self._analyze_python_code(content, lines))
            elif analysis['language'] in ['JavaScript', 'TypeScript']:
                analysis.update(self._analyze_javascript_code(content, lines))
            elif analysis['language'] == 'Java':
                analysis.update(self._analyze_java_code(content, lines))
            
        except Exception as e:
            analysis['issues'].append(f"Error reading file: {e}")
        
        return analysis
    
    def _analyze_python_code(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze Python code quality."""
        analysis = {'issues': [], 'suggestions': []}
        
        try:
            tree = ast.parse(content)
            
            # Check for common issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 5:
                        analysis['suggestions'].append(f"Function '{node.name}' has many parameters - consider using a data class")
                    
                elif isinstance(node, ast.ClassDef):
                    if len(node.body) > 20:
                        analysis['suggestions'].append(f"Class '{node.name}' is quite large - consider breaking it down")
                        
        except SyntaxError as e:
            analysis['issues'].append(f"Syntax error: {e}")
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            analysis['suggestions'].append(f"Lines {long_lines} exceed PEP 8 line length limit (79 characters)")
        
        return analysis
    
    def _analyze_javascript_code(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code quality."""
        analysis = {'issues': [], 'suggestions': []}
        
        # Check for common patterns
        if 'console.log(' in content:
            analysis['suggestions'].append("Consider removing console.log statements for production")
        
        if 'var ' in content:
            analysis['suggestions'].append("Consider using 'const' or 'let' instead of 'var'")
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 80]
        if long_lines:
            analysis['suggestions'].append(f"Lines {long_lines} exceed recommended line length (80 characters)")
        
        return analysis
    
    def _analyze_java_code(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze Java code quality."""
        analysis = {'issues': [], 'suggestions': []}
        
        # Check for common patterns
        if 'System.out.println(' in content:
            analysis['suggestions'].append("Consider using a proper logging framework instead of System.out.println")
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            analysis['suggestions'].append(f"Lines {long_lines} exceed recommended line length (120 characters)")
        
        return analysis
    
    def generate_code(self, language: str, purpose: str, requirements: List[str]) -> str:
        """
        Generate code based on requirements.
        
        Args:
            language: Programming language
            purpose: What the code should do
            requirements: List of specific requirements
            
        Returns:
            Generated code as string
        """
        self.logger.info(f"Generating {language} code for: {purpose}")
        
        if language.lower() == 'python':
            return self._generate_python_code(purpose, requirements)
        elif language.lower() in ['javascript', 'js']:
            return self._generate_javascript_code(purpose, requirements)
        elif language.lower() == 'java':
            return self._generate_java_code(purpose, requirements)
        else:
            return f"# Code generation for {language} is not yet implemented\n# Purpose: {purpose}\n# Requirements: {requirements}"
    
    def _generate_python_code(self, purpose: str, requirements: List[str]) -> str:
        """Generate Python code based on purpose and requirements."""
        code = f'''"""
{purpose}

Requirements:
{chr(10).join(f"- {req}" for req in requirements)}

Generated by Programming Agent
"""

'''
        
        if "class" in purpose.lower() or any("class" in req.lower() for req in requirements):
            class_name = "GeneratedClass"
            code += f'''class {class_name}:
    """{purpose}"""
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def process(self):
        """Main processing method."""
        # TODO: Implement based on requirements
        pass

'''
        
        if "function" in purpose.lower() or any("function" in req.lower() for req in requirements):
            code += f'''def main():
    """Main function for {purpose}"""
    # TODO: Implement based on requirements
    pass

if __name__ == "__main__":
    main()
'''
        
        return code
    
    def _generate_javascript_code(self, purpose: str, requirements: List[str]) -> str:
        """Generate JavaScript code based on purpose and requirements."""
        code = f'''/**
 * {purpose}
 * 
 * Requirements:
{chr(10).join(f" * - {req}" for req in requirements)}
 * 
 * Generated by Programming Agent
 */

'''
        
        if "class" in purpose.lower() or any("class" in req.lower() for req in requirements):
            class_name = "GeneratedClass"
            code += f'''class {class_name} {{
    constructor() {{
        // Initialize the class
    }}
    
    process() {{
        // TODO: Implement based on requirements
    }}
}}

'''
        
        code += f'''function main() {{
    // Main function for {purpose}
    // TODO: Implement based on requirements
}}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ main }};
}}
'''
        
        return code
    
    def _generate_java_code(self, purpose: str, requirements: List[str]) -> str:
        """Generate Java code based on purpose and requirements."""
        code = f'''/**
 * {purpose}
 * 
 * Requirements:
{chr(10).join(f" * - {req}" for req in requirements)}
 * 
 * Generated by Programming Agent
 */

'''
        
        if "class" in purpose.lower() or any("class" in req.lower() for req in requirements):
            class_name = "GeneratedClass"
            code += f'''public class {class_name} {{
    
    public {class_name}() {{
        // Initialize the class
    }}
    
    public void process() {{
        // TODO: Implement based on requirements
    }}
    
    public static void main(String[] args) {{
        {class_name} instance = new {class_name}();
        instance.process();
    }}
}}
'''
        else:
            code += f'''public class Main {{
    public static void main(String[] args) {{
        // Main function for {purpose}
        // TODO: Implement based on requirements
    }}
}}
'''
        
        return code
    
    def debug_code(self, file_path: str, error_message: str = None) -> Dict[str, Any]:
        """
        Debug code in a file and provide suggestions.
        
        Args:
            file_path: Path to the file to debug
            error_message: Optional error message to help with debugging
            
        Returns:
            Dict containing debugging analysis and suggestions
        """
        self.logger.info(f"Debugging code in: {file_path}")
        
        debug_info = {
            'file_path': file_path,
            'error_message': error_message,
            'analysis': {},
            'suggestions': [],
            'potential_fixes': []
        }
        
        try:
            analysis = self.analyze_code_quality(file_path)
            debug_info['analysis'] = analysis
            
            # Add debugging suggestions based on analysis
            if analysis['issues']:
                debug_info['suggestions'].extend(analysis['issues'])
            
            if analysis['suggestions']:
                debug_info['suggestions'].extend(analysis['suggestions'])
            
            # Language-specific debugging
            if analysis['language'] == 'Python':
                debug_info.update(self._debug_python_code(file_path, error_message))
            elif analysis['language'] in ['JavaScript', 'TypeScript']:
                debug_info.update(self._debug_javascript_code(file_path, error_message))
                
        except Exception as e:
            debug_info['suggestions'].append(f"Error during debugging: {e}")
        
        return debug_info
    
    def _debug_python_code(self, file_path: str, error_message: str) -> Dict[str, Any]:
        """Debug Python code specifically."""
        suggestions = []
        potential_fixes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse the code
            try:
                ast.parse(content)
            except SyntaxError as e:
                suggestions.append(f"Syntax error: {e}")
                potential_fixes.append("Check for missing colons, parentheses, or indentation issues")
            
            # Check for common Python issues
            if 'import *' in content:
                suggestions.append("Avoid using 'import *' - import specific modules instead")
            
            if 'except:' in content:
                suggestions.append("Use specific exception types instead of bare 'except:'")
                
        except Exception as e:
            suggestions.append(f"Error reading file: {e}")
        
        return {'suggestions': suggestions, 'potential_fixes': potential_fixes}
    
    def _debug_javascript_code(self, file_path: str, error_message: str) -> Dict[str, Any]:
        """Debug JavaScript code specifically."""
        suggestions = []
        potential_fixes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common JavaScript issues
            if 'var ' in content:
                suggestions.append("Consider using 'const' or 'let' instead of 'var'")
            
            if '===' not in content and '==' in content:
                suggestions.append("Consider using '===' for strict equality comparisons")
                
        except Exception as e:
            suggestions.append(f"Error reading file: {e}")
        
        return {'suggestions': suggestions, 'potential_fixes': potential_fixes}
    
    def refactor_code(self, file_path: str, refactoring_type: str) -> Dict[str, Any]:
        """
        Suggest refactoring for a file.
        
        Args:
            file_path: Path to the file to refactor
            refactoring_type: Type of refactoring (e.g., 'extract_method', 'rename_variable')
            
        Returns:
            Dict containing refactoring suggestions
        """
        self.logger.info(f"Suggesting refactoring for: {file_path}")
        
        refactor_info = {
            'file_path': file_path,
            'refactoring_type': refactoring_type,
            'suggestions': [],
            'before_code': '',
            'after_code': ''
        }
        
        try:
            analysis = self.analyze_code_quality(file_path)
            
            if refactoring_type == 'extract_method':
                refactor_info.update(self._suggest_extract_method(file_path, analysis))
            elif refactoring_type == 'rename_variable':
                refactor_info.update(self._suggest_rename_variable(file_path, analysis))
            elif refactoring_type == 'simplify_conditionals':
                refactor_info.update(self._suggest_simplify_conditionals(file_path, analysis))
            else:
                refactor_info['suggestions'].append(f"Refactoring type '{refactoring_type}' not yet implemented")
                
        except Exception as e:
            refactor_info['suggestions'].append(f"Error during refactoring analysis: {e}")
        
        return refactor_info
    
    def _suggest_extract_method(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest method extraction refactoring."""
        suggestions = []
        
        # This is a simplified suggestion - in a real implementation,
        # you would analyze the code more deeply to find opportunities
        suggestions.append("Look for code blocks longer than 10 lines that could be extracted into methods")
        suggestions.append("Identify repeated code patterns that could be extracted into utility methods")
        
        return {'suggestions': suggestions}
    
    def _suggest_rename_variable(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest variable renaming refactoring."""
        suggestions = []
        
        suggestions.append("Look for variables with unclear names like 'a', 'b', 'temp', 'data'")
        suggestions.append("Ensure variable names are descriptive and follow naming conventions")
        
        return {'suggestions': suggestions}
    
    def _suggest_simplify_conditionals(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest conditional simplification refactoring."""
        suggestions = []
        
        suggestions.append("Look for nested if statements that could be simplified")
        suggestions.append("Consider using early returns to reduce nesting")
        suggestions.append("Extract complex conditions into well-named boolean methods")
        
        return {'suggestions': suggestions}
    
    def run_tests(self, test_command: str = None) -> Dict[str, Any]:
        """
        Run tests for the project.
        
        Args:
            test_command: Custom test command to run
            
        Returns:
            Dict containing test results
        """
        self.logger.info("Running tests...")
        
        test_results = {
            'success': False,
            'output': '',
            'error': None,
            'test_command': test_command
        }
        
        try:
            if test_command:
                result = subprocess.run(test_command, shell=True, capture_output=True, text=True, cwd=self.workspace_path)
            else:
                # Try common test commands
                test_commands = [
                    'python -m pytest',
                    'python -m unittest discover',
                    'npm test',
                    'yarn test',
                    'mvn test',
                    'gradle test'
                ]
                
                for cmd in test_commands:
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.workspace_path, timeout=30)
                        if result.returncode == 0:
                            test_results['test_command'] = cmd
                            break
                    except subprocess.TimeoutExpired:
                        continue
                    except FileNotFoundError:
                        continue
                else:
                    test_results['error'] = "No suitable test command found"
                    return test_results
            
            test_results['output'] = result.stdout
            test_results['success'] = result.returncode == 0
            
            if result.stderr:
                test_results['error'] = result.stderr
                
        except Exception as e:
            test_results['error'] = str(e)
        
        return test_results
    
    def create_project_structure(self, project_type: str, project_name: str) -> Dict[str, Any]:
        """
        Create a new project structure.
        
        Args:
            project_type: Type of project (e.g., 'python', 'javascript', 'web')
            project_name: Name of the project
            
        Returns:
            Dict containing creation results
        """
        self.logger.info(f"Creating {project_type} project: {project_name}")
        
        result = {
            'success': False,
            'created_files': [],
            'error': None
        }
        
        try:
            project_path = self.workspace_path / project_name
            project_path.mkdir(exist_ok=True)
            
            if project_type.lower() == 'python':
                result.update(self._create_python_project(project_path))
            elif project_type.lower() in ['javascript', 'js']:
                result.update(self._create_javascript_project(project_path))
            elif project_type.lower() == 'web':
                result.update(self._create_web_project(project_path))
            else:
                result['error'] = f"Project type '{project_type}' not supported"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _create_python_project(self, project_path: Path) -> Dict[str, Any]:
        """Create a Python project structure."""
        created_files = []
        
        # Create basic Python project structure
        files_to_create = {
            'README.md': f'''# {project_path.name}

A Python project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
''',
            'main.py': '''#!/usr/bin/env python3
"""
Main entry point for the application.
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''',
            'requirements.txt': '# Add your Python dependencies here\n',
            '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
''',
            'tests/__init__.py': '',
            'tests/test_main.py': '''import unittest
from main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        """Test main function."""
        # Add your tests here
        pass

if __name__ == '__main__':
    unittest.main()
'''
        }
        
        for filename, content in files_to_create.items():
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            created_files.append(str(file_path))
        
        return {'success': True, 'created_files': created_files}
    
    def _create_javascript_project(self, project_path: Path) -> Dict[str, Any]:
        """Create a JavaScript project structure."""
        created_files = []
        
        files_to_create = {
            'package.json': '''{
  "name": "''' + project_path.name + '''",
  "version": "1.0.0",
  "description": "A JavaScript project",
  "main": "index.js",
  "scripts": {
    "test": "echo \\"Error: no test specified\\" && exit 1",
    "start": "node index.js"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
''',
            'index.js': '''/**
 * Main entry point for the application.
 */

function main() {
    console.log("Hello, World!");
}

main();
''',
            '.gitignore': '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
''',
            'README.md': f'''# {project_path.name}

A JavaScript project.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```
'''
        }
        
        for filename, content in files_to_create.items():
            file_path = project_path / filename
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            created_files.append(str(file_path))
        
        return {'success': True, 'created_files': created_files}
    
    def _create_web_project(self, project_path: Path) -> Dict[str, Any]:
        """Create a web project structure."""
        created_files = []
        
        files_to_create = {
            'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + project_path.name + '''</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to ''' + project_path.name + '''</h1>
        <p>This is a web project.</p>
    </div>
    <script src="script.js"></script>
</body>
</html>
''',
            'styles.css': '''/* CSS styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f0f0f0;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

h1 {
    color: #333;
    text-align: center;
}
''',
            'script.js': '''// JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Web page loaded!');
});
''',
            'README.md': f'''# {project_path.name}

A web project.

## Usage

Open `index.html` in your web browser to view the project.
'''
        }
        
        for filename, content in files_to_create.items():
            file_path = project_path / filename
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            created_files.append(str(file_path))
        
        return {'success': True, 'created_files': created_files}
    
    def get_help(self) -> str:
        """Get help information about the agent."""
        return '''
Programming Agent Help
=====================

Available Commands:
------------------

1. analyze_project_structure()
   - Analyzes the current project structure
   - Returns detailed information about files, languages, and metrics

2. analyze_code_quality(file_path)
   - Analyzes code quality for a specific file
   - Provides metrics, issues, and suggestions

3. generate_code(language, purpose, requirements)
   - Generates code based on requirements
   - Supported languages: Python, JavaScript, Java

4. debug_code(file_path, error_message=None)
   - Debugs code and provides suggestions
   - Analyzes syntax and common issues

5. refactor_code(file_path, refactoring_type)
   - Suggests refactoring for a file
   - Types: extract_method, rename_variable, simplify_conditionals

6. run_tests(test_command=None)
   - Runs tests for the project
   - Automatically detects test commands

7. create_project_structure(project_type, project_name)
   - Creates a new project structure
   - Types: python, javascript, web

8. get_help()
   - Shows this help information

Usage Examples:
---------------

# Analyze current project
agent = ProgrammingAgent()
analysis = agent.analyze_project_structure()
print(json.dumps(analysis, indent=2))

# Generate Python code
code = agent.generate_code('python', 'Create a data processor', ['Handle CSV files', 'Validate data'])
print(code)

# Debug a file
debug_info = agent.debug_code('main.py', 'SyntaxError: invalid syntax')
print(debug_info['suggestions'])

# Create a new Python project
result = agent.create_project_structure('python', 'my_new_project')
print(f"Created files: {result['created_files']}")
'''

def main():
    """Main function to demonstrate the programming agent."""
    agent = ProgrammingAgent()
    
    print("🤖 Programming Agent v1.0.0")
    print("=" * 50)
    
    # Analyze current project
    print("\n📊 Analyzing project structure...")
    analysis = agent.analyze_project_structure()
    print(f"Found {len(analysis['files'])} files in {len(analysis['languages'])} languages")
    print(f"Languages: {', '.join(analysis['languages'])}")
    print(f"Total lines of code: {analysis['total_lines']}")
    
    # Show help
    print("\n📖 Help Information:")
    print(agent.get_help())
    
    print("\n✨ Programming Agent is ready to help with your coding tasks!")

if __name__ == "__main__":
    main()