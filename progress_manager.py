# progress_manager.py - Handles progress tracking and persistence
import json
from datetime import datetime

class ProgressManager:
    """Manages study progress and statistics"""
    
    def __init__(self):
        self.progress_file = "study_progress.json"
        self.progress = {}
    
    def load_progress(self):
        """Load study progress from JSON file"""
        try:
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        except:
            self.progress = {
                'total_questions': 0,
                'total_correct': 0,
                'session_history': [],
                'drug_performance': {}
            }
    
    def save_progress(self):
        """Save study progress to JSON file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Failed to save progress: {str(e)}")
    
    def update_session_stats(self, session_correct, session_total):
        """Update overall session statistics"""
        self.progress['total_questions'] += session_total
        self.progress['total_correct'] += session_correct
    
    def record_session(self, mode, session_correct, session_total):
        """Record a completed session"""
        session_record = {
            'date': datetime.now().isoformat(),
            'mode': mode,
            'total': session_total,
            'correct': session_correct,
            'accuracy': (session_correct / max(session_total, 1)) * 100
        }
        self.progress['session_history'].append(session_record)
        self.save_progress()
    
    def update_drug_performance(self, drug_index, is_correct):
        """Update performance tracking for a specific drug"""
        drug_key = str(drug_index)
        if drug_key not in self.progress['drug_performance']:
            self.progress['drug_performance'][drug_key] = {'correct': 0, 'total': 0}
        
        self.progress['drug_performance'][drug_key]['total'] += 1
        if is_correct:
            self.progress['drug_performance'][drug_key]['correct'] += 1

