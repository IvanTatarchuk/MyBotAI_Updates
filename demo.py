#!/usr/bin/env python3
"""
Programming Agent Demo
Showcases the various capabilities of the Programming Agent
"""

import json
import os
from programming_agent import ProgrammingAgent

def demo_project_analysis():
    """Demonstrate project analysis capabilities."""
    print("🔍 Demo: Project Analysis")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    analysis = agent.analyze_project_structure()
    
    print(f"📁 Workspace: {analysis['workspace_path']}")
    print(f"📄 Total Files: {len(analysis['files'])}")
    print(f"🌐 Languages: {', '.join(analysis['languages'])}")
    print(f"📊 Total Lines: {analysis['total_lines']}")
    
    if analysis['file_types']:
        print("\n📋 Files by Language:")
        for lang, files in analysis['file_types'].items():
            print(f"  {lang}: {len(files)} files")
    
    print()

def demo_code_generation():
    """Demonstrate code generation capabilities."""
    print("💻 Demo: Code Generation")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    # Generate Python code
    print("🐍 Generating Python API Client...")
    python_code = agent.generate_code(
        'python', 
        'Create an API client for REST services',
        ['Handle HTTP requests', 'JSON parsing', 'Error handling', 'Authentication']
    )
    print(python_code)
    
    print("\n" + "-" * 30 + "\n")
    
    # Generate JavaScript code
    print("🟨 Generating JavaScript Data Processor...")
    js_code = agent.generate_code(
        'javascript',
        'Create a data processing utility',
        ['CSV parsing', 'Data validation', 'Export to JSON']
    )
    print(js_code)
    
    print()

def demo_code_quality_analysis():
    """Demonstrate code quality analysis."""
    print("📋 Demo: Code Quality Analysis")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    # Analyze the agent itself
    if os.path.exists('programming_agent.py'):
        print("🔍 Analyzing programming_agent.py...")
        analysis = agent.analyze_code_quality('programming_agent.py')
        
        print(f"📄 File: {analysis['file_path']}")
        print(f"🌐 Language: {analysis['language']}")
        print(f"📊 Metrics:")
        print(f"  - Total lines: {analysis['metrics']['total_lines']}")
        print(f"  - Code lines: {analysis['metrics']['code_lines']}")
        print(f"  - Comment lines: {analysis['metrics']['comment_lines']}")
        
        if analysis['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in analysis['suggestions'][:3]:  # Show first 3
                print(f"  - {suggestion}")
    
    print()

def demo_debugging():
    """Demonstrate debugging capabilities."""
    print("🐛 Demo: Debugging Assistant")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    # Create a sample file with issues for demonstration
    sample_code = '''def broken_function()
    print("This function has syntax issues"
    x = 10
    if x > 5
        print("Missing colon")
    return x'''
    
    with open('sample_broken.py', 'w') as f:
        f.write(sample_code)
    
    print("🔍 Analyzing sample_broken.py...")
    debug_info = agent.debug_code('sample_broken.py', 'SyntaxError: invalid syntax')
    
    print(f"📄 File: {debug_info['file_path']}")
    if debug_info['suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in debug_info['suggestions']:
            print(f"  - {suggestion}")
    
    # Clean up
    if os.path.exists('sample_broken.py'):
        os.remove('sample_broken.py')
    
    print()

def demo_project_creation():
    """Demonstrate project creation capabilities."""
    print("📁 Demo: Project Creation")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    # Create a demo Python project
    print("🐍 Creating demo Python project...")
    result = agent.create_project_structure('python', 'demo_project')
    
    if result['success']:
        print(f"✅ Project created successfully!")
        print(f"📄 Created files:")
        for file in result['created_files']:
            print(f"  - {file}")
        
        # Clean up demo project
        import shutil
        if os.path.exists('demo_project'):
            shutil.rmtree('demo_project')
            print("🧹 Demo project cleaned up")
    else:
        print(f"❌ Failed to create project: {result['error']}")
    
    print()

def demo_refactoring():
    """Demonstrate refactoring suggestions."""
    print("🔧 Demo: Refactoring Suggestions")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    if os.path.exists('programming_agent.py'):
        print("🔍 Analyzing programming_agent.py for refactoring opportunities...")
        
        refactor_types = ['extract_method', 'rename_variable', 'simplify_conditionals']
        
        for refactor_type in refactor_types:
            print(f"\n🔧 {refactor_type.replace('_', ' ').title()}:")
            result = agent.refactor_code('programming_agent.py', refactor_type)
            
            if result['suggestions']:
                for suggestion in result['suggestions'][:2]:  # Show first 2
                    print(f"  - {suggestion}")
            else:
                print("  No specific suggestions for this type")
    
    print()

def demo_testing():
    """Demonstrate testing capabilities."""
    print("🧪 Demo: Testing Support")
    print("=" * 50)
    
    agent = ProgrammingAgent()
    
    print("🔍 Attempting to run tests...")
    test_results = agent.run_tests()
    
    if test_results['test_command']:
        print(f"✅ Found test command: {test_results['test_command']}")
        print(f"📊 Success: {'Yes' if test_results['success'] else 'No'}")
        
        if test_results['output']:
            print(f"📄 Output: {test_results['output'][:200]}...")
        
        if test_results['error']:
            print(f"❌ Error: {test_results['error']}")
    else:
        print("ℹ️ No test command found or tests not configured")
    
    print()

def main():
    """Run all demos."""
    print("🤖 Programming Agent Demo")
    print("=" * 60)
    print("This demo showcases the various capabilities of the Programming Agent")
    print()
    
    try:
        demo_project_analysis()
        demo_code_generation()
        demo_code_quality_analysis()
        demo_debugging()
        demo_project_creation()
        demo_refactoring()
        demo_testing()
        
        print("🎉 Demo completed successfully!")
        print("\n💡 Try running individual commands:")
        print("  python agent_cli.py analyze")
        print("  python agent_cli.py quality programming_agent.py")
        print("  python agent_cli.py generate python 'web scraper' 'parse HTML,extract data'")
        print("  python agent_cli.py help")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Make sure all required files are present and Python dependencies are installed.")

if __name__ == "__main__":
    main()