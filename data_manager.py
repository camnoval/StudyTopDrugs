
# data_manager.py - Handles all data loading and management
import pandas as pd
import tkinter as tk
from tkinter import messagebox

class DataManager:
    """Manages drug data loading and selection"""
    
    def __init__(self):
        self.df = None
        self.sections = {}
        self.selected_sections = {}
        self.selected_drugs = {}
        self.file_path = r"C:\Users\camer\Documents\Coding\drugs.csv"
    
    def load_data(self):
        """Load and process the CSV data"""
        try:
            df = pd.read_csv(self.file_path)
            
            # Filter out section headers
            self.df = df[~df['Generic Name'].str.startswith('#', na=False)].reset_index(drop=True)
            
            # Define drug sections
            self.sections = {
                "Cardiovascular HTN (1-10)": self.df.iloc[0:10],
                "Cardiovascular Other (11-20)": self.df.iloc[10:20],
                "Diabetes (21-30)": self.df.iloc[20:30],
                "Antibiotics (31-41)": self.df.iloc[30:41],
                "Pain Management (42-52)": self.df.iloc[41:52],
                "Psychiatry Dep/Anx (53-63)": self.df.iloc[52:63],
                "Elderly Care (64-84)": self.df.iloc[63:84],
                "Pulmonary (85-94)": self.df.iloc[84:94],
                "Women's Health (95-106)": self.df.iloc[94:106],
                "Psych/Neuro (107-124)": self.df.iloc[106:124]
            }
            
            # Initialize selections (all selected by default)
            for section in self.sections:
                self.selected_sections[section] = tk.BooleanVar(value=True)
            
            for idx, row in self.df.iterrows():
                self.selected_drugs[idx] = tk.BooleanVar(value=True)
                
        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Failed to load drug data: {str(e)}")
    
    def get_selected_data(self):
        """Get currently selected drugs"""
        selected_data = []
        
        for section_name, is_selected in self.selected_sections.items():
            if is_selected.get():
                section_data = self.sections[section_name]
                for idx, row in section_data.iterrows():
                    if self.selected_drugs[idx].get():
                        selected_data.append(row)
        
        if not selected_data:
            messagebox.showwarning("No Selection", "Please select at least one drug or section.")
            return pd.DataFrame()
        
        return pd.DataFrame(selected_data)

