
# drug_selector.py - Drug and section selection interface
import tkinter as tk
from tkinter import messagebox, ttk

class DrugSelector:
    """Handles drug and section selection interface"""
    
    def __init__(self, app):
        self.app = app
    
    def open_drug_selection(self):
        """Open drug/section selection interface"""
        self.app.clear_window()
        
        # Create scrollable frame
        scrollable_frame = self.app.ui_components.create_scrollable_frame(self.app.root)
        
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="⚙️ Drug Selection", style="Title.TLabel").pack(pady=(0, 20))
        
        # Quick selection buttons
        self.create_quick_selection_buttons(main_frame)
        
        # Section selection
        self.create_section_selection(main_frame)
        
        # Navigation buttons
        self.create_navigation_buttons(main_frame)
    
    def create_quick_selection_buttons(self, parent):
        """Create quick selection buttons"""
        quick_frame = ttk.Frame(parent)
        quick_frame.pack(fill="x", pady=(0, 20))
        
        quick_buttons = [
            ("Select All", self.select_all_drugs),
            ("Deselect All", self.deselect_all_drugs),
            ("Reset Default", self.reset_drug_selection)
        ]
        
        for text, command in quick_buttons:
            ttk.Button(quick_frame, text=text, command=command, 
                      style="Primary.TButton").pack(side="left", padx=(0, 10))
    
    def create_section_selection(self, parent):
        """Create section selection interface"""
        for section_name, section_data in self.app.data_manager.sections.items():
            section_frame = ttk.LabelFrame(parent, text=section_name, padding="10")
            section_frame.pack(fill="x", pady=(0, 10))
            
            # Section checkbox
            section_cb = ttk.Checkbutton(
                section_frame, 
                text=f"Include entire section ({len(section_data)} drugs)",
                variable=self.app.data_manager.selected_sections[section_name],
                command=lambda sn=section_name: self.toggle_section(sn)
            )
            section_cb.pack(anchor="w", pady=(0, 10))
            
            # Individual drug checkboxes
            drug_frame = ttk.Frame(section_frame)
            drug_frame.pack(fill="x")
            
            for i, (idx, row) in enumerate(section_data.iterrows()):
                drug_text = f"{row['Generic Name']} ({row['Brand Name(s)']})"
                drug_cb = ttk.Checkbutton(
                    drug_frame, 
                    text=drug_text[:60] + "..." if len(drug_text) > 60 else drug_text,
                    variable=self.app.data_manager.selected_drugs[idx]
                )
                drug_cb.grid(row=i//2, column=i%2, sticky="w", padx=(20, 0), pady=2)
    
    def create_navigation_buttons(self, parent):
        """Create navigation buttons"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill="x", pady=20)
        
        ttk.Button(nav_frame, text="← Back", command=self.app.create_main_menu, 
                  style="Primary.TButton").pack(side="left")
        ttk.Button(nav_frame, text="Save Selection", command=self.save_drug_selection, 
                  style="Primary.TButton").pack(side="right")
    
    def toggle_section(self, section_name):
        """Toggle all drugs in a section"""
        is_selected = self.app.data_manager.selected_sections[section_name].get()
        section_data = self.app.data_manager.sections[section_name]
        
        for idx, row in section_data.iterrows():
            self.app.data_manager.selected_drugs[idx].set(is_selected)
    
    def select_all_drugs(self):
        """Select all drugs and sections"""
        for var in self.app.data_manager.selected_sections.values():
            var.set(True)
        for var in self.app.data_manager.selected_drugs.values():
            var.set(True)
    
    def deselect_all_drugs(self):
        """Deselect all drugs and sections"""
        for var in self.app.data_manager.selected_sections.values():
            var.set(False)
        for var in self.app.data_manager.selected_drugs.values():
            var.set(False)
    
    def reset_drug_selection(self):
        """Reset to default (all selected)"""
        self.select_all_drugs()
    
    def save_drug_selection(self):
        """Save selection and return to main menu"""
        selected_count = sum(1 for var in self.app.data_manager.selected_drugs.values() if var.get())
        messagebox.showinfo("Selection Saved", f"✅ {selected_count} drugs selected!")
        self.app.create_main_menu()