"""
VeroBrix Enhanced NLP Processor

Advanced natural language processing capabilities for legal document analysis
using spaCy, NLTK, and custom legal entity recognition.
"""

import re
import spacy
import nltk
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

from .config_manager import config
from .exceptions import AnalysisError, ConfigurationError
from .logger import get_logger, log_performance

logger = get_logger(__name__)

@dataclass
class LegalEntity:
    """Represents a legal entity found in text."""
    text: str
    label: str
    start: int
    end: int
    confidence: float
    context: str = ""

@dataclass
class ContradictionPair:
    """Represents a pair of contradictory statements."""
    statement1: str
    statement2: str
    confidence: float
    explanation: str
    location1: Tuple[int, int]
    location2: Tuple[int, int]

@dataclass
class LegalConcept:
    """Represents a legal concept identified in text."""
    concept: str
    category: str
    mentions: List[Tuple[int, int]]
    confidence: float
    related_terms: List[str]

class LegalNLPProcessor:
    """
    Enhanced NLP processor for legal document analysis.
    
    Provides advanced natural language processing capabilities including:
    - Legal entity extraction
    - Contradiction detection
    - Legal concept identification
    - Sentiment analysis
    - Clause extraction and classification
    """
    
    def __init__(self):
        """Initialize the NLP processor."""
        self.nlp = None
        self.legal_patterns = {}
        self.legal_entities = {}
        self.contradiction_patterns = []
        
        self._initialize_nlp()
        self._load_legal_patterns()
        self._load_contradiction_patterns()
    
    def _initialize_nlp(self) -> None:
        """Initialize spaCy NLP pipeline."""
        try:
            model_name = config.get('nlp.spacy_model', 'en_core_web_sm')
            logger.info(f"Loading spaCy model: {model_name}")
            
            self.nlp = spacy.load(model_name)
            
            # Add custom legal entity ruler if enabled
            if config.get('nlp.custom_legal_entities', True):
                self._add_legal_entity_ruler()
            
            logger.info("NLP processor initialized successfully")
            
        except OSError as e:
            error_msg = f"Failed to load spaCy model '{model_name}'. Please install it with: python -m spacy download {model_name}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg) from e
        except Exception as e:
            logger.error(f"Error initializing NLP processor: {e}")
            raise AnalysisError(f"NLP initialization failed: {e}") from e
    
    def _add_legal_entity_ruler(self) -> None:
        """Add custom legal entity recognition patterns."""
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
        
        # Legal entity patterns
        legal_patterns = [
            # Court types
            {"label": "COURT", "pattern": [{"LOWER": "supreme"}, {"LOWER": "court"}]},
            {"label": "COURT", "pattern": [{"LOWER": "district"}, {"LOWER": "court"}]},
            {"label": "COURT", "pattern": [{"LOWER": "circuit"}, {"LOWER": "court"}]},
            {"label": "COURT", "pattern": [{"LOWER": "appellate"}, {"LOWER": "court"}]},
            {"label": "COURT", "pattern": [{"LOWER": "municipal"}, {"LOWER": "court"}]},
            
            # Legal documents
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "summons"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "subpoena"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "warrant"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "citation"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "complaint"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "motion"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "brief"}]},
            {"label": "LEGAL_DOC", "pattern": [{"LOWER": "affidavit"}]},
            
            # Legal statuses
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "defendant"}]},
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "plaintiff"}]},
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "petitioner"}]},
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "respondent"}]},
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "appellant"}]},
            {"label": "LEGAL_STATUS", "pattern": [{"LOWER": "appellee"}]},
            
            # Legal concepts
            {"label": "LEGAL_CONCEPT", "pattern": [{"LOWER": "jurisdiction"}]},
            {"label": "LEGAL_CONCEPT", "pattern": [{"LOWER": "due"}, {"LOWER": "process"}]},
            {"label": "LEGAL_CONCEPT", "pattern": [{"LOWER": "constitutional"}, {"LOWER": "rights"}]},
            {"label": "LEGAL_CONCEPT", "pattern": [{"LOWER": "probable"}, {"LOWER": "cause"}]},
            {"label": "LEGAL_CONCEPT", "pattern": [{"LOWER": "reasonable"}, {"LOWER": "suspicion"}]},
            
            # Jurisdictional terms
            {"label": "JURISDICTION", "pattern": [{"LOWER": "federal"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "state"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "municipal"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "county"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "administrative"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "commercial"}]},
        ]
        
        ruler.add_patterns(legal_patterns)
        logger.debug(f"Added {len(legal_patterns)} legal entity patterns")
    
    def _load_legal_patterns(self) -> None:
        """Load legal concept patterns for analysis."""
        self.legal_patterns = {
            'contract_terms': [
                r'\b(?:shall|must|will|agree[sd]?|covenant[sd]?|undertake[sd]?)\b',
                r'\b(?:obligation|duty|responsibility|requirement)\b',
                r'\b(?:breach|default|violation|non-compliance)\b'
            ],
            'rights_and_powers': [
                r'\b(?:right|power|authority|privilege|immunity)\b',
                r'\b(?:entitled|authorized|empowered|permitted)\b',
                r'\b(?:constitutional|statutory|legal|lawful)\b'
            ],
            'temporal_terms': [
                r'\b(?:immediately|forthwith|within \d+|by \w+day|upon)\b',
                r'\b(?:deadline|due date|expiration|termination)\b',
                r'\b(?:effective|commence|begin|start|end)\b'
            ],
            'monetary_terms': [
                r'\$[\d,]+(?:\.\d{2})?',
                r'\b(?:fee|fine|penalty|damages|compensation)\b',
                r'\b(?:payment|remuneration|consideration|settlement)\b'
            ],
            'jurisdictional_terms': [
                r'\b(?:federal|state|local|municipal|county|city)\b',
                r'\b(?:court|tribunal|agency|department|commission)\b',
                r'\b(?:jurisdiction|venue|forum|authority)\b'
            ]
        }
    
    def _load_contradiction_patterns(self) -> None:
        """Load patterns for detecting contradictions."""
        self.contradiction_patterns = [
            # Direct negation patterns
            (r'\b(shall|must|will|required?)\b', r'\b(shall not|must not|will not|not required|prohibited|forbidden)\b'),
            (r'\b(mandatory|compulsory|obligatory)\b', r'\b(optional|voluntary|discretionary)\b'),
            (r'\b(always|invariably|without exception)\b', r'\b(never|sometimes|may|might|could)\b'),
            (r'\b(all|every|each)\b', r'\b(none|no|not any)\b'),
            (r'\b(include[sd]?|contain[sd]?)\b', r'\b(exclude[sd]?|omit[sd]?|not include)\b'),
            (r'\b(permit[sd]?|allow[sd]?|authorize[sd]?)\b', r'\b(prohibit[sd]?|forbid[sd]?|ban[sd]?)\b'),
            
            # Temporal contradictions
            (r'\b(before|prior to|preceding)\b', r'\b(after|following|subsequent to)\b'),
            (r'\b(immediate|instant|forthwith)\b', r'\b(delayed|postponed|deferred)\b'),
            
            # Quantitative contradictions
            (r'\b(maximum|at most|no more than)\b', r'\b(minimum|at least|no less than)\b'),
            (r'\b(increase|raise|elevate)\b', r'\b(decrease|lower|reduce)\b'),
        ]
    
    @log_performance("legal_entity_extraction")
    def extract_legal_entities(self, text: str) -> List[LegalEntity]:
        """
        Extract legal entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of legal entities found
        """
        if not self.nlp:
            raise AnalysisError("NLP processor not initialized")
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                # Get context around the entity
                start_idx = max(0, ent.start - 5)
                end_idx = min(len(doc), ent.end + 5)
                context = doc[start_idx:end_idx].text
                
                entity = LegalEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0,  # spaCy doesn't provide confidence scores by default
                    context=context
                )
                entities.append(entity)
            
            logger.debug(f"Extracted {len(entities)} legal entities")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting legal entities: {e}")
            raise AnalysisError(f"Legal entity extraction failed: {e}") from e
    
    @log_performance("contradiction_detection")
    def detect_contradictions(self, text: str) -> List[ContradictionPair]:
        """
        Detect contradictions in legal text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of contradiction pairs found
        """
        contradictions = []
        sentences = self._split_into_sentences(text)
        
        try:
            # Check for pattern-based contradictions
            for i, sent1 in enumerate(sentences):
                for j, sent2 in enumerate(sentences[i+1:], i+1):
                    contradiction = self._check_sentence_contradiction(sent1, sent2, text)
                    if contradiction:
                        contradictions.append(contradiction)
            
            # Check for semantic contradictions using spaCy
            if config.get('nlp.enable_contradiction_detection', True):
                semantic_contradictions = self._detect_semantic_contradictions(sentences, text)
                contradictions.extend(semantic_contradictions)
            
            logger.debug(f"Detected {len(contradictions)} contradictions")
            return contradictions
            
        except Exception as e:
            logger.error(f"Error detecting contradictions: {e}")
            raise AnalysisError(f"Contradiction detection failed: {e}") from e
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _check_sentence_contradiction(self, sent1: str, sent2: str, full_text: str) -> Optional[ContradictionPair]:
        """Check if two sentences contradict each other."""
        for pattern1, pattern2 in self.contradiction_patterns:
            match1 = re.search(pattern1, sent1, re.IGNORECASE)
            match2 = re.search(pattern2, sent2, re.IGNORECASE)
            
            if match1 and match2:
                # Calculate positions in full text
                pos1 = full_text.find(sent1)
                pos2 = full_text.find(sent2)
                
                if pos1 != -1 and pos2 != -1:
                    confidence = 0.8  # Pattern-based contradictions have high confidence
                    explanation = f"Contradictory patterns detected: '{match1.group()}' vs '{match2.group()}'"
                    
                    return ContradictionPair(
                        statement1=sent1,
                        statement2=sent2,
                        confidence=confidence,
                        explanation=explanation,
                        location1=(pos1, pos1 + len(sent1)),
                        location2=(pos2, pos2 + len(sent2))
                    )
        
        return None
    
    def _detect_semantic_contradictions(self, sentences: List[str], full_text: str) -> List[ContradictionPair]:
        """Detect semantic contradictions using spaCy similarity."""
        contradictions = []
        
        if not self.nlp or not self.nlp.has_pipe('tok2vec'):
            return contradictions
        
        try:
            # Process sentences with spaCy
            docs = [self.nlp(sent) for sent in sentences]
            
            # Look for sentences with high similarity but opposite sentiment
            for i, doc1 in enumerate(docs):
                for j, doc2 in enumerate(docs[i+1:], i+1):
                    similarity = doc1.similarity(doc2)
                    
                    # High similarity but potential contradiction
                    if similarity > 0.7:
                        # Check for negation patterns
                        if self._has_negation_difference(doc1, doc2):
                            pos1 = full_text.find(sentences[i])
                            pos2 = full_text.find(sentences[j])
                            
                            if pos1 != -1 and pos2 != -1:
                                contradiction = ContradictionPair(
                                    statement1=sentences[i],
                                    statement2=sentences[j],
                                    confidence=similarity * 0.6,  # Lower confidence for semantic
                                    explanation="Semantic contradiction detected through similarity analysis",
                                    location1=(pos1, pos1 + len(sentences[i])),
                                    location2=(pos2, pos2 + len(sentences[j]))
                                )
                                contradictions.append(contradiction)
            
        except Exception as e:
            logger.warning(f"Semantic contradiction detection failed: {e}")
        
        return contradictions
    
    def _has_negation_difference(self, doc1, doc2) -> bool:
        """Check if two documents have different negation patterns."""
        negation_words = {'not', 'no', 'never', 'none', 'nothing', 'neither', 'nor'}
        
        neg1 = any(token.text.lower() in negation_words for token in doc1)
        neg2 = any(token.text.lower() in negation_words for token in doc2)
        
        return neg1 != neg2  # One has negation, the other doesn't
    
    @log_performance("legal_concept_identification")
    def identify_legal_concepts(self, text: str) -> List[LegalConcept]:
        """
        Identify legal concepts in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of legal concepts found
        """
        concepts = []
        
        try:
            for category, patterns in self.legal_patterns.items():
                concept_mentions = defaultdict(list)
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        concept_text = match.group().lower()
                        concept_mentions[concept_text].append((match.start(), match.end()))
                
                # Create LegalConcept objects
                for concept_text, mentions in concept_mentions.items():
                    concept = LegalConcept(
                        concept=concept_text,
                        category=category,
                        mentions=mentions,
                        confidence=min(1.0, len(mentions) * 0.2),  # More mentions = higher confidence
                        related_terms=self._find_related_terms(concept_text, text)
                    )
                    concepts.append(concept)
            
            logger.debug(f"Identified {len(concepts)} legal concepts")
            return concepts
            
        except Exception as e:
            logger.error(f"Error identifying legal concepts: {e}")
            raise AnalysisError(f"Legal concept identification failed: {e}") from e
    
    def _find_related_terms(self, concept: str, text: str) -> List[str]:
        """Find terms related to a legal concept."""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            concept_token = self.nlp(concept)
            
            related_terms = []
            for token in doc:
                if token.text.lower() != concept and token.similarity(concept_token[0]) > 0.6:
                    related_terms.append(token.text.lower())
            
            # Return top 5 most similar terms
            return list(set(related_terms))[:5]
            
        except Exception:
            return []
    
    @log_performance("sentiment_analysis")
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of legal text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            if not self.nlp:
                raise AnalysisError("NLP processor not initialized")
            
            doc = self.nlp(text)
            
            # Basic sentiment analysis using spaCy
            # Note: This is a simplified approach; for production, consider using
            # specialized legal sentiment models
            
            positive_words = {'agree', 'consent', 'approve', 'accept', 'comply', 'honor', 'respect'}
            negative_words = {'deny', 'refuse', 'reject', 'violate', 'breach', 'default', 'fail'}
            legal_concern_words = {'liable', 'penalty', 'fine', 'damages', 'violation', 'breach'}
            
            word_counts = Counter(token.text.lower() for token in doc if token.is_alpha)
            
            positive_score = sum(word_counts.get(word, 0) for word in positive_words)
            negative_score = sum(word_counts.get(word, 0) for word in negative_words)
            concern_score = sum(word_counts.get(word, 0) for word in legal_concern_words)
            
            total_words = len([token for token in doc if token.is_alpha])
            
            if total_words == 0:
                return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}}
            
            # Normalize scores
            positive_ratio = positive_score / total_words
            negative_ratio = negative_score / total_words
            concern_ratio = concern_score / total_words
            
            # Determine overall sentiment
            if concern_ratio > 0.02:  # High legal concern threshold
                sentiment = 'concerning'
                confidence = min(1.0, concern_ratio * 10)
            elif positive_ratio > negative_ratio * 1.5:
                sentiment = 'positive'
                confidence = min(1.0, positive_ratio * 10)
            elif negative_ratio > positive_ratio * 1.5:
                sentiment = 'negative'
                confidence = min(1.0, negative_ratio * 10)
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'positive': positive_ratio,
                    'negative': negative_ratio,
                    'concern': concern_ratio
                },
                'word_counts': {
                    'positive_words': positive_score,
                    'negative_words': negative_score,
                    'concern_words': concern_score,
                    'total_words': total_words
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise AnalysisError(f"Sentiment analysis failed: {e}") from e
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract and classify legal clauses from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted clauses with classifications
        """
        try:
            if not self.nlp:
                raise AnalysisError("NLP processor not initialized")
            
            doc = self.nlp(text)
            clauses = []
            
            # Split text into sentences and analyze each
            for sent in doc.sents:
                clause_text = sent.text.strip()
                if len(clause_text) < 10:  # Skip very short sentences
                    continue
                
                clause_type = self._classify_clause(clause_text)
                importance = self._assess_clause_importance(clause_text)
                
                clause = {
                    'text': clause_text,
                    'type': clause_type,
                    'importance': importance,
                    'start': sent.start_char,
                    'end': sent.end_char,
                    'entities': [ent.text for ent in sent.ents],
                    'key_terms': self._extract_key_terms(sent)
                }
                clauses.append(clause)
            
            logger.debug(f"Extracted {len(clauses)} clauses")
            return clauses
            
        except Exception as e:
            logger.error(f"Error extracting clauses: {e}")
            raise AnalysisError(f"Clause extraction failed: {e}") from e
    
    def _classify_clause(self, clause_text: str) -> str:
        """Classify a legal clause by type."""
        clause_lower = clause_text.lower()
        
        # Classification patterns - order matters for priority
        # Check for penalty-related phrases first
        if re.search(r'\b(penalty|fine|damages|liable|breach|default)\b', clause_lower) or \
           re.search(r'(result in penalties|face penalties|penalties including)', clause_lower):
            return 'penalty'
        elif re.search(r'\b(if|when|upon|in the event|provided that)\b', clause_lower):
            return 'conditional'
        elif re.search(r'\b(effective|commence|terminate|expire)\b', clause_lower):
            return 'temporal'
        elif re.search(r'\b(right|entitled|privilege|immunity)\b', clause_lower):
            return 'rights'
        elif re.search(r'\b(definition|means|refers to|includes)\b', clause_lower):
            return 'definition'
        elif re.search(r'\b(shall|must|required|mandatory|obligation)\b', clause_lower):
            return 'obligation'
        elif re.search(r'\b(may|can|permitted|allowed|discretion)\b', clause_lower):
            return 'permission'
        else:
            return 'general'
    
    def _assess_clause_importance(self, clause_text: str) -> str:
        """Assess the importance level of a clause."""
        clause_lower = clause_text.lower()
        
        # High importance indicators
        high_importance_terms = [
            'constitutional', 'fundamental', 'essential', 'critical', 'mandatory',
            'shall', 'must', 'required', 'penalty', 'fine', 'damages', 'liable',
            'breach', 'default', 'violation', 'jurisdiction', 'court', 'legal'
        ]
        
        # Medium importance indicators
        medium_importance_terms = [
            'should', 'ought', 'recommended', 'advisable', 'appropriate',
            'reasonable', 'proper', 'suitable', 'necessary'
        ]
        
        high_count = sum(1 for term in high_importance_terms if term in clause_lower)
        medium_count = sum(1 for term in medium_importance_terms if term in clause_lower)
        
        # Check for penalty-related phrases that should be high importance
        penalty_phrases = ['face penalties', 'result in penalties', 'penalties including']
        has_penalty_phrase = any(phrase in clause_lower for phrase in penalty_phrases)
        
        if high_count >= 2 or has_penalty_phrase:
            return 'high'
        elif high_count >= 1 or medium_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _extract_key_terms(self, sent) -> List[str]:
        """Extract key terms from a sentence."""
        key_terms = []
        
        for token in sent:
            # Include important legal terms, proper nouns, and significant words
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                len(token.text) > 3 and 
                not token.is_stop and 
                token.is_alpha):
                key_terms.append(token.text.lower())
        
        return list(set(key_terms))[:10]  # Return top 10 unique key terms

# Global NLP processor instance
_nlp_processor: Optional[LegalNLPProcessor] = None

def get_nlp_processor() -> LegalNLPProcessor:
    """Get or create the global NLP processor instance."""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = LegalNLPProcessor()
    return _nlp_processor

def initialize_nlp() -> None:
    """Initialize the NLP processor."""
    global _nlp_processor
    _nlp_processor = LegalNLPProcessor()
    logger.info("NLP processor initialized")
