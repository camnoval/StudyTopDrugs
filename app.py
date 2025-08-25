"""
Drug Study Platform - Interactive pharmaceutical education application
Clean, web-ready version with improved formatting and styling
"""

import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
from datetime import datetime, timedelta


class DrugStudyApp:
    """Main Drug Study Application Class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Drug Study Platform")
        self.root.geometry("1400x900")
        
        # File paths and constants
        self.progress_file = "study_progress.json"
        
        # Session variables
        self.current_mode = None
        self.current_questions = []
        self.current_question_index = 0
        self.session_correct = 0
        self.session_total = 0
        
        # Selection variables - Initialize BEFORE load_data()
        self.selected_sections = {}
        self.selected_drugs = {}
        
        # Load data and setup
        self.load_data()
        self.load_progress()
        self.setup_styles()
        self.create_main_menu()
    
    def load_data(self):
        """Load and process the CSV data"""
        file_path = r"C:\Users\camer\Documents\Coding\drugs.csv"
        df = pd.read_csv(file_path)
        
        # Filter out section headers (rows starting with #)
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
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
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
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_main_menu(self):
        """Create the main menu interface with modern design"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title with emoji
        title_label = ttk.Label(main_frame, text="🏥 Drug Study Platform", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # Progress overview
        self.create_progress_overview(main_frame)
        
        # Study mode buttons with descriptions
        button_data = [
            ("🎯 Matching Game", "Match drug names with information", self.open_matching_game),
            ("❓ Q&A Practice", "Test knowledge with questions", self.open_qa_practice),
            ("📚 Learn Mode", "Study with flashcards", self.open_learn_mode),
            ("⚙️ Drug Selection", "Choose drugs to study", self.open_drug_selection),
            ("📈 Progress Tracker", "View study statistics", self.open_progress_tracker),
            ("🚪 Exit", "Close application", self.root.quit)
        ]
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        for i, (title, desc, command) in enumerate(button_data):
            row, col = divmod(i, 3)
            
            btn_container = ttk.LabelFrame(button_frame, text=desc, padding="10")
            btn_container.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
            
            ttk.Button(btn_container, text=title, command=command, 
                      style="Large.TButton", width=18).pack()
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)
    
    def create_progress_overview(self, parent):
        """Create progress overview section"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Your Progress", padding="15")
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 30))
        
        total_accuracy = (self.progress['total_correct'] / max(self.progress['total_questions'], 1)) * 100
        
        stats = [
            ("Questions:", self.progress['total_questions']),
            ("Correct:", self.progress['total_correct']),
            ("Accuracy:", f"{total_accuracy:.1f}%"),
            ("Sessions:", len(self.progress['session_history']))
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(progress_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=0, column=i*2, sticky="w", padx=(0, 5))
            ttk.Label(progress_frame, text=str(value), font=('Arial', 10)).grid(
                row=0, column=i*2+1, sticky="w", padx=(0, 20))
    
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
    
    # ==================== DRUG SELECTION ====================
    
    def open_drug_selection(self):
        """Open drug/section selection interface"""
        self.clear_window()
        
        # Create scrollable frame
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="⚙️ Drug Selection", style="Title.TLabel").pack(pady=(0, 20))
        
        # Quick selection buttons
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill="x", pady=(0, 20))
        
        quick_buttons = [
            ("Select All", self.select_all_drugs),
            ("Deselect All", self.deselect_all_drugs),
            ("Reset Default", self.reset_drug_selection)
        ]
        
        for text, command in quick_buttons:
            ttk.Button(quick_frame, text=text, command=command, 
                      style="Primary.TButton").pack(side="left", padx=(0, 10))
        
        # Section selection
        for section_name, section_data in self.sections.items():
            section_frame = ttk.LabelFrame(main_frame, text=section_name, padding="10")
            section_frame.pack(fill="x", pady=(0, 10))
            
            # Section checkbox
            section_cb = ttk.Checkbutton(
                section_frame, 
                text=f"Include entire section ({len(section_data)} drugs)",
                variable=self.selected_sections[section_name],
                command=lambda sn=section_name: self.toggle_section(sn)
            )
            section_cb.pack(anchor="w", pady=(0, 10))
            
            # Individual drug checkboxes
            drug_frame = ttk.Frame(section_frame)
            drug_frame.pack(fill="x")
            
            for i, (idx, row) in enumerate(section_data.iterrows()):
                drug_text = f"{row['Generic Name']} ({row['Brand Name(s)']})"
                drug_cb = ttk.Checkbutton(drug_frame, text=drug_text[:60] + "..." if len(drug_text) > 60 else drug_text,
                                        variable=self.selected_drugs[idx])
                drug_cb.grid(row=i//2, column=i%2, sticky="w", padx=(20, 0), pady=2)
        
        # Navigation
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill="x", pady=20)
        
        ttk.Button(nav_frame, text="← Back", command=self.create_main_menu, 
                  style="Primary.TButton").pack(side="left")
        ttk.Button(nav_frame, text="Save Selection", command=self.save_drug_selection, 
                  style="Primary.TButton").pack(side="right")
        
        # Mousewheel binding
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def toggle_section(self, section_name):
        """Toggle all drugs in a section"""
        is_selected = self.selected_sections[section_name].get()
        section_data = self.sections[section_name]
        
        for idx, row in section_data.iterrows():
            self.selected_drugs[idx].set(is_selected)
    
    def select_all_drugs(self):
        """Select all drugs and sections"""
        for var in self.selected_sections.values():
            var.set(True)
        for var in self.selected_drugs.values():
            var.set(True)
    
    def deselect_all_drugs(self):
        """Deselect all drugs and sections"""
        for var in self.selected_sections.values():
            var.set(False)
        for var in self.selected_drugs.values():
            var.set(False)
    
    def reset_drug_selection(self):
        """Reset to default (all selected)"""
        self.select_all_drugs()
    
    def save_drug_selection(self):
        """Save selection and return to main menu"""
        selected_count = sum(1 for var in self.selected_drugs.values() if var.get())
        messagebox.showinfo("Selection Saved", f"✅ {selected_count} drugs selected!")
        self.create_main_menu()
    
    # ==================== MATCHING GAME ====================
    
    def open_matching_game(self):
        """Open matching game setup"""
        selected_data = self.get_selected_data()
        if selected_data.empty:
            return
        
        self.clear_window()
        self.current_mode = "matching"
        
        main_frame = ttk.Frame(self.root, padding="30")
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
                    values=list(self.df.columns), state="readonly", width=25).grid(
            row=0, column=1, padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Category 2:", font=('Arial', 12, 'bold')).grid(
            row=0, column=2, padx=10, pady=5, sticky="w")
        ttk.Combobox(selection_frame, textvariable=self.category2, 
                    values=list(self.df.columns), state="readonly", width=25).grid(
            row=0, column=3, padx=10, pady=5)
        
        # Buttons
        ttk.Button(main_frame, text="🎮 Start Game", 
                  command=lambda: self.start_matching_game(selected_data), 
                  style="Large.TButton").grid(row=2, column=0, columnspan=4, pady=20)
        
        ttk.Button(main_frame, text="← Back", command=self.create_main_menu, 
                  style="Primary.TButton").grid(row=3, column=0, columnspan=4)
    
    def start_matching_game(self, data):
        """Start the matching game"""
        cat1, cat2 = self.category1.get(), self.category2.get()
        
        if not cat1 or not cat2 or cat1 == cat2:
            messagebox.showerror("Invalid Selection", "Please select two different categories.")
            return
        
        self.clear_window()
        self.selected_cards = []
        self.card_buttons = []
        
        game_frame = ttk.Frame(self.root, padding="20")
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
        ttk.Button(game_frame, text="← Back", command=self.create_main_menu, 
                  style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=20)
    
    def select_card(self, btn):
        """Handle card selection"""
        if len(self.selected_cards) < 2 and btn not in self.selected_cards and btn['state'] != 'disabled':
            self.selected_cards.append(btn)
            btn.config(style="Selected.TButton")
            
            if len(self.selected_cards) == 2:
                self.root.after(500, self.check_match)
    
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
                    self.create_main_menu()
            else:
                for btn in self.selected_cards:
                    btn.config(style="Error.TButton")
                self.root.after(1000, self.reset_selected_cards)
            
            self.selected_cards.clear()
    
    def reset_selected_cards(self):
        """Reset card appearance after error"""
        for btn in self.card_buttons:
            if btn.cget('style') == 'Error.TButton':
                btn.config(style="TButton")
    
    # ==================== Q&A PRACTICE ====================
    
    def open_qa_practice(self):
        """Open Q&A practice mode"""
        selected_data = self.get_selected_data()
        if selected_data.empty:
            return
        
        self.current_mode = "qa"
        self.generate_questions(selected_data)
        self.current_question_index = 0
        self.session_correct = 0
        self.session_total = 0
        
        self.show_question()
    
    def generate_questions(self, data):
        """Generate Q&A questions"""
        self.current_questions = []
        question_types = [
            ("Generic Name", "Brand Name(s)", "What is the brand name for {}?"),
            ("Brand Name(s)", "Generic Name", "What is the generic name for {}?"),
            ("Generic Name", "Drug Class", "What drug class does {} belong to?"),
            ("Generic Name", "Indication", "What is {} used for?"),
            ("Generic Name", "Side Effects", "What are the main side effects of {}?"),
            ("Drug Class", "Generic Name", "Name a drug from the {} class:"),
        ]
        
        for _, row in data.iterrows():
            for q_col, a_col, q_template in question_types:
                if pd.notna(row[q_col]) and pd.notna(row[a_col]):
                    question = {
                        'question': q_template.format(row[q_col]),
                        'correct_answer': str(row[a_col]),
                        'drug_index': row.name,
                        'type': f"{q_col}_to_{a_col}"
                    }
                    self.current_questions.append(question)
        
        random.shuffle(self.current_questions)
    
    def show_question(self):
        """Display current question"""
        if self.current_question_index >= len(self.current_questions):
            self.end_qa_session()
            return
        
        self.clear_window()
        question = self.current_questions[self.current_question_index]
        
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill="both", expand=True)
        
        # Progress
        progress_text = f"Question {self.current_question_index + 1} of {len(self.current_questions)} | Score: {self.session_correct}/{self.session_total}"
        ttk.Label(main_frame, text="❓ Q&A Practice", style="Title.TLabel").pack(pady=(0, 10))
        ttk.Label(main_frame, text=progress_text, font=('Arial', 12)).pack(pady=(0, 20))
        
        # Question
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding="25")
        question_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(question_frame, text=question['question'], font=('Arial', 16), 
                 wraplength=800, justify='center').pack()
        
        # Answer input
        answer_frame = ttk.LabelFrame(main_frame, text="Your Answer", padding="20")
        answer_frame.pack(fill="x", pady=(0, 20))
        
        self.answer_var = tk.StringVar()
        answer_entry = ttk.Entry(answer_frame, textvariable=self.answer_var, 
                               font=('Arial', 14), width=50, justify='center')
        answer_entry.pack(pady=10)
        answer_entry.focus()
        answer_entry.bind('<Return>', lambda e: self.check_qa_answer())
        
        ttk.Label(answer_frame, text="💡 Press Enter to submit", 
                 font=('Arial', 10), foreground='gray').pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        buttons = [
            ("✓ Submit", self.check_qa_answer),
            ("👁️ Show Answer", self.show_qa_answer),
            ("⏭️ Skip", self.skip_qa_question),
            ("🏁 End Session", self.end_qa_session)
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, 
                      style="Primary.TButton").pack(side="left", padx=5)
    
    def check_qa_answer(self):
        """Check user's answer"""
        question = self.current_questions[self.current_question_index]
        user_answer = self.answer_var.get().strip().lower()
        correct_answer = question['correct_answer'].strip().lower()
        
        self.session_total += 1
        
        # Check answer (with partial matching)
        is_correct = False
        if user_answer in correct_answer or correct_answer in user_answer:
            is_correct = True
        elif len(user_answer) > 3 and any(word in correct_answer.split() 
                                        for word in user_answer.split() if len(word) > 3):
            is_correct = True
        
        if is_correct:
            self.session_correct += 1
            messagebox.showinfo("✅ Correct!", f"Great job!\n\nAnswer: {question['correct_answer']}")
        else:
            messagebox.showinfo("❌ Incorrect", 
                              f"Not quite right.\n\nCorrect: {question['correct_answer']}\nYours: {self.answer_var.get()}")
        
        # Update drug performance tracking
        drug_idx = question['drug_index']
        if str(drug_idx) not in self.progress['drug_performance']:
            self.progress['drug_performance'][str(drug_idx)] = {'correct': 0, 'total': 0}
        
        self.progress['drug_performance'][str(drug_idx)]['total'] += 1
        if is_correct:
            self.progress['drug_performance'][str(drug_idx)]['correct'] += 1
        
        self.next_qa_question()
    
    def show_qa_answer(self):
        """Show correct answer"""
        question = self.current_questions[self.current_question_index]
        messagebox.showinfo("💡 Answer", f"Correct answer: {question['correct_answer']}")
        self.next_qa_question()
    
    def skip_qa_question(self):
        """Skip current question"""
        self.next_qa_question()
    
    def next_qa_question(self):
        """Move to next question"""
        self.current_question_index += 1
        self.show_question()
    
    def end_qa_session(self):
        """End Q&A session and show results"""
        # Update progress
        self.progress['total_questions'] += self.session_total
        self.progress['total_correct'] += self.session_correct
        
        # Record session
        session_record = {
            'date': datetime.now().isoformat(),
            'mode': 'qa_practice',
            'total': self.session_total,
            'correct': self.session_correct,
            'accuracy': (self.session_correct / max(self.session_total, 1)) * 100
        }
        self.progress['session_history'].append(session_record)
        
        self.save_progress()
        
        # Show results
        accuracy = (self.session_correct / max(self.session_total, 1)) * 100
        performance_msg = ("🌟 Outstanding!" if accuracy >= 90 else
                         "👍 Great job!" if accuracy >= 75 else
                         "📚 Good progress!" if accuracy >= 60 else
                         "💪 Keep practicing!")
        
        messagebox.showinfo("📊 Session Complete!", 
                          f"Questions: {self.session_total}\n"
                          f"Correct: {self.session_correct}\n"
                          f"Accuracy: {accuracy:.1f}%\n\n{performance_msg}")
        
        self.create_main_menu()
    
    # ==================== LEARN MODE ====================
    
    def open_learn_mode(self):
        """Open flashcard learning mode"""
        selected_data = self.get_selected_data()
        if selected_data.empty:
            return
        
        self.current_mode = "learn"
        self.current_cards = selected_data.to_dict('records')
        self.current_card_index = 0
        random.shuffle(self.current_cards)
        
        self.show_flashcard()
    
    def show_flashcard(self):
        """Show current flashcard"""
        if self.current_card_index >= len(self.current_cards):
            messagebox.showinfo("📚 Complete!", "You've reviewed all selected drugs! Great job!")
            self.create_main_menu()
            return
        
        self.clear_window()
        card = self.current_cards[self.current_card_index]
        
        main_frame = ttk.Frame(self.root, padding="25")
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
        
        ttk.Button(nav_frame, text="🏠 Menu", command=self.create_main_menu,
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
    
    # ==================== PROGRESS TRACKER ====================
    
    def open_progress_tracker(self):
        """Open progress tracking interface"""
        self.clear_window()
        
        # Scrollable frame
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(scrollable_frame, padding="25")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="📈 Progress Tracker", style="Title.TLabel").pack(pady=(0, 25))
        
        # Overall Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Overall Statistics", padding="20")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        total_accuracy = (self.progress['total_correct'] / max(self.progress['total_questions'], 1)) * 100
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")
        
        stats_data = [
            ("📝 Questions", self.progress['total_questions']),
            ("✅ Correct", self.progress['total_correct']),
            ("🎯 Accuracy", f"{total_accuracy:.1f}%"),
            ("📚 Sessions", len(self.progress['session_history']))
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
        
        # Recent Sessions
        if self.progress['session_history']:
            sessions_frame = ttk.LabelFrame(main_frame, text="🕒 Recent Sessions", padding="20")
            sessions_frame.pack(fill="x", pady=(0, 20))
            
            columns = ("Date", "Mode", "Questions", "Correct", "Accuracy")
            tree = ttk.Treeview(sessions_frame, columns=columns, show="headings", height=8)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            
            # Add recent sessions
            recent_sessions = self.progress['session_history'][-15:]
            for session in reversed(recent_sessions):
                date_str = datetime.fromisoformat(session['date']).strftime("%m/%d %H:%M")
                mode_str = session['mode'].replace('_', ' ').title()
                tree.insert("", "end", values=(
                    date_str, mode_str, session['total'], 
                    session['correct'], f"{session['accuracy']:.1f}%"
                ))
            
            tree.pack(fill="x")
        
        # Drug Performance
        if self.progress['drug_performance']:
            drug_frame = ttk.LabelFrame(main_frame, text="💊 Drug Performance", padding="20")
            drug_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(drug_frame, text="Drugs needing more practice (lowest accuracy first):",
                     font=('Arial', 11, 'bold')).pack(anchor="w", pady=(0, 10))
            
            # Calculate drug stats
            drug_stats = []
            for drug_idx, perf in self.progress['drug_performance'].items():
                try:
                    idx = int(drug_idx)
                    if idx < len(self.df):
                        drug_name = self.df.iloc[idx]['Generic Name']
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
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=25)
        
        ttk.Button(button_frame, text="🗑️ Clear Progress", command=self.clear_progress,
                  style="Primary.TButton").pack(side="left")
        ttk.Button(button_frame, text="💾 Export Data", command=self.export_progress,
                  style="Primary.TButton").pack(side="left", padx=(10, 0))
        ttk.Button(button_frame, text="← Back", command=self.create_main_menu,
                  style="Primary.TButton").pack(side="right")
        
        # Mousewheel binding
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def clear_progress(self):
        """Clear all progress data"""
        if messagebox.askyesno("Clear Progress", "⚠️ Clear ALL progress data? This cannot be undone!"):
            self.progress = {
                'total_questions': 0,
                'total_correct': 0,
                'session_history': [],
                'drug_performance': {}
            }
            self.save_progress()
            messagebox.showinfo("✅ Cleared", "All progress data cleared.")
            self.open_progress_tracker()
    
    def export_progress(self):
        """Export progress to JSON file"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'overall_stats': {
                    'total_questions': self.progress['total_questions'],
                    'total_correct': self.progress['total_correct'],
                    'accuracy': (self.progress['total_correct'] / max(self.progress['total_questions'], 1)) * 100
                },
                'session_history': self.progress['session_history'],
                'drug_performance': self.progress['drug_performance']
            }
            
            filename = f"drug_study_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("💾 Export Complete", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    try:
        app = DrugStudyApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        input("Press Enter to exit...")