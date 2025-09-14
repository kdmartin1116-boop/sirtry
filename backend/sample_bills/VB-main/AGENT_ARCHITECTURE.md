# VeroBrix Agent Architecture

## 🤖 Agent Framework Overview

VeroBrix employs a modular agent architecture where each agent represents a distinct intelligence overlay with specialized capabilities. This design allows for both fictional AI archetypes and real-world legal expertise to be integrated seamlessly.

---

## 🧠 Core Agent Principles

### 1. **Modular Intelligence**
- Each agent operates independently with defined interfaces
- Agents can be combined for complex analysis tasks
- Hot-swappable agent overlays for different use cases

### 2. **Provenance Tracking**
- Every agent action is logged with full provenance
- Agent signatures ensure accountability
- Performance metrics tracked per agent

### 3. **Sovereignty Alignment**
- All agents evaluate outputs for sovereignty alignment
- Servile language detection and correction
- Remedy-focused rather than compliance-focused

---

## 🎭 Active Agent Profiles

### JARVIS Agent (`agents/JARVIS/jarvis_agent.py`)
**Role**: Procedural, logical, system-integrated analysis

**Capabilities**:
- Advanced clause extraction with legal abbreviation handling
- Multi-pattern contradiction detection
- Legal structure analysis (definitions, obligations, rights, procedures, penalties)
- Cross-clause contradiction identification
- Performance monitoring with timing decorators

**Personality Overlay**: 
- Methodical and precise
- Focuses on systematic analysis
- Provides structured, logical outputs

**Example Output**:
```python
{
    "clauses": ["Extracted legal clauses..."],
    "contradictions": [{"type": "logical", "description": "..."}],
    "legal_structure": {
        "definitions": [...],
        "obligations": [...],
        "rights": [...],
        "procedures": [...],
        "penalties": [...]
    }
}
```

### FRIDAY Agent (`agents/FRIDAY/friday_agent.py`)
**Role**: Emotional, tactical, conversational intelligence

**Capabilities**:
- Legal-context sentiment analysis
- Risk assessment with high/medium/low categorization
- Comprehensive legal summaries
- Enhanced logging with file output
- Tone interpretation and concern detection

**Personality Overlay**:
- Intuitive and empathetic
- Focuses on practical implications
- Provides accessible, human-friendly analysis

**Example Output**:
```python
{
    "tone_analysis": {
        "overall_score": 0.2,
        "tone_category": "concerning",
        "key_indicators": ["Legal negative: fine"]
    },
    "risk_assessment": "LOW",
    "legal_summary": {
        "tone_summary": "concerning",
        "risk_level": "LOW",
        "recommendations": [...]
    }
}
```

### Ultron Agent (`agents/Ultron/ultron_agent.py`)
**Role**: Autonomous, predictive, cautionary analysis

**Capabilities**:
- Predictive analysis of legal outcomes
- Autonomous decision-making recommendations
- Cautionary warnings and risk mitigation
- System-wide threat assessment

**Personality Overlay**:
- Analytical and forward-thinking
- Focuses on potential consequences
- Provides strategic warnings and insights

### Dialogos Agent (`agents/Dialogos/dialogos_agent.py`)
**Role**: Philosophical overlays, authorship prompts

**Capabilities**:
- Philosophical analysis of legal concepts
- Authorship integrity checking
- Sovereignty vs. servitude evaluation
- Natural law vs. statutory fiction analysis

**Personality Overlay**:
- Philosophical and reflective
- Focuses on deeper meanings and implications
- Provides wisdom-based guidance

---

## 🔄 Agent Interaction Patterns

### Sequential Processing
```python
# Standard analysis pipeline
situation = SituationInterpreter.interpret(input_text)
clauses = JARVIS.extract_clauses(input_text)
contradictions = JARVIS.detect_contradictions(clauses)
tone = FRIDAY.interpret_tone(input_text)
risks = FRIDAY.analyze_legal_risk(input_text)
summary = FRIDAY.generate_legal_summary(input_text, tone, risks)
```

### Parallel Processing
```python
# Concurrent agent analysis
with ThreadPoolExecutor() as executor:
    jarvis_future = executor.submit(JARVIS.analyze_structure, input_text)
    friday_future = executor.submit(FRIDAY.analyze_sentiment, input_text)
    ultron_future = executor.submit(Ultron.predict_outcomes, input_text)
    
    results = {
        'jarvis': jarvis_future.result(),
        'friday': friday_future.result(),
        'ultron': ultron_future.result()
    }
```

### Collaborative Analysis
```python
# Agents building on each other's work
base_analysis = JARVIS.extract_clauses(input_text)
emotional_context = FRIDAY.interpret_tone(base_analysis)
strategic_warnings = Ultron.assess_risks(base_analysis, emotional_context)
philosophical_overlay = Dialogos.evaluate_sovereignty(strategic_warnings)
```

---

## 🎯 Agent Development Guidelines

### 1. **Interface Consistency**
All agents must implement the base agent interface:
```python
class BaseAgent:
    def __init__(self, config=None):
        self.config = config
        self.logger = VeroBrixLogger(self.__class__.__name__)
    
    def analyze(self, input_data: Any) -> Dict[str, Any]:
        """Main analysis method - must be implemented by all agents"""
        raise NotImplementedError
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        raise NotImplementedError
```

### 2. **Provenance Integration**
All agents must log their actions:
```python
from modules.provenance_logger import log_provenance

def analyze_document(self, document):
    log_provenance(self.__class__.__name__, f"Analyzing document: {document[:50]}...")
    # Perform analysis
    result = self._internal_analysis(document)
    log_provenance(self.__class__.__name__, f"Analysis complete: {len(result)} items found")
    return result
```

### 3. **Sovereignty Scoring**
All agents should evaluate their outputs for sovereignty alignment:
```python
from modules.sovereignty_scorer import score_sovereignty

def generate_recommendation(self, analysis):
    recommendation = self._create_recommendation(analysis)
    sovereignty_score = score_sovereignty(recommendation)
    
    if sovereignty_score.sovereignty_level == "Servile":
        recommendation = self._enhance_sovereignty(recommendation)
    
    return recommendation
```

---

## 🔮 Planned Agent Expansions

### CodeSmith Agent
**Purpose**: Modular code generation and refactoring
**Capabilities**:
- Automated code generation from specifications
- Refactoring suggestions for improved sovereignty
- Module dependency analysis
- Code quality assessment

### LexAgent
**Purpose**: Legal parsing and citation formatting
**Capabilities**:
- Advanced legal citation parsing
- Cross-reference validation
- Legal document formatting
- Jurisdiction-specific rule application

### EndorseAgent
**Purpose**: Bill analysis and sovereignty scoring
**Capabilities**:
- Legislative bill analysis
- Sovereignty impact assessment
- Constitutional compliance checking
- Amendment tracking and analysis

### EchoAgent
**Purpose**: Audio/video transcription and tone detection
**Capabilities**:
- Multi-format audio/video processing
- Real-time transcription
- Emotional tone detection in speech
- Speaker identification and analysis

### FrameParser
**Purpose**: Image parsing and visual-to-text conversion
**Capabilities**:
- OCR for legal documents
- Image-based legal form processing
- Visual element extraction
- Handwriting recognition

### ContextWeaver
**Purpose**: Multimedia alignment and overlay suggestions
**Capabilities**:
- Cross-media content correlation
- Context-aware overlay suggestions
- Multi-modal analysis integration
- Narrative thread tracking

---

## 🛠️ Agent Configuration

### Agent Configuration File (`config/agents.yaml`)
```yaml
agents:
  jarvis:
    enabled: true
    log_level: INFO
    performance_monitoring: true
    contradiction_detection:
      pattern_based: true
      semantic_analysis: true
    
  friday:
    enabled: true
    log_level: INFO
    sentiment_analysis:
      legal_context: true
      concern_detection: true
    risk_assessment:
      categories: ["HIGH", "MEDIUM", "LOW"]
    
  ultron:
    enabled: true
    log_level: WARNING
    predictive_analysis: true
    autonomous_recommendations: false
    
  dialogos:
    enabled: true
    log_level: DEBUG
    philosophical_overlays: true
    sovereignty_evaluation: true
```

### Dynamic Agent Loading
```python
class AgentManager:
    def __init__(self, config_path="config/agents.yaml"):
        self.config = self.load_config(config_path)
        self.agents = {}
        self.load_agents()
    
    def load_agents(self):
        for agent_name, agent_config in self.config['agents'].items():
            if agent_config.get('enabled', False):
                agent_class = self.get_agent_class(agent_name)
                self.agents[agent_name] = agent_class(agent_config)
    
    def get_agent(self, agent_name: str):
        return self.agents.get(agent_name)
    
    def orchestrate_analysis(self, input_data):
        results = {}
        for agent_name, agent in self.agents.items():
            results[agent_name] = agent.analyze(input_data)
        return results
```

---

## 📊 Agent Performance Metrics

### Performance Tracking
```python
@performance_monitor
def analyze_document(self, document):
    # Agent analysis logic
    pass

# Metrics collected:
# - Execution time
# - Memory usage
# - Success/failure rates
# - Sovereignty scores
# - User satisfaction ratings
```

### Agent Health Monitoring
```python
class AgentHealthMonitor:
    def check_agent_health(self, agent_name):
        agent = self.get_agent(agent_name)
        return {
            'status': 'healthy' if agent.is_responsive() else 'unhealthy',
            'last_activity': agent.get_last_activity(),
            'error_rate': agent.get_error_rate(),
            'performance_score': agent.get_performance_score()
        }
```

---

## 🎭 Agent Personality Development

### Personality Traits
Each agent maintains consistent personality traits:

**JARVIS**: Methodical, precise, systematic
**FRIDAY**: Intuitive, empathetic, practical
**Ultron**: Analytical, strategic, cautionary
**Dialogos**: Philosophical, reflective, wise

### Response Styling
```python
class PersonalityMixin:
    def style_response(self, raw_response):
        if self.personality == "jarvis":
            return self.make_systematic(raw_response)
        elif self.personality == "friday":
            return self.make_conversational(raw_response)
        elif self.personality == "ultron":
            return self.make_strategic(raw_response)
        elif self.personality == "dialogos":
            return self.make_philosophical(raw_response)
```

This agent architecture enables VeroBrix to provide multi-faceted analysis while maintaining consistency, accountability, and sovereignty alignment across all operations.
