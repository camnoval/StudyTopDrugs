# data_manager.py - Handles all data loading and management
import pandas as pd
import tkinter as tk
from tkinter import messagebox

class DataManager:
    """Manages drug data loading and selection"""

    def __init__(self, file_path=None):
        self.df = None
        self.sections = {}
        self.selected_sections = {}
        self.selected_drugs = {}
        self.file_path = file_path or "drugs.csv"

    def load_data(self):
        """Load and process the CSV data dynamically by section headers"""
        try:
            # Read CSV, skip commented lines initially
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            section_name = None
            records = []
            sections = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("#"):
                    # New section header
                    section_name = line[1:].strip()
                    sections[section_name] = []
                elif section_name:
                    # Only add real data rows (skip repeated headers)
                    if not line.lower().startswith("generic name"):
                        sections[section_name].append(line)

            # Flatten into a DataFrame with section info
            all_rows = []
            for section, rows in sections.items():
                for row in rows:
                    all_rows.append((section, row))

            # Convert to DataFrame
            self.df = pd.DataFrame([r[1].split(",") for r in all_rows], columns=[
                "Generic Name", "Brand Name(s)", "Drug Class", "Dosage Forms",
                "Indication", "Side Effects", "Clinical Pearls"
            ])
            self.df['Section'] = [r[0] for r in all_rows]

            # Build sections dictionary
            for section in self.df['Section'].unique():
                self.sections[section] = self.df[self.df['Section'] == section]

            # Initialize selections
            for section in self.sections:
                self.selected_sections[section] = tk.BooleanVar(value=True)

            for idx in self.df.index:
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
