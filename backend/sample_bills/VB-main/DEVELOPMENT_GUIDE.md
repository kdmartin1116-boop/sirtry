# VeroBrix Development Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Git for version control
- Virtual environment support (venv, conda, or virtualenv)

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd VB

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -c "import spacy; spacy.cli.download('en_core_web_sm')"

# Test the installation
python verobrix_cli.py --version
```

---

## 🏗️ Project Structure

```
VB/
├── agents/                     # AI agent modules
│   ├── JARVIS/                # Logical analysis agent
│   ├── FRIDAY/                # Emotional intelligence agent
│   ├── Ultron/                # Predictive analysis agent
│   └── Dialogos/              # Philosophical overlay agent
├── modules/                   # Core system modules
│   ├── config_manager.py      # Configuration management
│   ├── database.py           # Database operations
│   ├── exceptions.py         # Custom exceptions
│   ├── logger.py             # Logging system
│   ├── nlp_processor.py      # Advanced NLP processing
│   ├── provenance_logger.py  # Provenance tracking
│   ├── remedy_synthesizer.py # Legal remedy generation
│   ├── situation_interpreter.py # Situation analysis
│   └── sovereignty_scorer.py # Sovereignty evaluation
├── corpus/                   # Legal document corpus
│   └── legal/               # Legal texts and references
├── intake/                  # Input document processing
├── output/                  # Analysis results
├── logs/                    # System and provenance logs
│   └── provenance/         # Detailed provenance records
├── tests/                   # Test suites
├── config/                  # Configuration files
├── verobrix_launcher.py     # Main system orchestrator
├── verobrix_cli.py         # Command-line interface
└── requirements.txt         # Python dependencies
```

---

## 🧪 Testing Framework

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_nlp_processor.py -v

# Run with coverage
python -m pytest tests/ --cov=modules --cov-report=html

# Run performance tests
python -m pytest tests/ -m performance
```

### Test Categories
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Module interaction testing
- **Performance Tests**: Speed and memory benchmarks
- **Sovereignty Tests**: Sovereignty scoring validation

### Writing Tests
```python
import pytest
from modules.nlp_processor import LegalNLPProcessor

class TestLegalNLPProcessor:
    def setup_method(self):
        self.processor = LegalNLPProcessor()
    
    def test_entity_extraction(self):
        text = "John Doe signed the contract on January 1, 2024"
        entities = self.processor.extract_legal_entities(text)
        assert len(entities['people']) > 0
        assert len(entities['dates']) > 0
    
    @pytest.mark.performance
    def test_processing_speed(self):
        import time
        text = "Large legal document..." * 1000
        start_time = time.time()
        result = self.processor.process_document(text)
        processing_time = time.time() - start_time
        assert processing_time < 5.0  # Should process in under 5 seconds
```

---

## 🔧 Configuration Management

### Configuration Files
- `config/verobrix.yaml`: Main system configuration
- `config/agents.yaml`: Agent-specific settings (planned)
- `config/logging.yaml`: Logging configuration (planned)

### Configuration Structure
```yaml
# config/verobrix.yaml
system:
  name: "VeroBrix"
  version: "2.0"
  mode: "sovereign_intelligence"

nlp:
  spacy_model: "en_core_web_sm"
  enable_advanced_processing: true
  legal_entity_patterns: true

agents:
  jarvis:
    enabled: true
    performance_monitoring: true
  friday:
    enabled: true
    sentiment_analysis: true
  ultron:
    enabled: true
    predictive_analysis: true
  dialogos:
    enabled: true
    philosophical_overlays: true

logging:
  level: "INFO"
  file_output: true
  provenance_tracking: true

sovereignty:
  scoring_enabled: true
  servile_language_detection: true
  remedy_alignment_checking: true
```

### Using Configuration
```python
from modules.config_manager import ConfigManager

config = ConfigManager()
nlp_settings = config.get_nlp_config()
agent_settings = config.get_agent_config('jarvis')
```

---

## 🤖 Agent Development

### Creating a New Agent
1. Create agent directory: `agents/NewAgent/`
2. Implement agent class with base interface
3. Add configuration entries
4. Write comprehensive tests
5. Update documentation

### Base Agent Template
```python
# agents/NewAgent/new_agent.py
from modules.logger import VeroBrixLogger
from modules.provenance_logger import log_provenance
from modules.sovereignty_scorer import score_sovereignty

class NewAgent:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = VeroBrixLogger(__name__)
        
    def analyze(self, input_data):
        """Main analysis method"""
        log_provenance("NewAgent", f"Starting analysis: {type(input_data)}")
        
        try:
            result = self._perform_analysis(input_data)
            
            # Score for sovereignty alignment
            if isinstance(result, str):
                sovereignty_metrics = score_sovereignty(result)
                result = {
                    'analysis': result,
                    'sovereignty_score': sovereignty_metrics.overall_score
                }
            
            log_provenance("NewAgent", "Analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            log_provenance("NewAgent", f"Analysis failed: {e}")
            raise
    
    def _perform_analysis(self, input_data):
        """Internal analysis logic - implement in subclass"""
        raise NotImplementedError
    
    def get_capabilities(self):
        """Return list of agent capabilities"""
        return ["analysis", "sovereignty_scoring"]
```

---

## 📊 Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for unusual conditions
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical errors that may cause system failure

### Provenance Logging
```python
from modules.provenance_logger import get_provenance_logger

# Get global provenance logger
provenance = get_provenance_logger()

# Log an action
entry_id = provenance.log_action(
    action_type="analysis",
    action_description="Analyzing legal document",
    agent_name="JARVIS",
    input_data=document_text,
    output_data=analysis_result,
    sovereignty_score=0.75,
    confidence_level=0.9
)

# Track complex operations
with provenance.track_operation("document_processing", "FRIDAY") as op_id:
    result = process_document(document)
    # Operation completion logged automatically
```

### Performance Monitoring
```python
from modules.logger import performance_monitor

@performance_monitor
def expensive_operation(data):
    # This function's performance will be automatically tracked
    return process_data(data)
```

---

## 🔍 Debugging and Troubleshooting

### Common Issues

#### 1. spaCy Model Not Found
```bash
# Error: Can't find model 'en_core_web_sm'
# Solution:
python -c "import spacy; spacy.cli.download('en_core_web_sm')"
```

#### 2. Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure you're in the correct directory and virtual environment
cd /path/to/VB
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 3. Configuration Issues
```python
# Check configuration loading
from modules.config_manager import ConfigManager
config = ConfigManager()
print(config.config)  # Should show loaded configuration
```

### Debug Mode
```bash
# Run with debug logging
python verobrix_cli.py -f document.txt --debug

# Check log files
tail -f logs/verobrix.log
tail -f logs/friday_agent.log
```

### Provenance Debugging
```python
# Check provenance logs
from modules.provenance_logger import get_provenance_logger
provenance = get_provenance_logger()

# Get session summary
summary = provenance.get_session_summary()
print(f"Session has {summary['entry_count']} entries")

# Verify integrity
integrity = provenance.verify_integrity()
print(f"Integrity: {integrity['integrity_percentage']:.1f}%")
```

---

## 🚀 Deployment

### Production Setup
```bash
# Create production environment
python -m venv venv_prod
source venv_prod/bin/activate
pip install -r requirements.txt

# Set production configuration
export VEROBRIX_ENV=production
export VEROBRIX_LOG_LEVEL=WARNING

# Run system
python verobrix_launcher.py
```

### Docker Deployment (Planned)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')"

EXPOSE 8000
CMD ["python", "verobrix_launcher.py"]
```

---

## 🔄 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-capability`
3. Make changes with tests
4. Run test suite: `python -m pytest tests/`
5. Update documentation
6. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Include docstrings for all functions and classes
- Write comprehensive tests for new features
- Maintain sovereignty alignment in all outputs
- Log all significant operations with provenance

### Commit Message Format
```
type(scope): description

- feat(agents): add new sovereignty scoring agent
- fix(nlp): resolve entity extraction bug
- docs(readme): update installation instructions
- test(jarvis): add contradiction detection tests
```

---

## 📈 Performance Optimization

### Profiling
```python
import cProfile
import pstats

# Profile a function
cProfile.run('analyze_document(text)', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### Memory Optimization
```python
import tracemalloc

# Track memory usage
tracemalloc.start()
result = process_large_document(document)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

### Caching Strategies
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_nlp_operation(text_hash):
    # Cache expensive operations by text hash
    return process_text(text)
```

---

## 🔮 Future Development

### Roadmap Priorities
1. **Multimedia Pipeline**: Audio/video processing capabilities
2. **Web Interface**: Browser-based user interface
3. **Machine Learning**: Advanced pattern recognition
4. **Corpus Integration**: Full legal database integration
5. **Mobile App**: Smartphone access for field use

### Extension Points
- Custom agent development
- Plugin architecture for specialized analysis
- External API integrations
- Custom sovereignty scoring rules
- Jurisdiction-specific legal modules

### Research Areas
- Advanced contradiction detection algorithms
- Semantic legal reasoning
- Automated remedy synthesis
- Cross-jurisdictional analysis
- Natural language generation for legal documents

---

## 📚 Resources

### Documentation
- [VeroBrix Vision](VEROBRIX_VISION.md)
- [Agent Architecture](AGENT_ARCHITECTURE.md)
- [API Reference](docs/api_reference.md) (planned)
- [User Guide](docs/user_guide.md) (planned)

### External Resources
- [spaCy Documentation](https://spacy.io/usage)
- [NLTK Documentation](https://www.nltk.org/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pytest Documentation](https://docs.pytest.org/)

### Legal Resources
- UCC (Uniform Commercial Code)
- USC (United States Code)
- CFR (Code of Federal Regulations)
- Black's Law Dictionary

This development guide provides the foundation for contributing to and extending the VeroBrix Sovereign Modular Intelligence system.
