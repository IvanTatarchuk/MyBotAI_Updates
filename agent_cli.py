#!/usr/bin/env python3
"""
Command Line Interface for Programming Agent
"""

import argparse
import json
import sys
from programming_agent import ProgrammingAgent

def main():
    parser = argparse.ArgumentParser(
        description="Programming Agent - An intelligent assistant for software development tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent_cli.py analyze                    # Analyze current project
  python agent_cli.py quality programming_agent.py  # Analyze code quality
  python agent_cli.py generate python "data processor" "handle CSV,validate data"  # Generate code
  python agent_cli.py debug main.py "syntax error"  # Debug code
  python agent_cli.py create python my_project   # Create new project
  python agent_cli.py test                       # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze project structure
    analyze_parser = subparsers.add_parser('analyze', help='Analyze project structure')
    analyze_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                               help='Output format (default: text)')
    
    # Analyze code quality
    quality_parser = subparsers.add_parser('quality', help='Analyze code quality')
    quality_parser.add_argument('file', help='File to analyze')
    quality_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                               help='Output format (default: text)')
    
    # Generate code
    generate_parser = subparsers.add_parser('generate', help='Generate code')
    generate_parser.add_argument('language', help='Programming language')
    generate_parser.add_argument('purpose', help='Purpose of the code')
    generate_parser.add_argument('requirements', help='Comma-separated requirements')
    generate_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    # Debug code
    debug_parser = subparsers.add_parser('debug', help='Debug code')
    debug_parser.add_argument('file', help='File to debug')
    debug_parser.add_argument('error', nargs='?', help='Error message')
    debug_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                             help='Output format (default: text)')
    
    # Refactor code
    refactor_parser = subparsers.add_parser('refactor', help='Suggest refactoring')
    refactor_parser.add_argument('file', help='File to refactor')
    refactor_parser.add_argument('type', choices=['extract_method', 'rename_variable', 'simplify_conditionals'],
                                help='Type of refactoring')
    refactor_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                                help='Output format (default: text)')
    
    # Run tests
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--command', '-c', help='Custom test command')
    test_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                            help='Output format (default: text)')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create new project')
    create_parser.add_argument('type', choices=['python', 'javascript', 'web'], help='Project type')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                              help='Output format (default: text)')
    
    # Help
    help_parser = subparsers.add_parser('help', help='Show detailed help')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    agent = ProgrammingAgent()
    
    try:
        if args.command == 'analyze':
            result = agent.analyze_project_structure()
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                print(f"📊 Project Analysis")
                print(f"Workspace: {result['workspace_path']}")
                print(f"Files: {len(result['files'])}")
                print(f"Languages: {', '.join(result['languages'])}")
                print(f"Total lines: {result['total_lines']}")
                print(f"Analysis time: {result['analysis_timestamp']}")
                
        elif args.command == 'quality':
            result = agent.analyze_code_quality(args.file)
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                print(f"📋 Code Quality Analysis: {result['file_path']}")
                print(f"Language: {result['language']}")
                print(f"Total lines: {result['metrics']['total_lines']}")
                print(f"Code lines: {result['metrics']['code_lines']}")
                print(f"Comment lines: {result['metrics']['comment_lines']}")
                
                if result['issues']:
                    print(f"\n❌ Issues:")
                    for issue in result['issues']:
                        print(f"  - {issue}")
                
                if result['suggestions']:
                    print(f"\n💡 Suggestions:")
                    for suggestion in result['suggestions']:
                        print(f"  - {suggestion}")
                        
        elif args.command == 'generate':
            requirements = [req.strip() for req in args.requirements.split(',')]
            code = agent.generate_code(args.language, args.purpose, requirements)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(code)
                print(f"✅ Code generated and saved to {args.output}")
            else:
                print(code)
                
        elif args.command == 'debug':
            result = agent.debug_code(args.file, args.error)
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                print(f"🐛 Debug Analysis: {result['file_path']}")
                if result['error_message']:
                    print(f"Error: {result['error_message']}")
                
                if result['suggestions']:
                    print(f"\n💡 Suggestions:")
                    for suggestion in result['suggestions']:
                        print(f"  - {suggestion}")
                
                if result['potential_fixes']:
                    print(f"\n🔧 Potential Fixes:")
                    for fix in result['potential_fixes']:
                        print(f"  - {fix}")
                        
        elif args.command == 'refactor':
            result = agent.refactor_code(args.file, args.type)
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                print(f"🔧 Refactoring Suggestions: {result['file_path']}")
                print(f"Type: {result['refactoring_type']}")
                
                if result['suggestions']:
                    print(f"\n💡 Suggestions:")
                    for suggestion in result['suggestions']:
                        print(f"  - {suggestion}")
                        
        elif args.command == 'test':
            result = agent.run_tests(args.command)
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                print(f"🧪 Test Results")
                if result['test_command']:
                    print(f"Command: {result['test_command']}")
                print(f"Success: {'✅' if result['success'] else '❌'}")
                
                if result['output']:
                    print(f"\nOutput:\n{result['output']}")
                
                if result['error']:
                    print(f"\nError:\n{result['error']}")
                    
        elif args.command == 'create':
            result = agent.create_project_structure(args.type, args.name)
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                if result['success']:
                    print(f"✅ Project '{args.name}' created successfully!")
                    print(f"Created files:")
                    for file in result['created_files']:
                        print(f"  - {file}")
                else:
                    print(f"❌ Failed to create project: {result['error']}")
                    
        elif args.command == 'help':
            print(agent.get_help())
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()