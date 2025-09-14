import datetime
import re
import os

def interpret_tone(text):
    """
    Enhanced legal sentiment analysis that considers legal context.
    Returns a detailed analysis rather than just a simple score.
    """
    # Legal-specific positive indicators
    positive_legal = [
        'comply', 'agreement', 'consent', 'authorize', 'permit', 'grant', 'approve',
        'lawful', 'valid', 'proper', 'accordance', 'pursuant', 'entitled', 'right'
    ]
    
    # Legal-specific negative indicators
    negative_legal = [
        'violation', 'breach', 'default', 'penalty', 'fine', 'prohibited', 'forbidden',
        'unlawful', 'invalid', 'improper', 'contrary', 'dispute', 'conflict', 'problem'
    ]
    
    # Neutral legal terms (procedural)
    neutral_legal = [
        'shall', 'may', 'pursuant', 'whereas', 'therefore', 'notwithstanding',
        'subject to', 'provided that', 'except', 'unless'
    ]
    
    # General positive/negative words
    general_positive = ['good', 'great', 'excellent', 'positive', 'beneficial', 'favorable']
    general_negative = ['bad', 'terrible', 'negative', 'harmful', 'unfavorable', 'adverse']
    
    text_lower = text.lower()
    words = text_lower.split()
    
    analysis = {
        'legal_positive': 0,
        'legal_negative': 0,
        'general_positive': 0,
        'general_negative': 0,
        'neutral_legal': 0,
        'overall_score': 0,
        'tone_category': 'neutral',
        'key_indicators': []
    }
    
    # Count different types of sentiment indicators
    for word in words:
        if word in positive_legal:
            analysis['legal_positive'] += 1
            analysis['key_indicators'].append(f"Legal positive: {word}")
        elif word in negative_legal:
            analysis['legal_negative'] += 1
            analysis['key_indicators'].append(f"Legal negative: {word}")
        elif word in general_positive:
            analysis['general_positive'] += 1
            analysis['key_indicators'].append(f"General positive: {word}")
        elif word in general_negative:
            analysis['general_negative'] += 1
            analysis['key_indicators'].append(f"General negative: {word}")
        elif word in neutral_legal:
            analysis['neutral_legal'] += 1
    
    # Calculate weighted score (legal terms have more weight)
    analysis['overall_score'] = (
        (analysis['legal_positive'] * 2) + analysis['general_positive'] -
        (analysis['legal_negative'] * 2) - analysis['general_negative']
    )
    
    # Determine tone category
    if analysis['overall_score'] > 1:
        analysis['tone_category'] = 'positive'
    elif analysis['overall_score'] < -1:
        analysis['tone_category'] = 'negative'
    elif analysis['legal_negative'] > 0 or analysis['general_negative'] > 0:
        analysis['tone_category'] = 'concerning'
    else:
        analysis['tone_category'] = 'neutral'
    
    return analysis

def suggest_remedy(text, tone_analysis):
    """
    Enhanced remedy suggestion based on detailed tone analysis and legal context.
    """
    remedies = []
    
    if tone_analysis['tone_category'] == 'positive':
        remedies.append("Document appears legally sound. Consider preserving these favorable terms.")
        if tone_analysis['legal_positive'] > 0:
            remedies.append("Strong legal language detected. This may provide good protection.")
    
    elif tone_analysis['tone_category'] == 'negative':
        remedies.append("Negative legal language detected. Review for potential risks.")
        
        if tone_analysis['legal_negative'] > 0:
            remedies.append("Legal risk indicators found. Consider:")
            remedies.append("  - Seeking legal counsel for risk assessment")
            remedies.append("  - Negotiating more favorable terms")
            remedies.append("  - Adding protective clauses")
        
        if any('violation' in indicator for indicator in tone_analysis['key_indicators']):
            remedies.append("  - Review compliance requirements")
        
        if any('penalty' in indicator or 'fine' in indicator for indicator in tone_analysis['key_indicators']):
            remedies.append("  - Understand penalty structure and mitigation options")
    
    elif tone_analysis['tone_category'] == 'concerning':
        remedies.append("Mixed or concerning language detected. Recommend careful review.")
        remedies.append("Consider clarifying ambiguous terms and addressing potential issues.")
    
    else:  # neutral
        remedies.append("Neutral legal language. Standard procedural review recommended.")
        if tone_analysis['neutral_legal'] > 2:
            remedies.append("Heavy procedural language detected. Ensure compliance with all requirements.")
    
    # Add specific recommendations based on key indicators
    if any('notwithstanding' in text.lower() for text in [text]):
        remedies.append("'Notwithstanding' clause detected - pay special attention to exceptions.")
    
    if any('subject to' in text.lower() for text in [text]):
        remedies.append("'Subject to' clause detected - review conditional requirements.")
    
    return remedies

def analyze_legal_risk(text):
    """
    Analyze potential legal risks in the text.
    """
    risks = []
    text_lower = text.lower()
    
    # High-risk patterns
    high_risk_patterns = [
        ('waiver', 'Contains waiver language - may limit legal rights'),
        ('indemnify', 'Indemnification clause - potential financial liability'),
        ('liquidated damages', 'Liquidated damages clause - predetermined penalty amounts'),
        ('arbitration', 'Arbitration clause - may limit court access'),
        ('non-compete', 'Non-compete clause - may restrict future opportunities'),
        ('personal guarantee', 'Personal guarantee - individual liability exposure')
    ]
    
    # Medium-risk patterns
    medium_risk_patterns = [
        ('penalty', 'Penalty provisions - review enforcement mechanisms'),
        ('default', 'Default provisions - understand trigger conditions'),
        ('termination', 'Termination clauses - review exit conditions'),
        ('modification', 'Modification terms - understand change procedures')
    ]
    
    for pattern, description in high_risk_patterns:
        if pattern in text_lower:
            risks.append({'level': 'HIGH', 'pattern': pattern, 'description': description})
    
    for pattern, description in medium_risk_patterns:
        if pattern in text_lower:
            risks.append({'level': 'MEDIUM', 'pattern': pattern, 'description': description})
    
    return risks

def generate_legal_summary(text, tone_analysis, risks):
    """
    Generate a comprehensive legal summary of the analyzed text.
    """
    summary = {
        'text_length': len(text),
        'word_count': len(text.split()),
        'tone_summary': tone_analysis['tone_category'],
        'risk_level': 'LOW',
        'key_findings': [],
        'recommendations': []
    }
    
    # Determine overall risk level
    if any(risk['level'] == 'HIGH' for risk in risks):
        summary['risk_level'] = 'HIGH'
    elif any(risk['level'] == 'MEDIUM' for risk in risks):
        summary['risk_level'] = 'MEDIUM'
    
    # Add key findings
    if tone_analysis['legal_positive'] > 0:
        summary['key_findings'].append(f"Found {tone_analysis['legal_positive']} positive legal indicators")
    
    if tone_analysis['legal_negative'] > 0:
        summary['key_findings'].append(f"Found {tone_analysis['legal_negative']} negative legal indicators")
    
    if risks:
        summary['key_findings'].append(f"Identified {len(risks)} potential risk areas")
    
    # Add recommendations
    if summary['risk_level'] == 'HIGH':
        summary['recommendations'].append("Seek legal counsel before proceeding")
    elif summary['risk_level'] == 'MEDIUM':
        summary['recommendations'].append("Consider legal review for risk mitigation")
    
    if tone_analysis['tone_category'] == 'negative':
        summary['recommendations'].append("Review and potentially renegotiate unfavorable terms")
    
    return summary

def log_provenance(agent_name, action):
    """
    Enhanced logging with structured format and file output.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_message = f"[{timestamp}] Agent '{agent_name}': {action}"
    
    # Print to console
    print(log_message)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Write to log file
    try:
        with open("logs/friday_agent.log", "a", encoding='utf-8') as log_file:
            log_file.write(log_message + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

if __name__ == '__main__':
    agent_name = "FRIDAY"
    
    sample_texts = [
        "This is a good clause that grants the party the right to terminate with proper notice.",
        "Notwithstanding the prior statement, this clause is subject to penalty provisions and may result in violation if not followed properly.",
        "The party shall indemnify and hold harmless the other party from all claims and damages."
    ]
    
    print("=== FRIDAY Enhanced Legal Analysis ===")
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n--- Analysis {i} ---")
        print(f"Text: {text}")
        
        # Analyze tone
        tone_analysis = interpret_tone(text)
        print(f"Tone Category: {tone_analysis['tone_category']}")
        print(f"Overall Score: {tone_analysis['overall_score']}")
        
        if tone_analysis['key_indicators']:
            print("Key Indicators:")
            for indicator in tone_analysis['key_indicators']:
                print(f"  - {indicator}")
        
        # Suggest remedies
        remedies = suggest_remedy(text, tone_analysis)
        print("Remedies:")
        for remedy in remedies:
            print(f"  - {remedy}")
        
        # Analyze risks
        risks = analyze_legal_risk(text)
        if risks:
            print("Risk Analysis:")
            for risk in risks:
                print(f"  - {risk['level']} RISK: {risk['description']}")
        
        # Generate summary
        summary = generate_legal_summary(text, tone_analysis, risks)
        print(f"Risk Level: {summary['risk_level']}")
        
        log_provenance(agent_name, f"Completed analysis {i} - Risk: {summary['risk_level']}, Tone: {tone_analysis['tone_category']}")
