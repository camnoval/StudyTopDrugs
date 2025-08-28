
# drug_study_app.py - Main application class
import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
from datetime import datetime

from data_manager import DataManager
from progress_manager import ProgressManager
from ui_components import UIComponents
from matching_game import MatchingGame
from qa_practice import QAPractice
from learn_mode import LearnMode
from progress_tracker import ProgressTracker
from drug_selector import DrugSelector

class DrugStudyApp:
    """Main Drug Study Application Class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Drug Study Platform")
        self.root.geometry("1400x900")
        
        # Initialize managers
        self.data_manager = DataManager()
        self.progress_manager = ProgressManager()
        self.ui_components = UIComponents(self.root)
        
        # Initialize game modes
        self.matching_game = MatchingGame(self)
        self.qa_practice = QAPractice(self)
        self.learn_mode = LearnMode(self)
        self.progress_tracker = ProgressTracker(self)
        self.drug_selector = DrugSelector(self)
        
        # Load data and setup
        self.data_manager.load_data()
        self.progress_manager.load_progress()
        self.ui_components.setup_styles()
        self.create_main_menu()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_main_menu(self):
        """Create the main menu interface"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🏥 Drug Study Platform", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # Progress overview
        self.ui_components.create_progress_overview(main_frame, self.progress_manager.progress)
        
        # Study mode buttons
        button_data = [
            ("🎯 Matching Game", "Match drug names with information", self.matching_game.open_matching_game),
            ("❓ Q&A Practice", "Test knowledge with questions", self.qa_practice.open_qa_practice),
            ("📚 Learn Mode", "Study with flashcards", self.learn_mode.open_learn_mode),
            ("⚙️ Drug Selection", "Choose drugs to study", self.drug_selector.open_drug_selection),
            ("📈 Progress Tracker", "View study statistics", self.progress_tracker.open_progress_tracker),
            ("🚪 Exit", "Close application", self.root.quit)
        ]
        
        self.ui_components.create_menu_buttons(main_frame, button_data)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def get_selected_data(self):
        """Get currently selected drugs"""
        return self.data_manager.get_selected_data()
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")
