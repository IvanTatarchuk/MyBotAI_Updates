#!/usr/bin/env python3
"""
🤖 AI-Powered Code Generator
Natural language to code conversion and intelligent code generation
"""

import re
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class CodeLanguage(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"
    SWIFT = "swift"
    KOTLIN = "kotlin"

class CodeType(Enum):
    """Types of code to generate."""
    FUNCTION = "function"
    CLASS = "class"
    API_ENDPOINT = "api_endpoint"
    DATABASE_MODEL = "database_model"
    ALGORITHM = "algorithm"
    UTILITY = "utility"
    TEST = "test"
    CONFIGURATION = "configuration"

@dataclass
class CodeRequest:
    """Code generation request."""
    description: str
    language: CodeLanguage
    code_type: CodeType
    requirements: List[str]
    context: Dict[str, Any]

@dataclass
class GeneratedCode:
    """Generated code result."""
    code: str
    language: CodeLanguage
    type: CodeType
    description: str
    complexity: str
    estimated_time: str
    dependencies: List[str]
    usage_example: str
    tests: str

class AICodeGenerator:
    """AI-powered code generator."""
    
    def __init__(self):
        self.setup_logging()
        self.code_templates = self._load_code_templates()
        self.language_patterns = self._load_language_patterns()
        
        logging.info("🤖 AI Code Generator initialized")

    def setup_logging(self):
        """Setup logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _load_code_templates(self) -> Dict[str, Dict[str, str]]:
        """Load code templates for different languages and types."""
        return {
            "python": {
                "function": """
def {function_name}({parameters}):
    \"\"\"
    {description}
    
    Args:
        {args_doc}
    
    Returns:
        {return_type}: {return_description}
    \"\"\"
    {implementation}
    return {return_value}
""",
                "class": """
class {class_name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self, {init_params}):
        {init_implementation}
    
    {methods}
""",
                "api_endpoint": """
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('{endpoint}', methods=['{methods}'])
def {function_name}():
    \"\"\"
    {description}
    \"\"\"
    try:
        {implementation}
        return jsonify({response}), {status_code}
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500
""",
                "database_model": """
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {model_name}(Base):
    \"\"\"
    {description}
    \"\"\"
    __tablename__ = '{table_name}'
    
    {columns}
    
    def __repr__(self):
        return f'<{model_name}({repr_fields})>'
"""
            },
            "javascript": {
                "function": """
/**
 * {description}
 * @param {parameters} - {param_descriptions}
 * @returns {return_type} - {return_description}
 */
function {function_name}({parameters}) {{
    {implementation}
    return {return_value};
}}
""",
                "class": """
/**
 * {description}
 */
class {class_name} {{
    constructor({constructor_params}) {{
        {constructor_implementation}
    }}
    
    {methods}
}}
""",
                "api_endpoint": """
const express = require('express');
const router = express.Router();

/**
 * {description}
 */
router.get('{endpoint}', async (req, res) => {{
    try {{
        {implementation}
        res.status({status_code}).json({response});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});

module.exports = router;
"""
            }
        }

    def _load_language_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load language-specific patterns and conventions."""
        return {
            "python": {
                "naming": "snake_case",
                "indentation": "4 spaces",
                "docstring": "Google style",
                "imports": "standard library first, then third-party"
            },
            "javascript": {
                "naming": "camelCase",
                "indentation": "2 spaces",
                "docstring": "JSDoc",
                "imports": "ES6 modules"
            },
            "java": {
                "naming": "PascalCase for classes, camelCase for methods",
                "indentation": "4 spaces",
                "docstring": "JavaDoc",
                "imports": "package imports first"
            }
        }

    def generate_code(self, request: CodeRequest) -> GeneratedCode:
        """Generate code based on natural language description."""
        logging.info(f"🤖 Generating {request.code_type.value} in {request.language.value}")
        
        # Parse the description to extract key information
        parsed_info = self._parse_description(request.description)
        
        # Generate appropriate code based on type
        if request.code_type == CodeType.FUNCTION:
            code = self._generate_function(request, parsed_info)
        elif request.code_type == CodeType.CLASS:
            code = self._generate_class(request, parsed_info)
        elif request.code_type == CodeType.API_ENDPOINT:
            code = self._generate_api_endpoint(request, parsed_info)
        elif request.code_type == CodeType.DATABASE_MODEL:
            code = self._generate_database_model(request, parsed_info)
        else:
            code = self._generate_generic_code(request, parsed_info)
        
        # Generate tests and examples
        tests = self._generate_tests(request, code)
        usage_example = self._generate_usage_example(request, code)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            type=request.code_type,
            description=request.description,
            complexity=self._assess_complexity(parsed_info),
            estimated_time=self._estimate_development_time(parsed_info),
            dependencies=self._extract_dependencies(request, parsed_info),
            usage_example=usage_example,
            tests=tests
        )

    def _parse_description(self, description: str) -> Dict[str, Any]:
        """Parse natural language description to extract code requirements."""
        parsed = {
            "name": self._extract_name(description),
            "parameters": self._extract_parameters(description),
            "return_type": self._extract_return_type(description),
            "logic": self._extract_logic(description),
            "complexity": self._assess_complexity_from_text(description)
        }
        
        logging.info(f"📝 Parsed description: {parsed}")
        return parsed

    def _extract_name(self, description: str) -> str:
        """Extract function/class name from description."""
        # Look for patterns like "function called X" or "class X"
        patterns = [
            r"function\s+(?:called\s+)?(\w+)",
            r"class\s+(\w+)",
            r"(\w+)\s+function",
            r"create\s+(\w+)",
            r"build\s+(\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Generate a name based on the description
        words = description.lower().split()
        key_words = [w for w in words if w not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']]
        
        if key_words:
            return "_".join(key_words[:3])
        
        return "generated_function"

    def _extract_parameters(self, description: str) -> List[Dict[str, str]]:
        """Extract parameters from description."""
        parameters = []
        
        # Look for parameter patterns
        param_patterns = [
            r"(\w+)\s+(?:parameter|input|argument)",
            r"takes?\s+(\w+)",
            r"accepts?\s+(\w+)",
            r"(\w+)\s+value"
        ]
        
        for pattern in param_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                param_name = match.group(1)
                param_type = self._infer_parameter_type(param_name, description)
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "description": f"Input {param_name}"
                })
        
        return parameters

    def _infer_parameter_type(self, param_name: str, description: str) -> str:
        """Infer parameter type from context."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['number', 'count', 'size', 'length', 'index']):
            return "int"
        elif any(word in description_lower for word in ['text', 'string', 'name', 'message']):
            return "str"
        elif any(word in description_lower for word in ['list', 'array', 'collection']):
            return "list"
        elif any(word in description_lower for word in ['dictionary', 'dict', 'object']):
            return "dict"
        elif any(word in description_lower for word in ['boolean', 'flag', 'is_']):
            return "bool"
        else:
            return "any"

    def _extract_return_type(self, description: str) -> str:
        """Extract return type from description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['return', 'output', 'result']):
            if 'number' in description_lower or 'count' in description_lower:
                return "int"
            elif 'text' in description_lower or 'string' in description_lower:
                return "str"
            elif 'list' in description_lower or 'array' in description_lower:
                return "list"
            elif 'boolean' in description_lower or 'true/false' in description_lower:
                return "bool"
        
        return "any"

    def _extract_logic(self, description: str) -> str:
        """Extract the main logic from description."""
        # This is a simplified version - in a real AI system, this would use NLP
        logic_keywords = [
            'calculate', 'compute', 'process', 'validate', 'check',
            'filter', 'sort', 'search', 'find', 'create', 'update',
            'delete', 'transform', 'convert', 'format'
        ]
        
        for keyword in logic_keywords:
            if keyword in description.lower():
                return keyword
        
        return "process"

    def _assess_complexity_from_text(self, description: str) -> str:
        """Assess code complexity from description."""
        words = description.lower().split()
        
        if len(words) < 10:
            return "simple"
        elif len(words) < 20:
            return "medium"
        else:
            return "complex"

    def _generate_function(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> str:
        """Generate a function based on the request."""
        template = self.code_templates[request.language.value]["function"]
        
        # Prepare template variables
        function_name = parsed_info["name"]
        parameters = ", ".join([f"{p['name']}: {p['type']}" for p in parsed_info["parameters"]])
        args_doc = "\n        ".join([f"{p['name']} ({p['type']}): {p['description']}" for p in parsed_info["parameters"]])
        return_type = parsed_info["return_type"]
        return_description = f"Result of {parsed_info['logic']}"
        
        # Generate implementation based on logic
        implementation = self._generate_implementation(parsed_info)
        return_value = self._generate_return_value(parsed_info)
        
        return template.format(
            function_name=function_name,
            parameters=parameters,
            description=request.description,
            args_doc=args_doc,
            return_type=return_type,
            return_description=return_description,
            implementation=implementation,
            return_value=return_value
        )

    def _generate_implementation(self, parsed_info: Dict[str, Any]) -> str:
        """Generate function implementation."""
        logic = parsed_info["logic"]
        parameters = parsed_info["parameters"]
        
        if logic == "calculate":
            if len(parameters) >= 2:
                return f"result = {parameters[0]['name']} + {parameters[1]['name']}"
            else:
                return "result = 0"
        elif logic == "validate":
            return f"if not {parameters[0]['name']}:\n        raise ValueError('Invalid input')"
        elif logic == "process":
            return "result = processed_data"
        else:
            return "result = None"

    def _generate_return_value(self, parsed_info: Dict[str, Any]) -> str:
        """Generate return value."""
        return_type = parsed_info["return_type"]
        
        if return_type == "int":
            return "0"
        elif return_type == "str":
            return "'result'"
        elif return_type == "list":
            return "[]"
        elif return_type == "bool":
            return "True"
        else:
            return "None"

    def _generate_class(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> str:
        """Generate a class based on the request."""
        template = self.code_templates[request.language.value]["class"]
        
        class_name = parsed_info["name"].title()
        init_params = ", ".join([p['name'] for p in parsed_info["parameters"]])
        init_implementation = "\n        ".join([f"self.{p['name']} = {p['name']}" for p in parsed_info["parameters"]])
        
        # Generate methods
        methods = self._generate_class_methods(parsed_info)
        
        return template.format(
            class_name=class_name,
            description=request.description,
            init_params=init_params,
            init_implementation=init_implementation,
            methods=methods
        )

    def _generate_class_methods(self, parsed_info: Dict[str, Any]) -> str:
        """Generate class methods."""
        methods = []
        
        # Generate getter methods
        for param in parsed_info["parameters"]:
            methods.append(f"""
    @property
    def {param['name']}(self):
        return self._{param['name']}
""")
        
        return "\n".join(methods)

    def _generate_api_endpoint(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> str:
        """Generate an API endpoint."""
        template = self.code_templates[request.language.value]["api_endpoint"]
        
        endpoint = f"/{parsed_info['name']}"
        function_name = f"handle_{parsed_info['name']}"
        implementation = self._generate_api_implementation(parsed_info)
        response = "{'status': 'success', 'data': result}"
        status_code = "200"
        
        return template.format(
            endpoint=endpoint,
            function_name=function_name,
            description=request.description,
            implementation=implementation,
            response=response,
            status_code=status_code
        )

    def _generate_api_implementation(self, parsed_info: Dict[str, Any]) -> str:
        """Generate API implementation."""
        return f"result = self.process_{parsed_info['name']}()"

    def _generate_database_model(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> str:
        """Generate a database model."""
        template = self.code_templates[request.language.value]["database_model"]
        
        model_name = parsed_info["name"].title()
        table_name = parsed_info["name"].lower()
        columns = self._generate_model_columns(parsed_info)
        repr_fields = ", ".join([p['name'] for p in parsed_info["parameters"]])
        
        return template.format(
            model_name=model_name,
            description=request.description,
            table_name=table_name,
            columns=columns,
            repr_fields=repr_fields
        )

    def _generate_model_columns(self, parsed_info: Dict[str, Any]) -> str:
        """Generate model columns."""
        columns = []
        
        for param in parsed_info["parameters"]:
            if param["type"] == "int":
                columns.append(f"    {param['name']} = Column(Integer, primary_key=True)")
            elif param["type"] == "str":
                columns.append(f"    {param['name']} = Column(String(255))")
            elif param["type"] == "bool":
                columns.append(f"    {param['name']} = Column(Boolean, default=False)")
        
        return "\n".join(columns)

    def _generate_generic_code(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> str:
        """Generate generic code for unsupported types."""
        return f"""
# Generated code for: {request.description}
# Language: {request.language.value}
# Type: {request.code_type.value}

def {parsed_info['name']}():
    \"\"\"
    {request.description}
    \"\"\"
    # TODO: Implement based on requirements
    pass
"""

    def _generate_tests(self, request: CodeRequest, code: str) -> str:
        """Generate tests for the code."""
        # Extract name from the code or request
        name = self._extract_name(request.description)
        
        if request.language.value == "python":
            return f"""
import unittest

class Test{name.title()}(unittest.TestCase):
    def test_{name}(self):
        # TODO: Add test cases
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""
        else:
            return f"""
// TODO: Add tests for {name}
"""

    def _generate_usage_example(self, request: CodeRequest, code: str) -> str:
        """Generate usage example."""
        name = self._extract_name(request.description)
        return f"""
# Usage example for {name}:
# TODO: Add usage example
"""

    def _assess_complexity(self, parsed_info: Dict[str, Any]) -> str:
        """Assess code complexity."""
        return parsed_info.get("complexity", "medium")

    def _estimate_development_time(self, parsed_info: Dict[str, Any]) -> str:
        """Estimate development time."""
        complexity = parsed_info.get("complexity", "medium")
        
        if complexity == "simple":
            return "1-2 hours"
        elif complexity == "medium":
            return "4-8 hours"
        else:
            return "1-2 days"

    def _extract_dependencies(self, request: CodeRequest, parsed_info: Dict[str, Any]) -> List[str]:
        """Extract required dependencies."""
        dependencies = []
        
        if request.code_type == CodeType.API_ENDPOINT:
            if request.language.value == "python":
                dependencies.extend(["flask", "requests"])
            elif request.language.value == "javascript":
                dependencies.extend(["express", "axios"])
        
        elif request.code_type == CodeType.DATABASE_MODEL:
            if request.language.value == "python":
                dependencies.extend(["sqlalchemy", "alembic"])
        
        return dependencies

    def generate_code_from_natural_language(self, description: str, language: str = "python") -> GeneratedCode:
        """Generate code from natural language description."""
        # Auto-detect code type from description
        code_type = self._detect_code_type(description)
        
        request = CodeRequest(
            description=description,
            language=CodeLanguage(language),
            code_type=code_type,
            requirements=[],
            context={}
        )
        
        return self.generate_code(request)

    def _detect_code_type(self, description: str) -> CodeType:
        """Detect code type from description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['function', 'method', 'calculate', 'process']):
            return CodeType.FUNCTION
        elif any(word in description_lower for word in ['class', 'object', 'model']):
            return CodeType.CLASS
        elif any(word in description_lower for word in ['api', 'endpoint', 'route', 'rest']):
            return CodeType.API_ENDPOINT
        elif any(word in description_lower for word in ['database', 'table', 'model', 'entity']):
            return CodeType.DATABASE_MODEL
        else:
            return CodeType.FUNCTION

def main():
    """Demo the AI Code Generator."""
    print("🤖 AI-Powered Code Generator Demo")
    print("=" * 50)
    
    generator = AICodeGenerator()
    
    # Example requests
    examples = [
        {
            "description": "Create a function that calculates the sum of two numbers",
            "language": "python",
            "type": "function"
        },
        {
            "description": "Build a class to represent a user with name and email",
            "language": "python", 
            "type": "class"
        },
        {
            "description": "Create an API endpoint to get user data",
            "language": "javascript",
            "type": "api_endpoint"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example['description']}")
        print("-" * 40)
        
        request = CodeRequest(
            description=example["description"],
            language=CodeLanguage(example["language"]),
            code_type=CodeType(example["type"]),
            requirements=[],
            context={}
        )
        
        result = generator.generate_code(request)
        
        print(f"🤖 Generated {result.type.value} in {result.language.value}:")
        print(f"📊 Complexity: {result.complexity}")
        print(f"⏱️ Estimated time: {result.estimated_time}")
        print(f"📦 Dependencies: {', '.join(result.dependencies)}")
        print(f"\n💻 Code:")
        print(result.code)
        
        if result.tests:
            print(f"\n🧪 Tests:")
            print(result.tests)
        
        if result.usage_example:
            print(f"\n📖 Usage Example:")
            print(result.usage_example)

if __name__ == "__main__":
    main()