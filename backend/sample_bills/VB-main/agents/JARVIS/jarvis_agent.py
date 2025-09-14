import re
import os
import sys

def extract_clauses(text):
    """
    Enhanced clause extraction that handles legal document structure better.
    Splits text into meaningful legal clauses, not just sentences.
    """
    # Clean the text
    text = text.strip()
    
    # Split on sentence endings, but be smarter about it
    # Handle common legal abbreviations that shouldn't trigger splits
    abbreviations = ['U.S.', 'U.S.C.', 'C.F.R.', 'Fed.', 'Reg.', 'Inc.', 'Corp.', 'Ltd.', 'Co.', 'vs.', 'v.']
    
    # Temporarily replace abbreviations to avoid false splits
    temp_text = text
    for i, abbrev in enumerate(abbreviations):
        temp_text = temp_text.replace(abbrev, f"__ABBREV_{i}__")
    
    # Split on sentence boundaries
    clauses = re.split(r'[.!?]+\s+', temp_text)
    
    # Restore abbreviations
    for i, abbrev in enumerate(abbreviations):
        clauses = [clause.replace(f"__ABBREV_{i}__", abbrev) for clause in clauses]
    
    # Filter out empty clauses and clean whitespace
    clauses = [clause.strip() for clause in clauses if clause.strip()]
    
    return clauses

def detect_contradictions(clauses):
    """
    Enhanced contradiction detection using multiple legal patterns.
    Looks for various types of legal contradictions and inconsistencies.
    """
    contradictions = []
    
    # Pattern 1: Notwithstanding + subject to (original pattern)
    for clause in clauses:
        if 'notwithstanding' in clause.lower() and 'subject to' in clause.lower():
            contradictions.append({
                'type': 'notwithstanding_subject_to',
                'clause': clause,
                'description': 'Clause contains both "notwithstanding" and "subject to" which may create conflicting obligations'
            })
    
    # Pattern 2: Shall + may in same clause (conflicting obligation levels)
    for clause in clauses:
        if 'shall' in clause.lower() and 'may' in clause.lower():
            contradictions.append({
                'type': 'shall_may_conflict',
                'clause': clause,
                'description': 'Clause mixes mandatory ("shall") and permissive ("may") language'
            })
    
    # Pattern 3: Prohibited + permitted/allowed
    for clause in clauses:
        clause_lower = clause.lower()
        if any(word in clause_lower for word in ['prohibited', 'forbidden', 'not permitted']) and \
           any(word in clause_lower for word in ['permitted', 'allowed', 'authorized']):
            contradictions.append({
                'type': 'prohibition_permission_conflict',
                'clause': clause,
                'description': 'Clause contains conflicting prohibition and permission language'
            })
    
    # Pattern 4: Cross-clause contradictions (basic version)
    for i, clause1 in enumerate(clauses):
        for j, clause2 in enumerate(clauses[i+1:], i+1):
            if detect_clause_contradiction(clause1, clause2):
                contradictions.append({
                    'type': 'cross_clause_contradiction',
                    'clause': f"Clause {i+1}: {clause1} | Clause {j+1}: {clause2}",
                    'description': 'These clauses appear to contradict each other'
                })
    
    return contradictions

def detect_clause_contradiction(clause1, clause2):
    """
    Detect contradictions between two clauses using keyword analysis.
    This is a basic implementation that could be enhanced with NLP.
    """
    # Convert to lowercase for comparison
    c1_lower = clause1.lower()
    c2_lower = clause2.lower()
    
    # Look for opposite concepts
    opposites = [
        (['required', 'mandatory', 'shall', 'must'], ['optional', 'may', 'not required']),
        (['permitted', 'allowed', 'authorized'], ['prohibited', 'forbidden', 'not allowed']),
        (['include', 'includes'], ['exclude', 'excludes', 'does not include']),
        (['before', 'prior to'], ['after', 'following', 'subsequent to'])
    ]
    
    for positive_terms, negative_terms in opposites:
        if any(term in c1_lower for term in positive_terms) and \
           any(term in c2_lower for term in negative_terms):
            return True
        if any(term in c2_lower for term in positive_terms) and \
           any(term in c1_lower for term in negative_terms):
            return True
    
    return False

def analyze_legal_structure(text):
    """
    Analyze the legal structure of a document to identify key components.
    """
    structure = {
        'definitions': [],
        'obligations': [],
        'rights': [],
        'procedures': [],
        'penalties': []
    }
    
    clauses = extract_clauses(text)
    
    for clause in clauses:
        clause_lower = clause.lower()
        
        # Identify definitions
        if any(phrase in clause_lower for phrase in ['means', 'defined as', 'shall mean', 'definition']):
            structure['definitions'].append(clause)
        
        # Identify obligations
        if any(phrase in clause_lower for phrase in ['shall', 'must', 'required to', 'obligation']):
            structure['obligations'].append(clause)
        
        # Identify rights
        if any(phrase in clause_lower for phrase in ['right to', 'entitled to', 'may', 'permitted']):
            structure['rights'].append(clause)
        
        # Identify procedures
        if any(phrase in clause_lower for phrase in ['procedure', 'process', 'steps', 'filing']):
            structure['procedures'].append(clause)
        
        # Identify penalties
        if any(phrase in clause_lower for phrase in ['penalty', 'fine', 'violation', 'breach']):
            structure['penalties'].append(clause)
    
    return structure

if __name__ == '__main__':
    sample_text = """
    This is a good clause. The party shall comply with all requirements.
    Notwithstanding the foregoing, this clause is subject to the terms of the main agreement, which is a problem.
    The defendant may file a motion. The defendant shall not file any motions without permission.
    """
    
    print("=== JARVIS Enhanced Legal Analysis ===")
    
    # Extract clauses
    clauses = extract_clauses(sample_text)
    print(f"\nExtracted {len(clauses)} clauses:")
    for i, clause in enumerate(clauses, 1):
        print(f"{i}. {clause}")
    
    # Detect contradictions
    contradictions = detect_contradictions(clauses)
    print(f"\nDetected {len(contradictions)} contradictions:")
    for contradiction in contradictions:
        print(f"- Type: {contradiction['type']}")
        print(f"  Description: {contradiction['description']}")
        print(f"  Clause: {contradiction['clause']}")
        print()
    
    # Analyze structure
    structure = analyze_legal_structure(sample_text)
    print("Legal Structure Analysis:")
    for category, items in structure.items():
        if items:
            print(f"- {category.title()}: {len(items)} found")
