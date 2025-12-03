# Nom : player.py
# Auteur : Arda Tuna Kaya
# Date : 19.11.2025


class Player:
    """Classe représentant un joueur de Blackjack"""
    
    def __init__(self, name, balance=1000):
        self.name = name
        self.balance = balance
        self.hand = []
        self.current_bet = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.is_busted = False
        self.is_standing = False
    
    def place_bet(self, amount):
        """Place une mise"""
        if amount <= self.balance and amount > 0:
            self.current_bet = amount
            self.balance -= amount
            return True
        return False
    
    def win_bet(self, multiplier=2):
        """Gagne le pari (multiplie par 2 par défaut)"""
        winnings = self.current_bet * multiplier
        self.balance += winnings
        self.wins += 1
        self.current_bet = 0
        return winnings
    
    def lose_bet(self):
        """Perd le pari"""
        self.losses += 1
        self.current_bet = 0
    
    def draw_bet(self):
        """Match nul - récupère la mise"""
        self.balance += self.current_bet
        self.draws += 1
        self.current_bet = 0
    
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
    
    def reset_hand(self):
        """Réinitialise la main pour une nouvelle partie"""
        self.hand = []
        self.is_busted = False
        self.is_standing = False
    
    def check_bust(self):
        """Vérifie si le joueur a dépassé 21"""
        if self.get_score() > 21:
            self.is_busted = True
        return self.is_busted
    
    def has_blackjack(self):
        """Vérifie si le joueur a un Blackjack (21 avec 2 cartes)"""
        return len(self.hand) == 2 and self.get_score() == 21
    
    def __str__(self):
        return f"{self.name} - Solde: {self.balance} CHF - Score: {self.get_score()}"