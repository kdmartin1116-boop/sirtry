"""
VeroBrix Provenance Logging System
==================================

Tracks all interactions, decisions, and authorship within the VeroBrix system.
Maintains comprehensive audit trails for sovereignty and accountability.

Author: VeroBrix Sovereign Intelligence System
Created: 2025-01-17
"""

import json
import hashlib
import datetime
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from contextlib import contextmanager

from .logger import VeroBrixLogger
from .exceptions import VeroBrixError


@dataclass
class ProvenanceEntry:
    """Single provenance record entry."""
    
    # Core identification
    entry_id: str
    timestamp: str
    session_id: str
    
    # Authorship tracking
    agent_name: str
    human_operator: Optional[str]
    system_version: str
    
    # Action details
    action_type: str  # analysis, generation, decision, input, output
    action_description: str
    input_hash: Optional[str]
    output_hash: Optional[str]
    
    # Context and metadata
    document_path: Optional[str]
    legal_context: Optional[str]
    sovereignty_score: Optional[float]
    confidence_level: Optional[float]
    
    # Relationships
    parent_entry_id: Optional[str]
    related_entries: List[str]
    
    # Integrity
    entry_hash: Optional[str] = None


class ProvenanceLogger:
    """
    Comprehensive provenance logging system for VeroBrix.
    
    Tracks all system interactions, decisions, and authorship
    to maintain sovereignty and accountability.
    """
    
    def __init__(self, config_manager=None):
        """Initialize the provenance logging system."""
        self.logger = VeroBrixLogger(__name__)
        self.config = config_manager
        
        # Session management
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.datetime.now().isoformat()
        
        # Storage paths
        self.provenance_dir = Path("logs/provenance")
        self.provenance_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.provenance_dir / f"session_{self.session_id[:8]}.json"
        self.master_log = self.provenance_dir / "master_provenance.jsonl"
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Entry tracking
        self.entries: List[ProvenanceEntry] = []
        self.entry_index: Dict[str, ProvenanceEntry] = {}
        
        # Initialize session
        self._initialize_session()
        
        self.logger.info(f"Provenance logging initialized for session {self.session_id[:8]}")
    
    def _initialize_session(self):
        """Initialize a new provenance session."""
        session_info = {
            "session_id": self.session_id,
            "start_time": self.session_start,
            "system_version": "VeroBrix v2.0 - Sovereign Modular Intelligence",
            "provenance_version": "1.0",
            "entries": []
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_info, f, indent=2)
    
    def _generate_hash(self, content: Any) -> str:
        """Generate SHA-256 hash of content."""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        elif not isinstance(content, str):
            content = str(content)
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _generate_entry_hash(self, entry: ProvenanceEntry) -> str:
        """Generate integrity hash for provenance entry."""
        # Create hash from core entry data (excluding the hash field itself)
        entry_dict = asdict(entry)
        entry_dict.pop('entry_hash', None)
        return self._generate_hash(entry_dict)
    
    def log_action(self,
                   action_type: str,
                   action_description: str,
                   agent_name: str = "System",
                   input_data: Any = None,
                   output_data: Any = None,
                   document_path: str = None,
                   legal_context: str = None,
                   sovereignty_score: float = None,
                   confidence_level: float = None,
                   human_operator: str = None,
                   parent_entry_id: str = None,
                   related_entries: List[str] = None) -> str:
        """
        Log a provenance entry for any system action.
        
        Args:
            action_type: Type of action (analysis, generation, decision, etc.)
            action_description: Human-readable description of the action
            agent_name: Name of the agent performing the action
            input_data: Input data for the action
            output_data: Output data from the action
            document_path: Path to related document
            legal_context: Legal context or jurisdiction
            sovereignty_score: Sovereignty alignment score (0-1)
            confidence_level: Confidence in the action (0-1)
            human_operator: Human operator if applicable
            parent_entry_id: ID of parent entry for hierarchical tracking
            related_entries: List of related entry IDs
            
        Returns:
            str: Entry ID for the logged action
        """
        with self._lock:
            # Generate entry ID
            entry_id = str(uuid.uuid4())
            
            # Generate content hashes
            input_hash = self._generate_hash(input_data) if input_data else None
            output_hash = self._generate_hash(output_data) if output_data else None
            
            # Create provenance entry
            entry = ProvenanceEntry(
                entry_id=entry_id,
                timestamp=datetime.datetime.now().isoformat(),
                session_id=self.session_id,
                agent_name=agent_name,
                human_operator=human_operator,
                system_version="VeroBrix v2.0",
                action_type=action_type,
                action_description=action_description,
                input_hash=input_hash,
                output_hash=output_hash,
                document_path=document_path,
                legal_context=legal_context,
                sovereignty_score=sovereignty_score,
                confidence_level=confidence_level,
                parent_entry_id=parent_entry_id,
                related_entries=related_entries or []
            )
            
            # Generate integrity hash
            entry.entry_hash = self._generate_entry_hash(entry)
            
            # Store entry
            self.entries.append(entry)
            self.entry_index[entry_id] = entry
            
            # Persist to files
            self._persist_entry(entry)
            
            self.logger.debug(f"Logged provenance entry: {entry_id[:8]} - {action_description}")
            
            return entry_id
    
    def _persist_entry(self, entry: ProvenanceEntry):
        """Persist entry to storage files."""
        entry_dict = asdict(entry)
        
        # Append to master log (JSONL format)
        with open(self.master_log, 'a') as f:
            f.write(json.dumps(entry_dict) + '\n')
        
        # Update session file
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data['entries'].append(entry_dict)
            session_data['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update session file: {e}")
    
    def get_entry(self, entry_id: str) -> Optional[ProvenanceEntry]:
        """Retrieve a specific provenance entry."""
        return self.entry_index.get(entry_id)
    
    def get_entries_by_agent(self, agent_name: str) -> List[ProvenanceEntry]:
        """Get all entries for a specific agent."""
        return [entry for entry in self.entries if entry.agent_name == agent_name]
    
    def get_entries_by_type(self, action_type: str) -> List[ProvenanceEntry]:
        """Get all entries of a specific action type."""
        return [entry for entry in self.entries if entry.action_type == action_type]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate a summary of the current session."""
        if not self.entries:
            return {
                "session_id": self.session_id,
                "start_time": self.session_start,
                "entry_count": 0,
                "agents": [],
                "action_types": []
            }
        
        agents = list(set(entry.agent_name for entry in self.entries))
        action_types = list(set(entry.action_type for entry in self.entries))
        
        sovereignty_scores = [
            entry.sovereignty_score for entry in self.entries 
            if entry.sovereignty_score is not None
        ]
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_start,
            "entry_count": len(self.entries),
            "agents": agents,
            "action_types": action_types,
            "avg_sovereignty_score": sum(sovereignty_scores) / len(sovereignty_scores) if sovereignty_scores else None,
            "duration_minutes": (datetime.datetime.now() - datetime.datetime.fromisoformat(self.session_start)).total_seconds() / 60
        }
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of all provenance entries."""
        results = {
            "total_entries": len(self.entries),
            "verified_entries": 0,
            "corrupted_entries": [],
            "missing_hashes": []
        }
        
        for entry in self.entries:
            if not entry.entry_hash:
                results["missing_hashes"].append(entry.entry_id)
                continue
            
            # Recalculate hash
            calculated_hash = self._generate_entry_hash(entry)
            
            if calculated_hash == entry.entry_hash:
                results["verified_entries"] += 1
            else:
                results["corrupted_entries"].append({
                    "entry_id": entry.entry_id,
                    "stored_hash": entry.entry_hash,
                    "calculated_hash": calculated_hash
                })
        
        results["integrity_percentage"] = (results["verified_entries"] / results["total_entries"]) * 100 if results["total_entries"] > 0 else 100
        
        return results
    
    @contextmanager
    def track_operation(self, operation_name: str, agent_name: str = "System", **kwargs):
        """Context manager for tracking complex operations."""
        start_time = datetime.datetime.now()
        
        # Log operation start
        start_entry_id = self.log_action(
            action_type="operation_start",
            action_description=f"Started operation: {operation_name}",
            agent_name=agent_name,
            **kwargs
        )
        
        try:
            yield start_entry_id
            
            # Log successful completion
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.log_action(
                action_type="operation_complete",
                action_description=f"Completed operation: {operation_name} (duration: {duration:.2f}s)",
                agent_name=agent_name,
                parent_entry_id=start_entry_id,
                confidence_level=1.0
            )
            
        except Exception as e:
            # Log operation failure
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.log_action(
                action_type="operation_error",
                action_description=f"Failed operation: {operation_name} - {str(e)} (duration: {duration:.2f}s)",
                agent_name=agent_name,
                parent_entry_id=start_entry_id,
                confidence_level=0.0
            )
            raise
    
    def export_session(self, format_type: str = "json") -> str:
        """Export current session data."""
        if format_type == "json":
            export_data = {
                "session_info": self.get_session_summary(),
                "entries": [asdict(entry) for entry in self.entries],
                "integrity_check": self.verify_integrity()
            }
            
            export_file = self.provenance_dir / f"export_{self.session_id[:8]}.json"
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return str(export_file)
        
        else:
            raise VeroBrixError(f"Unsupported export format: {format_type}")
    
    def close_session(self):
        """Close the current provenance session."""
        # Log session closure
        self.log_action(
            action_type="session_close",
            action_description="Provenance session closed",
            agent_name="ProvenanceLogger"
        )
        
        # Generate final session summary
        summary = self.get_session_summary()
        integrity = self.verify_integrity()
        
        # Update session file with final data
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data.update({
                "end_time": datetime.datetime.now().isoformat(),
                "final_summary": summary,
                "integrity_check": integrity,
                "status": "closed"
            })
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to finalize session file: {e}")
        
        self.logger.info(f"Provenance session {self.session_id[:8]} closed with {len(self.entries)} entries")


# Global provenance logger instance
_global_provenance_logger = None


def get_provenance_logger(config_manager=None) -> ProvenanceLogger:
    """Get or create the global provenance logger instance."""
    global _global_provenance_logger
    
    if _global_provenance_logger is None:
        _global_provenance_logger = ProvenanceLogger(config_manager)
    
    return _global_provenance_logger


def log_provenance(action_type: str, description: str, agent_name: str = "System", **kwargs) -> str:
    """Convenience function for logging provenance entries."""
    logger = get_provenance_logger()
    return logger.log_action(action_type, description, agent_name, **kwargs)
