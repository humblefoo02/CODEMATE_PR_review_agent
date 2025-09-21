import os
import json
from typing import List, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class AIHelper:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Install with: pip install openai")
                self.enabled = False

    def generate_feedback(self, file_path: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI-powered feedback for code issues"""
        if not self.enabled:
            return []
        
        try:
            # Prepare context for AI
            context = self._prepare_context(file_path, issues)
            
            # Generate AI feedback
            ai_response = self._call_openai(context)
            
            # Parse and format response
            return self._parse_ai_response(ai_response, issues)
            
        except Exception as e:
            logger.error(f"AI feedback generation failed: {e}")
            return []

    def _prepare_context(self, file_path: str, issues: List[Dict[str, Any]]) -> str:
        """Prepare context for AI analysis"""
        context = f"""
Code Review Analysis for: {file_path}

Issues Found:
"""
        
        for i, issue in enumerate(issues, 1):
            context += f"""
{i}. {issue.get('category', 'unknown').upper()} - {issue.get('severity', 'info').upper()}
   Tool: {issue.get('tool', 'unknown')}
   Line: {issue.get('line', 0)}
   Message: {issue.get('message', 'No message')}
"""
            
            if issue.get('code'):
                context += f"   Code: {issue.get('code')}\n"
            if issue.get('complexity'):
                context += f"   Complexity: {issue.get('complexity')}\n"
            if issue.get('function'):
                context += f"   Function: {issue.get('function')}\n"
        
        context += """
Please provide:
1. A brief summary of the main issues
2. Specific, actionable suggestions for each issue
3. Overall code quality assessment
4. Priority recommendations for fixes

Format your response as JSON with the following structure:
{
  "summary": "Brief overview of issues",
  "suggestions": [
    {
      "issue_id": 1,
      "suggestion": "Specific suggestion",
      "priority": "high|medium|low",
      "reasoning": "Why this fix is important"
    }
  ],
  "overall_assessment": "Overall code quality assessment",
  "priority_fixes": ["List of high-priority fixes"]
}
"""
        
        return context

    def _call_openai(self, context: str) -> str:
        """Call OpenAI API for feedback generation"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Provide constructive, actionable feedback for code issues. Focus on code quality, security, performance, and maintainability."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    def _parse_ai_response(self, response: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse AI response and convert to feedback format"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                ai_data = json.loads(json_str)
                
                feedback_items = []
                
                # Add AI summary as a special feedback item
                if ai_data.get('summary'):
                    feedback_items.append({
                        'file': issues[0].get('file', '') if issues else '',
                        'line': 0,
                        'severity': 'info',
                        'category': 'ai_summary',
                        'message': f"AI Analysis: {ai_data['summary']}",
                        'suggestions': [],
                        'tool': 'ai'
                    })
                
                # Add AI suggestions
                for suggestion in ai_data.get('suggestions', []):
                    issue_id = suggestion.get('issue_id', 0)
                    if 0 <= issue_id - 1 < len(issues):
                        original_issue = issues[issue_id - 1]
                        feedback_items.append({
                            'file': original_issue.get('file', ''),
                            'line': original_issue.get('line', 0),
                            'severity': suggestion.get('priority', 'medium'),
                            'category': 'ai_suggestion',
                            'message': suggestion.get('suggestion', ''),
                            'suggestions': [suggestion.get('reasoning', '')],
                            'tool': 'ai'
                        })
                
                # Add overall assessment
                if ai_data.get('overall_assessment'):
                    feedback_items.append({
                        'file': issues[0].get('file', '') if issues else '',
                        'line': 0,
                        'severity': 'info',
                        'category': 'ai_assessment',
                        'message': f"Overall Assessment: {ai_data['overall_assessment']}",
                        'suggestions': ai_data.get('priority_fixes', []),
                        'tool': 'ai'
                    })
                
                return feedback_items
                
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        # Fallback: return a simple text-based feedback
        return [{
            'file': issues[0].get('file', '') if issues else '',
            'line': 0,
            'severity': 'info',
            'category': 'ai_feedback',
            'message': f"AI Feedback: {response[:200]}...",
            'suggestions': [],
            'tool': 'ai'
        }]

    def generate_inline_comments(self, file_path: str, line_number: int, code_snippet: str, issue: Dict[str, Any]) -> str:
        """Generate inline comment for specific code line"""
        if not self.enabled:
            return ""
        
        try:
            context = f"""
Code Review - Inline Comment

File: {file_path}
Line: {line_number}
Code: {code_snippet}

Issue: {issue.get('message', 'No specific issue')}
Category: {issue.get('category', 'unknown')}
Severity: {issue.get('severity', 'info')}

Please provide a concise, helpful inline comment (max 200 characters) that:
1. Explains the issue clearly
2. Suggests a specific fix
3. Is constructive and professional

Format: Just provide the comment text, no additional formatting.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code reviewer providing inline comments. Be concise, helpful, and constructive."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI inline comment generation failed: {e}")
            return ""

    def suggest_code_improvements(self, code_snippet: str, language: str = "python") -> List[str]:
        """Suggest general code improvements"""
        if not self.enabled:
            return []
        
        try:
            context = f"""
Code Improvement Suggestions

Language: {language}
Code:
{code_snippet}

Please suggest 3-5 specific improvements for this code snippet.
Focus on:
- Readability and maintainability
- Performance optimizations
- Best practices
- Security considerations

Format: Provide a numbered list of suggestions.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer providing code improvement suggestions. Be specific and actionable."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse numbered list
            suggestions = []
            for line in response.choices[0].message.content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    suggestions.append(line)
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"AI code improvement suggestions failed: {e}")
            return []
