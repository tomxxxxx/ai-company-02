"""
Konfiguration für das AI Automation Lab
Enthält Token-Budgets, Batch-Processing-Einstellungen und System-Parameter
"""

# Token-Management-Konfiguration
TOKEN_BUDGET_LIMITS = {
    # Maximum Token pro einzelner Task/Chunk
    'max_tokens_per_chunk': 4000,
    
    # Sicherheitspuffer (80% des Limits verwenden)
    'safety_margin': 0.8,
    
    # Token-Schätzung: Zeichen zu Token Verhältnis
    'chars_per_token_estimate': 3,  # Konservative Schätzung
    
    # Rate-Limit-Management
    'rate_limit_buffer': 1000,  # Token-Puffer für Rate-Limits
    'max_retries': 3,
    'retry_delay_seconds': 5.0
}

# Batch-Processing-Konfiguration  
BATCH_PROCESSING_CONFIG = {
    # Delay zwischen Sub-Tasks um Rate-Limits zu vermeiden
    'delay_between_subtasks': 2.0,
    
    # Maximale Anzahl paralleler Batches
    'max_concurrent_batches': 1,
    
    # Auto-Resume unterbrochener Batches
    'auto_resume_incomplete': True,
    
    # Speichere Zwischenergebnisse
    'save_intermediate_results': True,
    
    # Cleanup-Einstellungen
    'cleanup_completed_after_days': 7,
    'max_batch_history': 50
}

# Datei-Analyse-Konfiguration
FILE_ANALYSIS_CONFIG = {
    # Unterstützte Dateierweiterungen für Token-Analyse
    'supported_extensions': ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml'],
    
    # Verzeichnisse die ignoriert werden sollen
    'ignore_directories': [
        '__pycache__', 
        '.git', 
        'node_modules', 
        'venv', 
        '.venv',
        'env',
        '.pytest_cache',
        '.coverage'
    ],
    
    # Maximale Dateigröße für Analyse (in Bytes)
    'max_file_size_bytes': 1_000_000,  # 1MB
    
    # Chunk-Größe für große Dateien
    'large_file_chunk_size': 2000  # Token
}

# Logging-Konfiguration für Token-Management
LOGGING_CONFIG = {
    'log_token_usage': True,
    'log_batch_progress': True,
    'log_file_analysis': False,  # Nur bei Debug
    'log_level': 'INFO'
}

# System-Pfade
PATHS = {
    'data_dir': 'data',
    'batch_plans_dir': 'data',
    'logs_dir': 'logs',
    'temp_dir': 'temp'
}

# Entwicklungs-Einstellungen
DEV_SETTINGS = {
    # Trockenlauf-Modus für Testing
    'dry_run_default': False,
    
    # Detaillierte Debug-Ausgaben
    'verbose_token_counting': False,
    
    # Simuliere Rate-Limits für Testing
    'simulate_rate_limits': False
}

# Export der wichtigsten Konfigurationen
__all__ = [
    'TOKEN_BUDGET_LIMITS',
    'BATCH_PROCESSING_CONFIG', 
    'FILE_ANALYSIS_CONFIG',
    'LOGGING_CONFIG',
    'PATHS',
    'DEV_SETTINGS'
]