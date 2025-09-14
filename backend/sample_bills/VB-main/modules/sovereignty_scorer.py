"""
VeroBrix Sovereignty Scoring Framework
=====================================

Evaluates language, decisions, and remedies for alignment with sovereign principles.
Flags servile language and scores remedy alignment with lawful sovereignty.

Author: VeroBrix Sovereign Intelligence System
Created: 2025-01-17
"""

import re
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .logger import VeroBrixLogger
from .exceptions import VeroBrixError


@dataclass
class SovereigntyMetrics:
    """Sovereignty scoring metrics for a text or decision."""
    
    # Overall scores (0-1 scale)
    overall_score: float
    language_score: float
    remedy_score: float
    autonomy_score: float
    
    # Detailed analysis
    servile_flags: List[Dict[str, Any]]
    sovereign_indicators: List[Dict[str, Any]]
    remedy_alignment: Dict[str, Any]
    
    # Recommendations
    improvement_suggestions: List[str]
    sovereignty_level: str  # "Sovereign", "Transitional", "Servile"


class SovereigntyScorer:
    """
    Comprehensive sovereignty scoring system for VeroBrix.
    
    Evaluates text, decisions, and remedies for alignment with
    sovereign principles and lawful remedy frameworks.
    """
    
    def __init__(self, config_manager=None):
        """Initialize the sovereignty scoring system."""
        self.logger = VeroBrixLogger(__name__)
        self.config = config_manager
        
        # Load scoring patterns and rules
        self._load_scoring_patterns()
        
        self.logger.info("Sovereignty scoring system initialized")
    
    def _load_scoring_patterns(self):
        """Load sovereignty scoring patterns and rules."""
        
        # Servile language patterns (negative indicators)
        self.servile_patterns = {
            "submission_language": [
                r"\bplease\b.*\b(help|assist|allow|permit)\b",
                r"\bi\s+(humbly|respectfully)\s+(request|ask|beg)\b",
                r"\bif\s+it\s+pleases?\s+(the\s+)?(court|your\s+honor)\b",
                r"\bwith\s+all\s+due\s+respect\b",
                r"\bi\s+am\s+(just|only|merely)\s+a\b",
                r"\bi\s+don'?t\s+understand\s+(the\s+)?law\b"
            ],
            
            "dependency_language": [
                r"\bneed\s+(your\s+)?(permission|approval|authorization)\b",
                r"\bcan\s+(you|i)\s+please\b",
                r"\bwould\s+(you|it)\s+be\s+possible\b",
                r"\bi\s+hope\s+(you|the\s+court)\s+will\b",
                r"\bif\s+(you|the\s+court)\s+(would|could|might)\b"
            ],
            
            "victim_language": [
                r"\bi\s+can'?t\s+(afford|pay|handle)\b",
                r"\bi\s+don'?t\s+have\s+(money|resources|means)\b",
                r"\bi\s+am\s+(poor|indigent|unable)\b",
                r"\bthis\s+is\s+(unfair|unjust)\s+to\s+me\b",
                r"\bwhy\s+is\s+this\s+happening\s+to\s+me\b"
            ],
            
            "corporate_fiction_acceptance": [
                r"\bmy\s+(social\s+security\s+number|ssn)\s+is\b",
                r"\bi\s+am\s+a\s+(us\s+)?(citizen|resident)\b",
                r"\bunder\s+penalty\s+of\s+perjury\b",
                r"\bi\s+(understand|acknowledge)\s+that\s+i\s+am\s+required\b",
                r"\bi\s+consent\s+to\s+(jurisdiction|this\s+court)\b"
            ]
        }
        
        # Sovereign language patterns (positive indicators)
        self.sovereign_patterns = {
            "lawful_standing": [
                r"\bi\s+am\s+a\s+(living\s+)?(man|woman)\b",
                r"\bacting\s+in\s+my\s+private\s+capacity\b",
                r"\bnot\s+acting\s+as\s+(agent|representative|trustee)\b",
                r"\bby\s+special\s+appearance\s+only\b",
                r"\breserving\s+all\s+(rights|claims)\b"
            ],
            
            "authority_challenges": [
                r"\bwhat\s+is\s+(your\s+)?authority\s+for\b",
                r"\bprove\s+(your\s+)?(jurisdiction|authority|standing)\b",
                r"\bshow\s+me\s+the\s+(law|statute|regulation)\b",
                r"\bwhere\s+is\s+the\s+(injured\s+party|victim)\b",
                r"\bwhat\s+is\s+the\s+nature\s+of\s+the\s+(claim|complaint)\b"
            ],
            
            "constitutional_assertions": [
                r"\bconstitutional\s+(right|protection|guarantee)\b",
                r"\bfourth\s+amendment\s+(right|protection)\b",
                r"\bfifth\s+amendment\s+(right|protection)\b",
                r"\bdue\s+process\s+(right|violation|requirement)\b",
                r"\bequal\s+protection\s+(under\s+)?law\b"
            ],
            
            "commercial_awareness": [
                r"\bthis\s+appears\s+to\s+be\s+a\s+commercial\s+(matter|transaction)\b",
                r"\bi\s+do\s+not\s+consent\s+to\s+(commercial\s+)?jurisdiction\b",
                r"\bno\s+contract\s+(exists|was\s+formed)\b",
                r"\bwhere\s+is\s+the\s+(consideration|meeting\s+of\s+minds)\b",
                r"\bucc\s+(article\s+)?\d+\s+(applies|governs)\b"
            ],
            
            "remedy_focused": [
                r"\bi\s+(demand|require|claim)\s+(lawful\s+)?remedy\b",
                r"\bmake\s+me\s+whole\b",
                r"\bcompensation\s+for\s+(damages|harm|injury)\b",
                r"\brestitution\s+(is\s+)?(required|demanded)\b",
                r"\bspecific\s+performance\s+(is\s+)?(required|demanded)\b"
            ]
        }
        
        # Remedy alignment patterns
        self.remedy_patterns = {
            "lawful_remedy_indicators": [
                r"\bspecific\s+performance\b",
                r"\brestitution\b",
                r"\bmake\s+whole\b",
                r"\bcompensation\s+for\s+(actual\s+)?(damages|harm)\b",
                r"\binjunctive\s+relief\b"
            ],
            
            "unlawful_remedy_indicators": [
                r"\bpunitive\s+damages\b",
                r"\bpunishment\b",
                r"\bfines?\s+and\s+penalties\b",
                r"\bimprisonment\b",
                r"\bincarceration\b"
            ]
        }
        
        # Autonomy indicators
        self.autonomy_patterns = {
            "self_determination": [
                r"\bi\s+(choose|elect|decide)\s+to\b",
                r"\bby\s+my\s+own\s+(choice|decision|will)\b",
                r"\bacting\s+under\s+my\s+own\s+authority\b",
                r"\bself[\-\s]?determining\b",
                r"\bautonomous\s+(action|decision|choice)\b"
            ],
            
            "non_consent": [
                r"\bi\s+do\s+not\s+consent\b",
                r"\bwithout\s+my\s+consent\b",
                r"\bno\s+consent\s+(given|granted|implied)\b",
                r"\bunder\s+duress\b",
                r"\bcoercion\s+(is\s+)?present\b"
            ]
        }
    
    def score_text(self, text: str, context: str = "general") -> SovereigntyMetrics:
        """
        Score a text for sovereignty alignment.
        
        Args:
            text: Text to analyze
            context: Context type (general, legal_document, correspondence, etc.)
            
        Returns:
            SovereigntyMetrics: Comprehensive sovereignty scoring
        """
        if not text or not text.strip():
            return SovereigntyMetrics(
                overall_score=0.5,
                language_score=0.5,
                remedy_score=0.5,
                autonomy_score=0.5,
                servile_flags=[],
                sovereign_indicators=[],
                remedy_alignment={},
                improvement_suggestions=["No text provided for analysis"],
                sovereignty_level="Unknown"
            )
        
        text_lower = text.lower()
        
        # Analyze servile language
        servile_flags = self._detect_servile_language(text_lower)
        
        # Analyze sovereign indicators
        sovereign_indicators = self._detect_sovereign_language(text_lower)
        
        # Analyze remedy alignment
        remedy_alignment = self._analyze_remedy_alignment(text_lower)
        
        # Analyze autonomy indicators
        autonomy_score = self._calculate_autonomy_score(text_lower)
        
        # Calculate component scores
        language_score = self._calculate_language_score(servile_flags, sovereign_indicators, len(text))
        remedy_score = remedy_alignment.get("score", 0.5)
        
        # Calculate overall score
        overall_score = (language_score * 0.4 + remedy_score * 0.3 + autonomy_score * 0.3)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            servile_flags, sovereign_indicators, remedy_alignment, autonomy_score
        )
        
        # Determine sovereignty level
        sovereignty_level = self._determine_sovereignty_level(overall_score)
        
        return SovereigntyMetrics(
            overall_score=overall_score,
            language_score=language_score,
            remedy_score=remedy_score,
            autonomy_score=autonomy_score,
            servile_flags=servile_flags,
            sovereign_indicators=sovereign_indicators,
            remedy_alignment=remedy_alignment,
            improvement_suggestions=suggestions,
            sovereignty_level=sovereignty_level
        )
    
    def _detect_servile_language(self, text: str) -> List[Dict[str, Any]]:
        """Detect servile language patterns in text."""
        flags = []
        
        for category, patterns in self.servile_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    flags.append({
                        "category": category,
                        "pattern": pattern,
                        "match": match.group(),
                        "position": match.span(),
                        "severity": self._get_servile_severity(category),
                        "suggestion": self._get_servile_suggestion(category, match.group())
                    })
        
        return flags
    
    def _detect_sovereign_language(self, text: str) -> List[Dict[str, Any]]:
        """Detect sovereign language patterns in text."""
        indicators = []
        
        for category, patterns in self.sovereign_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    indicators.append({
                        "category": category,
                        "pattern": pattern,
                        "match": match.group(),
                        "position": match.span(),
                        "strength": self._get_sovereign_strength(category),
                        "explanation": self._get_sovereign_explanation(category, match.group())
                    })
        
        return indicators
    
    def _analyze_remedy_alignment(self, text: str) -> Dict[str, Any]:
        """Analyze remedy alignment in text."""
        lawful_matches = []
        unlawful_matches = []
        
        # Check for lawful remedy indicators
        for pattern in self.remedy_patterns["lawful_remedy_indicators"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            lawful_matches.extend([match.group() for match in matches])
        
        # Check for unlawful remedy indicators
        for pattern in self.remedy_patterns["unlawful_remedy_indicators"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            unlawful_matches.extend([match.group() for match in matches])
        
        # Calculate remedy score
        lawful_count = len(lawful_matches)
        unlawful_count = len(unlawful_matches)
        total_count = lawful_count + unlawful_count
        
        if total_count == 0:
            score = 0.5  # Neutral if no remedy language detected
        else:
            score = lawful_count / total_count
        
        return {
            "score": score,
            "lawful_indicators": lawful_matches,
            "unlawful_indicators": unlawful_matches,
            "analysis": self._get_remedy_analysis(score, lawful_count, unlawful_count)
        }
    
    def _calculate_autonomy_score(self, text: str) -> float:
        """Calculate autonomy score based on self-determination indicators."""
        autonomy_matches = 0
        dependency_matches = 0
        
        # Count autonomy indicators
        for category, patterns in self.autonomy_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if category == "self_determination":
                    autonomy_matches += matches
                elif category == "non_consent":
                    autonomy_matches += matches * 0.8  # Slightly lower weight
        
        # Count dependency indicators (from servile patterns)
        for pattern in self.servile_patterns["dependency_language"]:
            dependency_matches += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Calculate score
        total_matches = autonomy_matches + dependency_matches
        if total_matches == 0:
            return 0.5  # Neutral if no relevant language
        
        return min(1.0, autonomy_matches / (autonomy_matches + dependency_matches * 2))
    
    def _calculate_language_score(self, servile_flags: List[Dict], sovereign_indicators: List[Dict], text_length: int) -> float:
        """Calculate overall language score."""
        # Weight servile flags negatively
        servile_penalty = sum(flag["severity"] for flag in servile_flags) / max(text_length / 100, 1)
        
        # Weight sovereign indicators positively
        sovereign_bonus = sum(indicator["strength"] for indicator in sovereign_indicators) / max(text_length / 100, 1)
        
        # Base score starts at 0.5 (neutral)
        score = 0.5 - servile_penalty + sovereign_bonus
        
        return max(0.0, min(1.0, score))
    
    def _get_servile_severity(self, category: str) -> float:
        """Get severity score for servile language category."""
        severity_map = {
            "submission_language": 0.3,
            "dependency_language": 0.4,
            "victim_language": 0.5,
            "corporate_fiction_acceptance": 0.6
        }
        return severity_map.get(category, 0.3)
    
    def _get_sovereign_strength(self, category: str) -> float:
        """Get strength score for sovereign language category."""
        strength_map = {
            "lawful_standing": 0.4,
            "authority_challenges": 0.5,
            "constitutional_assertions": 0.4,
            "commercial_awareness": 0.3,
            "remedy_focused": 0.5
        }
        return strength_map.get(category, 0.3)
    
    def _get_servile_suggestion(self, category: str, match: str) -> str:
        """Get improvement suggestion for servile language."""
        suggestions = {
            "submission_language": "Replace submissive language with assertive statements of rights and standing",
            "dependency_language": "Assert your authority rather than seeking permission",
            "victim_language": "Focus on lawful remedy rather than personal circumstances",
            "corporate_fiction_acceptance": "Clarify your standing as a living man/woman, not a legal fiction"
        }
        return suggestions.get(category, "Consider more sovereign language alternatives")
    
    def _get_sovereign_explanation(self, category: str, match: str) -> str:
        """Get explanation for sovereign language indicator."""
        explanations = {
            "lawful_standing": "Properly establishes standing as a living being with inherent rights",
            "authority_challenges": "Appropriately challenges presumed authority and jurisdiction",
            "constitutional_assertions": "Invokes constitutional protections and guarantees",
            "commercial_awareness": "Demonstrates understanding of commercial vs. lawful distinctions",
            "remedy_focused": "Focuses on lawful remedy rather than punishment or penalties"
        }
        return explanations.get(category, "Demonstrates sovereign awareness and understanding")
    
    def _get_remedy_analysis(self, score: float, lawful_count: int, unlawful_count: int) -> str:
        """Generate remedy alignment analysis."""
        if score >= 0.8:
            return f"Strong lawful remedy focus ({lawful_count} lawful indicators, {unlawful_count} unlawful)"
        elif score >= 0.6:
            return f"Good remedy alignment ({lawful_count} lawful indicators, {unlawful_count} unlawful)"
        elif score >= 0.4:
            return f"Mixed remedy approach ({lawful_count} lawful indicators, {unlawful_count} unlawful)"
        else:
            return f"Concerning unlawful remedy focus ({lawful_count} lawful indicators, {unlawful_count} unlawful)"
    
    def _generate_improvement_suggestions(self, servile_flags: List[Dict], sovereign_indicators: List[Dict], 
                                        remedy_alignment: Dict, autonomy_score: float) -> List[str]:
        """Generate specific improvement suggestions."""
        suggestions = []
        
        # Address servile language
        if servile_flags:
            categories = set(flag["category"] for flag in servile_flags)
            for category in categories:
                if category == "submission_language":
                    suggestions.append("Replace submissive phrases with assertive statements of rights and standing")
                elif category == "dependency_language":
                    suggestions.append("Assert your inherent authority rather than seeking permission")
                elif category == "victim_language":
                    suggestions.append("Focus on lawful remedy and rights rather than personal circumstances")
                elif category == "corporate_fiction_acceptance":
                    suggestions.append("Clarify your standing as a living being, not a corporate fiction")
        
        # Encourage sovereign language
        if len(sovereign_indicators) < 3:
            suggestions.append("Include more sovereign language patterns (authority challenges, constitutional assertions)")
        
        # Address remedy alignment
        if remedy_alignment["score"] < 0.6:
            suggestions.append("Focus on lawful remedies (restitution, specific performance) rather than punitive measures")
        
        # Address autonomy
        if autonomy_score < 0.6:
            suggestions.append("Emphasize self-determination and autonomous decision-making")
        
        # General suggestions if score is low
        if not suggestions:
            suggestions.append("Consider incorporating more sovereign principles and lawful remedy focus")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _determine_sovereignty_level(self, score: float) -> str:
        """Determine sovereignty level based on overall score."""
        if score >= 0.75:
            return "Sovereign"
        elif score >= 0.5:
            return "Transitional"
        else:
            return "Servile"
    
    def score_decision(self, decision_data: Dict[str, Any]) -> SovereigntyMetrics:
        """Score a decision or recommendation for sovereignty alignment."""
        # Extract text from decision data
        text_parts = []
        
        if "description" in decision_data:
            text_parts.append(decision_data["description"])
        if "reasoning" in decision_data:
            text_parts.append(decision_data["reasoning"])
        if "recommendations" in decision_data:
            if isinstance(decision_data["recommendations"], list):
                text_parts.extend(decision_data["recommendations"])
            else:
                text_parts.append(str(decision_data["recommendations"]))
        
        combined_text = " ".join(text_parts)
        
        # Score the combined text
        metrics = self.score_text(combined_text, context="decision")
        
        # Adjust scoring for decision context
        if "remedy_type" in decision_data:
            remedy_type = decision_data["remedy_type"].lower()
            if any(unlawful in remedy_type for unlawful in ["punitive", "penalty", "fine", "punishment"]):
                metrics.remedy_score *= 0.5
                metrics.overall_score = (metrics.language_score * 0.4 + metrics.remedy_score * 0.3 + metrics.autonomy_score * 0.3)
        
        return metrics
    
    def generate_sovereignty_report(self, metrics: SovereigntyMetrics, include_details: bool = True) -> str:
        """Generate a human-readable sovereignty report."""
        report = []
        
        # Header
        report.append("=" * 50)
        report.append("VEROBRIX SOVEREIGNTY ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Overall assessment
        report.append(f"\nSOVEREIGNTY LEVEL: {metrics.sovereignty_level}")
        report.append(f"Overall Score: {metrics.overall_score:.2f}/1.00")
        report.append(f"Language Score: {metrics.language_score:.2f}/1.00")
        report.append(f"Remedy Score: {metrics.remedy_score:.2f}/1.00")
        report.append(f"Autonomy Score: {metrics.autonomy_score:.2f}/1.00")
        
        if include_details:
            # Servile language flags
            if metrics.servile_flags:
                report.append(f"\n⚠️  SERVILE LANGUAGE DETECTED ({len(metrics.servile_flags)} instances):")
                for flag in metrics.servile_flags[:5]:  # Show top 5
                    report.append(f"  • {flag['match']} ({flag['category']})")
                    report.append(f"    Suggestion: {flag['suggestion']}")
            
            # Sovereign indicators
            if metrics.sovereign_indicators:
                report.append(f"\n✅ SOVEREIGN LANGUAGE FOUND ({len(metrics.sovereign_indicators)} instances):")
                for indicator in metrics.sovereign_indicators[:5]:  # Show top 5
                    report.append(f"  • {indicator['match']} ({indicator['category']})")
                    report.append(f"    Strength: {indicator['explanation']}")
            
            # Remedy analysis
            if metrics.remedy_alignment:
                report.append(f"\n⚖️  REMEDY ALIGNMENT:")
                report.append(f"  {metrics.remedy_alignment.get('analysis', 'No remedy analysis available')}")
        
        # Improvement suggestions
        if metrics.improvement_suggestions:
            report.append(f"\n💡 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(metrics.improvement_suggestions, 1):
                report.append(f"  {i}. {suggestion}")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# Global sovereignty scorer instance
_global_sovereignty_scorer = None


def get_sovereignty_scorer(config_manager=None) -> SovereigntyScorer:
    """Get or create the global sovereignty scorer instance."""
    global _global_sovereignty_scorer
    
    if _global_sovereignty_scorer is None:
        _global_sovereignty_scorer = SovereigntyScorer(config_manager)
    
    return _global_sovereignty_scorer


def score_sovereignty(text: str, context: str = "general") -> SovereigntyMetrics:
    """Convenience function for scoring sovereignty."""
    scorer = get_sovereignty_scorer()
    return scorer.score_text(text, context)
