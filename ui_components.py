# ui_components.py - Common UI components and styling
import tkinter as tk
from tkinter import ttk

class UIComponents:
    """Common UI components and styling utilities"""
    
    def __init__(self, root):
        self.root = root
    
    def setup_styles(self):
        """Configure modern styles for better UI"""
        style = ttk.Style()
        
        # Button styles
        style.configure("Large.TButton", font=('Arial', 12, 'bold'), padding=(15, 8))
        style.configure("Primary.TButton", font=('Arial', 10, 'bold'))
        
        # Game styles
        style.configure("Selected.TButton", foreground="blue")
        style.configure("Matched.TButton", foreground="green", background="lightgreen")
        style.configure("Error.TButton", foreground="red", background="lightcoral")
        
        # Label styles
        style.configure("Title.TLabel", font=('Arial', 18, 'bold'))
        style.configure("Subtitle.TLabel", font=('Arial', 14, 'bold'))
    
    def create_progress_overview(self, parent, progress_data):
        """Create progress overview section"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Your Progress", padding="15")
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 30))
        
        total_accuracy = (progress_data['total_correct'] / max(progress_data['total_questions'], 1)) * 100
        
        stats = [
            ("Questions:", progress_data['total_questions']),
            ("Correct:", progress_data['total_correct']),
            ("Accuracy:", f"{total_accuracy:.1f}%"),
            ("Sessions:", len(progress_data['session_history']))
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(progress_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=0, column=i*2, sticky="w", padx=(0, 5))
            ttk.Label(progress_frame, text=str(value), font=('Arial', 10)).grid(
                row=0, column=i*2+1, sticky="w", padx=(0, 20))
    
    def create_menu_buttons(self, parent, button_data):
        """Create menu buttons with descriptions"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        for i, (title, desc, command) in enumerate(button_data):
            row, col = divmod(i, 3)
            
            btn_container = ttk.LabelFrame(button_frame, text=desc, padding="10")
            btn_container.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
            
            ttk.Button(btn_container, text=title, command=command, 
                      style="Large.TButton", width=18).pack()
        
        # Configure grid weights
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame with canvas and scrollbar"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel binding
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        return scrollable_frame
