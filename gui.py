# Nom : gui.py
# Auteur : Arda Tuna Kaya et Leonardo Rodrigues
# Date : 19.11.2025

import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from blackjack import BlackjackGame

# -------------------- Paramètres visuels --------------------
CARD_WIDTH = 130          # Largeur des cartes en pixels
CARD_SPACING = 8          # Espacement horizontal entre les cartes
TABLE_BG = "#0b3d0b"      # Couleur du fond (vert foncé)
PANEL_BG = "#114d14"      # Couleur des panneaux joueurs
GOLD = "#D4AF37"          # Couleur dorée pour les accents
TEXT_CLR = "#f4f4f4"      # Couleur du texte principal
SUBTEXT_CLR = "#cfe8cf"   # Couleur du texte secondaire
WARN_CLR = "#ffb74d"      # Couleur orange pour les mises
ACCENT_BLUE = "#6ec6ff"   # Couleur bleue pour les statistiques

# Conversion des noms pour les fichiers images
VALUE_MAP = {
    "A": "as", "K": "roi", "Q": "reine", "J": "valet",
    "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
    "7": "7", "8": "8", "9": "9", "10": "10"
}
SUIT_MAP = {
    "♠": "pique",
    "♥": "coeur",
    "♦": "carreau",
    "♣": "trefle"
}
IMAGE_ROOT = "images"  # Dossier contenant les images des cartes


class BlackjackGUI:
    """Interface graphique du jeu Blackjack avec affichage des cartes en images"""
    def __init__(self, root):
        # Configuration de la fenêtre principale
        self.root = root
        self.root.title("Blackjack — Deux Joueurs vs Croupier")
        self.root.geometry("1100x740")
        self.root.configure(bg=TABLE_BG)

        # Style des boutons et labels via ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("C.TButton", font=("Helvetica", 12, "bold"),
                        foreground="#1b1b1b", background=GOLD,
                        padding=(14, 10), borderwidth=0)
        style.map("C.TButton", background=[("active", "#f7d774")])
        style.configure("C.TLabel", background=TABLE_BG, foreground=TEXT_CLR, font=("Helvetica", 12))
        style.configure("Title.TLabel", background=TABLE_BG, foreground=GOLD, font=("Helvetica", 15, "bold"))
        style.configure("Small.TLabel", background=TABLE_BG, foreground=SUBTEXT_CLR, font=("Helvetica", 10))

        # Cache pour les images (évite les rechargements)
        self.image_cache = {}
        self.card_back = None
        self._load_back_image()

        # Initialisation du jeu
        self.game = BlackjackGame()
        self.game.create_deck()

        # Construction de l'interface
        self._build_layout()
        self.show_betting_screen()

    # -------------------- Chargement des images --------------------
    def _load_back_image(self):
        """Charge l'image du dos de carte (si disponible), sinon crée un placeholder"""
        path = os.path.join(IMAGE_ROOT, "back.jpg")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
        else:
            img = Image.new("RGBA", (CARD_WIDTH, int(CARD_WIDTH * 1.45)), (212, 175, 55, 255))
        img.thumbnail((CARD_WIDTH, 10000), Image.LANCZOS)
        self.card_back = ImageTk.PhotoImage(img)

    def _get_card_image(self, value, suit):
        """Retourne l'image correspondante à la carte (value, suit)"""
        key = (value, suit)
        if key in self.image_cache:
            return self.image_cache[key]

        value_name = VALUE_MAP.get(value, value).lower()
        suit_name = SUIT_MAP.get(suit, suit).lower()
        path = os.path.join(IMAGE_ROOT, f"{suit_name}-{value_name}.jpg")

        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
        else:
            img = Image.new("RGBA", (CARD_WIDTH, int(CARD_WIDTH * 1.45)), (17, 77, 20, 255))

        img.thumbnail((CARD_WIDTH, 10000), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        self.image_cache[key] = tk_img
        return tk_img

    # -------------------- Interface graphique --------------------
    def _build_layout(self):
        """Construit la disposition principale"""
        self.main = tk.Frame(self.root, bg=TABLE_BG)
        self.main.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        # Zone du croupier
        self.dealer_frame = tk.LabelFrame(self.main, text="Croupier", bg=PANEL_BG, fg=TEXT_CLR,
                                          font=("Helvetica", 14, "bold"))
        self.dealer_frame.pack(fill=tk.X, pady=(0, 14))
        self.dealer_cards_container = tk.Frame(self.dealer_frame, bg=PANEL_BG)
        self.dealer_cards_container.pack(pady=10)
        self.dealer_score_label = ttk.Label(self.dealer_frame, text="Score: ?", style="C.TLabel")
        self.dealer_score_label.pack(pady=(0, 10))

        # Zone des joueurs
        players_wrap = tk.Frame(self.main, bg=TABLE_BG)
        players_wrap.pack(fill=tk.BOTH, expand=True)

        # Joueur 1
        self.p1_frame = tk.LabelFrame(players_wrap, text="Joueur 1", bg=PANEL_BG, fg=TEXT_CLR,
                                      font=("Helvetica", 14, "bold"))
        self.p1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.p1_cards_container = tk.Frame(self.p1_frame, bg=PANEL_BG)
        self.p1_cards_container.pack(pady=10)
        self.p1_score = ttk.Label(self.p1_frame, text="Score: 0", style="C.TLabel")
        self.p1_score.pack()
        self.p1_balance = ttk.Label(self.p1_frame, text="Solde: 1000 CHF", style="Small.TLabel")
        self.p1_balance.pack()
        self.p1_bet = ttk.Label(self.p1_frame, text="Mise: 0 CHF", style="Small.TLabel", foreground=WARN_CLR)
        self.p1_bet.pack(pady=(0, 4))

        # Joueur 2
        self.p2_frame = tk.LabelFrame(players_wrap, text="Joueur 2", bg=PANEL_BG, fg=TEXT_CLR,
                                      font=("Helvetica", 14, "bold"))
        self.p2_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self.p2_cards_container = tk.Frame(self.p2_frame, bg=PANEL_BG)
        self.p2_cards_container.pack(pady=10)
        self.p2_score = ttk.Label(self.p2_frame, text="Score: 0", style="C.TLabel")
        self.p2_score.pack()
        self.p2_balance = ttk.Label(self.p2_frame, text="Solde: 1000 CHF", style="Small.TLabel")
        self.p2_balance.pack()
        self.p2_bet = ttk.Label(self.p2_frame, text="Mise: 0 CHF", style="Small.TLabel", foreground=WARN_CLR)
        self.p2_bet.pack(pady=(0, 4))

        # Zone de contrôle
        controls = tk.Frame(self.main, bg=TABLE_BG)
        controls.pack(fill=tk.X, pady=16)
        self.status_label = ttk.Label(controls, text="", style="Title.TLabel")
        self.status_label.pack(pady=(0, 10))

        btns = tk.Frame(controls, bg=TABLE_BG)
        btns.pack()
        self.hit_button = ttk.Button(btns, text="Tirer", command=self.hit, style="C.TButton")
        self.stand_button = ttk.Button(btns, text="Rester", command=self.stand, style="C.TButton")
        self.replay_button = ttk.Button(btns, text="Rejouer", command=self.show_betting_screen, style="C.TButton")
        self.quit_button = ttk.Button(btns, text="Quitter", command=self.root.quit, style="C.TButton")
        for b in (self.hit_button, self.stand_button, self.replay_button, self.quit_button):
            b.pack(side=tk.LEFT, padx=6)

        self.stats_label = ttk.Label(controls, text="", style="Small.TLabel", foreground=ACCENT_BLUE)
        self.stats_label.pack(pady=(10, 0))

        self._set_play_buttons(False)

    # -------------------- Fonctions principales --------------------
    def _set_play_buttons(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.hit_button.config(state=state)
        self.stand_button.config(state=state)

    def show_betting_screen(self):
        """Affiche la fenêtre pour placer les mises"""
        bet_w = tk.Toplevel(self.root)
        bet_w.title("Placer vos mises")
        bet_w.configure(bg=TABLE_BG)
        bet_w.geometry("420x320")
        bet_w.transient(self.root)
        bet_w.grab_set()

        ttk.Label(bet_w, text="Placez vos mises", style="Title.TLabel").pack(pady=18)
        # Joueur 1
        p1 = tk.Frame(bet_w, bg=TABLE_BG)
        p1.pack(pady=8)
        ttk.Label(p1, text=f"Joueur 1 (Solde: {self.game.player1.balance} CHF)", style="C.TLabel").pack()
        p1_entry = tk.Entry(p1, font=("Helvetica", 12), width=12, justify="center")
        p1_entry.insert(0, "10")
        p1_entry.pack(pady=6)
        # Joueur 2
        p2 = tk.Frame(bet_w, bg=TABLE_BG)
        p2.pack(pady=8)
        ttk.Label(p2, text=f"Joueur 2 (Solde: {self.game.player2.balance} CHF)", style="C.TLabel").pack()
        p2_entry = tk.Entry(p2, font=("Helvetica", 12), width=12, justify="center")
        p2_entry.insert(0, "10")
        p2_entry.pack(pady=6)

        def place_bets():
            try:
                b1 = int(p1_entry.get())
                b2 = int(p2_entry.get())
                if b1 <= 0 or b2 <= 0:
                    messagebox.showerror("Erreur", "Les mises doivent être positives !")
                    return
                if not self.game.player1.place_bet(b1):
                    messagebox.showerror("Erreur", "Joueur 1: Solde insuffisant !")
                    return
                if not self.game.player2.place_bet(b2):
                    self.game.player1.balance += b1
                    messagebox.showerror("Erreur", "Joueur 2: Solde insuffisant !")
                    return
                bet_w.destroy()
                self.start_game()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides !")

        ttk.Button(bet_w, text="Commencer la partie", command=place_bets, style="C.TButton").pack(pady=18)

    def start_game(self):
        """Démarre une nouvelle manche"""
        self.game.start_new_round()
        self._set_play_buttons(True)
        self.replay_button.config(state=tk.DISABLED)
        self.update_display()
        self._update_status()

    def hit(self):
        """Action : tirer une carte"""
        if self.game.current_player:
            result = self.game.hit(self.game.current_player)
            self.update_display()
            if result in ("bust", "21"):
                if result == "bust":
                    messagebox.showinfo("Dépassé !", f"{self.game.current_player.name} a dépassé 21 !")
                self.next_turn()

    def stand(self):
        """Action : rester"""
        if self.game.current_player:
            self.game.stand(self.game.current_player)
            self.next_turn()

    def next_turn(self):
        """Passe au joueur suivant ou au croupier"""
        has_next = self.game.switch_player()
        if has_next:
            self.update_display()
            self._update_status()
        else:
            self.dealer_turn()

    def dealer_turn(self):
        """Tour du croupier avec animation simple"""
        self._set_play_buttons(False)
        self.status_label.config(text="Tour du croupier...")
        self.update_display(show_dealer_card=True)
        self.root.after(700, self._dealer_draw_animation)

    def _dealer_draw_animation(self):
        """Animation : le croupier tire ses cartes"""
        if self.game.dealer.should_draw():
            self.game.dealer.add_card(self.game.draw_card())
            self.update_display(show_dealer_card=True)
            self.root.after(650, self._dealer_draw_animation)
        else:
            self.game.dealer.check_bust()
            self.show_results()

    # -------------------- Affichage des cartes --------------------
    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def _render_cards(self, container, cards, hide_from_index=None):
        """Affiche les cartes sous forme d'images"""
        self._clear_container(container)
        for idx, (val, suit) in enumerate(cards):
            img = self.card_back if hide_from_index and idx >= hide_from_index else self._get_card_image(val, suit)
            lbl = tk.Label(container, image=img, bg=PANEL_BG, bd=0)
            lbl.image = img
            lbl.pack(side=tk.LEFT, padx=(0 if idx == 0 else CARD_SPACING), pady=2)

    def update_display(self, show_dealer_card=False):
        """Met à jour l'affichage complet"""
        if show_dealer_card or self.game.game_state in ("dealer_turn", "finished"):
            self._render_cards(self.dealer_cards_container, self.game.dealer.hand)
            self.dealer_score_label.config(text=f"Score: {self.game.dealer.get_score()}")
        else:
            hide_from_index = 1 if len(self.game.dealer.hand) >= 2 else None
            self._render_cards(self.dealer_cards_container, self.game.dealer.hand, hide_from_index)
            self.dealer_score_label.config(text="Score: ?")

        self._render_cards(self.p1_cards_container, self.game.player1.hand)
        self.p1_score.config(text=f"Score: {self.game.player1.get_score()}")
        self.p1_balance.config(text=f"Solde: {self.game.player1.balance} CHF")
        self.p1_bet.config(text=f"Mise: {self.game.player1.current_bet} CHF")

        self._render_cards(self.p2_cards_container, self.game.player2.hand)
        self.p2_score.config(text=f"Score: {self.game.player2.get_score()}")
        self.p2_balance.config(text=f"Solde: {self.game.player2.balance} CHF")
        self.p2_bet.config(text=f"Mise: {self.game.player2.current_bet} CHF")

    def _update_status(self):
        """Met à jour le statut du tour"""
        if self.game.current_player:
            self.status_label.config(text=f"Tour de {self.game.current_player.name}")
        else:
            self.status_label.config(text="")

    def show_results(self):
        """Affiche les résultats finaux"""
        results = self.game.get_game_results()
        self.update_display(show_dealer_card=True)
        text = "=== RÉSULTATS ===\n\n"
        text += f"Croupier: {results['dealer_score']} points\n\n"
        for i, player in enumerate([self.game.player1, self.game.player2], start=1):
            status, msg = results[f"player{i}"]
            text += f"Joueur {i}: {player.get_score()} points\n"
            if status == "win":
                text += f"✓ GAGNÉ ! {msg}\n"
            elif status == "blackjack":
                text += f"★ BLACKJACK ! {msg}\n"
            elif status == "lose":
                text += f"✗ PERDU ! {msg}\n"
            else:
                text += f"= ÉGALITÉ ! {msg}\n"
            text += f"Nouveau solde: {player.balance} CHF\n\n"
        messagebox.showinfo("Fin de la partie", text)
        self.replay_button.config(state=tk.NORMAL)
        self.status_label.config(text="Partie terminée !")