"""
VeroBrix Database Integration Module

Provides database functionality for storing and retrieving legal documents,
analysis results, and system data using SQLite with full-text search capabilities.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from contextlib import contextmanager
import hashlib

from .config_manager import config
from .exceptions import DatabaseError, ValidationError
from .logger import get_logger, log_performance

logger = get_logger(__name__)

class DatabaseManager:
    """
    Database manager for VeroBrix system.
    
    Handles all database operations including:
    - Document storage and retrieval
    - Analysis results storage
    - Full-text search capabilities
    - Data integrity and backup
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Optional path to database file. Uses config if not provided.
        """
        self.db_path = db_path or config.get_database_path()
