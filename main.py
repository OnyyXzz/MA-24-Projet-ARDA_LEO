#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jeu de Blackjack Multijoueur
Développé par Arda & Léo

Un jeu de Blackjack pour deux joueurs contre un croupier automatique.
Interface graphique réalisée avec Tkinter.
"""

import tkinter as tk
from gui import BlackjackGUI

def main():
    """Fonction principale du jeu"""
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()