"""
Comprehensive tests for the VeroBrix NLP Processor.

Tests all major functionality including entity extraction, contradiction detection,
legal concept identification, sentiment analysis, and clause extraction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import spacy
from typing import List

from modules.nlp_processor import (
    LegalNLPProcessor,
    LegalEntity,
    ContradictionPair,
    LegalConcept,
    get_nlp_processor,
    initialize_nlp
)
from modules.exceptions import AnalysisError, ConfigurationError


class TestLegalNLPProcessor:
    """Test suite for LegalNLPProcessor class."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        with patch('modules.nlp_processor.config') as mock:
            mock.get.side_effect = lambda key, default=None: {
                'nlp.spacy_model': 'en_core_web_sm',
                'nlp.custom_legal_entities': True,
                'nlp.enable_contradiction_detection': True
            }.get(key, default)
            yield mock
    
    @pytest.fixture
    def mock_nlp_model(self):
        """Mock spaCy NLP model."""
        mock_nlp = MagicMock()
        mock_nlp.pipe_names = []
        mock_nlp.has_pipe.return_value = True
        
        # Mock entity ruler
        mock_ruler = MagicMock()
        mock_nlp.add_pipe.return_value = mock_ruler
        mock_nlp.get_pipe.return_value = mock_ruler
        
        return mock_nlp
    
    @pytest.fixture
    def processor(self, mock_config, mock_nlp_model):
        """Create a test NLP processor instance."""
        with patch('spacy.load', return_value=mock_nlp_model):
            processor = LegalNLPProcessor()
            return processor
    
    def test_initialization_success(self, mock_config, mock_nlp_model):
        """Test successful initialization of NLP processor."""
        with patch('spacy.load', return_value=mock_nlp_model):
            processor = LegalNLPProcessor()
            assert processor.nlp is not None
            assert processor.legal_patterns is not None
            assert processor.contradiction_patterns is not None
    
    def test_initialization_model_not_found(self, mock_config):
        """Test initialization failure when spaCy model is not found."""
        with patch('spacy.load', side_effect=OSError("Model not found")):
            with pytest.raises(ConfigurationError) as exc_info:
                LegalNLPProcessor()
            assert "Failed to load spaCy model" in str(exc_info.value)
    
    def test_initialization_general_error(self, mock_config):
        """Test initialization failure with general error."""
        with patch('spacy.load', side_effect=Exception("Unknown error")):
            with pytest.raises(AnalysisError) as exc_info:
                LegalNLPProcessor()
            assert "NLP initialization failed" in str(exc_info.value)
    
    def test_extract_legal_entities(self, processor):
        """Test legal entity extraction."""
        # Mock document and entities
        mock_doc = MagicMock()
        mock_entity = MagicMock()
        mock_entity.text = "Supreme Court"
        mock_entity.label_ = "COURT"
        mock_entity.start_char = 0
        mock_entity.end_char = 13
        mock_entity.start = 0
        mock_entity.end = 2
        
        mock_doc.ents = [mock_entity]
        mock_doc.__len__.return_value = 10
        mock_doc.__getitem__.return_value.text = "The Supreme Court ruled today"
        
        processor.nlp.return_value = mock_doc
        
        text = "The Supreme Court ruled today on the case."
        entities = processor.extract_legal_entities(text)
        
        assert len(entities) == 1
        assert entities[0].text == "Supreme Court"
        assert entities[0].label == "COURT"
        assert entities[0].start == 0
        assert entities[0].end == 13
    
    def test_extract_legal_entities_no_nlp(self):
        """Test entity extraction when NLP is not initialized."""
        processor = LegalNLPProcessor()
        processor.nlp = None
        
        with pytest.raises(AnalysisError) as exc_info:
            processor.extract_legal_entities("Test text")
        assert "NLP processor not initialized" in str(exc_info.value)
    
    def test_detect_contradictions_pattern_based(self, processor):
        """Test pattern-based contradiction detection."""
        text = "The defendant shall appear in court. The defendant shall not appear in court."
        
        # Mock sentence splitting
        processor.nlp.return_value.sents = [
            Mock(text="The defendant shall appear in court."),
            Mock(text="The defendant shall not appear in court.")
        ]
        
        contradictions = processor.detect_contradictions(text)
        
        # Should detect at least one contradiction
        assert len(contradictions) > 0
        if contradictions:
            assert "shall" in contradictions[0].statement1.lower()
            assert "shall not" in contradictions[0].statement2.lower()
    
    def test_detect_contradictions_temporal(self, processor):
        """Test temporal contradiction detection."""
        text = "The payment is due before January 1st. The payment is due after January 1st."
        
        processor.nlp.return_value.sents = [
            Mock(text="The payment is due before January 1st."),
            Mock(text="The payment is due after January 1st.")
        ]
        
        contradictions = processor.detect_contradictions(text)
        
        assert len(contradictions) > 0
        if contradictions:
            assert "before" in contradictions[0].statement1.lower()
            assert "after" in contradictions[0].statement2.lower()
    
    def test_identify_legal_concepts(self, processor):
        """Test legal concept identification."""
        text = "The court has jurisdiction over this matter. The defendant must pay damages."
        
        concepts = processor.identify_legal_concepts(text)
        
        assert len(concepts) > 0
        
        # Check for expected concepts
        concept_texts = [c.concept for c in concepts]
        assert any("jurisdiction" in c for c in concept_texts)
        assert any("damages" in c for c in concept_texts)
        
        # Check categories
        categories = [c.category for c in concepts]
        assert any(cat in ['jurisdictional_terms', 'monetary_terms'] for cat in categories)
    
    def test_analyze_sentiment_positive(self, processor):
        """Test sentiment analysis for positive text."""
        mock_doc = MagicMock()
        mock_tokens = [
            Mock(text="agree", is_alpha=True),
            Mock(text="consent", is_alpha=True),
            Mock(text="approve", is_alpha=True),
            Mock(text="the", is_alpha=True),
            Mock(text="terms", is_alpha=True)
        ]
        mock_doc.__iter__.return_value = mock_tokens
        processor.nlp.return_value = mock_doc
        
        text = "The parties agree and consent to approve the terms."
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] in ['positive', 'neutral']
        assert 'confidence' in result
        assert 'scores' in result
        assert result['scores']['positive'] > 0
    
    def test_analyze_sentiment_negative(self, processor):
        """Test sentiment analysis for negative text."""
        mock_doc = MagicMock()
        mock_tokens = [
            Mock(text="deny", is_alpha=True),
            Mock(text="refuse", is_alpha=True),
            Mock(text="reject", is_alpha=True),
            Mock(text="the", is_alpha=True),
            Mock(text="claim", is_alpha=True)
        ]
        mock_doc.__iter__.return_value = mock_tokens
        processor.nlp.return_value = mock_doc
        
        text = "We deny, refuse, and reject the claim."
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] in ['negative', 'neutral']
        assert result['scores']['negative'] > 0
    
    def test_analyze_sentiment_concerning(self, processor):
        """Test sentiment analysis for concerning legal text."""
        mock_doc = MagicMock()
        mock_tokens = [
            Mock(text="liable", is_alpha=True),
            Mock(text="penalty", is_alpha=True),
            Mock(text="damages", is_alpha=True),
            Mock(text="breach", is_alpha=True),
            Mock(text="violation", is_alpha=True)
        ]
        mock_doc.__iter__.return_value = mock_tokens
        processor.nlp.return_value = mock_doc
        
        text = "You may be liable for penalty and damages due to breach and violation."
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] == 'concerning'
        assert result['scores']['concern'] > 0
    
    def test_extract_clauses(self, processor):
        """Test clause extraction and classification."""
        mock_doc = MagicMock()
        
        # Mock sentences
        mock_sent1 = MagicMock()
        mock_sent1.text = "The defendant shall appear in court on the specified date."
        mock_sent1.start_char = 0
        mock_sent1.end_char = 58
        mock_sent1.ents = []
        mock_sent1.__iter__.return_value = [
            Mock(text="defendant", pos_="NOUN", is_stop=False, is_alpha=True),
            Mock(text="court", pos_="NOUN", is_stop=False, is_alpha=True)
        ]
        
        mock_sent2 = MagicMock()
        mock_sent2.text = "Failure to appear may result in penalties."
        mock_sent2.start_char = 59
        mock_sent2.end_char = 102
        mock_sent2.ents = []
        mock_sent2.__iter__.return_value = [
            Mock(text="penalties", pos_="NOUN", is_stop=False, is_alpha=True)
        ]
        
        mock_doc.sents = [mock_sent1, mock_sent2]
        processor.nlp.return_value = mock_doc
        
        text = "The defendant shall appear in court on the specified date. Failure to appear may result in penalties."
        clauses = processor.extract_clauses(text)
        
        assert len(clauses) == 2
        
        # Check first clause
        assert clauses[0]['type'] == 'obligation'  # Contains "shall"
        assert clauses[0]['importance'] in ['high', 'medium']
        assert 'defendant' in clauses[0]['key_terms']
        
        # Check second clause
        assert clauses[1]['type'] in ['penalty', 'conditional']  # Contains "penalties" or "may"
    
    def test_classify_clause_types(self, processor):
        """Test clause classification for different types."""
        test_cases = [
            ("The party shall comply with all regulations.", "obligation"),
            ("The party may request an extension.", "permission"),
            ("If the condition is met, payment is due.", "conditional"),
            ("Breach will result in penalties.", "penalty"),
            ("The party is entitled to legal representation.", "rights"),
            ("'Agreement' means the contract dated January 1.", "definition"),
            ("This contract shall commence on January 1.", "temporal"),
            ("This is a general provision.", "general")
        ]
        
        for text, expected_type in test_cases:
            clause_type = processor._classify_clause(text)
            assert clause_type == expected_type, f"Expected {expected_type} for '{text}', got {clause_type}"
    
    def test_assess_clause_importance(self, processor):
        """Test clause importance assessment."""
        test_cases = [
            ("The court has mandatory jurisdiction over constitutional matters.", "high"),
            ("The party shall comply or face penalties.", "high"),
            ("It is recommended to follow proper procedures.", "medium"),
            ("The party should consider the options.", "medium"),
            ("This section provides general information.", "low")
        ]
        
        for text, expected_importance in test_cases:
            importance = processor._assess_clause_importance(text)
            assert importance == expected_importance, f"Expected {expected_importance} for '{text}', got {importance}"
    
    def test_split_into_sentences_with_nlp(self, processor):
        """Test sentence splitting with spaCy."""
        mock_doc = MagicMock()
        mock_doc.sents = [
            Mock(text="First sentence."),
            Mock(text="Second sentence."),
            Mock(text="")  # Empty sentence should be filtered
        ]
        processor.nlp.return_value = mock_doc
        
        text = "First sentence. Second sentence."
        sentences = processor._split_into_sentences(text)
        
        assert len(sentences) == 2
        assert sentences[0] == "First sentence."
        assert sentences[1] == "Second sentence."
    
    def test_split_into_sentences_fallback(self, processor):
        """Test sentence splitting fallback when NLP is not available."""
        processor.nlp = None
        
        text = "First sentence. Second sentence! Third sentence?"
        sentences = processor._split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
    
    def test_has_negation_difference(self, processor):
        """Test negation difference detection."""
        mock_doc1 = MagicMock()
        mock_doc1.__iter__.return_value = [
            Mock(text="not"),
            Mock(text="allowed")
        ]
        
        mock_doc2 = MagicMock()
        mock_doc2.__iter__.return_value = [
            Mock(text="allowed")
        ]
        
        # One has negation, other doesn't - should return True
        assert processor._has_negation_difference(mock_doc1, mock_doc2) == True
        
        # Both have negation - should return False
        mock_doc3 = MagicMock()
        mock_doc3.__iter__.return_value = [
            Mock(text="never"),
            Mock(text="allowed")
        ]
        assert processor._has_negation_difference(mock_doc1, mock_doc3) == False
    
    def test_find_related_terms(self, processor):
        """Test finding related terms."""
        # Mock the NLP processing
        mock_doc = MagicMock()
        mock_token1 = Mock(text="contract", similarity=Mock(return_value=0.8))
        mock_token2 = Mock(text="agreement", similarity=Mock(return_value=0.7))
        mock_token3 = Mock(text="unrelated", similarity=Mock(return_value=0.3))
        mock_doc.__iter__.return_value = [mock_token1, mock_token2, mock_token3]
        
        processor.nlp.side_effect = [mock_doc, MagicMock()]
        
        text = "The contract and agreement are binding."
        related = processor._find_related_terms("document", text)
        
        # Should return terms with high similarity
        assert isinstance(related, list)
        assert len(related) <= 5
    
    def test_find_related_terms_no_nlp(self, processor):
        """Test finding related terms when NLP is not available."""
        processor.nlp = None
        
        related = processor._find_related_terms("test", "Some text")
        assert related == []


class TestGlobalFunctions:
    """Test global functions in the NLP processor module."""
    
    def test_get_nlp_processor_singleton(self):
        """Test that get_nlp_processor returns a singleton."""
        with patch('modules.nlp_processor.LegalNLPProcessor') as MockProcessor:
            mock_instance = MockProcessor.return_value
            
            # Reset global instance
            import modules.nlp_processor
            modules.nlp_processor._nlp_processor = None
            
            # First call should create instance
            processor1 = get_nlp_processor()
            assert processor1 == mock_instance
            MockProcessor.assert_called_once()
            
            # Second call should return same instance
            processor2 = get_nlp_processor()
            assert processor2 == processor1
            MockProcessor.assert_called_once()  # Still only called once
    
    def test_initialize_nlp(self):
        """Test NLP initialization function."""
        with patch('modules.nlp_processor.LegalNLPProcessor') as MockProcessor:
            mock_instance = MockProcessor.return_value
            
            initialize_nlp()
            
            MockProcessor.assert_called_once()
            
            # Check that global instance was set
            import modules.nlp_processor
            assert modules.nlp_processor._nlp_processor == mock_instance


class TestIntegration:
    """Integration tests for the NLP processor."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not spacy.util.is_package("en_core_web_sm"), 
                        reason="Requires en_core_web_sm model")
    def test_full_document_analysis(self):
        """Test full document analysis with real spaCy model."""
        processor = LegalNLPProcessor()
        
        test_document = """
        LEGAL NOTICE
        
        The defendant John Doe shall appear before the District Court on January 15, 2024.
        Failure to appear may result in penalties including fines up to $5,000.
        
        The court has jurisdiction over this matter pursuant to Section 123 of the State Code.
        The defendant has the right to legal representation.
        
        If the defendant fails to comply with this order, a warrant may be issued.
        The defendant must not leave the state without court permission.
        """
        
        # Test entity extraction
        entities = processor.extract_legal_entities(test_document)
        assert len(entities) > 0
        entity_types = [e.label for e in entities]
        assert any(label in entity_types for label in ['PERSON', 'DATE', 'MONEY', 'ORG'])
        
        # Test contradiction detection
        contradictions = processor.detect_contradictions(test_document)
        # May or may not find contradictions in this specific text
        assert isinstance(contradictions, list)
        
        # Test legal concept identification
        concepts = processor.identify_legal_concepts(test_document)
        assert len(concepts) > 0
        concept_categories = [c.category for c in concepts]
        assert 'jurisdictional_terms' in concept_categories
        
        # Test sentiment analysis
        sentiment = processor.analyze_sentiment(test_document)
        assert sentiment['sentiment'] in ['positive', 'negative', 'neutral', 'concerning']
        assert 0 <= sentiment['confidence'] <= 1
        
        # Test clause extraction
        clauses = processor.extract_clauses(test_document)
        assert len(clauses) > 0
        clause_types = [c['type'] for c in clauses]
        assert 'obligation' in clause_types  # "shall appear"
        assert 'penalty' in clause_types  # "penalties including fines"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
