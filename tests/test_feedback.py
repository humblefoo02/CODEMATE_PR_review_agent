import pytest
import os
from unittest.mock import patch, MagicMock
from core.feedback import FeedbackGenerator

class TestFeedbackGenerator:
    def setup_method(self):
        """Setup test fixtures"""
        self.feedback_generator = FeedbackGenerator(use_ai=False)
        
    def test_feedback_generator_initialization(self):
        """Test feedback generator initialization"""
        assert hasattr(self.feedback_generator, 'templates')
        assert 'style' in self.feedback_generator.templates
        assert 'error' in self.feedback_generator.templates
        assert 'security' in self.feedback_generator.templates
        assert 'complexity' in self.feedback_generator.templates

    def test_generate_empty_issues(self):
        """Test feedback generation with empty issues"""
        issues = []
        feedback = self.feedback_generator.generate(issues)
        assert feedback == []

    def test_generate_flake8_feedback(self):
        """Test feedback generation for flake8 issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'code': 'E501',
                'message': 'line too long (80 > 79 characters)',
                'severity': 'error',
                'category': 'style',
                'tool': 'flake8'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['file'] == 'test.py'
        assert feedback[0]['line'] == 1
        assert feedback[0]['severity'] == 'error'
        assert feedback[0]['category'] == 'style'
        assert feedback[0]['tool'] == 'flake8'
        assert 'line too long' in feedback[0]['message']

    def test_generate_security_feedback(self):
        """Test feedback generation for security issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Use of hardcoded password detected',
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'test_id': 'B101',
                'confidence': 'high'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['severity'] == 'high'
        assert feedback[0]['category'] == 'security'
        assert feedback[0]['tool'] == 'bandit'
        assert 'Security issue' in feedback[0]['message']
        assert len(feedback[0]['suggestions']) > 0

    def test_generate_complexity_feedback(self):
        """Test feedback generation for complexity issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'function': 'complex_function',
                'complexity': 15,
                'severity': 'high',
                'category': 'complexity',
                'tool': 'radon'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['severity'] == 'high'
        assert feedback[0]['category'] == 'complexity'
        assert feedback[0]['tool'] == 'radon'
        assert 'complex_function' in feedback[0]['message']
        assert len(feedback[0]['suggestions']) > 0

    def test_generate_custom_feedback(self):
        """Test feedback generation for custom issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Found TODO: implement this',
                'severity': 'low',
                'category': 'maintenance',
                'tool': 'custom'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['severity'] == 'low'
        assert feedback[0]['category'] == 'maintenance'
        assert feedback[0]['tool'] == 'custom'
        assert 'TODO' in feedback[0]['message']

    def test_generate_generic_feedback(self):
        """Test feedback generation for unknown issue types"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Unknown issue',
                'severity': 'info',
                'category': 'unknown',
                'tool': 'unknown'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['severity'] == 'info'
        assert feedback[0]['category'] == 'unknown'
        assert feedback[0]['tool'] == 'unknown'

    def test_generate_flake8_feedback_with_suggestions(self):
        """Test flake8 feedback with specific suggestions"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'code': 'F841',
                'message': 'local variable is assigned to but never used',
                'severity': 'error',
                'category': 'style',
                'tool': 'flake8'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert len(feedback[0]['suggestions']) > 0
        assert 'Remove unused variable' in feedback[0]['suggestions'][0]

    def test_generate_security_feedback_with_suggestions(self):
        """Test security feedback with specific suggestions"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Use of exec() detected',
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'test_id': 'B102',
                'confidence': 'high'
            }
        ]
        
        feedback = self.feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert len(feedback[0]['suggestions']) > 0
        assert any('exec()' in suggestion for suggestion in feedback[0]['suggestions'])

    def test_prioritize_feedback(self):
        """Test feedback prioritization by severity"""
        feedback_items = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'low',
                'category': 'style',
                'message': 'Low priority issue'
            },
            {
                'file': 'test.py',
                'line': 2,
                'severity': 'high',
                'category': 'security',
                'message': 'High priority issue'
            },
            {
                'file': 'test.py',
                'line': 3,
                'severity': 'error',
                'category': 'error',
                'message': 'Error issue'
            }
        ]
        
        prioritized = self.feedback_generator._prioritize_feedback(feedback_items)
        
        # Should be sorted by severity: error, high, low
        assert prioritized[0]['severity'] == 'error'
        assert prioritized[1]['severity'] == 'high'
        assert prioritized[2]['severity'] == 'low'

    def test_generate_template_feedback(self):
        """Test template-based feedback generation"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'code': 'E501',
                'message': 'line too long',
                'severity': 'error',
                'category': 'style',
                'tool': 'flake8'
            }
        ]
        
        feedback = self.feedback_generator._generate_template_feedback(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['tool'] == 'flake8'

    def test_generate_flake8_feedback_specific_codes(self):
        """Test flake8 feedback for specific error codes"""
        test_cases = [
            ('E501', 'Line too long'),
            ('F841', 'Variable defined but not used'),
            ('F401', 'Module imported but unused'),
            ('W293', 'Blank line contains whitespace')
        ]
        
        for code, expected in test_cases:
            issues = [
                {
                    'file': 'test.py',
                    'line': 1,
                    'code': code,
                    'message': f'{code} {expected}',
                    'severity': 'error',
                    'category': 'style',
                    'tool': 'flake8'
                }
            ]
            
            feedback = self.feedback_generator._generate_flake8_feedback(issues[0])
            
            assert feedback['code'] == code
            assert feedback['severity'] == 'error'
            assert feedback['category'] == 'style'

    def test_generate_security_feedback_hardcoded_secrets(self):
        """Test security feedback for hardcoded secrets"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Use of hardcoded password detected',
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'test_id': 'B101',
                'confidence': 'high'
            }
        ]
        
        feedback = self.feedback_generator._generate_security_feedback(issues[0])
        
        assert feedback['severity'] == 'high'
        assert feedback['category'] == 'security'
        assert 'hardcoded' in feedback['message'].lower()
        assert len(feedback['suggestions']) > 0

    def test_generate_complexity_feedback_high_complexity(self):
        """Test complexity feedback for high complexity functions"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'function': 'complex_function',
                'complexity': 20,
                'severity': 'high',
                'category': 'complexity',
                'tool': 'radon'
            }
        ]
        
        feedback = self.feedback_generator._generate_complexity_feedback(issues[0])
        
        assert feedback['severity'] == 'high'
        assert feedback['category'] == 'complexity'
        assert 'complex_function' in feedback['message']
        assert feedback['complexity'] == 20
        assert len(feedback['suggestions']) > 0

    def test_generate_custom_feedback_maintenance(self):
        """Test custom feedback for maintenance issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Found FIXME: fix this later',
                'severity': 'low',
                'category': 'maintenance',
                'tool': 'custom'
            }
        ]
        
        feedback = self.feedback_generator._generate_custom_feedback(issues[0])
        
        assert feedback['severity'] == 'low'
        assert feedback['category'] == 'maintenance'
        assert 'FIXME' in feedback['message']
        assert len(feedback['suggestions']) > 0

    def test_generate_generic_feedback_unknown(self):
        """Test generic feedback for unknown issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Some unknown issue',
                'severity': 'info',
                'category': 'unknown',
                'tool': 'unknown'
            }
        ]
        
        feedback = self.feedback_generator._generate_generic_feedback(issues[0])
        
        assert feedback['severity'] == 'info'
        assert feedback['category'] == 'unknown'
        assert feedback['tool'] == 'unknown'
        assert 'Some unknown issue' in feedback['message']

    def test_generate_with_ai_disabled(self):
        """Test feedback generation with AI disabled"""
        feedback_generator = FeedbackGenerator(use_ai=False)
        
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'message': 'Test issue',
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8'
            }
        ]
        
        feedback = feedback_generator.generate(issues)
        
        assert len(feedback) == 1
        assert feedback[0]['tool'] == 'flake8'

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_generate_with_ai_enabled(self):
        """Test feedback generation with AI enabled"""
        with patch('utils.ai_helpers.AIHelper') as mock_ai_helper:
            mock_ai_instance = MagicMock()
            mock_ai_instance.generate_feedback.return_value = [
                {
                    'file': 'test.py',
                    'line': 1,
                    'severity': 'medium',
                    'category': 'ai_suggestion',
                    'message': 'AI suggestion',
                    'suggestions': ['AI recommendation'],
                    'tool': 'ai'
                }
            ]
            mock_ai_helper.return_value = mock_ai_instance
            
            feedback_generator = FeedbackGenerator(use_ai=True)
            
            issues = [
                {
                    'file': 'test.py',
                    'line': 1,
                    'message': 'Test issue',
                    'severity': 'medium',
                    'category': 'style',
                    'tool': 'flake8'
                }
            ]
            
            feedback = feedback_generator.generate(issues)
            
            # Should have both template and AI feedback
            assert len(feedback) >= 1
            ai_feedback = [f for f in feedback if f['tool'] == 'ai']
            assert len(ai_feedback) >= 1

    def test_generate_with_ai_error_fallback(self):
        """Test feedback generation when AI fails and falls back to templates"""
        with patch('utils.ai_helpers.AIHelper') as mock_ai_helper:
            mock_ai_instance = MagicMock()
            mock_ai_instance.generate_feedback.side_effect = Exception("AI error")
            mock_ai_helper.return_value = mock_ai_instance
            
            feedback_generator = FeedbackGenerator(use_ai=True)
            
            issues = [
                {
                    'file': 'test.py',
                    'line': 1,
                    'message': 'Test issue',
                    'severity': 'medium',
                    'category': 'style',
                    'tool': 'flake8'
                }
            ]
            
            feedback = feedback_generator.generate(issues)
            
            # Should fall back to template feedback
            assert len(feedback) == 1
            assert feedback[0]['tool'] == 'flake8'
