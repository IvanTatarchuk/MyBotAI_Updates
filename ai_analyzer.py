#!/usr/bin/env python3
"""
AI-Powered Code Analysis Module
Advanced analysis using pattern recognition, machine learning, and intelligent suggestions
"""

import re
import ast
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import difflib
import statistics

class AICodeAnalyzer:
    """
    Advanced AI-powered code analysis with pattern recognition,
    machine learning insights, and intelligent recommendations.
    """
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.complexity_metrics = {}
        self.code_smells = []
        self.security_issues = []
        self.performance_issues = []
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load predefined code patterns and anti-patterns."""
        return {
            'security': {
                'sql_injection': [
                    r'execute\s*\(\s*["\'].*\+.*["\']',
                    r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',
                    r'query\s*=\s*["\'].*\+.*["\']'
                ],
                'xss': [
                    r'innerHTML\s*=',
                    r'document\.write\s*\(',
                    r'eval\s*\('
                ],
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']'
                ]
            },
            'performance': {
                'n_plus_one': [
                    r'for.*in.*:\s*\n.*\.query\(',
                    r'for.*in.*:\s*\n.*\.filter\('
                ],
                'memory_leak': [
                    r'global\s+\w+',
                    r'nonlocal\s+\w+'
                ],
                'inefficient_loops': [
                    r'for.*in.*range\(',
                    r'while.*True:'
                ]
            },
            'code_smells': {
                'long_method': r'def\s+\w+\([^)]*\):\s*\n(?:[^\n]*\n){20,}',
                'large_class': r'class\s+\w+[^:]*:\s*\n(?:[^\n]*\n){50,}',
                'duplicate_code': r'(\w+\([^)]*\)[^}]*)(?=\1)',
                'magic_numbers': r'\b\d{3,}\b',
                'deep_nesting': r'if.*:\s*\n\s*if.*:\s*\n\s*if.*:\s*\n\s*if'
            }
        }
    
    def analyze_code_intelligence(self, content: str, language: str) -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered code analysis.
        
        Args:
            content: Source code content
            language: Programming language
            
        Returns:
            Dict containing AI analysis results
        """
        analysis = {
            'ai_score': 0.0,
            'complexity_metrics': {},
            'security_analysis': {},
            'performance_analysis': {},
            'code_smells': [],
            'intelligent_suggestions': [],
            'patterns_detected': [],
            'refactoring_opportunities': [],
            'best_practices': [],
            'risk_assessment': {},
            'maintainability_index': 0.0,
            'technical_debt_score': 0.0
        }
        
        # Calculate AI score based on multiple factors
        analysis['ai_score'] = self._calculate_ai_score(content, language)
        
        # Analyze complexity
        analysis['complexity_metrics'] = self._analyze_complexity(content, language)
        
        # Security analysis
        analysis['security_analysis'] = self._analyze_security(content, language)
        
        # Performance analysis
        analysis['performance_analysis'] = self._analyze_performance(content, language)
        
        # Code smells detection
        analysis['code_smells'] = self._detect_code_smells(content, language)
        
        # Intelligent suggestions
        analysis['intelligent_suggestions'] = self._generate_intelligent_suggestions(
            content, language, analysis
        )
        
        # Pattern detection
        analysis['patterns_detected'] = self._detect_patterns(content, language)
        
        # Refactoring opportunities
        analysis['refactoring_opportunities'] = self._find_refactoring_opportunities(
            content, language
        )
        
        # Best practices analysis
        analysis['best_practices'] = self._analyze_best_practices(content, language)
        
        # Risk assessment
        analysis['risk_assessment'] = self._assess_risks(content, language)
        
        # Calculate maintainability and technical debt
        analysis['maintainability_index'] = self._calculate_maintainability_index(analysis)
        analysis['technical_debt_score'] = self._calculate_technical_debt_score(analysis)
        
        return analysis
    
    def _calculate_ai_score(self, content: str, language: str) -> float:
        """Calculate overall AI quality score (0-100)."""
        score = 100.0
        
        # Deduct points for various issues
        lines = content.split('\n')
        
        # Complexity penalty
        if len(lines) > 1000:
            score -= 20
        elif len(lines) > 500:
            score -= 10
        
        # Security issues
        security_issues = self._count_security_issues(content)
        score -= security_issues * 5
        
        # Code smells
        code_smells = len(self._detect_code_smells(content, language))
        score -= code_smells * 3
        
        # Performance issues
        performance_issues = self._count_performance_issues(content)
        score -= performance_issues * 2
        
        # Maintainability
        if self._has_deep_nesting(content):
            score -= 15
        
        if self._has_long_methods(content):
            score -= 10
        
        return max(0.0, score)
    
    def _analyze_complexity(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        metrics = {
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'nesting_depth': 0,
            'function_complexity': {},
            'class_complexity': {},
            'module_complexity': 0
        }
        
        if language == 'Python':
            try:
                tree = ast.parse(content)
                metrics.update(self._analyze_python_complexity(tree))
            except SyntaxError:
                pass
        
        return metrics
    
    def _analyze_python_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze Python-specific complexity."""
        complexity = {
            'cyclomatic_complexity': 1,
            'cognitive_complexity': 0,
            'nesting_depth': 0,
            'function_complexity': {},
            'class_complexity': {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity['cyclomatic_complexity'] += 1
                complexity['cognitive_complexity'] += 1
            
            elif isinstance(node, (ast.And, ast.Or)):
                complexity['cognitive_complexity'] += 1
            
            elif isinstance(node, ast.FunctionDef):
                func_complexity = self._calculate_function_complexity(node)
                complexity['function_complexity'][node.name] = func_complexity
            
            elif isinstance(node, ast.ClassDef):
                class_complexity = self._calculate_class_complexity(node)
                complexity['class_complexity'][node.name] = class_complexity
        
        return complexity
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate complexity for a single function."""
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _calculate_class_complexity(self, class_node: ast.ClassDef) -> int:
        """Calculate complexity for a single class."""
        complexity = 1
        for node in ast.walk(class_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _analyze_security(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze security vulnerabilities."""
        security_analysis = {
            'vulnerabilities': [],
            'risk_level': 'LOW',
            'security_score': 100,
            'recommendations': []
        }
        
        # Check for SQL injection
        sql_patterns = self.patterns['security']['sql_injection']
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_analysis['vulnerabilities'].append({
                    'type': 'SQL_INJECTION',
                    'severity': 'HIGH',
                    'description': 'Potential SQL injection vulnerability detected'
                })
                security_analysis['security_score'] -= 30
        
        # Check for XSS
        xss_patterns = self.patterns['security']['xss']
        for pattern in xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_analysis['vulnerabilities'].append({
                    'type': 'XSS',
                    'severity': 'HIGH',
                    'description': 'Potential XSS vulnerability detected'
                })
                security_analysis['security_score'] -= 25
        
        # Check for hardcoded secrets
        secret_patterns = self.patterns['security']['hardcoded_secrets']
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_analysis['vulnerabilities'].append({
                    'type': 'HARDCODED_SECRET',
                    'severity': 'MEDIUM',
                    'description': 'Hardcoded secrets detected'
                })
                security_analysis['security_score'] -= 15
        
        # Determine risk level
        if security_analysis['security_score'] < 50:
            security_analysis['risk_level'] = 'HIGH'
        elif security_analysis['security_score'] < 75:
            security_analysis['risk_level'] = 'MEDIUM'
        
        return security_analysis
    
    def _analyze_performance(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze performance issues."""
        performance_analysis = {
            'issues': [],
            'performance_score': 100,
            'optimization_opportunities': []
        }
        
        # Check for N+1 queries
        n_plus_one_patterns = self.patterns['performance']['n_plus_one']
        for pattern in n_plus_one_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                performance_analysis['issues'].append({
                    'type': 'N_PLUS_ONE_QUERY',
                    'severity': 'MEDIUM',
                    'description': 'Potential N+1 query problem detected'
                })
                performance_analysis['performance_score'] -= 20
        
        # Check for memory leaks
        memory_patterns = self.patterns['performance']['memory_leak']
        for pattern in memory_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                performance_analysis['issues'].append({
                    'type': 'MEMORY_LEAK',
                    'severity': 'HIGH',
                    'description': 'Potential memory leak detected'
                })
                performance_analysis['performance_score'] -= 25
        
        # Check for inefficient loops
        loop_patterns = self.patterns['performance']['inefficient_loops']
        for pattern in loop_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                performance_analysis['issues'].append({
                    'type': 'INEFFICIENT_LOOP',
                    'severity': 'LOW',
                    'description': 'Inefficient loop pattern detected'
                })
                performance_analysis['performance_score'] -= 10
        
        return performance_analysis
    
    def _detect_code_smells(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Detect code smells and anti-patterns."""
        smells = []
        
        # Long method smell
        long_method_pattern = self.patterns['code_smells']['long_method']
        if re.search(long_method_pattern, content, re.MULTILINE):
            smells.append({
                'type': 'LONG_METHOD',
                'severity': 'MEDIUM',
                'description': 'Method is too long, consider breaking it down'
            })
        
        # Large class smell
        large_class_pattern = self.patterns['code_smells']['large_class']
        if re.search(large_class_pattern, content, re.MULTILINE):
            smells.append({
                'type': 'LARGE_CLASS',
                'severity': 'MEDIUM',
                'description': 'Class is too large, consider splitting it'
            })
        
        # Deep nesting smell
        deep_nesting_pattern = self.patterns['code_smells']['deep_nesting']
        if re.search(deep_nesting_pattern, content, re.MULTILINE):
            smells.append({
                'type': 'DEEP_NESTING',
                'severity': 'HIGH',
                'description': 'Code has deep nesting, consider refactoring'
            })
        
        # Magic numbers
        magic_number_pattern = self.patterns['code_smells']['magic_numbers']
        magic_numbers = re.findall(magic_number_pattern, content)
        if len(magic_numbers) > 5:
            smells.append({
                'type': 'MAGIC_NUMBERS',
                'severity': 'LOW',
                'description': f'Found {len(magic_numbers)} magic numbers, consider using constants'
            })
        
        return smells
    
    def _generate_intelligent_suggestions(self, content: str, language: str, 
                                        analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions based on analysis."""
        suggestions = []
        
        # Based on complexity
        if analysis['complexity_metrics'].get('cyclomatic_complexity', 0) > 10:
            suggestions.append("Consider breaking down complex functions into smaller, more manageable pieces")
        
        # Based on security
        if analysis['security_analysis']['security_score'] < 80:
            suggestions.append("Review and fix security vulnerabilities before deployment")
        
        # Based on performance
        if analysis['performance_analysis']['performance_score'] < 80:
            suggestions.append("Optimize performance-critical sections of the code")
        
        # Based on code smells
        if len(analysis['code_smells']) > 3:
            suggestions.append("Address code smells to improve maintainability")
        
        # Language-specific suggestions
        if language == 'Python':
            if 'import *' in content:
                suggestions.append("Replace 'import *' with specific imports for better clarity")
            if 'except:' in content:
                suggestions.append("Use specific exception types instead of bare 'except:'")
        
        return suggestions
    
    def _detect_patterns(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Detect common patterns and anti-patterns."""
        patterns = []
        
        # Design patterns
        if re.search(r'class\s+\w+Factory', content):
            patterns.append({
                'type': 'DESIGN_PATTERN',
                'name': 'Factory Pattern',
                'description': 'Factory pattern implementation detected'
            })
        
        if re.search(r'class\s+\w+Singleton', content):
            patterns.append({
                'type': 'DESIGN_PATTERN',
                'name': 'Singleton Pattern',
                'description': 'Singleton pattern implementation detected'
            })
        
        # Anti-patterns
        if re.search(r'if\s+type\(.*\)\s*==\s*str', content):
            patterns.append({
                'type': 'ANTI_PATTERN',
                'name': 'Type Checking Anti-pattern',
                'description': 'Use isinstance() instead of type() comparison'
            })
        
        return patterns
    
    def _find_refactoring_opportunities(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Find opportunities for refactoring."""
        opportunities = []
        
        # Extract method opportunities
        long_blocks = re.findall(r'def\s+\w+\([^)]*\):\s*\n((?:[^\n]*\n){10,})', content)
        for i, block in enumerate(long_blocks):
            if len(block.split('\n')) > 15:
                opportunities.append({
                    'type': 'EXTRACT_METHOD',
                    'description': f'Method {i+1} is long and could be broken down',
                    'priority': 'MEDIUM'
                })
        
        # Rename variable opportunities
        short_vars = re.findall(r'\b[a-z]\b', content)
        if len(short_vars) > 10:
            opportunities.append({
                'type': 'RENAME_VARIABLE',
                'description': 'Consider renaming short variable names for clarity',
                'priority': 'LOW'
            })
        
        return opportunities
    
    def _analyze_best_practices(self, content: str, language: str) -> List[str]:
        """Analyze adherence to best practices."""
        practices = []
        
        if language == 'Python':
            # PEP 8 compliance
            if re.search(r'[a-z_][a-z0-9_]*\s*=\s*[^=]', content):
                practices.append("Follow PEP 8 naming conventions")
            
            # Docstring usage
            if not re.search(r'"""[^"]*"""', content):
                practices.append("Add docstrings to functions and classes")
            
            # Type hints
            if not re.search(r':\s*(str|int|float|bool|list|dict)', content):
                practices.append("Consider adding type hints for better code clarity")
        
        return practices
    
    def _assess_risks(self, content: str, language: str) -> Dict[str, Any]:
        """Assess overall code risks."""
        risks = {
            'overall_risk': 'LOW',
            'risk_factors': [],
            'risk_score': 0
        }
        
        # Calculate risk score
        risk_score = 0
        
        # Security risks
        security_issues = len(self._analyze_security(content, language)['vulnerabilities'])
        risk_score += security_issues * 10
        
        # Complexity risks
        if self._has_deep_nesting(content):
            risk_score += 5
        
        if self._has_long_methods(content):
            risk_score += 3
        
        # Performance risks
        performance_issues = len(self._analyze_performance(content, language)['issues'])
        risk_score += performance_issues * 2
        
        risks['risk_score'] = risk_score
        
        # Determine overall risk level
        if risk_score > 20:
            risks['overall_risk'] = 'HIGH'
        elif risk_score > 10:
            risks['overall_risk'] = 'MEDIUM'
        
        return risks
    
    def _calculate_maintainability_index(self, analysis: Dict[str, Any]) -> float:
        """Calculate maintainability index (0-100)."""
        index = 100.0
        
        # Deduct for complexity
        complexity = analysis['complexity_metrics'].get('cyclomatic_complexity', 0)
        index -= complexity * 2
        
        # Deduct for code smells
        index -= len(analysis['code_smells']) * 5
        
        # Deduct for security issues
        index -= len(analysis['security_analysis'].get('vulnerabilities', [])) * 3
        
        return max(0.0, index)
    
    def _calculate_technical_debt_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate technical debt score (0-100)."""
        debt = 0.0
        
        # Add debt for code smells
        debt += len(analysis['code_smells']) * 5
        
        # Add debt for complexity
        complexity = analysis['complexity_metrics'].get('cyclomatic_complexity', 0)
        debt += complexity * 1.5
        
        # Add debt for security issues
        debt += len(analysis['security_analysis'].get('vulnerabilities', [])) * 10
        
        # Add debt for performance issues
        debt += len(analysis['performance_analysis'].get('issues', [])) * 3
        
        return min(100.0, debt)
    
    def _count_security_issues(self, content: str) -> int:
        """Count security issues in content."""
        count = 0
        for category in self.patterns['security'].values():
            for pattern in category:
                if re.search(pattern, content, re.IGNORECASE):
                    count += 1
        return count
    
    def _count_performance_issues(self, content: str) -> int:
        """Count performance issues in content."""
        count = 0
        for category in self.patterns['performance'].values():
            for pattern in category:
                if re.search(pattern, content, re.IGNORECASE):
                    count += 1
        return count
    
    def _has_deep_nesting(self, content: str) -> bool:
        """Check if code has deep nesting."""
        return bool(re.search(self.patterns['code_smells']['deep_nesting'], content, re.MULTILINE))
    
    def _has_long_methods(self, content: str) -> bool:
        """Check if code has long methods."""
        return bool(re.search(self.patterns['code_smells']['long_method'], content, re.MULTILINE))