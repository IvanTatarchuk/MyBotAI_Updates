#!/usr/bin/env python3
"""
Simple test file for the Programming Agent
"""

import unittest
from programming_agent import ProgrammingAgent

class TestProgrammingAgent(unittest.TestCase):
    """Test cases for ProgrammingAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ProgrammingAgent()
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.workspace_path)
    
    def test_project_analysis(self):
        """Test project structure analysis."""
        analysis = self.agent.analyze_project_structure()
        
        self.assertIn('workspace_path', analysis)
        self.assertIn('files', analysis)
        self.assertIn('languages', analysis)
        self.assertIn('total_lines', analysis)
        self.assertIsInstance(analysis['files'], list)
        self.assertIsInstance(analysis['languages'], list)
        self.assertIsInstance(analysis['total_lines'], int)
    
    def test_code_generation_python(self):
        """Test Python code generation."""
        code = self.agent.generate_code('python', 'test function', ['simple test'])
        
        self.assertIsInstance(code, str)
        self.assertIn('test function', code)
        self.assertIn('simple test', code)
        self.assertIn('def', code)
    
    def test_code_generation_javascript(self):
        """Test JavaScript code generation."""
        code = self.agent.generate_code('javascript', 'test function', ['simple test'])
        
        self.assertIsInstance(code, str)
        self.assertIn('test function', code)
        self.assertIn('simple test', code)
        self.assertIn('function', code)
    
    def test_project_creation(self):
        """Test project creation."""
        result = self.agent.create_project_structure('python', 'test_project')
        
        self.assertIn('success', result)
        self.assertIn('created_files', result)
        self.assertIsInstance(result['created_files'], list)
        
        # Clean up
        import shutil
        import os
        if os.path.exists('test_project'):
            shutil.rmtree('test_project')

if __name__ == '__main__':
    unittest.main()