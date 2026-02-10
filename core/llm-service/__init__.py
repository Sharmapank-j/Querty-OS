"""Querty-OS LLM Service Package"""
from .llm_service import LLMService, LLMMode, create_llm_service

__version__ = "0.1.0"
__all__ = ["LLMService", "LLMMode", "create_llm_service"]
