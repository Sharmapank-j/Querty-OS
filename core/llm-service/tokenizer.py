"""
Tokenizer Wrapper for LLM Service

Basic tokenizer wrapper that can work with different tokenizer backends.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Union

logger = logging.getLogger(__name__)


class TokenizerBackend(ABC):
    """Abstract base class for tokenizer backends."""

    @abstractmethod
    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs.

        Args:
            text: Text to encode

        Returns:
            List of token IDs
        """
        pass

    @abstractmethod
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs to text.

        Args:
            token_ids: List of token IDs

        Returns:
            Decoded text
        """
        pass

    @abstractmethod
    def vocab_size(self) -> int:
        """
        Get vocabulary size.

        Returns:
            Size of the vocabulary
        """
        pass


class HuggingFaceTokenizer(TokenizerBackend):
    """Tokenizer backend using HuggingFace transformers."""

    def __init__(self, model_name: str):
        """
        Initialize HuggingFace tokenizer.

        Args:
            model_name: Name or path of the model/tokenizer
        """
        self.model_name = model_name
        self.tokenizer = None

        try:
            from transformers import AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Loaded HuggingFace tokenizer: {model_name}")
        except ImportError:
            logger.error("transformers library not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}", exc_info=True)
            raise

    def encode(self, text: str) -> List[int]:
        """Encode text using HuggingFace tokenizer."""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized")
        return self.tokenizer.encode(text, add_special_tokens=True)

    def decode(self, token_ids: List[int]) -> str:
        """Decode tokens using HuggingFace tokenizer."""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized")
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def vocab_size(self) -> int:
        """Get vocabulary size."""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized")
        return len(self.tokenizer)


class SentencePieceTokenizer(TokenizerBackend):
    """Tokenizer backend using SentencePiece."""

    def __init__(self, model_path: str):
        """
        Initialize SentencePiece tokenizer.

        Args:
            model_path: Path to SentencePiece model file
        """
        self.model_path = model_path
        self.sp = None

        try:
            import sentencepiece as spm

            self.sp = spm.SentencePieceProcessor()
            self.sp.Load(model_path)
            logger.info(f"Loaded SentencePiece tokenizer: {model_path}")
        except ImportError:
            logger.error("sentencepiece library not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}", exc_info=True)
            raise

    def encode(self, text: str) -> List[int]:
        """Encode text using SentencePiece."""
        if self.sp is None:
            raise RuntimeError("Tokenizer not initialized")
        return self.sp.EncodeAsIds(text)

    def decode(self, token_ids: List[int]) -> str:
        """Decode tokens using SentencePiece."""
        if self.sp is None:
            raise RuntimeError("Tokenizer not initialized")
        return self.sp.DecodeIds(token_ids)

    def vocab_size(self) -> int:
        """Get vocabulary size."""
        if self.sp is None:
            raise RuntimeError("Tokenizer not initialized")
        return self.sp.GetPieceSize()


class BasicTokenizer(TokenizerBackend):
    """Simple word-based tokenizer for testing/fallback."""

    def __init__(self, vocab_size: int = 50000):
        """
        Initialize basic tokenizer.

        Args:
            vocab_size: Size of vocabulary (for compatibility)
        """
        self._vocab_size = vocab_size
        self.word_to_id = {}
        self.id_to_word = {}
        self._next_id = 0
        logger.info("Initialized basic word tokenizer")

    def encode(self, text: str) -> List[int]:
        """
        Encode text using simple word splitting.

        Args:
            text: Text to encode

        Returns:
            List of token IDs
        """
        words = text.lower().split()
        token_ids = []

        for word in words:
            if word not in self.word_to_id:
                if self._next_id < self._vocab_size:
                    self.word_to_id[word] = self._next_id
                    self.id_to_word[self._next_id] = word
                    self._next_id += 1
                else:
                    # Use unknown token ID (0)
                    token_ids.append(0)
                    continue

            token_ids.append(self.word_to_id[word])

        return token_ids

    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs to text.

        Args:
            token_ids: List of token IDs

        Returns:
            Decoded text
        """
        words = []
        for token_id in token_ids:
            word = self.id_to_word.get(token_id, "<UNK>")
            words.append(word)
        return " ".join(words)

    def vocab_size(self) -> int:
        """Get vocabulary size."""
        return self._vocab_size


class Tokenizer:
    """
    Tokenizer wrapper that can work with different backends.

    Provides a unified interface for encoding/decoding text with various tokenizer backends.
    """

    def __init__(self, backend: Optional[TokenizerBackend] = None):
        """
        Initialize tokenizer.

        Args:
            backend: Tokenizer backend to use (defaults to BasicTokenizer)
        """
        self.backend = backend or BasicTokenizer()
        logger.info(f"Tokenizer initialized with backend: {self.backend.__class__.__name__}")

    @classmethod
    def from_pretrained(cls, model_name: str, backend_type: str = "huggingface") -> "Tokenizer":
        """
        Create tokenizer from pretrained model.

        Args:
            model_name: Model name or path
            backend_type: Type of backend ("huggingface", "sentencepiece")

        Returns:
            Tokenizer instance
        """
        if backend_type == "huggingface":
            try:
                backend = HuggingFaceTokenizer(model_name)
                return cls(backend)
            except Exception as e:
                logger.error(f"Failed to load HuggingFace tokenizer: {e}")
                logger.warning("Falling back to basic tokenizer")
                return cls(BasicTokenizer())

        elif backend_type == "sentencepiece":
            try:
                backend = SentencePieceTokenizer(model_name)
                return cls(backend)
            except Exception as e:
                logger.error(f"Failed to load SentencePiece tokenizer: {e}")
                logger.warning("Falling back to basic tokenizer")
                return cls(BasicTokenizer())

        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

    def encode(
        self,
        text: Union[str, List[str]],
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
    ) -> Union[List[int], List[List[int]]]:
        """
        Encode text to token IDs.

        Args:
            text: Text or list of texts to encode
            add_special_tokens: Whether to add special tokens (ignored for basic tokenizer)
            max_length: Maximum sequence length (truncate if exceeded)

        Returns:
            Token IDs or list of token ID lists
        """
        if isinstance(text, str):
            token_ids = self.backend.encode(text)
            if max_length and len(token_ids) > max_length:
                token_ids = token_ids[:max_length]
            return token_ids
        else:
            # Batch encoding
            return [self.encode(t, add_special_tokens, max_length) for t in text]

    def decode(
        self,
        token_ids: Union[List[int], List[List[int]]],
        skip_special_tokens: bool = True,
    ) -> Union[str, List[str]]:
        """
        Decode token IDs to text.

        Args:
            token_ids: Token IDs or list of token ID lists
            skip_special_tokens: Whether to skip special tokens (ignored for basic tokenizer)

        Returns:
            Decoded text or list of texts
        """
        if isinstance(token_ids[0], int):
            # Single sequence
            return self.backend.decode(token_ids)
        else:
            # Batch decoding
            return [self.backend.decode(ids) for ids in token_ids]

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.encode(text))

    def truncate(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to maximum token count.

        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens

        Returns:
            Truncated text
        """
        token_ids = self.encode(text)
        if len(token_ids) <= max_tokens:
            return text
        truncated_ids = token_ids[:max_tokens]
        return self.decode(truncated_ids)

    @property
    def vocab_size(self) -> int:
        """Get vocabulary size."""
        return self.backend.vocab_size()
