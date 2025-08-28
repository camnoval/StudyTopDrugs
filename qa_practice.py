# qa_practice.py - Q&A practice implementation
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import random

class QAPractice:
    """Handles the Q&A practice functionality"""
    
    def __init__(self, app):
        self.app = app
        self.current_questions = []
        self.current_question_index = 0
        self.session_correct = 0
        self.session_total = 0
        self.answer_var = None
    
    def open_qa_practice(self):
        """Open Q&A practice mode"""
        selected_data = self.app.get_selected_data()
        if selected_data.empty:
            return
        
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
        
        self.app.clear_window()
        question = self.current_questions[self.current_question_index]
        
        main_frame = ttk.Frame(self.app.root, padding="30")
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
        self.app.progress_manager.update_drug_performance(question['drug_index'], is_correct)
        
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
        self.app.progress_manager.update_session_stats(self.session_correct, self.session_total)
        self.app.progress_manager.record_session('qa_practice', self.session_correct, self.session_total)
        
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
        
        self.app.create_main_menu()
