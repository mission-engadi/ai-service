"""Abacus.AI Integration Client.

Provides integration with Abacus.AI for LLM-powered content generation,
translation, enhancement, and other AI operations.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import abacusai
from abacusai import ApiException

from app.core.config import settings

logger = logging.getLogger(__name__)


class AbacusAIClient:
    """Abacus.AI client for AI operations.
    
    Provides methods for:
    - Text generation (content creation)
    - Translation
    - Text enhancement
    - Image generation (if available)
    """
    
    def __init__(self):
        """Initialize Abacus.AI client."""
        self.client = abacusai.ApiClient()
        self.deployment_token = settings.ABACUS_AI_DEPLOYMENT_TOKEN
        self.deployment_id = settings.ABACUS_AI_DEPLOYMENT_ID
        
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using Abacus.AI LLM.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system_message: Optional system message for context
            
        Returns:
            Dict with 'text', 'tokens_used', 'model_used' keys
            
        Raises:
            ApiException: If API call fails
        """
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.chat_llm(
                    deployment_token=self.deployment_token,
                    deployment_id=self.deployment_id,
                    messages=[
                        {"role": "system", "content": system_message or "You are a helpful AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            
            return {
                "text": result.get("content", ""),
                "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                "model_used": result.get("model", "unknown"),
            }
            
        except ApiException as e:
            logger.error(f"Abacus.AI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_text: {e}")
            raise
    
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> Dict[str, Any]:
        """Translate text using Abacus.AI.
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, es, fr, pt)
            target_lang: Target language code (en, es, fr, pt)
            
        Returns:
            Dict with 'translated_text', 'tokens_used', 'quality_score' keys
            
        Raises:
            ApiException: If translation fails
        """
        lang_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "pt": "Portuguese",
        }
        
        prompt = f"""Translate the following text from {lang_names.get(source_lang, source_lang)} to {lang_names.get(target_lang, target_lang)}.
Provide ONLY the translation, no explanations.

Text to translate:
{text}

Translation:"""
        
        result = await self.generate_text(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent translations
            system_message="You are a professional translator.",
        )
        
        return {
            "translated_text": result["text"].strip(),
            "tokens_used": result["tokens_used"],
            "quality_score": 0.85,  # Default quality score
        }
    
    async def enhance_text(
        self,
        text: str,
        enhancement_type: str,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhance text using Abacus.AI.
        
        Args:
            text: Text to enhance
            enhancement_type: Type of enhancement (grammar, tone, seo, summarize, improve)
            additional_context: Additional context for enhancement
            
        Returns:
            Dict with 'enhanced_text', 'tokens_used', 'changes_made' keys
            
        Raises:
            ApiException: If enhancement fails
        """
        enhancement_prompts = {
            "grammar": "Fix all grammar, spelling, and punctuation errors in the following text. Keep the same tone and style:",
            "tone": f"Adjust the tone of the following text to be {additional_context or 'professional and friendly'}:",
            "seo": "Optimize the following text for SEO. Add relevant keywords naturally and improve readability:",
            "summarize": "Provide a concise summary of the following text:",
            "improve": "Improve the following text by making it clearer, more engaging, and more impactful:",
        }
        
        prompt = f"{enhancement_prompts.get(enhancement_type, enhancement_prompts['improve'])}\n\n{text}\n\nEnhanced version:"
        
        result = await self.generate_text(
            prompt=prompt,
            temperature=0.5,
            system_message="You are an expert editor and content strategist.",
        )
        
        return {
            "enhanced_text": result["text"].strip(),
            "tokens_used": result["tokens_used"],
            "changes_made": ["Enhanced"],  # Could be more detailed
        }
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        """Generate image using AI (placeholder - implement with actual image generation API).
        
        Args:
            prompt: Image description prompt
            size: Image size (e.g., "1024x1024", "512x512")
            
        Returns:
            Dict with 'image_url', 'size', 'format' keys
            
        Note:
            This is a placeholder. Implement with actual image generation API
            (e.g., DALL-E, Stable Diffusion, or Abacus.AI if available)
        """
        # Placeholder implementation
        logger.warning("Image generation not yet implemented")
        return {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/975px-No-Image-Placeholder.svg.png",
            "size": size,
            "format": "jpg",
        }
    
    async def batch_generate(
        self,
        prompts: List[str],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Generate text for multiple prompts in parallel.
        
        Args:
            prompts: List of prompts
            max_tokens: Maximum tokens per generation
            temperature: Sampling temperature
            
        Returns:
            List of generation results
        """
        tasks = [
            self.generate_text(prompt, max_tokens, temperature)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Global client instance
abacus_client = AbacusAIClient()
