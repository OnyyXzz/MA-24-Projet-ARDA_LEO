# Nom : main.py
# Auteur : Arda Tuna Kaya
# Date : 17.12.2025
# Version : 2.0
# Description : Point d'entrée de l'application Blackjack

import tkinter as tk
from gui import BlackjackGUI

def main():
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()