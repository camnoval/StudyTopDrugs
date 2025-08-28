# main.py - Main application entry point
import tkinter as tk
from tkinter import messagebox
from drug_study_app import DrugStudyApp

if __name__ == "__main__":
    try:
        app = DrugStudyApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        input("Press Enter to exit...")
