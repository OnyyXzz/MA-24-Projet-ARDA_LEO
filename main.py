import tkinter as tk
from tkinter import messagebox, ttk
import random
from pathlib import Path

# Tentative d'importation de Pillow pour les images
try:
    from PIL import Image, ImageTk # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Pillow n'est pas installé. Utilisation du mode texte pour les cartes.")


class Carte:
    """Représente une carte à jouer avec sa valeur et sa couleur."""
    
    COULEURS = ['coeur', 'carreau', 'pique', 'trefle']
    VALEURS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'valet', 'reine', 'roi', 'as']
    
    def __init__(self, valeur, couleur):
        self.valeur = valeur
        self.couleur = couleur
    
    def obtenir_valeur_numerique(self):
        """Retourne la valeur numérique de la carte."""
        if self.valeur in ['valet', 'reine', 'roi']:
            return 10
        elif self.valeur == 'as':
            return 11  # Valeur par défaut, sera ajustée selon la main
        else:
            return int(self.valeur)
    
    def obtenir_nom_fichier(self):
        """Retourne le nom du fichier image correspondant."""
        return f"{self.couleur}-{self.valeur}.jpg"
    
    def __str__(self):
        return f"{self.valeur} de {self.couleur}"


class JeuDeCartes:
    """Gère le paquet de cartes."""
    
    def __init__(self):
        self.cartes = []
        self.reinitialiser()
    
    def reinitialiser(self):
        """Crée un nouveau paquet de 52 cartes et le mélange."""
        self.cartes = []
        for couleur in Carte.COULEURS:
            for valeur in Carte.VALEURS:
                self.cartes.append(Carte(valeur, couleur))
        self.melanger()
    
    def melanger(self):
        """Mélange le paquet de cartes."""
        random.shuffle(self.cartes)
    
    def tirer_carte(self):
        """Tire une carte du paquet."""
        if len(self.cartes) == 0:
            self.reinitialiser()
        return self.cartes.pop()


class Joueur:
    """Représente un joueur avec sa main et son solde."""
    
    def __init__(self, nom, solde_initial=1000):
        self.nom = nom
        self.solde = solde_initial
        self.main = []
        self.mise = 0
        self.a_termine = False
    
    def recevoir_carte(self, carte):
        """Ajoute une carte à la main du joueur."""
        self.main.append(carte)
    
    def calculer_score(self):
        """Calcule le score de la main en gérant les As."""
        score = 0
        nb_as = 0
        
        for carte in self.main:
            if carte.valeur == 'as':
                nb_as += 1
                score += 11
            else:
                score += carte.obtenir_valeur_numerique()
        
        # Ajuster la valeur des As si nécessaire
        while score > 21 and nb_as > 0:
            score -= 10
            nb_as -= 1
        
        return score
    
    def a_blackjack(self):
        """Vérifie si le joueur a un Blackjack (21 avec 2 cartes)."""
        return len(self.main) == 2 and self.calculer_score() == 21
    
    def a_depasse(self):
        """Vérifie si le joueur a dépassé 21."""
        return self.calculer_score() > 21
    
    def placer_mise(self, montant):
        """Place une mise."""
        if montant <= self.solde:
            self.mise = montant
            return True
        return False
    
    def gagner(self, multiplicateur=1):
        """Ajoute les gains au solde."""
        gain = self.mise * multiplicateur
        self.solde += gain
        return gain
    
    def perdre(self):
        """Déduit la mise du solde."""
        self.solde -= self.mise
    
    def reinitialiser_main(self):
        """Réinitialise la main pour une nouvelle partie."""
        self.main = []
        self.mise = 0
        self.a_termine = False


class Croupier(Joueur):
    """Représente le croupier avec ses règles spécifiques."""
    
    def __init__(self):
        super().__init__("Croupier", 0)
    
    def doit_tirer(self):
        """Le croupier doit tirer jusqu'à atteindre 17 ou plus."""
        return self.calculer_score() < 17


class BlackjackJeu:
    """Gère la logique du jeu de Blackjack."""
    
    def __init__(self):
        self.paquet = JeuDeCartes()
        self.joueur1 = Joueur("Joueur 1")
        self.joueur2 = Joueur("Joueur 2")
        self.croupier = Croupier()
        self.joueur_actif = None
        self.phase = "mise"  # mise, jeu, croupier, fin
    
    def demarrer_partie(self, mise1, mise2):
        """Démarre une nouvelle partie."""
        # Réinitialiser les mains
        self.joueur1.reinitialiser_main()
        self.joueur2.reinitialiser_main()
        self.croupier.reinitialiser_main()
        
        # Placer les mises
        if not self.joueur1.placer_mise(mise1):
            return False, "Joueur 1 : mise supérieure au solde"
        if not self.joueur2.placer_mise(mise2):
            return False, "Joueur 2 : mise supérieure au solde"
        
        # Distribuer les cartes initiales
        for _ in range(2):
            self.joueur1.recevoir_carte(self.paquet.tirer_carte())
            self.joueur2.recevoir_carte(self.paquet.tirer_carte())
            self.croupier.recevoir_carte(self.paquet.tirer_carte())
        
        # Commencer avec le joueur 1
        self.joueur_actif = self.joueur1
        self.phase = "jeu"
        
        return True, "Partie démarrée"
    
    def tirer_carte_joueur(self):
        """Le joueur actif tire une carte."""
        if self.joueur_actif and not self.joueur_actif.a_termine:
            self.joueur_actif.recevoir_carte(self.paquet.tirer_carte())
            
            if self.joueur_actif.a_depasse():
                self.joueur_actif.a_termine = True
                self.passer_joueur_suivant()
            
            return True
        return False
    
    def rester(self):
        """Le joueur actif reste avec sa main actuelle."""
        if self.joueur_actif:
            self.joueur_actif.a_termine = True
            self.passer_joueur_suivant()
    
    def passer_joueur_suivant(self):
        """Passe au joueur suivant ou au croupier."""
        if self.joueur_actif == self.joueur1:
            if not self.joueur2.a_termine:
                self.joueur_actif = self.joueur2
            else:
                self.phase_croupier()
        elif self.joueur_actif == self.joueur2:
            self.phase_croupier()
    
    def phase_croupier(self):
        """Le croupier joue son tour."""
        self.phase = "croupier"
        self.joueur_actif = None
        
        # Le croupier tire jusqu'à avoir 17 ou plus
        while self.croupier.doit_tirer():
            self.croupier.recevoir_carte(self.paquet.tirer_carte())
        
        # Calculer les résultats
        self.calculer_resultats()
    
    def calculer_resultats(self):
        """Calcule les résultats et met à jour les soldes."""
        self.phase = "fin"
        score_croupier = self.croupier.calculer_score()
        croupier_depasse = self.croupier.a_depasse()
        
        resultats = []
        
        # Évaluer chaque joueur
        for joueur in [self.joueur1, self.joueur2]:
            score_joueur = joueur.calculer_score()
            
            if joueur.a_depasse():
                joueur.perdre()
                resultats.append(f"{joueur.nom} : Bust ! Perte de {joueur.mise} jetons")
            elif joueur.a_blackjack() and not self.croupier.a_blackjack():
                gain = joueur.gagner(2.5)
                resultats.append(f"{joueur.nom} : Blackjack ! Gain de {gain} jetons")
            elif croupier_depasse:
                gain = joueur.gagner(2)
                resultats.append(f"{joueur.nom} : Victoire ! Gain de {gain} jetons")
            elif score_joueur > score_croupier:
                gain = joueur.gagner(2)
                resultats.append(f"{joueur.nom} : Victoire ! Gain de {gain} jetons")
            elif score_joueur == score_croupier:
                resultats.append(f"{joueur.nom} : Égalité ! Mise récupérée")
            else:
                joueur.perdre()
                resultats.append(f"{joueur.nom} : Défaite ! Perte de {joueur.mise} jetons")
        
        return resultats


class BlackjackGUI:
    """Interface graphique du jeu de Blackjack."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Multijoueur")
        self.root.geometry("1200x800")
        
        # Couleurs modernes et luxueuses
        self.bg_principal = '#1a1a2e'  # Bleu nuit profond
        self.bg_secondaire = '#16213e'  # Bleu foncé
        self.accent_or = '#FFD700'  # Or
        self.accent_rouge = '#e94560'  # Rouge élégant
        self.accent_vert = '#00ff88'  # Vert néon
        self.bg_carte = '#0f3460'  # Bleu moyen
        
        self.root.configure(bg=self.bg_principal)
        
        self.jeu = BlackjackJeu()
        self.images_cache = {}
        
        self.creer_interface()
    
    def creer_interface(self):
        """Crée tous les éléments de l'interface."""
        # Header avec gradient simulé
        header_frame = tk.Frame(self.root, bg=self.bg_secondaire, height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Titre luxueux avec ombres
        titre_container = tk.Frame(header_frame, bg=self.bg_secondaire)
        titre_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Effet d'ombre
        ombre = tk.Label(
            titre_container,
            text="♠ BLACKJACK ♦",
            font=("Georgia", 42, "bold"),
            bg=self.bg_secondaire,
            fg='#000000'
        )
        ombre.pack()
        
        titre = tk.Label(
            titre_container,
            text="♠ BLACKJACK ♦",
            font=("Georgia", 42, "bold"),
            bg=self.bg_secondaire,
            fg=self.accent_or
        )
        titre.place(x=-2, y=-2)
        
        sous_titre = tk.Label(
            header_frame,
            text="ÉDITION PREMIUM",
            font=("Arial", 11, "italic"),
            bg=self.bg_secondaire,
            fg=self.accent_or
        )
        sous_titre.pack(side=tk.BOTTOM, pady=5)
        
        # Frame principal avec bordure élégante
        container = tk.Frame(self.root, bg=self.bg_principal)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        self.frame_principal = tk.Frame(
            container, 
            bg=self.bg_principal,
            highlightbackground=self.accent_or,
            highlightthickness=1
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Zone du croupier
        self.creer_zone_croupier()
        
        # Zone des joueurs
        self.creer_zone_joueurs()
        
        # Zone des contrôles
        self.creer_zone_controles()
        
        # Afficher l'écran de mise
        self.afficher_ecran_mise()
    
    def creer_zone_croupier(self):
        """Crée la zone d'affichage du croupier."""
        # Container avec effet de carte
        container = tk.Frame(self.frame_principal, bg=self.bg_principal)
        container.pack(pady=15)
        
        frame = tk.Frame(
            container,
            bg=self.bg_carte,
            highlightbackground=self.accent_or,
            highlightthickness=2,
            bd=0
        )
        frame.pack(padx=3, pady=3)
        
        # En-tête élégant
        header = tk.Frame(frame, bg=self.bg_secondaire, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="♔ CROUPIER ♔",
            font=("Georgia", 16, "bold"),
            bg=self.bg_secondaire,
            fg=self.accent_or
        ).pack(pady=10)
        
        # Corps
        body = tk.Frame(frame, bg=self.bg_carte)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        self.label_score_croupier = tk.Label(
            body,
            text="Score: ?",
            font=("Arial", 14, "bold"),
            bg=self.bg_carte,
            fg='white'
        )
        self.label_score_croupier.pack(pady=5)
        
        self.frame_cartes_croupier = tk.Frame(body, bg=self.bg_carte)
        self.frame_cartes_croupier.pack(pady=10)
    
    def creer_zone_joueurs(self):
        """Crée la zone d'affichage des joueurs."""
        frame_joueurs = tk.Frame(self.frame_principal, bg='#0d5c0d')
        frame_joueurs.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Joueur 1
        self.frame_joueur1 = self.creer_zone_joueur(frame_joueurs, self.jeu.joueur1, 0)
        
        # Joueur 2
        self.frame_joueur2 = self.creer_zone_joueur(frame_joueurs, self.jeu.joueur2, 1)
    
    def creer_zone_joueur(self, parent, joueur, colonne):
        """Crée la zone d'affichage pour un joueur."""
        # Container externe
        container = tk.Frame(parent, bg=self.bg_principal)
        container.grid(row=0, column=colonne, padx=15, sticky='nsew')
        parent.columnconfigure(colonne, weight=1)
        
        # Frame avec effet de carte luxueuse
        frame = tk.Frame(
            container,
            bg=self.bg_carte,
            highlightbackground=self.accent_or,
            highlightthickness=2,
            bd=0
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # En-tête
        header = tk.Frame(frame, bg=self.bg_secondaire, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        symbole = "♠" if colonne == 0 else "♥"
        tk.Label(
            header,
            text=f"{symbole} {joueur.nom.upper()} {symbole}",
            font=("Georgia", 15, "bold"),
            bg=self.bg_secondaire,
            fg=self.accent_or
        ).pack(pady=8)
        
        # Séparateur doré
        tk.Frame(header, bg=self.accent_or, height=2).pack(fill=tk.X, side=tk.BOTTOM)
        
        # Corps
        body = tk.Frame(frame, bg=self.bg_carte)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Solde avec icône
        label_solde = tk.Label(
            body,
            text=f"💰 {joueur.solde} jetons",
            font=("Arial", 13, "bold"),
            bg=self.bg_carte,
            fg=self.accent_vert
        )
        label_solde.pack(pady=3)
        
        # Score
        label_score = tk.Label(
            body,
            text="Score: 0",
            font=("Arial", 12, "bold"),
            bg=self.bg_carte,
            fg='white'
        )
        label_score.pack(pady=3)
        
        # Zone des cartes
        frame_cartes = tk.Frame(body, bg=self.bg_carte)
        frame_cartes.pack(pady=10)
        
        # Stocker les références
        if joueur == self.jeu.joueur1:
            self.label_solde_j1 = label_solde
            self.label_score_j1 = label_score
            self.frame_cartes_j1 = frame_cartes
            self.container_joueur1 = container
        else:
            self.label_solde_j2 = label_solde
            self.label_score_j2 = label_score
            self.frame_cartes_j2 = frame_cartes
            self.container_joueur2 = container
        
        return frame
    
    def creer_zone_controles(self):
        """Crée la zone des boutons de contrôle."""
        frame = tk.Frame(self.root, bg='#0d5c0d')
        frame.pack(pady=10)
        
        self.btn_tirer = tk.Button(
            frame,
            text="Tirer (Hit)",
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            width=15,
            command=self.action_tirer
        )
        self.btn_tirer.grid(row=0, column=0, padx=5)
        
        self.btn_rester = tk.Button(
            frame,
            text="Rester (Stand)",
            font=("Arial", 12, "bold"),
            bg='#f44336',
            fg='white',
            width=15,
            command=self.action_rester
        )
        self.btn_rester.grid(row=0, column=1, padx=5)
        
        self.btn_nouvelle_partie = tk.Button(
            frame,
            text="Nouvelle Partie",
            font=("Arial", 12, "bold"),
            bg='#2196F3',
            fg='white',
            width=15,
            command=self.afficher_ecran_mise
        )
        self.btn_nouvelle_partie.grid(row=0, column=2, padx=5)
        
        tk.Button(
            frame,
            text="Quitter",
            font=("Arial", 12, "bold"),
            bg='#607D8B',
            fg='white',
            width=15,
            command=self.root.quit
        ).grid(row=0, column=3, padx=5)
        
        self.desactiver_boutons_jeu()
    
    def afficher_ecran_mise(self):
        """Affiche l'écran de saisie des mises."""
        fenetre_mise = tk.Toplevel(self.root)
        fenetre_mise.title("Placer les mises")
        fenetre_mise.geometry("400x250")
        fenetre_mise.configure(bg='#0d5c0d')
        fenetre_mise.transient(self.root)
        fenetre_mise.grab_set()
        
        tk.Label(
            fenetre_mise,
            text="Placer les mises",
            font=("Arial", 16, "bold"),
            bg='#0d5c0d',
            fg='white'
        ).pack(pady=15)
        
        # Mise Joueur 1
        frame_j1 = tk.Frame(fenetre_mise, bg='#0d5c0d')
        frame_j1.pack(pady=10)
        
        tk.Label(
            frame_j1,
            text=f"Joueur 1 (Solde: {self.jeu.joueur1.solde}):",
            font=("Arial", 11),
            bg='#0d5c0d',
            fg='white'
        ).grid(row=0, column=0, padx=5)
        
        entry_mise1 = tk.Entry(frame_j1, font=("Arial", 11), width=10)
        entry_mise1.grid(row=0, column=1, padx=5)
        entry_mise1.insert(0, "10")
        
        # Mise Joueur 2
        frame_j2 = tk.Frame(fenetre_mise, bg='#0d5c0d')
        frame_j2.pack(pady=10)
        
        tk.Label(
            frame_j2,
            text=f"Joueur 2 (Solde: {self.jeu.joueur2.solde}):",
            font=("Arial", 11),
            bg='#0d5c0d',
            fg='white'
        ).grid(row=0, column=0, padx=5)
        
        entry_mise2 = tk.Entry(frame_j2, font=("Arial", 11), width=10)
        entry_mise2.grid(row=0, column=1, padx=5)
        entry_mise2.insert(0, "10")
        
        def valider_mises():
            try:
                mise1 = int(entry_mise1.get())
                mise2 = int(entry_mise2.get())
                
                if mise1 <= 0 or mise2 <= 0:
                    messagebox.showerror("Erreur", "Les mises doivent être positives !")
                    return
                
                succes, message = self.jeu.demarrer_partie(mise1, mise2)
                if succes:
                    fenetre_mise.destroy()
                    self.actualiser_affichage()
                    self.activer_boutons_jeu()
                else:
                    messagebox.showerror("Erreur", message)
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides !")
        
        tk.Button(
            fenetre_mise,
            text="Commencer la partie",
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            command=valider_mises
        ).pack(pady=20)
    
    def charger_image_carte(self, carte, cache=False):
        """Charge l'image d'une carte ou retourne un widget texte."""
        nom_fichier = carte.obtenir_nom_fichier()
        chemin = Path("images") / nom_fichier
        
        if PILLOW_AVAILABLE and chemin.exists():
            if cache or nom_fichier not in self.images_cache:
                try:
                    img = Image.open(chemin)
                    img = img.resize((70, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    if cache:
                        self.images_cache[nom_fichier] = photo
                    return photo
                except Exception as e:
                    print(f"Erreur chargement image {nom_fichier}: {e}")
            else:
                return self.images_cache[nom_fichier]
        
        # Fallback: retourner None pour utiliser le mode texte
        return None
    
    def afficher_cartes(self, frame, cartes, cacher_derniere=False):
        """Affiche les cartes dans un frame."""
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        for i, carte in enumerate(cartes):
            if cacher_derniere and i == len(cartes) - 1:
                # Carte cachée
                label = tk.Label(
                    frame,
                    text="🂠",
                    font=("Arial", 50),
                    bg='#0d5c0d',
                    fg='white'
                )
                label.grid(row=0, column=i, padx=2)
            else:
                photo = self.charger_image_carte(carte, cache=True)
                if photo:
                    label = tk.Label(frame, image=photo, bg='#0d5c0d')
                    label.image = photo  # Garder une référence
                else:
                    # Mode texte
                    symboles = {
                        'coeur': '♥',
                        'carreau': '♦',
                        'pique': '♠',
                        'trefle': '♣'
                    }
                    valeurs_affichage = {
                        'valet': 'V',
                        'reine': 'D',
                        'roi': 'R',
                        'as': 'A'
                    }
                    
                    valeur_txt = valeurs_affichage.get(carte.valeur, carte.valeur)
                    symbole = symboles.get(carte.couleur, '')
                    couleur = 'red' if carte.couleur in ['coeur', 'carreau'] else 'black'
                    
                    label = tk.Label(
                        frame,
                        text=f"{valeur_txt}\n{symbole}",
                        font=("Arial", 16, "bold"),
                        bg='white',
                        fg=couleur,
                        width=4,
                        height=3,
                        relief=tk.RAISED,
                        bd=2
                    )
                
                label.grid(row=0, column=i, padx=2)
    
    def actualiser_affichage(self):
        """Met à jour l'affichage complet."""
        # Croupier
        if self.jeu.phase == "jeu":
            self.afficher_cartes(
                self.frame_cartes_croupier,
                self.jeu.croupier.main,
                cacher_derniere=True
            )
            score_visible = self.jeu.croupier.main[0].obtenir_valeur_numerique()
            self.label_score_croupier.config(text=f"Score: {score_visible}+?")
        else:
            self.afficher_cartes(self.frame_cartes_croupier, self.jeu.croupier.main)
            self.label_score_croupier.config(
                text=f"Score: {self.jeu.croupier.calculer_score()}"
            )
        
        # Joueur 1
        self.afficher_cartes(self.frame_cartes_j1, self.jeu.joueur1.main)
        self.label_score_j1.config(text=f"Score: {self.jeu.joueur1.calculer_score()}")
        self.label_solde_j1.config(text=f"Solde: {self.jeu.joueur1.solde} jetons")
        
        # Joueur 2
        self.afficher_cartes(self.frame_cartes_j2, self.jeu.joueur2.main)
        self.label_score_j2.config(text=f"Score: {self.jeu.joueur2.calculer_score()}")
        self.label_solde_j2.config(text=f"Solde: {self.jeu.joueur2.solde} jetons")
        
        # Mettre en évidence le joueur actif
        if self.jeu.joueur_actif == self.jeu.joueur1:
            self.frame_joueur1.config(bg='#1a7a1a', highlightbackground='yellow', highlightthickness=3)
            self.frame_joueur2.config(bg='#0d5c0d', highlightthickness=0)
        elif self.jeu.joueur_actif == self.jeu.joueur2:
            self.frame_joueur2.config(bg='#1a7a1a', highlightbackground='yellow', highlightthickness=3)
            self.frame_joueur1.config(bg='#0d5c0d', highlightthickness=0)
        else:
            self.frame_joueur1.config(bg='#0d5c0d', highlightthickness=0)
            self.frame_joueur2.config(bg='#0d5c0d', highlightthickness=0)
    
    def action_tirer(self):
        """Action du bouton Tirer."""
        self.jeu.tirer_carte_joueur()
        self.actualiser_affichage()
        
        if self.jeu.phase == "fin":
            self.desactiver_boutons_jeu()
            self.afficher_resultats()
    
    def action_rester(self):
        """Action du bouton Rester."""
        self.jeu.rester()
        self.actualiser_affichage()
        
        if self.jeu.phase == "fin":
            self.desactiver_boutons_jeu()
            self.afficher_resultats()
    
    def afficher_resultats(self):
        """Affiche les résultats de la partie."""
        resultats = self.jeu.calculer_resultats()
        
        message = "🎲 Résultats de la partie 🎲\n\n"
        message += f"Croupier: {self.jeu.croupier.calculer_score()}\n\n"
        message += "\n".join(resultats)
        
        messagebox.showinfo("Fin de la partie", message)
    
    def activer_boutons_jeu(self):
        """Active les boutons de jeu."""
        self.btn_tirer.config(state=tk.NORMAL)
        self.btn_rester.config(state=tk.NORMAL)
    
    def desactiver_boutons_jeu(self):
        """Désactive les boutons de jeu."""
        self.btn_tirer.config(state=tk.DISABLED)
        self.btn_rester.config(state=tk.DISABLED)


def main():
    """Fonction principale pour lancer le jeu."""
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()