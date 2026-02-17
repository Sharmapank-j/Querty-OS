"""
Text Parser for Natural Language Command Processing

Extracts intents and entities from text input for command execution.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Common command intents."""

    UNKNOWN = "unknown"
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SYSTEM_CONTROL = "system_control"
    FILE_OPERATION = "file_operation"
    NETWORK_CONTROL = "network_control"
    QUERY = "query"
    AUTOMATION = "automation"
    SNAPSHOT = "snapshot"
    CONFIGURATION = "configuration"


@dataclass
class Entity:
    """Represents an extracted entity from text."""

    type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class ParsedCommand:
    """Represents a parsed command with intent and entities."""

    raw_text: str
    intent: Intent
    entities: List[Entity]
    confidence: float
    metadata: Dict[str, Any]

    def get_entity(self, entity_type: str) -> Optional[Entity]:
        """
        Get first entity of a specific type.

        Args:
            entity_type: Type of entity to retrieve

        Returns:
            Entity if found, None otherwise
        """
        for entity in self.entities:
            if entity.type == entity_type:
                return entity
        return None

    def get_entities(self, entity_type: str) -> List[Entity]:
        """
        Get all entities of a specific type.

        Args:
            entity_type: Type of entities to retrieve

        Returns:
            List of matching entities
        """
        return [e for e in self.entities if e.type == entity_type]


class TextParser:
    """
    Natural language command parser.

    Extracts intents and entities from text input using pattern matching
    and keyword analysis.
    """

    def __init__(self):
        """Initialize the text parser."""
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
        logger.info("Text parser initialized")

    def _build_intent_patterns(self) -> Dict[Intent, List[str]]:
        """
        Build intent recognition patterns.

        Returns:
            Dictionary mapping intents to keyword patterns
        """
        return {
            Intent.OPEN_APP: [
                r"\b(open|launch|start|run)\b.*\b(app|application|program)\b",
                r"\b(open|launch|start)\b\s+(\w+)",
            ],
            Intent.CLOSE_APP: [
                r"\b(close|stop|kill|terminate|exit)\b.*\b(app|application|program)\b",
                r"\b(close|stop|kill)\b\s+(\w+)",
            ],
            Intent.SYSTEM_CONTROL: [
                r"\b(shutdown|restart|reboot|sleep|hibernate)\b",
                r"\b(turn\s+off|power\s+off)\b.*\b(system|device|phone)\b",
            ],
            Intent.FILE_OPERATION: [
                r"\b(copy|move|delete|remove|rename)\b.*\b(file|folder|directory)\b",
                r"\b(create|make)\b.*\b(file|folder|directory)\b",
            ],
            Intent.NETWORK_CONTROL: [
                r"\b(enable|disable|turn\s+on|turn\s+off)\b.*\b(internet|wifi|network|data)\b",
                r"\b(connect|disconnect)\b.*\b(vpn|network)\b",
            ],
            Intent.SNAPSHOT: [
                r"\b(create|take|make)\b.*\b(snapshot|backup)\b",
                r"\b(restore|rollback)\b.*\b(snapshot|backup)\b",
            ],
            Intent.AUTOMATION: [
                r"\b(automate|schedule|run)\b.*\b(task|workflow|script)\b",
            ],
            Intent.QUERY: [
                r"\b(what|when|where|who|why|how|show|display|list|get)\b",
                r"\b(tell\s+me|show\s+me)\b",
            ],
            Intent.CONFIGURATION: [
                r"\b(configure|setup|set|change)\b.*\b(setting|config|option)\b",
            ],
        }

    def _build_entity_patterns(self) -> Dict[str, str]:
        """
        Build entity extraction patterns.

        Returns:
            Dictionary mapping entity types to regex patterns
        """
        return {
            "app_name": r"\b(chrome|firefox|gmail|whatsapp|telegram|spotify|youtube)\b",
            "file_path": r"(/[\w/.-]+|[A-Z]:\\[\w\\.-]+)",
            "network_interface": r"\b(wifi|wlan0|eth0|mobile|cellular)\b",
            "number": r"\b\d+\b",
            "time": r"\b\d{1,2}:\d{2}\b",
            "date": r"\b\d{4}-\d{2}-\d{2}\b",
        }

    def parse(self, text: str) -> ParsedCommand:
        """
        Parse text input into structured command.

        Args:
            text: Input text to parse

        Returns:
            ParsedCommand with extracted intent and entities
        """
        text = text.strip().lower()

        # Detect intent
        intent, intent_confidence = self._detect_intent(text)

        # Extract entities
        entities = self._extract_entities(text)

        # Build metadata
        metadata = {
            "word_count": len(text.split()),
            "char_count": len(text),
        }

        return ParsedCommand(
            raw_text=text,
            intent=intent,
            entities=entities,
            confidence=intent_confidence,
            metadata=metadata,
        )

    def _detect_intent(self, text: str) -> tuple[Intent, float]:
        """
        Detect intent from text.

        Args:
            text: Input text

        Returns:
            Tuple of (Intent, confidence score)
        """
        best_intent = Intent.UNKNOWN
        best_score = 0.0

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Simple scoring based on match length
                    score = len(match.group(0)) / len(text)
                    if score > best_score:
                        best_score = score
                        best_intent = intent

        # Default confidence for pattern matches
        confidence = 0.8 if best_intent != Intent.UNKNOWN else 0.3

        return best_intent, confidence

    def _extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities from text.

        Args:
            text: Input text

        Returns:
            List of extracted entities
        """
        entities = []

        for entity_type, pattern in self.entity_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = Entity(
                    type=entity_type,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,
                )
                entities.append(entity)

        return entities

    def parse_batch(self, texts: List[str]) -> List[ParsedCommand]:
        """
        Parse multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of parsed commands
        """
        return [self.parse(text) for text in texts]

    def add_intent_pattern(self, intent: Intent, pattern: str) -> None:
        """
        Add a custom intent pattern.

        Args:
            intent: Intent to add pattern for
            pattern: Regex pattern string
        """
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = []
        self.intent_patterns[intent].append(pattern)
        logger.info(f"Added pattern for intent {intent.value}: {pattern}")

    def add_entity_pattern(self, entity_type: str, pattern: str) -> None:
        """
        Add a custom entity pattern.

        Args:
            entity_type: Type of entity
            pattern: Regex pattern string
        """
        self.entity_patterns[entity_type] = pattern
        logger.info(f"Added pattern for entity {entity_type}: {pattern}")

    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intents.

        Returns:
            List of intent names
        """
        return [intent.value for intent in Intent]
