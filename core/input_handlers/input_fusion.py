"""
Input Fusion for Multi-Modal Input Processing

Combines results from different input handlers (voice, text, camera) into unified output.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InputModality(Enum):
    """Input modality types."""

    TEXT = "text"
    VOICE = "voice"
    CAMERA = "camera"
    GESTURE = "gesture"
    SENSOR = "sensor"


class FusionStrategy(Enum):
    """Strategies for combining multi-modal inputs."""

    WEIGHTED_AVERAGE = "weighted_average"  # Average confidence scores with weights
    HIGHEST_CONFIDENCE = "highest_confidence"  # Pick result with highest confidence
    CONSENSUS = "consensus"  # Require agreement from multiple modalities
    SEQUENTIAL = "sequential"  # Process in order, use first successful result


@dataclass
class InputResult:
    """Result from a single input handler."""

    modality: InputModality
    data: Any
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "modality": self.modality.value,
            "data": self.data,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class FusedResult:
    """Combined result from multiple input modalities."""

    primary_modality: InputModality
    data: Any
    confidence: float
    contributing_modalities: List[InputModality]
    fusion_strategy: FusionStrategy
    timestamp: datetime = field(default_factory=datetime.now)
    individual_results: List[InputResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "primary_modality": self.primary_modality.value,
            "data": self.data,
            "confidence": self.confidence,
            "contributing_modalities": [m.value for m in self.contributing_modalities],
            "fusion_strategy": self.fusion_strategy.value,
            "timestamp": self.timestamp.isoformat(),
            "individual_results": [r.to_dict() for r in self.individual_results],
        }


class InputFusion:
    """
    Multi-modal input fusion that combines results from different input handlers.

    Supports various fusion strategies to intelligently combine inputs from
    text, voice, camera, and other modalities.
    """

    def __init__(self, default_strategy: FusionStrategy = FusionStrategy.HIGHEST_CONFIDENCE):
        """
        Initialize input fusion.

        Args:
            default_strategy: Default fusion strategy to use
        """
        self.default_strategy = default_strategy
        self.modality_weights = {
            InputModality.TEXT: 1.0,
            InputModality.VOICE: 0.9,
            InputModality.CAMERA: 0.8,
            InputModality.GESTURE: 0.7,
            InputModality.SENSOR: 0.6,
        }
        self.min_confidence_threshold = 0.3
        logger.info(f"Input fusion initialized with strategy: {default_strategy.value}")

    def set_modality_weight(self, modality: InputModality, weight: float) -> None:
        """
        Set weight for a specific modality.

        Args:
            modality: Input modality
            weight: Weight value (0.0 to 1.0)
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        self.modality_weights[modality] = weight
        logger.debug(f"Set weight for {modality.value}: {weight}")

    def fuse(
        self,
        results: List[InputResult],
        strategy: Optional[FusionStrategy] = None,
    ) -> Optional[FusedResult]:
        """
        Fuse multiple input results into a single output.

        Args:
            results: List of input results from different modalities
            strategy: Fusion strategy to use (defaults to instance default)

        Returns:
            Fused result, or None if fusion failed
        """
        if not results:
            logger.warning("No results to fuse")
            return None

        # Filter out low-confidence results
        filtered_results = [r for r in results if r.confidence >= self.min_confidence_threshold]

        if not filtered_results:
            logger.warning("All results below confidence threshold")
            return None

        strategy = strategy or self.default_strategy

        if strategy == FusionStrategy.HIGHEST_CONFIDENCE:
            return self._fuse_highest_confidence(filtered_results)
        elif strategy == FusionStrategy.WEIGHTED_AVERAGE:
            return self._fuse_weighted_average(filtered_results)
        elif strategy == FusionStrategy.CONSENSUS:
            return self._fuse_consensus(filtered_results)
        elif strategy == FusionStrategy.SEQUENTIAL:
            return self._fuse_sequential(filtered_results)
        else:
            logger.error(f"Unknown fusion strategy: {strategy}")
            return None

    def _fuse_highest_confidence(self, results: List[InputResult]) -> FusedResult:
        """
        Fuse by selecting result with highest confidence.

        Args:
            results: Input results

        Returns:
            Fused result
        """
        best_result = max(results, key=lambda r: r.confidence)

        return FusedResult(
            primary_modality=best_result.modality,
            data=best_result.data,
            confidence=best_result.confidence,
            contributing_modalities=[r.modality for r in results],
            fusion_strategy=FusionStrategy.HIGHEST_CONFIDENCE,
            individual_results=results,
        )

    def _fuse_weighted_average(self, results: List[InputResult]) -> FusedResult:
        """
        Fuse by weighted average of confidences.

        Args:
            results: Input results

        Returns:
            Fused result
        """
        # Calculate weighted confidence
        total_weight = 0.0
        weighted_confidence = 0.0

        for result in results:
            weight = self.modality_weights.get(result.modality, 1.0)
            weighted_confidence += result.confidence * weight
            total_weight += weight

        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0

        # Use the result with highest base confidence as primary data
        primary_result = max(results, key=lambda r: r.confidence)

        return FusedResult(
            primary_modality=primary_result.modality,
            data=primary_result.data,
            confidence=avg_confidence,
            contributing_modalities=[r.modality for r in results],
            fusion_strategy=FusionStrategy.WEIGHTED_AVERAGE,
            individual_results=results,
        )

    def _fuse_consensus(self, results: List[InputResult]) -> Optional[FusedResult]:
        """
        Fuse by requiring consensus (agreement) from multiple modalities.

        Args:
            results: Input results

        Returns:
            Fused result if consensus reached, None otherwise
        """
        # Simple consensus: at least 2 modalities with similar high confidence
        high_confidence_results = [r for r in results if r.confidence >= 0.7]

        if len(high_confidence_results) < 2:
            logger.warning("Consensus not reached (need at least 2 high-confidence results)")
            return None

        # Use highest confidence result as primary
        primary_result = max(high_confidence_results, key=lambda r: r.confidence)

        # Average the high-confidence results
        avg_confidence = sum(r.confidence for r in high_confidence_results) / len(
            high_confidence_results
        )

        return FusedResult(
            primary_modality=primary_result.modality,
            data=primary_result.data,
            confidence=avg_confidence,
            contributing_modalities=[r.modality for r in high_confidence_results],
            fusion_strategy=FusionStrategy.CONSENSUS,
            individual_results=results,
        )

    def _fuse_sequential(self, results: List[InputResult]) -> FusedResult:
        """
        Fuse by processing sequentially and using first successful result.

        Args:
            results: Input results (should be ordered by priority)

        Returns:
            Fused result
        """
        # Sort by confidence (highest first)
        sorted_results = sorted(results, key=lambda r: r.confidence, reverse=True)

        # Use first result above threshold
        primary_result = sorted_results[0]

        return FusedResult(
            primary_modality=primary_result.modality,
            data=primary_result.data,
            confidence=primary_result.confidence,
            contributing_modalities=[primary_result.modality],
            fusion_strategy=FusionStrategy.SEQUENTIAL,
            individual_results=results,
        )

    def combine_text_and_voice(
        self, text_result: InputResult, voice_result: InputResult
    ) -> FusedResult:
        """
        Specialized fusion for text and voice inputs.

        Args:
            text_result: Text input result
            voice_result: Voice input result

        Returns:
            Fused result
        """
        # Voice typically has priority for spoken commands
        if voice_result.confidence > text_result.confidence:
            primary = voice_result
            confidence = voice_result.confidence * 0.7 + text_result.confidence * 0.3
        else:
            primary = text_result
            confidence = text_result.confidence * 0.7 + voice_result.confidence * 0.3

        return FusedResult(
            primary_modality=primary.modality,
            data=primary.data,
            confidence=confidence,
            contributing_modalities=[InputModality.TEXT, InputModality.VOICE],
            fusion_strategy=FusionStrategy.WEIGHTED_AVERAGE,
            individual_results=[text_result, voice_result],
        )

    def combine_with_context(
        self,
        results: List[InputResult],
        context: Dict[str, Any],
    ) -> Optional[FusedResult]:
        """
        Fuse results with additional context information.

        Args:
            results: Input results
            context: Context information (e.g., time, location, user preferences)

        Returns:
            Context-aware fused result
        """
        # Adjust confidences based on context
        adjusted_results = []
        for result in results:
            # Example: boost voice confidence during specific times
            if context.get("time_of_day") == "night" and result.modality == InputModality.VOICE:
                adjusted_confidence = min(1.0, result.confidence * 1.1)
            else:
                adjusted_confidence = result.confidence

            adjusted_result = InputResult(
                modality=result.modality,
                data=result.data,
                confidence=adjusted_confidence,
                timestamp=result.timestamp,
                metadata={**result.metadata, "context": context},
            )
            adjusted_results.append(adjusted_result)

        return self.fuse(adjusted_results)
