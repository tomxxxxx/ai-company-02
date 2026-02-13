"""
Token Manager für das AI Automation Lab
Verwaltet Token-Budgets und teilt große Tasks in kleinere Chunks auf
"""

import os
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path

class TokenManager:
    """Verwaltet Token-Budgets und Task-Splitting für Rate-Limit-Management"""
    
    def __init__(self, max_tokens_per_chunk: int = 4000):
        self.max_tokens_per_chunk = max_tokens_per_chunk
        
    def estimate_tokens(self, text: str) -> int:
        """
        Schätzt Token-Anzahl basierend auf Zeichen-Count
        Approximation: ~4 Zeichen = 1 Token (konservativ)
        """
        return len(text) // 3  # Konservative Schätzung
    
    def estimate_file_tokens(self, file_path: str) -> int:
        """Schätzt Token-Anzahl einer Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.estimate_tokens(content)
        except Exception:
            return 0
    
    def estimate_directory_tokens(self, directory_path: str, extensions: List[str] = None) -> Dict[str, int]:
        """
        Schätzt Token-Anzahl aller Dateien in einem Verzeichnis
        Returns: {file_path: token_count}
        """
        if extensions is None:
            extensions = ['.py', '.md', '.txt', '.json', '.yaml', '.yml']
            
        token_counts = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            return token_counts
            
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                token_count = self.estimate_file_tokens(str(file_path))
                if token_count > 0:
                    token_counts[str(file_path)] = token_count
                    
        return token_counts
    
    def split_file_analysis_task(self, directory_path: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Teilt eine Verzeichnis-Analyse in kleinere Token-Chunks auf
        Returns: Liste von Sub-Tasks, jede unter max_tokens_per_chunk
        """
        token_counts = self.estimate_directory_tokens(directory_path, extensions)
        
        if not token_counts:
            return []
            
        # Sortiere Dateien nach Token-Count (kleinste zuerst)
        sorted_files = sorted(token_counts.items(), key=lambda x: x[1])
        
        chunks = []
        current_chunk = {
            'files': [],
            'total_tokens': 0,
            'task_type': 'file_analysis',
            'directory': directory_path
        }
        
        for file_path, token_count in sorted_files:
            # Wenn eine einzelne Datei zu groß ist, erstelle eigenen Chunk
            if token_count > self.max_tokens_per_chunk:
                # Aktuellen Chunk abschließen falls nicht leer
                if current_chunk['files']:
                    chunks.append(current_chunk.copy())
                    current_chunk = {
                        'files': [],
                        'total_tokens': 0,
                        'task_type': 'file_analysis',
                        'directory': directory_path
                    }
                
                # Große Datei als eigener Chunk
                chunks.append({
                    'files': [file_path],
                    'total_tokens': token_count,
                    'task_type': 'large_file_analysis',
                    'directory': directory_path,
                    'requires_splitting': True
                })
                continue
            
            # Prüfe ob Datei in aktuellen Chunk passt
            if current_chunk['total_tokens'] + token_count <= self.max_tokens_per_chunk:
                current_chunk['files'].append(file_path)
                current_chunk['total_tokens'] += token_count
            else:
                # Aktuellen Chunk abschließen und neuen starten
                if current_chunk['files']:
                    chunks.append(current_chunk.copy())
                
                current_chunk = {
                    'files': [file_path],
                    'total_tokens': token_count,
                    'task_type': 'file_analysis',
                    'directory': directory_path
                }
        
        # Letzten Chunk hinzufügen falls nicht leer
        if current_chunk['files']:
            chunks.append(current_chunk)
            
        return chunks
    
    def create_analysis_subtasks(self, task_description: str, target_directories: List[str]) -> List[Dict[str, Any]]:
        """
        Erstellt eine Liste von Analyse-Sub-Tasks für mehrere Verzeichnisse
        """
        all_subtasks = []
        
        for directory in target_directories:
            chunks = self.split_file_analysis_task(directory)
            
            for i, chunk in enumerate(chunks):
                subtask = {
                    'id': f"{directory.replace('/', '_')}_{i+1}",
                    'title': f"Analyse {directory} - Teil {i+1}/{len(chunks)}",
                    'description': f"{task_description} - Verzeichnis: {directory}",
                    'chunk_info': chunk,
                    'estimated_tokens': chunk['total_tokens'],
                    'status': 'pending'
                }
                all_subtasks.append(subtask)
                
        return all_subtasks
    
    def validate_token_budget(self, estimated_tokens: int, safety_margin: float = 0.8) -> bool:
        """
        Prüft ob eine Task innerhalb des Token-Budgets liegt
        safety_margin: Prozent des Limits als Sicherheitspuffer
        """
        safe_limit = int(self.max_tokens_per_chunk * safety_margin)
        return estimated_tokens <= safe_limit
    
    def get_chunk_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Erstellt Zusammenfassung der Chunk-Aufteilung"""
        total_files = sum(len(chunk['files']) for chunk in chunks)
        total_tokens = sum(chunk['total_tokens'] for chunk in chunks)
        
        return {
            'total_chunks': len(chunks),
            'total_files': total_files,
            'total_estimated_tokens': total_tokens,
            'average_tokens_per_chunk': total_tokens // len(chunks) if chunks else 0,
            'max_tokens_per_chunk': max(chunk['total_tokens'] for chunk in chunks) if chunks else 0,
            'chunks_requiring_splitting': len([c for c in chunks if c.get('requires_splitting', False)])
        }