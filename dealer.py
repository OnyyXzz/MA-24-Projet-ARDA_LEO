# Nom : dealer.py
# Auteur : Arda Tuna Kaya
# Date : 19.11.2025

class Dealer:
    """Classe représentant le croupier"""
    
    def __init__(self):
        self.hand = []
        self.is_busted = False
    
    def add_card(self, card):
        """Ajoute une carte à la main"""
        self.hand.append(card)
    
    def get_score(self):
        """Calcule le score de la main avec gestion de l'As"""
        score = 0
        aces = 0
        
        for card in self.hand:
            value = card[0]
            if value in ['J', 'Q', 'K']:
                score += 10
            elif value == 'A':
                aces += 1
                score += 11
            else:
                score += int(value)
        
        # Ajustement pour les As
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    def should_draw(self):
        """Le croupier tire jusqu'à 17"""
        return self.get_score() < 17
    
    def check_bust(self):
        """Vérifie si le croupier a dépassé 21"""
        if self.get_score() > 21:
            self.is_busted = True
        return self.is_busted
    
    def has_blackjack(self):
        """Vérifie si le croupier a un Blackjack"""
        return len(self.hand) == 2 and self.get_score() == 21
    
    def reset_hand(self):
        """Réinitialise la main pour une nouvelle partie"""
        self.hand = []
        self.is_busted = False
    
    def get_visible_card(self):
        """Retourne la première carte visible"""
        if len(self.hand) > 0:
            return self.hand[0]
        return None
    
    def __str__(self):
        return f"Croupier - Score: {self.get_score()}"