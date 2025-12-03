# Nom : blackjack.py
# Auteur : Arda Tuna Kaya et Leonardo Rodrigues
# Date : 19.11.2025

import random
from player import Player
from dealer import Dealer

class BlackjackGame:
    """Classe principale gérant la logique du jeu"""
    
    def __init__(self):
        self.deck = []
        self.player1 = Player("Joueur 1")
        self.player2 = Player("Joueur 2")
        self.dealer = Dealer()
        self.current_player = None
        self.game_state = "betting"  # betting, playing, dealer_turn, finished
        
    def create_deck(self):
        """Crée un jeu de 52 cartes"""
        suits = ['♠', '♥', '♦', '♣']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [(value, suit) for suit in suits for value in values]
        random.shuffle(self.deck)
    
    def draw_card(self):
        """Tire une carte du paquet"""
        if len(self.deck) < 10:
            self.create_deck()
        return self.deck.pop()
    
    def start_new_round(self):
        """Démarre une nouvelle manche"""
        self.player1.reset_hand()
        self.player2.reset_hand()
        self.dealer.reset_hand()
        
        if len(self.deck) < 20:
            self.create_deck()
        
        # Distribution initiale : 2 cartes pour chaque joueur et le croupier
        for _ in range(2):
            self.player1.add_card(self.draw_card())
            self.player2.add_card(self.draw_card())
            self.dealer.add_card(self.draw_card())
        
        self.current_player = self.player1
        self.game_state = "playing"
        
        # Vérifier les Blackjacks naturels
        if self.player1.has_blackjack():
            self.player1.is_standing = True
        if self.player2.has_blackjack():
            self.player2.is_standing = True
    
    def hit(self, player):
        """Le joueur tire une carte"""
        card = self.draw_card()
        player.add_card(card)
        
        if player.check_bust():
            return "bust"
        elif player.get_score() == 21:
            return "21"
        return "continue"
    
    def stand(self, player):
        """Le joueur reste"""
        player.is_standing = True
    
    def switch_player(self):
        """Passe au joueur suivant"""
        if self.current_player == self.player1:
            self.current_player = self.player2
            return True
        else:
            self.current_player = None
            self.game_state = "dealer_turn"
            return False
    
    def dealer_play(self):
        """Le croupier joue automatiquement"""
        while self.dealer.should_draw():
            card = self.draw_card()
            self.dealer.add_card(card)
        
        self.dealer.check_bust()
        self.game_state = "finished"
    
    def determine_winner(self, player):
        """Détermine le résultat pour un joueur"""
        if player.is_busted:
            player.lose_bet()
            return "lose", "Dépassé 21"
        
        dealer_score = self.dealer.get_score()
        player_score = player.get_score()
        
        # Blackjack naturel du joueur
        if player.has_blackjack() and not self.dealer.has_blackjack():
            player.win_bet(2.5)  # Paye 3:2
            return "blackjack", "Blackjack!"
        
        # Blackjack du croupier
        if self.dealer.has_blackjack() and not player.has_blackjack():
            player.lose_bet()
            return "lose", "Croupier a Blackjack"
        
        # Croupier dépassé
        if self.dealer.is_busted:
            player.win_bet()
            return "win", "Croupier dépassé"
        
        # Comparaison des scores
        if player_score > dealer_score:
            player.win_bet()
            return "win", f"{player_score} vs {dealer_score}"
        elif player_score < dealer_score:
            player.lose_bet()
            return "lose", f"{player_score} vs {dealer_score}"
        else:
            player.draw_bet()
            return "draw", f"Égalité à {player_score}"
    
    def can_player_act(self, player):
        """Vérifie si le joueur peut encore agir"""
        return not player.is_busted and not player.is_standing
    
    def get_game_results(self):
        """Retourne les résultats finaux pour les deux joueurs"""
        result1 = self.determine_winner(self.player1)
        result2 = self.determine_winner(self.player2)
        return {
            'player1': result1,
            'player2': result2,
            'dealer_score': self.dealer.get_score()
        }