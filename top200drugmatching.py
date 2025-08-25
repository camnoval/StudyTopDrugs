import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import random

# Set the relative path for the CSV file
file_path = r"C:\Users\camer\Documents\Coding\drugs.csv" #os.path.join(os.path.dirname(__file__), 'drugs.csv')
df = pd.read_csv(file_path)

# Filter out rows that start with # (section headers)
df = df[~df['Generic Name'].str.startswith('#', na=False)]
# Reset index after filtering
df = df.reset_index(drop=True)

def start_matching_game():
    root = tk.Tk()
    root.title("Drug Matching Game")

    current_streak = 0
    longest_streak = 0
    selected_cards = []
    retry_queue = []
    questions_asked = 0
    
    # Fixed ranges to match the actual CSV structure (after filtering out # headers)
    # Since we filtered out the # rows, we need to count actual drug rows
    top_10_drugs = df.iloc[0:10]              # First 10 drugs (CARDIOVASCULAR - HYPERTENSION)
    drugs_11_20 = df.iloc[10:20]              # Next 10 drugs (CARDIOVASCULAR - OTHER/LIPIDS/GERD/BONE/THYROID)
    drugs_21_30 = df.iloc[20:30]              # Next 10 drugs (DIABETES)
    drugs_31_41 = df.iloc[30:42]              # Next 11 drugs (ANTIBIOTICS/ANTIFUNGAL)
    drugs_21_41 = df.iloc[20:42]              # DIABETES + ANTIBIOTICS
    drugs_42_52 = df.iloc[42:53]              # Next 11 drugs (PAIN MANAGEMENT)
    drugs_53_63 = df.iloc[53:64]              # Next 11 drugs (PSYCHIATRY - DEPRESSION/ANXIETY)
    drugs_64_84 = df.iloc[64:85]              # Next 21 drugs (ELDERLY CARE EXTENDED)
    drugs_85_94 = df.iloc[85:95]              # Next 10 drugs (PULMONARY)
    drugs_95_106 = df.iloc[95:107]            # Next 12 drugs (WOMEN'S HEALTH/CONTRACEPTION/HRT)
    drugs_107_124 = df.iloc[107:125]          # Remaining drugs (PSYCHIATRY - ANTIPSYCHOTICS + NEUROLOGY)
    drugs_all = df.copy()                     # All filtered drugs

    def get_next_question(data):
        if retry_queue and len(questions_asked) % 5 == 0:
            return retry_queue.pop(0)
        
        while True:
            row = data.sample().iloc[0]
            if row.name not in questions_asked:
                questions_asked.append(row.name)
                return row

    def flash_red(widget):
        original_color = widget.cget("style")
        widget.config(style="Error.TButton")
        root.after(500, lambda: widget.config(style=original_color))

    def check_match(matches, game_frame, data):
        if len(selected_cards) == 2:
            card1, card2 = selected_cards
            match_found = False

            for match in matches:
                if (card1['text'], card2['text']) == match or (card2['text'], card1['text']) == match:
                    match_found = True
                    break

            if match_found:
                for btn in selected_cards:
                    btn.config(state="disabled", text="")
                    card_buttons.remove(btn)
                if not card_buttons:
                    match_cards(game_frame, data)
            else:
                for btn in selected_cards:
                    flash_red(btn)
                root.after(500, lambda: [btn.config(style="TButton", state="normal") for btn in selected_cards])

            selected_cards.clear()

    def select_card(btn, matches, game_frame, data):
        if len(selected_cards) < 2 and btn not in selected_cards:
            selected_cards.append(btn)
            btn.config(style="Selected.TButton")
            if len(selected_cards) == 2:
                check_match(matches, game_frame, data)

    def match_cards(game_frame, data):
        global card_buttons
        card_buttons = []

        for widget in game_frame.winfo_children():
            widget.destroy()

        # Get selected categories
        cat1 = category1.get()
        cat2 = category2.get()

        if cat1 and cat2 and cat1 != cat2:
            # Determine number of cards based on dataset size
            num_cards = min(len(data), 10)  # Default to 10 or size of dataset if smaller
            
            rows = data.sample(num_cards) if len(data) >= num_cards else data

            matches = list(zip(rows[cat1], rows[cat2]))
            items1 = rows[cat1].tolist()
            items2 = rows[cat2].tolist()

            # Shuffle the lists
            random.shuffle(items1)
            random.shuffle(items2)

            for i, item1 in enumerate(items1):
                btn = ttk.Button(game_frame, text=item1, width=30)
                btn.config(command=lambda b=btn: select_card(b, matches, game_frame, data))
                btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
                card_buttons.append(btn)

            for i, item2 in enumerate(items2):
                btn = ttk.Button(game_frame, text=item2, width=30)
                btn.config(command=lambda b=btn: select_card(b, matches, game_frame, data))
                btn.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                card_buttons.append(btn)

    def start_game(data):
        # Hide the frame with the selection menu
        frame.grid_forget()
        
        game_frame = ttk.Frame(root, padding="20")
        game_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        match_cards(game_frame, data)

    # User selects categories to match and drug set
    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Select two categories to match", font=('Arial', 14)).grid(row=0, column=0, columnspan=4, pady=10)

    category1 = tk.StringVar()
    category2 = tk.StringVar()

    # Drop-down for category 1
    ttk.Label(frame, text="Category 1:").grid(row=1, column=0, padx=10, pady=5)
    category1_menu = ttk.Combobox(frame, textvariable=category1, values=list(df.columns), state="readonly", width=25)
    category1_menu.grid(row=1, column=1, padx=10, pady=5)

    # Drop-down for category 2
    ttk.Label(frame, text="Category 2:").grid(row=1, column=2, padx=10, pady=5)
    category2_menu = ttk.Combobox(frame, textvariable=category2, values=list(df.columns), state="readonly", width=25)
    category2_menu.grid(row=1, column=3, padx=10, pady=5)

    # Drug set selection
    drug_set = tk.StringVar(value="all")
    
    ttk.Label(frame, text="Select Drug Set:", font=('Arial', 12)).grid(row=2, column=0, columnspan=4, pady=(20,10))
    
    # Row 3 - Main categories
    ttk.Radiobutton(frame, text="All Drugs", variable=drug_set, value="all").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Cardiovascular HTN (1-10)", variable=drug_set, value="1-10").grid(row=3, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Cardiovascular Other (11-20)", variable=drug_set, value="11-20").grid(row=3, column=2, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Diabetes (21-30)", variable=drug_set, value="21-30").grid(row=3, column=3, padx=5, pady=2, sticky="w")
    
    # Row 4
    ttk.Radiobutton(frame, text="Antibiotics (31-41)", variable=drug_set, value="31-41").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Diabetes+Antibiotics (21-41)", variable=drug_set, value="21-41").grid(row=4, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Pain Management (42-52)", variable=drug_set, value="42-52").grid(row=4, column=2, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Psychiatry Dep/Anx (53-63)", variable=drug_set, value="53-63").grid(row=4, column=3, padx=5, pady=2, sticky="w")
    
    # Row 5
    ttk.Radiobutton(frame, text="Elderly Care (64-84)", variable=drug_set, value="64-84").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Pulmonary (85-94)", variable=drug_set, value="85-94").grid(row=5, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Women's Health (95-106)", variable=drug_set, value="95-106").grid(row=5, column=2, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame, text="Psych/Neuro (107-124)", variable=drug_set, value="107-124").grid(row=5, column=3, padx=5, pady=2, sticky="w")

    ttk.Button(frame, text="Start Game", command=lambda: start_game(
        top_10_drugs if drug_set.get() == "1-10" 
        else drugs_11_20 if drug_set.get() == "11-20" 
        else drugs_21_30 if drug_set.get() == "21-30" 
        else drugs_31_41 if drug_set.get() == "31-41"
        else drugs_21_41 if drug_set.get() == "21-41"
        else drugs_42_52 if drug_set.get() == "42-52"
        else drugs_53_63 if drug_set.get() == "53-63"
        else drugs_64_84 if drug_set.get() == "64-84"
        else drugs_85_94 if drug_set.get() == "85-94"
        else drugs_95_106 if drug_set.get() == "95-106"
        else drugs_107_124 if drug_set.get() == "107-124"
        else drugs_all if drug_set.get() == "all"
        else df
    )).grid(row=6, column=0, columnspan=4, pady=20)

    style = ttk.Style()
    style.configure("Error.TButton", foreground="red", background="white")
    style.configure("Selected.TButton", foreground="blue", background="white")
    style.configure("TButton", foreground="black", background="white")

    root.mainloop()

start_matching_game()