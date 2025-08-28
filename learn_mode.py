

# learn_mode.py - Learn mode (flashcards) implementation
import tkinter as tk
from tkinter import messagebox, ttk
import random

class LearnMode:
    """Handles the learn mode (flashcards) functionality"""
    
    def __init__(self, app):
        self.app = app
        self.current_cards = []
        self.current_card_index = 0
    
    def open_learn_mode(self):
        """Open flashcard learning mode"""
        selected_data = self.app.get_selected_data()
        if selected_data.empty:
            return
        
        self.current_cards = selected_data.to_dict('records')
        self.current_card_index = 0
        random.shuffle(self.current_cards)
        
        self.show_flashcard()
    
    def show_flashcard(self):
        """Show current flashcard"""
        if self.current_card_index >= len(self.current_cards):
            messagebox.showinfo("📚 Complete!", "You've reviewed all selected drugs! Great job!")
            self.app.create_main_menu()
            return
        
        self.app.clear_window()
        card = self.current_cards[self.current_card_index]
        
        main_frame = ttk.Frame(self.app.root, padding="25")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        ttk.Label(main_frame, text="📚 Learn Mode", style="Title.TLabel").pack()
        
        progress_text = f"Card {self.current_card_index + 1} of {len(self.current_cards)}"
        ttk.Label(main_frame, text=progress_text, font=('Arial', 12)).pack(pady=(5, 20))
        
        # Card content
        card_frame = ttk.LabelFrame(main_frame, text=f"💊 {card.get('Generic Name', 'Drug Info')}", 
                                   padding="25")
        card_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Scrollable text
        text_widget = tk.Text(card_frame, wrap=tk.WORD, font=('Arial', 12), height=18,
                             bg='white', relief='flat', padx=20, pady=20)
        scrollbar = ttk.Scrollbar(card_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Format drug information
        info_sections = [
            ("🏷️ Generic Name", card.get('Generic Name', 'N/A')),
            ("🏪 Brand Name(s)", card.get('Brand Name(s)', 'N/A')),
            ("🧪 Drug Class", card.get('Drug Class', 'N/A')),
            ("💊 Dosage Forms", card.get('Dosage Forms', 'N/A')),
            ("🎯 Indication", card.get('Indication', 'N/A')),
            ("⚠️ Side Effects", card.get('Side Effects', 'N/A')),
            ("💡 Clinical Pearls", card.get('Clinical Pearls', 'N/A'))
        ]
        
        for header, content in info_sections:
            if content and str(content) != 'N/A':
                text_widget.insert(tk.END, f"{header}\n", "header")
                text_widget.insert(tk.END, f"{content}\n\n", "content")
        
        text_widget.tag_configure("header", font=('Arial', 14, 'bold'), foreground='#2E86AB')
        text_widget.tag_configure("content", font=('Arial', 12), lmargin1=20, lmargin2=20)
        text_widget.config(state=tk.DISABLED)
        
        # Navigation
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill="x")
        
        ttk.Button(nav_frame, text="← Previous", command=self.previous_flashcard,
                  state="normal" if self.current_card_index > 0 else "disabled",
                  style="Primary.TButton").pack(side="left")
        
        ttk.Button(nav_frame, text="🔀 Shuffle", command=self.shuffle_flashcards,
                  style="Primary.TButton").pack(side="left", padx=(20, 0))
        
        ttk.Button(nav_frame, text="🏠 Menu", command=self.app.create_main_menu,
                  style="Primary.TButton").pack(side="right", padx=(0, 20))
        
        ttk.Button(nav_frame, text="Next →", command=self.next_flashcard,
                  style="Primary.TButton").pack(side="right")
    
    def next_flashcard(self):
        """Show next flashcard"""
        self.current_card_index += 1
        self.show_flashcard()
    
    def previous_flashcard(self):
        """Show previous flashcard"""
        if self.current_card_index > 0:
            self.current_card_index -= 1
            self.show_flashcard()
    
    def shuffle_flashcards(self):
        """Shuffle and restart flashcards"""
        random.shuffle(self.current_cards)
        self.current_card_index = 0
        messagebox.showinfo("🔀 Shuffled", "Cards shuffled! Starting over.")
        self.show_flashcard()
