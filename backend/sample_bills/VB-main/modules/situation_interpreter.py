"""
VeroBrix Situation Interpreter Module

This module translates real-world inputs (e.g., traffic stops, fee demands, 
document requests) into structured legal constructs for analysis.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class SituationInterpreter:
    """
    Interprets real-world legal situations and converts them into structured data
    for analysis by other VeroBrix modules.
    """
    
    def __init__(self):
        self.situation_patterns = self._load_situation_patterns()
        self.legal_entities = self._load_legal_entities()
        self.jurisdiction_indicators = self._load_jurisdiction_indicators()
    
    def _load_situation_patterns(self) -> Dict[str, Any]:
        """Load patterns for identifying different types of legal situations."""
        return {
            'traffic_stop': {
                'keywords': [
                    'traffic', 'driving', 'vehicle', 'license', 'registration', 
                    'insurance', 'speeding', 'violation', 'citation', 'ticket',
                    'officer', 'police', 'patrol', 'stop', 'pulled over'
                ],
                'phrases': [
                    'pulled over', 'traffic stop', 'speeding ticket', 'license and registration',
                    'proof of insurance', 'vehicle inspection', 'moving violation'
                ],
                'entities': ['officer', 'department', 'citation_number', 'vehicle', 'location']
            },
            'fee_demand': {
                'keywords': [
                    'fee', 'fine', 'penalty', 'charge', 'payment', 'bill', 'invoice',
                    'assessment', 'tax', 'levy', 'collection', 'demand', 'notice'
                ],
                'phrases': [
                    'payment due', 'fee schedule', 'penalty assessment', 'collection notice',
                    'final demand', 'administrative fee', 'processing charge'
                ],
                'entities': ['agency', 'amount', 'due_date', 'account_number', 'fee_type']
            },
            'court_summons': {
                'keywords': [
                    'court', 'summons', 'complaint', 'lawsuit', 'litigation', 'hearing',
                    'appearance', 'defendant', 'plaintiff', 'case', 'docket', 'judge'
                ],
                'phrases': [
                    'court appearance', 'legal proceeding', 'civil action', 'court order',
                    'summons and complaint', 'hearing date', 'case number'
                ],
                'entities': ['court', 'case_number', 'hearing_date', 'plaintiff', 'judge']
            },
            'contract_dispute': {
                'keywords': [
                    'contract', 'agreement', 'breach', 'default', 'terms', 'conditions',
                    'obligation', 'performance', 'consideration', 'party', 'dispute'
                ],
                'phrases': [
                    'breach of contract', 'contract dispute', 'terms and conditions',
                    'failure to perform', 'contract violation', 'agreement terms'
                ],
                'entities': ['parties', 'contract_date', 'terms', 'breach_type', 'damages']
            },
            'administrative_action': {
                'keywords': [
                    'agency', 'department', 'administrative', 'regulation', 'compliance',
                    'enforcement', 'investigation', 'audit', 'inspection', 'permit'
                ],
                'phrases': [
                    'administrative action', 'regulatory compliance', 'agency investigation',
                    'permit application', 'inspection notice', 'compliance order'
                ],
                'entities': ['agency', 'regulation', 'permit_number', 'inspector', 'violation']
            },
            'property_dispute': {
                'keywords': [
                    'property', 'real estate', 'land', 'title', 'deed', 'ownership',
                    'boundary', 'easement', 'lien', 'mortgage', 'foreclosure'
                ],
                'phrases': [
                    'property dispute', 'title issue', 'boundary dispute', 'property rights',
                    'real estate matter', 'land ownership', 'property claim'
                ],
                'entities': ['property_address', 'title_company', 'deed_date', 'owner', 'claimant']
            }
        }
    
    def _load_legal_entities(self) -> Dict[str, List[str]]:
        """Load patterns for identifying legal entities and roles."""
        return {
            'government_entities': [
                'department', 'agency', 'bureau', 'office', 'commission', 'board',
                'authority', 'administration', 'service', 'division'
            ],
            'law_enforcement': [
                'police', 'officer', 'deputy', 'sheriff', 'trooper', 'patrol',
                'department', 'force', 'bureau', 'agency'
            ],
            'judicial_entities': [
                'court', 'judge', 'magistrate', 'clerk', 'bailiff', 'tribunal',
                'justice', 'judicial', 'judiciary'
            ],
            'commercial_entities': [
                'corporation', 'company', 'llc', 'inc', 'ltd', 'partnership',
                'business', 'enterprise', 'firm', 'organization'
            ]
        }
    
    def _load_jurisdiction_indicators(self) -> Dict[str, List[str]]:
        """Load indicators for different jurisdictional contexts."""
        return {
            'federal': [
                'federal', 'united states', 'u.s.', 'irs', 'fbi', 'dea', 'atf',
                'customs', 'immigration', 'social security', 'medicare'
            ],
            'state': [
                'state', 'commonwealth', 'dmv', 'department of', 'state police',
                'state court', 'state agency', 'governor', 'legislature'
            ],
            'local': [
                'city', 'county', 'municipal', 'town', 'village', 'parish',
                'local', 'mayor', 'council', 'commissioner'
            ],
            'commercial': [
                'commercial', 'business', 'trade', 'commerce', 'ucc', 'contract',
                'agreement', 'transaction', 'sale', 'purchase'
            ]
        }
    
    def interpret_situation(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main method to interpret a real-world situation from text input.
        
        Args:
            input_text: Raw text describing the situation
            context: Optional additional context information
            
        Returns:
            Structured situation analysis
        """
        # Clean and normalize input
        normalized_text = self._normalize_text(input_text)
        
        # Identify situation type
        situation_type = self._identify_situation_type(normalized_text)
        
        # Extract entities
        entities = self._extract_entities(normalized_text, situation_type)
        
        # Determine jurisdiction
        jurisdiction = self._determine_jurisdiction(normalized_text, entities)
        
        # Identify legal relationships
        relationships = self._identify_relationships(normalized_text, entities)
        
        # Extract key facts
        facts = self._extract_key_facts(normalized_text, situation_type)
        
        # Assess urgency and timeline
        urgency = self._assess_urgency(normalized_text, entities)
        
        # Build structured situation
        situation = {
            'type': situation_type,
            'raw_input': input_text,
            'normalized_text': normalized_text,
            'entities': entities,
            'jurisdiction': jurisdiction,
            'relationships': relationships,
            'key_facts': facts,
            'urgency': urgency,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'legal_framework': self._determine_legal_framework(situation_type, jurisdiction),
            'potential_issues': self._identify_potential_issues(normalized_text, situation_type),
            'required_actions': self._suggest_required_actions(situation_type, urgency)
        }
        
        return situation
    
    def _normalize_text(self, text: str) -> str:
        """Normalize input text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Standardize common abbreviations
        abbreviations = {
            'dept': 'department',
            'gov': 'government',
            'admin': 'administrative',
            'reg': 'regulation',
            'sec': 'section',
            'vs': 'versus',
            'v.': 'versus'
        }
        
        for abbrev, full in abbreviations.items():
            text = re.sub(r'\b' + abbrev + r'\b', full, text)
        
        return text
    
    def _identify_situation_type(self, text: str) -> str:
        """Identify the type of legal situation from the text."""
        scores = {}
        
        for situation_type, patterns in self.situation_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in text:
                    score += 1
            
            # Check phrases (weighted higher)
            for phrase in patterns['phrases']:
                if phrase in text:
                    score += 3
            
            scores[situation_type] = score
        
        # Return the situation type with the highest score
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            if best_match[1] > 0:
                return best_match[0]
        
        return 'general'
    
    def _extract_entities(self, text: str, situation_type: str) -> Dict[str, List[str]]:
        """Extract relevant entities from the text based on situation type."""
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'amounts': [],
            'identifiers': [],
            'legal_instruments': []
        }
        
        # Extract people (basic pattern matching)
        people_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b(?:officer|judge|attorney|mr|ms|mrs)\.?\s+[A-Z][a-z]+\b'
        ]
        
        for pattern in people_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['people'].extend(matches)
        
        # Extract organizations
        org_patterns = [
            r'\b[A-Z][a-z]*\s+(?:department|agency|bureau|office|court|police)\b',
            r'\b(?:department|agency|bureau|office|court|police)\s+of\s+[A-Z][a-z]+\b'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['organizations'].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Extract monetary amounts
        amount_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s+dollars?\b'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['amounts'].extend(matches)
        
        # Extract case numbers, citation numbers, etc.
        id_patterns = [
            r'\b(?:case|citation|ticket|docket)\s*#?\s*[A-Z0-9-]+\b',
            r'\b[A-Z]{2,}\d{4,}\b'
        ]
        
        for pattern in id_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['identifiers'].extend(matches)
        
        return entities
    
    def _determine_jurisdiction(self, text: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Determine the applicable jurisdiction(s) for the situation."""
        jurisdiction = {
            'primary': 'unknown',
            'secondary': [],
            'indicators': [],
            'confidence': 0.0
        }
        
        scores = {'federal': 0, 'state': 0, 'local': 0, 'commercial': 0}
        
        for jurisdiction_type, indicators in self.jurisdiction_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    scores[jurisdiction_type] += 1
                    jurisdiction['indicators'].append(f"{jurisdiction_type}: {indicator}")
        
        # Determine primary jurisdiction
        if scores:
            primary = max(scores.items(), key=lambda x: x[1])
            if primary[1] > 0:
                jurisdiction['primary'] = primary[0]
                jurisdiction['confidence'] = min(primary[1] / 5.0, 1.0)  # Normalize to 0-1
        
        # Add secondary jurisdictions
        for jtype, score in scores.items():
            if jtype != jurisdiction['primary'] and score > 0:
                jurisdiction['secondary'].append(jtype)
        
        return jurisdiction
    
    def _identify_relationships(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Identify legal relationships between entities."""
        relationships = []
        
        # Common relationship patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:vs?\.?|versus)\s+(\w+)', 'adversarial'),
            (r'(\w+)\s+(?:and|&)\s+(\w+)', 'joint'),
            (r'(\w+)\s+(?:represents?|representing)\s+(\w+)', 'representation'),
            (r'(\w+)\s+(?:sues?|suing)\s+(\w+)', 'litigation'),
            (r'(\w+)\s+(?:contracts?|contracting)\s+(?:with\s+)?(\w+)', 'contractual')
        ]
        
        for pattern, relationship_type in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                relationships.append({
                    'type': relationship_type,
                    'entity1': match[0],
                    'entity2': match[1]
                })
        
        return relationships
    
    def _extract_key_facts(self, text: str, situation_type: str) -> List[str]:
        """Extract key factual elements from the text."""
        facts = []
        
        # Situation-specific fact extraction
        if situation_type == 'traffic_stop':
            fact_patterns = [
                r'(?:speed|speeding).*?(\d+\s*mph)',
                r'(?:location|where|at).*?([A-Z][a-z]+\s+(?:street|road|avenue|highway))',
                r'(?:time|when).*?(\d{1,2}:\d{2}(?:\s*[ap]m)?)'
            ]
        elif situation_type == 'fee_demand':
            fact_patterns = [
                r'(?:amount|fee|fine).*?(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:due|deadline).*?(\d{1,2}/\d{1,2}/\d{2,4})',
                r'(?:account|reference).*?([A-Z0-9-]+)'
            ]
        else:
            fact_patterns = [
                r'(?:date|when).*?(\d{1,2}/\d{1,2}/\d{2,4})',
                r'(?:amount|cost|fee).*?(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:location|where|at).*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ]
        
        for pattern in fact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            facts.extend(matches)
        
        return facts
    
    def _assess_urgency(self, text: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Assess the urgency level of the situation."""
        urgency_indicators = {
            'high': ['immediate', 'urgent', 'emergency', 'deadline', 'final notice', 'court date'],
            'medium': ['soon', 'within', 'by', 'before', 'due'],
            'low': ['when convenient', 'at your earliest', 'please']
        }
        
        urgency = {
            'level': 'medium',
            'indicators': [],
            'timeline': None
        }
        
        for level, indicators in urgency_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    urgency['indicators'].append(indicator)
                    if level == 'high':
                        urgency['level'] = 'high'
                    elif level == 'low' and urgency['level'] != 'high':
                        urgency['level'] = 'low'
        
        # Extract timeline information
        timeline_patterns = [
            r'(?:within|by|before)\s+(\d+\s+(?:days?|weeks?|months?))',
            r'(?:due|deadline).*?(\d{1,2}/\d{1,2}/\d{2,4})'
        ]
        
        for pattern in timeline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                urgency['timeline'] = matches[0]
                break
        
        return urgency
    
    def _determine_legal_framework(self, situation_type: str, jurisdiction: Dict[str, Any]) -> List[str]:
        """Determine applicable legal frameworks."""
        frameworks = []
        
        # Base frameworks by situation type
        framework_map = {
            'traffic_stop': ['Constitutional law', 'Administrative law', 'Traffic regulations'],
            'fee_demand': ['Administrative law', 'Due process', 'Collection procedures'],
            'court_summons': ['Civil procedure', 'Constitutional law', 'Jurisdictional law'],
            'contract_dispute': ['Contract law', 'UCC', 'Commercial law'],
            'administrative_action': ['Administrative law', 'Regulatory compliance', 'Due process'],
            'property_dispute': ['Property law', 'Real estate law', 'Title law']
        }
        
        frameworks.extend(framework_map.get(situation_type, ['General law']))
        
        # Add jurisdiction-specific frameworks
        if jurisdiction['primary'] == 'federal':
            frameworks.append('Federal law')
        elif jurisdiction['primary'] == 'state':
            frameworks.append('State law')
        elif jurisdiction['primary'] == 'local':
            frameworks.append('Local ordinances')
        
        return frameworks
    
    def _identify_potential_issues(self, text: str, situation_type: str) -> List[str]:
        """Identify potential legal issues or red flags."""
        issues = []
        
        # Common issue indicators
        issue_patterns = [
            ('waiver', 'Potential rights waiver'),
            ('consent', 'Consent issues'),
            ('jurisdiction', 'Jurisdictional questions'),
            ('authority', 'Authority challenges'),
            ('due process', 'Due process concerns'),
            ('notice', 'Notice requirements'),
            ('deadline', 'Time-sensitive requirements'),
            ('penalty', 'Penalty provisions'),
            ('default', 'Default consequences')
        ]
        
        for pattern, issue in issue_patterns:
            if pattern in text:
                issues.append(issue)
        
        return issues
    
    def _suggest_required_actions(self, situation_type: str, urgency: Dict[str, Any]) -> List[str]:
        """Suggest immediate required actions based on situation type and urgency."""
        actions = []
        
        # Base actions by situation type
        action_map = {
            'traffic_stop': [
                'Document the encounter',
                'Preserve evidence',
                'Review citation for errors',
                'Consider challenging jurisdiction'
            ],
            'fee_demand': [
                'Challenge fee authority',
                'Request fee schedule',
                'Demand due process hearing',
                'Preserve payment deadline'
            ],
            'court_summons': [
                'File timely response',
                'Challenge jurisdiction if applicable',
                'Demand bill of particulars',
                'Preserve all rights'
            ],
            'contract_dispute': [
                'Review contract terms',
                'Document breach if applicable',
                'Preserve evidence',
                'Consider mediation'
            ]
        }
        
        actions.extend(action_map.get(situation_type, ['Seek legal counsel', 'Document situation']))
        
        # Add urgency-based actions
        if urgency['level'] == 'high':
            actions.insert(0, 'URGENT: Immediate action required')
            actions.append('Consider emergency legal assistance')
        
        return actions

if __name__ == '__main__':
    # Test the situation interpreter
    interpreter = SituationInterpreter()
    
    test_scenarios = [
        "I was pulled over by Officer Smith on Highway 101 for allegedly speeding 75 mph in a 65 mph zone. He gave me citation #TR-2024-001 and wants me to appear in court on March 15th.",
        
        "The Department of Motor Vehicles sent me a notice demanding a $150 administrative fee for late registration renewal. They say I have 30 days to pay or face additional penalties.",
        
        "I received a summons from Superior Court in case #CV-2024-0123. The plaintiff is ABC Corporation claiming I breached our service contract signed last year."
    ]
    
    print("=== VeroBrix Situation Interpreter Test ===")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Scenario {i} ---")
        print(f"Input: {scenario}")
        
        situation = interpreter.interpret_situation(scenario)
        
        print(f"Situation Type: {situation['type']}")
        print(f"Primary Jurisdiction: {situation['jurisdiction']['primary']}")
        print(f"Urgency Level: {situation['urgency']['level']}")
        
        if situation['entities']['people']:
            print(f"People: {', '.join(situation['entities']['people'])}")
        
        if situation['entities']['organizations']:
            print(f"Organizations: {', '.join(situation['entities']['organizations'])}")
        
        if situation['key_facts']:
            print(f"Key Facts: {', '.join(situation['key_facts'])}")
        
        if situation['potential_issues']:
            print(f"Potential Issues: {', '.join(situation['potential_issues'])}")
        
        print("Required Actions:")
        for action in situation['required_actions']:
            print(f"  - {action}")
