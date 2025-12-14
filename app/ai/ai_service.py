from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import openai

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AIServiceInterface(ABC):
 

    @abstractmethod
    async def generate_page_summary(self, page_data: Dict[str, Any]) -> str:
        """
        Generate a summary for a LinkedIn page.

        Args:
            page_data: Dictionary containing page information

        Returns:
            Generated summary text
        """
        pass

    @abstractmethod
    async def analyze_engagement(self, posts_data: list) -> Dict[str, Any]:
        """
        Analyze engagement metrics from posts.

        Args:
            posts_data: List of post dictionaries

        Returns:
            Dictionary with engagement analysis
        """
        pass


class OpenAIService(AIServiceInterface):
  

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY

        if not self.api_key:
            logger.warning("OpenAI API key not configured. AI features will be disabled.")
            self.enabled = False
        else:
            openai.api_key = self.api_key
            self.enabled = True
            self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate_page_summary(self, page_data: Dict[str, Any]) -> str:
        """
        Generate a summary for a LinkedIn page using OpenAI.

        Args:
            page_data: Dictionary containing page information

        Returns:
            Generated summary text
        """
        if not self.enabled:
            return "AI summary unavailable: API key not configured"

        try:
            # Construct prompt
            prompt = self._build_summary_prompt(page_data)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business analyst. Generate concise, insightful summaries of LinkedIn company pages."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for page: {page_data.get('page_id')}")

            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    async def analyze_engagement(self, posts_data: list) -> Dict[str, Any]:
       
        if not self.enabled:
            return {"error": "AI analysis unavailable: API key not configured"}

        try:
            # Calculate basic metrics
            total_posts = len(posts_data)
            total_likes = sum(post.get("likes", 0) for post in posts_data)
            total_comments = sum(post.get("comments_count", 0) for post in posts_data)

            avg_likes = total_likes / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0

            # Build prompt for AI analysis
            prompt = f"""
            Analyze the following engagement data for LinkedIn posts:

            Total Posts: {total_posts}
            Total Likes: {total_likes}
            Total Comments: {total_comments}
            Average Likes per Post: {avg_likes:.2f}
            Average Comments per Post: {avg_comments:.2f}

            Provide a brief analysis of the engagement trends and suggestions for improvement.
            """

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media analytics expert. Analyze engagement metrics and provide actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )

            analysis = response.choices[0].message.content.strip()

            return {
                "total_posts": total_posts,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "ai_analysis": analysis
            }

        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return {"error": f"Error analyzing engagement: {str(e)}"}

    def _build_summary_prompt(self, page_data: Dict[str, Any]) -> str:

        return f"""
        Generate a concise summary for the following LinkedIn company page:

        Company Name: {page_data.get('name')}
        Industry: {page_data.get('industry', 'Not specified')}
        Followers: {page_data.get('followers_count', 0):,}
        Description: {page_data.get('description', 'Not available')}
        Website: {page_data.get('website', 'Not available')}

        Provide a professional 2-3 sentence summary highlighting the company's key characteristics and market presence.
        """


class MockAIService(AIServiceInterface):


    async def generate_page_summary(self, page_data: Dict[str, Any]) -> str:
        """Generate a mock summary"""
        name = page_data.get('name', 'Unknown Company')
        industry = page_data.get('industry', 'various sectors')
        followers = page_data.get('followers_count', 0)

        return (
            f"{name} is a leading organization in {industry} "
            f"with {followers:,} followers on LinkedIn. "
            f"The company demonstrates strong market presence and engagement."
        )

    async def analyze_engagement(self, posts_data: list) -> Dict[str, Any]:
        """Generate mock engagement analysis"""
        total_posts = len(posts_data)
        total_likes = sum(post.get("likes", 0) for post in posts_data)
        total_comments = sum(post.get("comments_count", 0) for post in posts_data)

        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        avg_comments = total_comments / total_posts if total_posts > 0 else 0

        return {
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "ai_analysis": "Mock analysis: Engagement metrics show healthy interaction rates. Consider posting more regularly to increase visibility."
        }


def get_ai_service() -> AIServiceInterface:
   
    if settings.OPENAI_API_KEY:
        return OpenAIService()
    else:
        logger.info("Using Mock AI Service (no API key configured)")
        return MockAIService()
