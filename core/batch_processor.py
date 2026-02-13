"""
Batch Processor für das AI Automation Lab
Verarbeitet große Tasks in kleineren Sub-Tasks um Rate-Limits zu vermeiden
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timezone

from core.token_manager import TokenManager

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Verarbeitet große Tasks in kleineren Batches um Rate-Limits zu vermeiden"""
    
    def __init__(self, token_manager: TokenManager = None, delay_between_batches: float = 1.0):
        self.token_manager = token_manager or TokenManager()
        self.delay_between_batches = delay_between_batches
        self.batch_history = []
        
    def create_batch_plan(self, task_description: str, target_directories: List[str]) -> Dict[str, Any]:
        """
        Erstellt einen Batch-Plan für eine große Analyse-Task
        """
        subtasks = self.token_manager.create_analysis_subtasks(task_description, target_directories)
        
        plan = {
            'id': f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            'title': task_description,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'target_directories': target_directories,
            'subtasks': subtasks,
            'status': 'pending',
            'progress': {
                'completed': 0,
                'failed': 0,
                'total': len(subtasks)
            },
            'results': [],
            'errors': []
        }
        
        return plan
    
    def save_batch_plan(self, plan: Dict[str, Any], file_path: str = None) -> str:
        """Speichert einen Batch-Plan in eine JSON-Datei"""
        if file_path is None:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            file_path = data_dir / f"batch_plan_{plan['id']}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Batch plan saved: {file_path}")
        return str(file_path)
    
    def load_batch_plan(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Lädt einen Batch-Plan aus einer JSON-Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
            return plan
        except Exception as e:
            logger.error(f"Failed to load batch plan from {file_path}: {e}")
            return None
    
    def execute_subtask(self, subtask: Dict[str, Any], processor_func: Callable) -> Dict[str, Any]:
        """
        Führt eine einzelne Sub-Task aus
        processor_func: Funktion die die eigentliche Verarbeitung macht
        """
        logger.info(f"Executing subtask: {subtask['id']}")
        
        start_time = time.time()
        result = {
            'subtask_id': subtask['id'],
            'started_at': datetime.now(timezone.utc).isoformat(),
            'status': 'running'
        }
        
        try:
            # Führe die eigentliche Verarbeitung aus
            output = processor_func(subtask)
            
            result.update({
                'status': 'completed',
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'duration_seconds': time.time() - start_time,
                'output': output,
                'files_processed': len(subtask['chunk_info']['files']),
                'tokens_processed': subtask['estimated_tokens']
            })
            
            logger.info(f"Subtask {subtask['id']} completed successfully")
            
        except Exception as e:
            result.update({
                'status': 'failed',
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'duration_seconds': time.time() - start_time,
                'error': str(e),
                'files_processed': 0,
                'tokens_processed': 0
            })
            
            logger.error(f"Subtask {subtask['id']} failed: {e}")
        
        return result
    
    def process_batch(self, plan: Dict[str, Any], processor_func: Callable, 
                     save_progress: bool = True) -> Dict[str, Any]:
        """
        Verarbeitet alle Sub-Tasks eines Batch-Plans
        processor_func: Funktion die einzelne Sub-Tasks verarbeitet
        """
        logger.info(f"Starting batch processing: {plan['id']}")
        
        plan['status'] = 'running'
        plan['started_at'] = datetime.now(timezone.utc).isoformat()
        
        for i, subtask in enumerate(plan['subtasks']):
            if subtask['status'] != 'pending':
                continue  # Skip bereits verarbeitete Sub-Tasks
                
            logger.info(f"Processing subtask {i+1}/{len(plan['subtasks'])}: {subtask['id']}")
            
            # Führe Sub-Task aus
            result = self.execute_subtask(subtask, processor_func)
            plan['results'].append(result)
            
            # Update Progress
            if result['status'] == 'completed':
                plan['progress']['completed'] += 1
                subtask['status'] = 'completed'
            else:
                plan['progress']['failed'] += 1
                subtask['status'] = 'failed'
                plan['errors'].append(result.get('error', 'Unknown error'))
            
            # Speichere Fortschritt
            if save_progress:
                self.save_batch_plan(plan)
            
            # Delay zwischen Sub-Tasks um Rate-Limits zu vermeiden
            if i < len(plan['subtasks']) - 1:  # Nicht nach der letzten Sub-Task
                logger.info(f"Waiting {self.delay_between_batches}s before next subtask...")
                time.sleep(self.delay_between_batches)
        
        # Finalisiere Batch
        plan['status'] = 'completed' if plan['progress']['failed'] == 0 else 'partial'
        plan['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        if save_progress:
            self.save_batch_plan(plan)
        
        logger.info(f"Batch processing completed: {plan['id']}")
        logger.info(f"Results: {plan['progress']['completed']} completed, {plan['progress']['failed']} failed")
        
        return plan
    
    def resume_batch(self, plan_file: str, processor_func: Callable) -> Optional[Dict[str, Any]]:
        """Setzt einen unterbrochenen Batch fort"""
        plan = self.load_batch_plan(plan_file)
        if not plan:
            return None
            
        if plan['status'] == 'completed':
            logger.info(f"Batch {plan['id']} is already completed")
            return plan
        
        logger.info(f"Resuming batch: {plan['id']}")
        return self.process_batch(plan, processor_func)
    
    def get_batch_summary(self, plan: Dict[str, Any]) -> str:
        """Erstellt eine Zusammenfassung eines Batch-Plans"""
        total = plan['progress']['total']
        completed = plan['progress']['completed']
        failed = plan['progress']['failed']
        
        lines = [
            f"Batch: {plan['id']}",
            f"Title: {plan['title']}",
            f"Status: {plan['status']}",
            f"Progress: {completed}/{total} completed, {failed} failed",
        ]
        
        if plan.get('started_at'):
            lines.append(f"Started: {plan['started_at']}")
        if plan.get('completed_at'):
            lines.append(f"Completed: {plan['completed_at']}")
            
        if plan['errors']:
            lines.append(f"Errors: {len(plan['errors'])}")
            for error in plan['errors'][:3]:  # Show first 3 errors
                lines.append(f"  - {error}")
            if len(plan['errors']) > 3:
                lines.append(f"  ... and {len(plan['errors']) - 3} more")
        
        return "\n".join(lines)
    
    def list_batch_files(self, data_dir: str = "data") -> List[str]:
        """Listet alle Batch-Plan-Dateien auf"""
        data_path = Path(data_dir)
        if not data_path.exists():
            return []
            
        batch_files = []
        for file_path in data_path.glob("batch_plan_*.json"):
            batch_files.append(str(file_path))
            
        return sorted(batch_files)
    
    def cleanup_completed_batches(self, data_dir: str = "data", keep_days: int = 7) -> int:
        """Entfernt alte, abgeschlossene Batch-Dateien"""
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=keep_days)
        removed_count = 0
        
        for file_path in self.list_batch_files(data_dir):
            plan = self.load_batch_plan(file_path)
            if not plan:
                continue
                
            if plan['status'] == 'completed' and plan.get('completed_at'):
                completed_at = datetime.fromisoformat(plan['completed_at'].replace('Z', '+00:00'))
                if completed_at < cutoff_date:
                    Path(file_path).unlink()
                    removed_count += 1
                    logger.info(f"Removed old batch file: {file_path}")
        
        return removed_count