
# progress_tracker.py - Progress tracking and statistics display
import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime

class ProgressTracker:
    """Handles progress tracking interface and statistics"""
    
    def __init__(self, app):
        self.app = app
    
    def open_progress_tracker(self):
        """Open progress tracking interface"""
        self.app.clear_window()
        
        # Create scrollable frame
        scrollable_frame = self.app.ui_components.create_scrollable_frame(self.app.root)
        
        main_frame = ttk.Frame(scrollable_frame, padding="25")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="📈 Progress Tracker", style="Title.TLabel").pack(pady=(0, 25))
        
        # Overall Statistics
        self.create_overall_stats(main_frame)
        
        # Recent Sessions
        if self.app.progress_manager.progress['session_history']:
            self.create_recent_sessions(main_frame)
        
        # Drug Performance
        if self.app.progress_manager.progress['drug_performance']:
            self.create_drug_performance(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def create_overall_stats(self, parent):
        """Create overall statistics section"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Overall Statistics", padding="20")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        progress = self.app.progress_manager.progress
        total_accuracy = (progress['total_correct'] / max(progress['total_questions'], 1)) * 100
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")
        
        stats_data = [
            ("📝 Questions", progress['total_questions']),
            ("✅ Correct", progress['total_correct']),
            ("🎯 Accuracy", f"{total_accuracy:.1f}%"),
            ("📚 Sessions", len(progress['session_history']))
        ]
        
        for i, (label, value) in enumerate(stats_data):
            row, col = divmod(i, 2)
            
            stat_frame = ttk.Frame(stats_grid)
            stat_frame.grid(row=row, column=col, padx=20, pady=10, sticky="ew")
            
            ttk.Label(stat_frame, text=label, font=('Arial', 12, 'bold')).pack()
            ttk.Label(stat_frame, text=str(value), font=('Arial', 16, 'bold'),
                     foreground='#2E86AB').pack()
        
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
    
    def create_recent_sessions(self, parent):
        """Create recent sessions section"""
        sessions_frame = ttk.LabelFrame(parent, text="🕒 Recent Sessions", padding="20")
        sessions_frame.pack(fill="x", pady=(0, 20))
        
        columns = ("Date", "Mode", "Questions", "Correct", "Accuracy")
        tree = ttk.Treeview(sessions_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Add recent sessions
        recent_sessions = self.app.progress_manager.progress['session_history'][-15:]
        for session in reversed(recent_sessions):
            date_str = datetime.fromisoformat(session['date']).strftime("%m/%d %H:%M")
            mode_str = session['mode'].replace('_', ' ').title()
            tree.insert("", "end", values=(
                date_str, mode_str, session['total'], 
                session['correct'], f"{session['accuracy']:.1f}%"
            ))
        
        tree.pack(fill="x")
    
    def create_drug_performance(self, parent):
        """Create drug performance section"""
        drug_frame = ttk.LabelFrame(parent, text="💊 Drug Performance", padding="20")
        drug_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(drug_frame, text="Drugs needing more practice (lowest accuracy first):",
                 font=('Arial', 11, 'bold')).pack(anchor="w", pady=(0, 10))
        
        # Calculate drug stats
        drug_stats = []
        for drug_idx, perf in self.app.progress_manager.progress['drug_performance'].items():
            try:
                idx = int(drug_idx)
                if idx < len(self.app.data_manager.df):
                    drug_name = self.app.data_manager.df.iloc[idx]['Generic Name']
                    accuracy = (perf['correct'] / max(perf['total'], 1)) * 100
                    drug_stats.append({
                        'name': drug_name,
                        'total': perf['total'],
                        'correct': perf['correct'],
                        'accuracy': accuracy
                    })
            except (ValueError, IndexError):
                continue
        
        # Sort by accuracy (lowest first)
        drug_stats.sort(key=lambda x: x['accuracy'])
        
        if drug_stats:
            drug_columns = ("Drug Name", "Questions", "Correct", "Accuracy")
            drug_tree = ttk.Treeview(drug_frame, columns=drug_columns, show="headings", height=10)
            
            for col in drug_columns:
                drug_tree.heading(col, text=col)
                drug_tree.column(col, width=150, anchor="center")
            
            for drug in drug_stats[:15]:  # Show top 15 that need practice
                drug_tree.insert("", "end", values=(
                    drug['name'], drug['total'], drug['correct'], f"{drug['accuracy']:.1f}%"
                ))
            
            drug_tree.pack(fill="x")
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=25)
        
        ttk.Button(button_frame, text="🗑️ Clear Progress", command=self.clear_progress,
                  style="Primary.TButton").pack(side="left")
        ttk.Button(button_frame, text="💾 Export Data", command=self.export_progress,
                  style="Primary.TButton").pack(side="left", padx=(10, 0))
        ttk.Button(button_frame, text="← Back", command=self.app.create_main_menu,
                  style="Primary.TButton").pack(side="right")
    
    def clear_progress(self):
        """Clear all progress data"""
        if messagebox.askyesno("Clear Progress", "⚠️ Clear ALL progress data? This cannot be undone!"):
            self.app.progress_manager.progress = {
                'total_questions': 0,
                'total_correct': 0,
                'session_history': [],
                'drug_performance': {}
            }
            self.app.progress_manager.save_progress()
            messagebox.showinfo("✅ Cleared", "All progress data cleared.")
            self.open_progress_tracker()
    
    def export_progress(self):
        """Export progress to JSON file"""
        try:
            progress = self.app.progress_manager.progress
            export_data = {
                'export_date': datetime.now().isoformat(),
                'overall_stats': {
                    'total_questions': progress['total_questions'],
                    'total_correct': progress['total_correct'],
                    'accuracy': (progress['total_correct'] / max(progress['total_questions'], 1)) * 100
                },
                'session_history': progress['session_history'],
                'drug_performance': progress['drug_performance']
            }
            
            filename = f"drug_study_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("💾 Export Complete", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

