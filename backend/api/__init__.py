from .audio import router as audio_router
from .generation import router as generation_router
from .feedback import router as feedback_router
from .auth import router as auth_router

__all__ = ['audio_router', 'generation_router', 'feedback_router', 'auth_router']
