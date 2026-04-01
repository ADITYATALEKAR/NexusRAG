"""Rule-based query classifier for routing."""

from __future__ import annotations

from datetime import datetime, timezone
import re

from src.layer1_contracts.schemas.query import QueryType
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis, QueryComplexity
from src.layer2_domain.query_understanding.entity_extractor import EntityExtractor
from src.layer2_domain.query_understanding.intent_detector import IntentDetector
from src.layer2_domain.query_understanding.query_expander import QueryExpander


class QueryClassifier:
    """Classify queries into bounded route-friendly categories."""

    COMPARATIVE_PATTERNS = [
        r"\bvs\.?\b",
        r"\bversus\b",
        r"\bcompare\b",
        r"\bcomparison\b",
        r"\bdifference between\b",
        r"\bbetter than\b",
        r"\bworse than\b",
        r"\badvantages of .+ over\b",
        r"\bpros and cons\b",
    ]
    STRUCTURED_PATTERNS = [
        r"\bhow many\b",
        r"\bhow much\b",
        r"\btotal\b",
        r"\baverage\b",
        r"\bsum of\b",
        r"\bcount\b",
        r"\blist all\b",
        r"\bshow me all\b",
        r"\bwhat is the .+ of\b",
        r"\bwhat are the .+ for\b",
    ]
    MULTI_HOP_PATTERNS = [
        r"\band then\b",
        r"\bafter that\b",
        r"\bbased on that\b",
        r"\bwho .+ that .+\b",
        r"\bwhat .+ of the .+ that\b",
        r"\bwhose .+ is\b",
    ]
    KEYWORD_HEAVY_PATTERNS = [
        r'^"[^"]+"$',
        r"\b[A-Z]{2,}\b",
        r"\b\d{4,}\b",
        r"error:?\s*\w+",
        r"code:?\s*\w+",
    ]
    SEMANTIC_PATTERNS = [
        r"\bexplain\b",
        r"\bdescribe\b",
        r"\boverview\b",
        r"\bconcept\b",
        r"\bwhy\b",
        r"\bhow does\b",
    ]

    def __init__(
        self,
        entity_extractor: EntityExtractor | None = None,
        intent_detector: IntentDetector | None = None,
        query_expander: QueryExpander | None = None,
    ) -> None:
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.intent_detector = intent_detector or IntentDetector()
        self.query_expander = query_expander or QueryExpander()

    def classify(self, query_text: str) -> QueryAnalysis:
        """Return a routing-oriented analysis for the supplied query text."""
        start = datetime.now(timezone.utc)
        cleaned = self._clean_query(query_text)
        query_type, confidence = self._detect_query_type(cleaned)
        intent = self.intent_detector.detect(cleaned)
        complexity = self._detect_complexity(cleaned, query_type)
        entities = self.entity_extractor.extract(cleaned)
        keywords = self.query_expander.expand_keywords(cleaned)
        requires_decomposition = query_type in (QueryType.COMPARATIVE, QueryType.MULTI_HOP)
        sub_queries = self._generate_sub_queries(cleaned, query_type) if requires_decomposition else []
        elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

        return QueryAnalysis(
            query_id="",
            original_text=query_text,
            cleaned_text=cleaned,
            query_type=query_type,
            intent=intent,
            complexity=complexity,
            entities=entities,
            keywords=keywords,
            requires_structured=query_type == QueryType.STRUCTURED,
            requires_decomposition=requires_decomposition,
            sub_queries=sub_queries,
            confidence=confidence,
            analysis_time_ms=elapsed,
        )

    def _clean_query(self, text: str) -> str:
        return " ".join(text.split())

    def _detect_query_type(self, text: str) -> tuple[QueryType, float]:
        text_lower = text.lower()

        for pattern in self.COMPARATIVE_PATTERNS:
            if re.search(pattern, text_lower):
                return QueryType.COMPARATIVE, 0.85
        for pattern in self.STRUCTURED_PATTERNS:
            if re.search(pattern, text_lower):
                return QueryType.STRUCTURED, 0.8
        for pattern in self.MULTI_HOP_PATTERNS:
            if re.search(pattern, text_lower):
                return QueryType.MULTI_HOP, 0.78
        for pattern in self.KEYWORD_HEAVY_PATTERNS:
            if re.search(pattern, text):
                return QueryType.KEYWORD, 0.82
        for pattern in self.SEMANTIC_PATTERNS:
            if re.search(pattern, text_lower):
                return QueryType.SEMANTIC, 0.76
        return QueryType.HYBRID, 0.7

    def _detect_complexity(self, text: str, query_type: QueryType) -> QueryComplexity:
        word_count = len(text.split())
        if query_type in (QueryType.COMPARATIVE, QueryType.MULTI_HOP):
            return QueryComplexity.COMPLEX
        if query_type == QueryType.STRUCTURED:
            return QueryComplexity.STRUCTURED
        if word_count > 20 or " and " in text.lower():
            return QueryComplexity.MODERATE
        return QueryComplexity.SIMPLE

    def _generate_sub_queries(self, text: str, query_type: QueryType) -> list[str]:
        if query_type == QueryType.COMPARATIVE:
            match = re.search(r"(.+?)\s+(?:vs\.?|versus|compared to|or)\s+(.+)", text, re.IGNORECASE)
            if match:
                entity1, entity2 = match.groups()
                return [
                    f"What is {entity1.strip()}?",
                    f"What is {entity2.strip()}?",
                    f"Key differences between {entity1.strip()} and {entity2.strip()}",
                ]
        if query_type == QueryType.MULTI_HOP:
            return [text]
        return []
