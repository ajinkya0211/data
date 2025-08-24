from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import asyncio
import structlog
from enum import Enum

from app.core.config import settings

logger = structlog.get_logger()

class AIProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"

class AIProviderBase(ABC):
    """Base class for AI providers"""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.is_available = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider and check availability"""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the AI model"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        pass

class OllamaProvider(AIProviderBase):
    """Ollama local AI provider"""
    
    def __init__(self):
        super().__init__(AIProvider.OLLAMA)
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.max_tokens = settings.OLLAMA_MAX_TOKENS
        self.temperature = settings.OLLAMA_TEMPERATURE
    
    async def initialize(self) -> bool:
        """Initialize Ollama provider"""
        try:
            import ollama
            # Test connection
            response = await asyncio.to_thread(
                ollama.list
            )
            self.is_available = True
            logger.info("Ollama provider initialized successfully", models=response)
            return True
        except Exception as e:
            logger.error("Failed to initialize Ollama provider", error=str(e))
            self.is_available = False
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Ollama"""
        try:
            import ollama
            
            model = kwargs.get('model', self.default_model)
            
            # Prepare the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ollama.chat,
                    model=model,
                    messages=[{
                        'role': 'user',
                        'content': full_prompt
                    }],
                    options={
                        'temperature': kwargs.get('temperature', self.temperature),
                        'num_predict': kwargs.get('max_tokens', self.max_tokens),
                    }
                ),
                timeout=20.0  # Reduce timeout to 20 seconds
            )
            
            return {
                'provider': self.provider,
                'model': model,
                'response': response['message']['content'],
                'usage': {
                    'prompt_tokens': len(full_prompt.split()),
                    'completion_tokens': len(response['message']['content'].split()),
                    'total_tokens': len(full_prompt.split()) + len(response['message']['content'].split())
                },
                'metadata': response
            }
            
        except Exception as e:
            logger.error("Ollama generation failed", error=str(e))
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Ollama health"""
        try:
            import ollama
            await asyncio.wait_for(
                asyncio.to_thread(ollama.list),
                timeout=10.0  # 10 second timeout
            )
            return True
        except Exception:
            return False
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the full prompt with context"""
        if not context:
            return prompt
        
        context_str = ""
        if 'project_info' in context:
            context_str += f"Project: {context['project_info']}\n"
        if 'dataset_info' in context:
            context_str += f"Dataset: {context['dataset_info']}\n"
        if 'user_request' in context:
            context_str += f"User Request: {context['user_request']}\n"
        
        return f"{context_str}\n{prompt}"

class OpenAIProvider(AIProviderBase):
    """OpenAI AI provider"""
    
    def __init__(self):
        super().__init__(AIProvider.OPENAI)
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        self.base_url = settings.OPENAI_BASE_URL
    
    async def initialize(self) -> bool:
        """Initialize OpenAI provider"""
        if not self.api_key:
            logger.warning("OpenAI API key not provided")
            self.is_available = False
            return False
        
        try:
            import openai
            openai.api_key = self.api_key
            openai.base_url = self.base_url
            
            # Test connection with a simple request
            response = await asyncio.to_thread(
                openai.models.list
            )
            self.is_available = True
            logger.info("OpenAI provider initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize OpenAI provider", error=str(e))
            self.is_available = False
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            import openai
            
            model = kwargs.get('model', self.model)
            
            # Prepare the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model=model,
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
            )
            
            return {
                'provider': self.provider,
                'model': model,
                'response': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'metadata': response.model_dump()
            }
            
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check OpenAI health"""
        try:
            import openai
            await asyncio.to_thread(openai.models.list)
            return True
        except Exception:
            return False
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the full prompt with context"""
        if not context:
            return prompt
        
        context_str = ""
        if 'project_info' in context:
            context_str += f"Project: {context['project_info']}\n"
        if 'dataset_info' in context:
            context_str += f"Dataset: {context['dataset_info']}\n"
        if 'user_request' in context:
            context_str += f"User Request: {context['user_request']}\n"
        
        return f"{context_str}\n{prompt}"

class GeminiProvider(AIProviderBase):
    """Google Gemini AI provider"""
    
    def __init__(self):
        super().__init__(AIProvider.GEMINI)
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE
    
    async def initialize(self) -> bool:
        """Initialize Gemini provider"""
        if not self.api_key:
            logger.warning("Gemini API key not provided")
            self.is_available = False
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Test connection
            model = genai.GenerativeModel(self.model)
            response = await asyncio.to_thread(
                model.generate_content, "Hello"
            )
            self.is_available = True
            logger.info("Gemini provider initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize Gemini provider", error=str(e))
            self.is_available = False
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Gemini"""
        try:
            import google.generativeai as genai
            
            model_name = kwargs.get('model', self.model)
            model = genai.GenerativeModel(model_name)
            
            # Prepare the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            response = await asyncio.to_thread(
                model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', self.temperature),
                    max_output_tokens=kwargs.get('max_tokens', self.max_tokens),
                )
            )
            
            return {
                'provider': self.provider,
                'model': model_name,
                'response': response.text,
                'usage': {
                    'prompt_tokens': len(full_prompt.split()),
                    'completion_tokens': len(response.text.split()),
                    'total_tokens': len(full_prompt.split()) + len(response.text.split())
                },
                'metadata': response
            }
            
        except Exception as e:
            logger.error("Gemini generation failed", error=str(e))
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Gemini health"""
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(self.model)
            await asyncio.to_thread(model.generate_content, "Test")
            return True
        except Exception:
            return False
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the full prompt with context"""
        if not context:
            return prompt
        
        context_str = ""
        if 'project_info' in context:
            context_str += f"Project: {context['project_info']}\n"
        if 'dataset_info' in context:
            context_str += f"Dataset: {context['dataset_info']}\n"
        if 'user_request' in context:
            context_str += f"User Request: {context['user_request']}\n"
        
        return f"{context_str}\n{prompt}"

class AIProviderService:
    """Main service for managing AI providers"""
    
    def __init__(self):
        self.providers: Dict[AIProvider, AIProviderBase] = {}
        self.default_provider = AIProvider(settings.DEFAULT_AI_PROVIDER)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all available AI providers"""
        if self.initialized:
            return True
        
        logger.info("Initializing AI providers...")
        
        # Initialize only configured providers
        provider_classes = []
        
        # Always try Ollama first (local)
        provider_classes.append((AIProvider.OLLAMA, OllamaProvider))
        
        # Only try OpenAI if API key is configured
        if settings.OPENAI_API_KEY:
            provider_classes.append((AIProvider.OPENAI, OpenAIProvider))
        
        # Only try Gemini if API key is configured
        if settings.GEMINI_API_KEY:
            provider_classes.append((AIProvider.GEMINI, GeminiProvider))
        
        for provider_enum, provider_class in provider_classes:
            try:
                provider = provider_class()
                if await provider.initialize():
                    self.providers[provider_enum] = provider
                    logger.info(f"Provider {provider_enum} initialized successfully")
                else:
                    logger.warning(f"Provider {provider_enum} failed to initialize")
            except Exception as e:
                logger.error(f"Error initializing provider {provider_enum}", error=str(e))
        
        # Check if default provider is available
        if self.default_provider not in self.providers:
            # Fallback to first available provider
            available_providers = list(self.providers.keys())
            if available_providers:
                self.default_provider = available_providers[0]
                logger.info(f"Default provider changed to {self.default_provider}")
            else:
                logger.error("No AI providers available")
                return False
        
        self.initialized = True
        logger.info(f"AI providers initialized. Default: {self.default_provider}")
        return True
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[AIProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified or default provider"""
        if not self.initialized:
            await self.initialize()
        
        # Use specified provider or default
        target_provider = provider or self.default_provider
        
        if target_provider not in self.providers:
            raise Exception(f"Provider {target_provider} not available")
        
        provider_instance = self.providers[target_provider]
        
        try:
            response = await provider_instance.generate_response(prompt, context, **kwargs)
            logger.info(f"Generated response using {target_provider}")
            return response
        except Exception as e:
            logger.error(f"Generation failed with {target_provider}, trying fallback", error=str(e))
            
            # Try fallback to other available providers
            for fallback_provider in self.providers:
                if fallback_provider != target_provider:
                    try:
                        fallback_instance = self.providers[fallback_provider]
                        response = await fallback_instance.generate_response(prompt, context, **kwargs)
                        logger.info(f"Fallback successful using {fallback_provider}")
                        return response
                    except Exception as fallback_error:
                        logger.warning(f"Fallback to {fallback_provider} failed", error=str(fallback_error))
            
            raise Exception("All AI providers failed")
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        if not self.initialized:
            await self.initialize()
        
        providers_info = []
        for provider_enum, provider_instance in self.providers.items():
            is_healthy = await provider_instance.health_check()
            providers_info.append({
                'provider': provider_enum,
                'available': provider_instance.is_available,
                'healthy': is_healthy,
                'is_default': provider_enum == self.default_provider
            })
        
        return providers_info
    
    async def switch_default_provider(self, provider: AIProvider) -> bool:
        """Switch the default AI provider"""
        if provider not in self.providers:
            return False
        
        self.default_provider = provider
        logger.info(f"Default AI provider switched to {provider}")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        if not self.initialized:
            await self.initialize()
        
        health_status = {}
        for provider_enum, provider_instance in self.providers.items():
            is_healthy = await provider_instance.health_check()
            health_status[provider_enum] = {
                'available': provider_instance.is_available,
                'healthy': is_healthy
            }
        
        return health_status
    
    async def chat_with_ai(
        self,
        message: str,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> str:
        """Chat with AI for general assistance"""
        try:
            # Build context
            context = {"user_message": message}
            
            if project_id:
                context["project_id"] = project_id
            if dataset_id:
                context["dataset_id"] = dataset_id
            
            # Generate response
            response = await self.generate_response(
                prompt=message,
                context=context,
                provider=provider
            )
            
            return response.get("response", "I'm sorry, I couldn't generate a response.")
            
        except Exception as e:
            logger.error("Chat with AI failed", error=str(e))
            return f"I encountered an error: {str(e)}"
    
    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        project_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> str:
        """Generate code based on prompt"""
        try:
            # Build code generation context
            code_prompt = f"""
            You are an expert {language} programmer. Generate code based on the following request:
            
            Request: {prompt}
            
            Requirements:
            1. Write clean, well-commented code
            2. Include proper error handling
            3. Make the code reusable and well-structured
            4. Return only the code, no explanations
            
            Language: {language}
            """
            
            # Generate response
            response = await self.generate_response(
                prompt=code_prompt,
                context={"code_generation": True, "language": language, "project_id": project_id},
                provider=provider
            )
            
            return response.get("response", f"# Could not generate {language} code for: {prompt}")
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            return f"# Error generating code: {str(e)}"

# Global instance
ai_provider_service = AIProviderService() 