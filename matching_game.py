
# matching_game.py - Matching game implementation
import tkinter as tk
from tkinter import messagebox, ttk
import random

class MatchingGame:
    """Handles the matching game functionality"""
    
    def __init__(self, app):
        self.app = app
        self.selected_cards = []
        self.card_buttons = []
        self.matches = []
        self.category1 = None
        self.category2 = None
    
    def open_matching_game(self):
        """Open matching game setup"""
        selected_data = self.app.get_selected_data()
        if selected_data.empty:
            return
        
        self.app.clear_window()
        
        main_frame = ttk.Frame(self.app.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="🎯 Matching Game Setup", style="Title.TLabel").grid(
            row=0, column=0, columnspan=4, pady=(0, 30))
        
        # Category selection
        self.category1 = tk.StringVar()
        self.category2 = tk.StringVar()
        
        selection_frame = ttk.LabelFrame(main_frame, text="Select Categories to Match", padding="20")
        selection_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(selection_frame, text="Category 1:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Combobox(selection_frame, textvariable=self.category1, 
                    values=list(self.app.data_manager.df.columns), state="readonly", width=25).grid(
            row=0, column=1, padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Category 2:", font=('Arial', 12, 'bold')).grid(
            row=0, column=2, padx=10, pady=5, sticky="w")
        ttk.Combobox(selection_frame, textvariable=self.category2, 
                    values=list(self.app.data_manager.df.columns), state="readonly", width=25).grid(
            row=0, column=3, padx=10, pady=5)
        
        # Buttons
        ttk.Button(main_frame, text="🎮 Start Game", 
                  command=lambda: self.start_matching_game(selected_data), 
                  style="Large.TButton").grid(row=2, column=0, columnspan=4, pady=20)
        
        ttk.Button(main_frame, text="← Back", command=self.app.create_main_menu, 
                  style="Primary.TButton").grid(row=3, column=0, columnspan=4)
    
    def start_matching_game(self, data):
        """Start the matching game"""
        cat1, cat2 = self.category1.get(), self.category2.get()
        
        if not cat1 or not cat2 or cat1 == cat2:
            messagebox.showerror("Invalid Selection", "Please select two different categories.")
            return
        
        self.app.clear_window()
        self.selected_cards = []
        self.card_buttons = []
        
        game_frame = ttk.Frame(self.app.root, padding="20")
        game_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(game_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(header_frame, text="🎯 Matching Game", style="Title.TLabel").pack()
        ttk.Label(header_frame, text=f"Match {cat1} with {cat2}", 
                 font=('Arial', 14)).pack(pady=5)
        
        # Prepare game data
        num_pairs = min(len(data), 8)
        sample_data = data.sample(num_pairs) if len(data) >= num_pairs else data
        
        self.matches = list(zip(sample_data[cat1], sample_data[cat2]))
        items1 = sample_data[cat1].tolist()
        items2 = sample_data[cat2].tolist()
        
        random.shuffle(items1)
        random.shuffle(items2)
        
        # Create game board
        board_frame = ttk.LabelFrame(game_frame, text="Game Board", padding="20")
        board_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Column headers
        ttk.Label(board_frame, text=cat1, style="Subtitle.TLabel").grid(row=0, column=0, pady=(0, 10))
        ttk.Label(board_frame, text=cat2, style="Subtitle.TLabel").grid(row=0, column=1, pady=(0, 10))
        
        # Create cards
        for i, item in enumerate(items1):
            btn = ttk.Button(board_frame, text=str(item)[:50], width=45)
            btn.config(command=lambda b=btn: self.select_card(b))
            btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.card_buttons.append(btn)
        
        for i, item in enumerate(items2):
            btn = ttk.Button(board_frame, text=str(item)[:50], width=45)
            btn.config(command=lambda b=btn: self.select_card(b))
            btn.grid(row=i+1, column=1, padx=10, pady=5, sticky="ew")
            self.card_buttons.append(btn)
        
        # Controls
        ttk.Button(game_frame, text="← Back", command=self.app.create_main_menu, 
                  style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=20)
    
    def select_card(self, btn):
        """Handle card selection"""
        if len(self.selected_cards) < 2 and btn not in self.selected_cards and btn['state'] != 'disabled':
            self.selected_cards.append(btn)
            btn.config(style="Selected.TButton")
            
            if len(self.selected_cards) == 2:
                self.app.root.after(500, self.check_match)
    
    def check_match(self):
        """Check if cards match"""
        if len(self.selected_cards) == 2:
            card1, card2 = self.selected_cards
            match_found = False
            
            for match in self.matches:
                if ((str(match[0])[:50] == card1['text'] and str(match[1])[:50] == card2['text']) or
                    (str(match[1])[:50] == card1['text'] and str(match[0])[:50] == card2['text'])):
                    match_found = True
                    break
            
            if match_found:
                for btn in self.selected_cards:
                    btn.config(state="disabled", style="Matched.TButton")
                    if btn in self.card_buttons:
                        self.card_buttons.remove(btn)
                
                if not self.card_buttons:
                    messagebox.showinfo("🎉 Congratulations!", "You matched all cards!")
                    self.app.create_main_menu()
            else:
                for btn in self.selected_cards:
                    btn.config(style="Error.TButton")
                self.app.root.after(1000, self.reset_selected_cards)
            
            self.selected_cards.clear()
    
    def reset_selected_cards(self):
        """Reset card appearance after error"""
        for btn in self.card_buttons:
            if btn.cget('style') == 'Error.TButton':
                btn.config(style="TButton")

