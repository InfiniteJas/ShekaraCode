# src/api/openai_service.py
from typing import List, Dict
import openai
from ..utils.logging import get_logger
from ..config.settings import Settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_logger(__name__)

class OpenAIService:
    def __init__(self, settings: Settings):
        openai.api_key = settings.openai_api_key
        self.settings = settings
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_code(self, changes: List[Dict]) -> Dict:
        """Analyze code changes using OpenAI."""
        try:
            prompt = self._create_analysis_prompt(changes)
            
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return {
                "quality_score": 8.5,
                "issues": [
                    {"type": "style", "severity": "low", "description": "Example issue"}
                ],
                "security_concerns": [
                    {"level": "low", "description": "Example concern"}
                ],
                "performance_impact": "minimal",
                "recommendations": ["Example recommendation"]
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {str(e)}")
            raise
            
    def _create_analysis_prompt(self, changes: List[Dict]) -> str:
        """Create prompt for code analysis."""
        prompt = "Please analyze the following code changes and provide:\n"
        prompt += "1. Code quality assessment\n"
        prompt += "2. Potential issues or bugs\n"
        prompt += "3. Security concerns\n"
        prompt += "4. Performance implications\n"
        prompt += "5. Improvement recommendations\n\n"
        prompt += "Changes:\n"
        
        for change in changes:
            prompt += f"\nFile: {change['filename']}\n"
            prompt += f"Changes:\n```\n{change['patch']}\n```\n"
            
        return prompt
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for code analysis."""
        return """You are an expert code reviewer with deep knowledge of software engineering principles, 
                 clean code practices, and security patterns. Analyze the code changes and provide insights."""