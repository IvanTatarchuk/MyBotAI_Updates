#!/usr/bin/env python3
"""
AI Programming Agent - Inteligentny Asystent Programisty
Stworzony do pomocy w zadaniach programistycznych

Funkcjonalności:
- Analiza kodu i projektów
- Generowanie kodu w różnych językach
- Refaktoryzacja i optymalizacja
- Debugging i znajdowanie błędów
- Automatyzacja zadań programistycznych
- Zarządzanie projektami
"""

import os
import sys
import json
import subprocess
import re
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import importlib.util

@dataclass
class CodeAnalysis:
    """Struktura przechowująca wyniki analizy kodu"""
    file_path: str
    language: str
    lines_count: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity_score: int
    issues: List[str]
    suggestions: List[str]

class ProgrammingAgent:
    """Główna klasa agenta programisty"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
        self.analysis_cache = {}
        
    def detect_language(self, file_path: str) -> str:
        """Wykrywa język programowania na podstawie rozszerzenia pliku"""
        extension = Path(file_path).suffix.lower()
        return self.supported_languages.get(extension, 'unknown')
    
    def analyze_python_file(self, file_path: str) -> CodeAnalysis:
        """Szczegółowa analiza pliku Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            issues = []
            suggestions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        imports.append(node.module or "")
            
            lines_count = len(content.split('\n'))
            complexity_score = self._calculate_complexity(tree)
            
            # Podstawowe sprawdzenia jakości kodu
            if complexity_score > 10:
                issues.append("Wysoka złożoność cyklomatyczna")
                suggestions.append("Rozważ podział na mniejsze funkcje")
            
            if lines_count > 500:
                suggestions.append("Duży plik - rozważ podział na moduły")
            
            if not functions and not classes:
                issues.append("Brak funkcji lub klas - kod może być słabo zorganizowany")
            
            return CodeAnalysis(
                file_path=file_path,
                language='python',
                lines_count=lines_count,
                functions=functions,
                classes=classes,
                imports=imports,
                complexity_score=complexity_score,
                issues=issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            return CodeAnalysis(
                file_path=file_path,
                language='python',
                lines_count=0,
                functions=[],
                classes=[],
                imports=[],
                complexity_score=0,
                issues=[f"Błąd analizy: {str(e)}"],
                suggestions=[]
            )
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Oblicza złożoność cyklomatyczną kodu Python"""
        complexity = 1  # Bazowa złożoność
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def analyze_file(self, file_path: str) -> CodeAnalysis:
        """Analizuje plik w zależności od języka programowania"""
        if file_path in self.analysis_cache:
            return self.analysis_cache[file_path]
        
        language = self.detect_language(file_path)
        
        if language == 'python':
            analysis = self.analyze_python_file(file_path)
        else:
            # Podstawowa analiza dla innych języków
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines_count = len(content.split('\n'))
                
                analysis = CodeAnalysis(
                    file_path=file_path,
                    language=language,
                    lines_count=lines_count,
                    functions=[],
                    classes=[],
                    imports=[],
                    complexity_score=0,
                    issues=[],
                    suggestions=[]
                )
            except Exception as e:
                analysis = CodeAnalysis(
                    file_path=file_path,
                    language=language,
                    lines_count=0,
                    functions=[],
                    classes=[],
                    imports=[],
                    complexity_score=0,
                    issues=[f"Błąd odczytu pliku: {str(e)}"],
                    suggestions=[]
                )
        
        self.analysis_cache[file_path] = analysis
        return analysis
    
    def scan_project(self, path: str = None) -> Dict[str, CodeAnalysis]:
        """Skanuje cały projekt i analizuje wszystkie pliki kodu"""
        if path is None:
            path = self.workspace_path
        
        project_analysis = {}
        
        for file_path in Path(path).rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_languages:
                # Pomijaj pliki w katalogach cache/build
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    continue
                
                analysis = self.analyze_file(str(file_path))
                project_analysis[str(file_path)] = analysis
        
        return project_analysis
    
    def generate_code_template(self, language: str, template_type: str) -> str:
        """Generuje szablon kodu dla różnych języków i typów"""
        templates = {
            'python': {
                'class': '''class NewClass:
    """Opis klasy"""
    
    def __init__(self):
        """Konstruktor"""
        pass
    
    def method(self):
        """Opis metody"""
        pass
''',
                'function': '''def new_function(param1, param2):
    """
    Opis funkcji
    
    Args:
        param1: Opis parametru 1
        param2: Opis parametru 2
    
    Returns:
        Opis zwracanej wartości
    """
    pass
''',
                'script': '''#!/usr/bin/env python3
"""
Opis skryptu
"""

import sys
import os

def main():
    """Główna funkcja"""
    pass

if __name__ == "__main__":
    main()
''',
                'test': '''import unittest

class TestNewClass(unittest.TestCase):
    """Testy dla klasy NewClass"""
    
    def setUp(self):
        """Przygotowanie do testów"""
        pass
    
    def test_method(self):
        """Test metody"""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
            },
            'javascript': {
                'function': '''function newFunction(param1, param2) {
    /**
     * Opis funkcji
     * @param {type} param1 - Opis parametru 1
     * @param {type} param2 - Opis parametru 2
     * @returns {type} Opis zwracanej wartości
     */
    return null;
}''',
                'class': '''class NewClass {
    /**
     * Konstruktor klasy
     */
    constructor() {
        
    }
    
    /**
     * Metoda klasy
     */
    method() {
        
    }
}''',
                'module': '''/**
 * Opis modułu
 */

export default class NewModule {
    
}'''
            }
        }
        
        return templates.get(language, {}).get(template_type, f"# Szablon dla {language} - {template_type}")
    
    def refactor_code(self, file_path: str, refactor_type: str) -> str:
        """Sugeruje refaktoryzację kodu"""
        analysis = self.analyze_file(file_path)
        suggestions = []
        
        if refactor_type == "extract_function":
            suggestions.append("Wyodrębnij powtarzające się fragmenty kodu do osobnych funkcji")
        elif refactor_type == "split_class":
            if len(analysis.functions) > 10:
                suggestions.append("Klasa ma zbyt wiele metod - rozważ podział")
        elif refactor_type == "optimize":
            suggestions.extend([
                "Użyj list comprehensions zamiast pętli for",
                "Zastąp wielokrotne if-elif konstrukcją słownikową",
                "Użyj context managerów dla zarządzania zasobami"
            ])
        
        return "\n".join(suggestions)
    
    def find_bugs(self, file_path: str) -> List[str]:
        """Znajduje potencjalne błędy w kodzie"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            bugs = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Sprawdzanie potencjalnych problemów
                if 'except:' in line and 'pass' in line:
                    bugs.append(f"Linia {i}: Pusta klauzula except może ukrywać błędy")
                
                if 'print(' in line and 'debug' not in line.lower():
                    bugs.append(f"Linia {i}: Pozostawiony print() - rozważ użycie loggera")
                
                if '== True' in line or '== False' in line:
                    bugs.append(f"Linia {i}: Niepotrzebne porównanie z True/False")
                
                if 'eval(' in line:
                    bugs.append(f"Linia {i}: Użycie eval() może być niebezpieczne")
            
            return bugs
            
        except Exception as e:
            return [f"Błąd analizy: {str(e)}"]
    
    def create_project_structure(self, project_name: str, project_type: str) -> None:
        """Tworzy strukturę nowego projektu"""
        project_path = self.workspace_path / project_name
        project_path.mkdir(exist_ok=True)
        
        structures = {
            'python_package': {
                'dirs': ['src', 'tests', 'docs'],
                'files': {
                    'requirements.txt': '',
                    'setup.py': f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[],
    author="Twój autor",
    description="Opis projektu",
)''',
                    'README.md': f'# {project_name}\n\nOpis projektu',
                    'src/__init__.py': '',
                    'tests/__init__.py': '',
                    'tests/test_main.py': self.generate_code_template('python', 'test')
                }
            },
            'web_project': {
                'dirs': ['static', 'templates', 'static/css', 'static/js'],
                'files': {
                    'app.py': '''from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
''',
                    'requirements.txt': 'Flask==2.0.1',
                    'templates/index.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Nowy Projekt</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Witaj w nowym projekcie!</h1>
</body>
</html>''',
                    'static/css/style.css': '''body {
    font-family: Arial, sans-serif;
    margin: 40px;
}'''
                }
            }
        }
        
        structure = structures.get(project_type, structures['python_package'])
        
        # Tworzenie katalogów
        for dir_name in structure.get('dirs', []):
            (project_path / dir_name).mkdir(exist_ok=True)
        
        # Tworzenie plików
        for file_path, content in structure.get('files', {}).items():
            file_full_path = project_path / file_path
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def generate_report(self, project_analysis: Dict[str, CodeAnalysis]) -> str:
        """Generuje raport z analizy projektu"""
        total_files = len(project_analysis)
        total_lines = sum(analysis.lines_count for analysis in project_analysis.values())
        total_functions = sum(len(analysis.functions) for analysis in project_analysis.values())
        total_classes = sum(len(analysis.classes) for analysis in project_analysis.values())
        
        languages = {}
        for analysis in project_analysis.values():
            lang = analysis.language
            languages[lang] = languages.get(lang, 0) + 1
        
        all_issues = []
        for analysis in project_analysis.values():
            all_issues.extend(analysis.issues)
        
        report = f"""
# RAPORT ANALIZY PROJEKTU
Wygenerowany: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## STATYSTYKI OGÓLNE
- Liczba plików: {total_files}
- Łączna liczba linii: {total_lines}
- Liczba funkcji: {total_functions}
- Liczba klas: {total_classes}

## JĘZYKI PROGRAMOWANIA
"""
        
        for lang, count in languages.items():
            report += f"- {lang}: {count} plików\n"
        
        if all_issues:
            report += f"\n## ZNALEZIONE PROBLEMY ({len(all_issues)})\n"
            for issue in set(all_issues):  # Unikalne problemy
                report += f"- {issue}\n"
        
        report += "\n## SZCZEGÓŁOWA ANALIZA PLIKÓW\n"
        for file_path, analysis in project_analysis.items():
            report += f"\n### {file_path}\n"
            report += f"- Język: {analysis.language}\n"
            report += f"- Linie kodu: {analysis.lines_count}\n"
            report += f"- Funkcje: {len(analysis.functions)}\n"
            report += f"- Klasy: {len(analysis.classes)}\n"
            report += f"- Złożoność: {analysis.complexity_score}\n"
            
            if analysis.suggestions:
                report += "- Sugestie:\n"
                for suggestion in analysis.suggestions:
                    report += f"  * {suggestion}\n"
        
        return report

def main():
    """Główna funkcja CLI"""
    parser = argparse.ArgumentParser(description='Agent Programista - AI Assistant')
    parser.add_argument('command', choices=[
        'analyze', 'scan', 'generate', 'refactor', 'bugs', 'create', 'report'
    ], help='Komenda do wykonania')
    
    parser.add_argument('--file', '-f', help='Ścieżka do pliku')
    parser.add_argument('--path', '-p', help='Ścieżka do projektu', default='.')
    parser.add_argument('--language', '-l', help='Język programowania')
    parser.add_argument('--type', '-t', help='Typ szablonu lub refaktoryzacji')
    parser.add_argument('--name', '-n', help='Nazwa projektu')
    parser.add_argument('--output', '-o', help='Plik wyjściowy dla raportu')
    
    args = parser.parse_args()
    
    agent = ProgrammingAgent(args.path)
    
    if args.command == 'analyze':
        if not args.file:
            print("Wymagana ścieżka do pliku (--file)")
            return
        
        analysis = agent.analyze_file(args.file)
        print(f"Analiza pliku: {analysis.file_path}")
        print(f"Język: {analysis.language}")
        print(f"Linie kodu: {analysis.lines_count}")
        print(f"Funkcje: {len(analysis.functions)}")
        print(f"Klasy: {len(analysis.classes)}")
        
        if analysis.issues:
            print("Problemy:")
            for issue in analysis.issues:
                print(f"  - {issue}")
        
        if analysis.suggestions:
            print("Sugestie:")
            for suggestion in analysis.suggestions:
                print(f"  - {suggestion}")
    
    elif args.command == 'scan':
        project_analysis = agent.scan_project(args.path)
        print(f"Przeskanowano {len(project_analysis)} plików")
        
        for file_path, analysis in project_analysis.items():
            print(f"{file_path}: {analysis.language} ({analysis.lines_count} linii)")
    
    elif args.command == 'generate':
        if not args.language or not args.type:
            print("Wymagane: --language i --type")
            return
        
        template = agent.generate_code_template(args.language, args.type)
        print(template)
    
    elif args.command == 'refactor':
        if not args.file or not args.type:
            print("Wymagane: --file i --type")
            return
        
        suggestions = agent.refactor_code(args.file, args.type)
        print("Sugestie refaktoryzacji:")
        print(suggestions)
    
    elif args.command == 'bugs':
        if not args.file:
            print("Wymagana ścieżka do pliku (--file)")
            return
        
        bugs = agent.find_bugs(args.file)
        if bugs:
            print("Znalezione potencjalne problemy:")
            for bug in bugs:
                print(f"  - {bug}")
        else:
            print("Nie znaleziono oczywistych problemów")
    
    elif args.command == 'create':
        if not args.name or not args.type:
            print("Wymagane: --name i --type")
            return
        
        agent.create_project_structure(args.name, args.type)
        print(f"Utworzono projekt: {args.name}")
    
    elif args.command == 'report':
        project_analysis = agent.scan_project(args.path)
        report = agent.generate_report(project_analysis)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Raport zapisano do: {args.output}")
        else:
            print(report)

if __name__ == "__main__":
    main()