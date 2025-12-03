# Nom : main.py
# Auteur : Arda Tuna Kaya et Leonardo Rodrigues
# Date : 19.11.2025

import tkinter as tk
from gui import BlackjackGUI

def main():
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()