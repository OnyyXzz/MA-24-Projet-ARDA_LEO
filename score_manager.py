# Nom : score_manager.py
# Auteur : Arda Tuna Kaya
# Auteur 2 : Leonardo Rodrigues
# Date : 17.12.2025
# Version : 2.0
# Description : Gestion de l'enregistrement et de l'importation des scores
# Changements v2.0 : Ajout UUID pour unicité des scores, import anti-duplicates

import json
import os
import uuid
from datetime import datetime


class ScoreManager:
    """Classe pour gérer l'enregistrement et l'importation des scores"""
    
    def __init__(self, filename="scores.json"):
        """Initialise le gestionnaire de scores
        
        Args:
            filename (str): Nom du fichier JSON contenant les scores
        """
        self.filename = filename
        self.scores = []
        self._load_scores()
    
    def _load_scores(self):
        """Charge les scores depuis le fichier JSON si disponible"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                # Si le fichier est corrompu, on repart avec une liste vide
                self.scores = []
        else:
            self.scores = []
    
    def _save_scores(self):
        """Enregistre les scores dans le fichier JSON"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur lors de l'enregistrement des scores: {e}")
            return False
    
    def add_score(self, player1_name, player1_result, player1_score, player1_balance,
                  player2_name, player2_result, player2_score, player2_balance,
                  dealer_score):
        """Enregistre les résultats d'une manche
        
        Args:
            player1_name (str): Nom du joueur 1
            player1_result (str): Résultat du joueur 1 (win, lose, draw, blackjack)
            player1_score (int): Score final du joueur 1
            player1_balance (int): Solde final du joueur 1
            player2_name (str): Nom du joueur 2
            player2_result (str): Résultat du joueur 2 (win, lose, draw, blackjack)
            player2_score (int): Score final du joueur 2
            player2_balance (int): Solde final du joueur 2
            dealer_score (int): Score final du croupier
        
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        # Utiliser timestamp avec UUID pour garantir l'unicité
        unique_id = str(uuid.uuid4())[:8]  # Premier 8 caractères de UUID
        score_entry = {
            "id": unique_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "joueur1": {
                "nom": player1_name,
                "resultat": player1_result,
                "score": player1_score,
                "solde": player1_balance
            },
            "joueur2": {
                "nom": player2_name,
                "resultat": player2_result,
                "score": player2_score,
                "solde": player2_balance
            },
            "croupier": {
                "score": dealer_score
            }
        }
        
        self.scores.append(score_entry)
        return self._save_scores()
    
    def get_scores(self):
        """Retourne tous les scores enregistrés
        
        Returns:
            list: Liste de tous les scores
        """
        return self.scores
    
    def get_scores_count(self):
        """Retourne le nombre de manches enregistrées
        
        Returns:
            int: Nombre de manches
        """
        return len(self.scores)
    
    def get_player_stats(self, player_name):
        """Retourne les statistiques pour un joueur spécifique
        
        Args:
            player_name (str): Nom du joueur
        
        Returns:
            dict: Statistiques du joueur (victoires, défaites, égalités, solde final)
        """
        wins = 0
        losses = 0
        draws = 0
        blackjacks = 0
        final_balance = 0
        
        for score in self.scores:
            # Vérifier si c'est joueur 1
            if score["joueur1"]["nom"] == player_name:
                result = score["joueur1"]["resultat"]
                if result == "win":
                    wins += 1
                elif result == "lose":
                    losses += 1
                elif result == "draw":
                    draws += 1
                elif result == "blackjack":
                    blackjacks += 1
                final_balance = score["joueur1"]["solde"]
            
            # Vérifier si c'est joueur 2
            if score["joueur2"]["nom"] == player_name:
                result = score["joueur2"]["resultat"]
                if result == "win":
                    wins += 1
                elif result == "lose":
                    losses += 1
                elif result == "draw":
                    draws += 1
                elif result == "blackjack":
                    blackjacks += 1
                final_balance = score["joueur2"]["solde"]
        
        return {
            "nom": player_name,
            "victoires": wins,
            "defaites": losses,
            "egalites": draws,
            "blackjacks": blackjacks,
            "solde_final": final_balance
        }
    
    def clear_scores(self):
        """Efface tous les scores enregistrés
        
        Returns:
            bool: True si l'effacement a réussi
        """
        self.scores = []
        return self._save_scores()
    
    def import_scores(self, filepath):
        """Importe des scores à partir d'un fichier JSON externe
        
        Args:
            filepath (str): Chemin du fichier à importer
        
        Returns:
            bool: True si l'importation a réussi, False sinon
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_scores = json.load(f)
            
            # Vérifier que c'est une liste
            if not isinstance(imported_scores, list):
                return False
            
            # Ajouter les scores importés SANS DUPLICATES
            # Vérifier chaque score importé pour éviter les doublons
            for imported_score in imported_scores:
                # Vérifier si ce score existe déjà (même ID ou même timestamp + données)
                is_duplicate = False
                
                # Vérifier par ID en priorité
                imported_id = imported_score.get("id")
                if imported_id:
                    for existing_score in self.scores:
                        if existing_score.get("id") == imported_id:
                            is_duplicate = True
                            break
                
                # Sinon, vérifier par timestamp + données (compatibilité anciens scores)
                if not is_duplicate:
                    for existing_score in self.scores:
                        if (existing_score.get("timestamp") == imported_score.get("timestamp") and
                            existing_score.get("joueur1") == imported_score.get("joueur1") and
                            existing_score.get("joueur2") == imported_score.get("joueur2")):
                            is_duplicate = True
                            break
                
                # N'ajouter que si ce n'est pas un doublon
                if not is_duplicate:
                    self.scores.append(imported_score)
            
            return self._save_scores()
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            return False
    
    def export_scores(self, filepath):
        """Exporte tous les scores vers un fichier JSON
        
        Args:
            filepath (str): Chemin du fichier de destination
        
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get_last_balances(self):
        """Retourne les derniers soldes des joueurs
        
        Returns:
            dict: {"Joueur 1": balance1, "Joueur 2": balance2} ou {}
        """
        if not self.scores:
            return {}
        
        last_score = self.scores[-1]  # Dernier score
        return {
            "Joueur 1": last_score["joueur1"]["solde"],
            "Joueur 2": last_score["joueur2"]["solde"]
        }
