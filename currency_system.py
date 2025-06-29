class CurrencySystem:
    """Manages the pet's currency (coins)"""
    
    def __init__(self, pet_state):
        self.pet_state = pet_state
        if not hasattr(self.pet_state, 'currency'):
            self.pet_state.currency = 100  # Starting amount
    
    def add_currency(self, amount):
        """Add currency to the pet's balance"""
        self.pet_state.currency += amount
        return self.pet_state.currency
    
    def remove_currency(self, amount):
        """Remove currency from the pet's balance"""
        if self.pet_state.currency >= amount:
            self.pet_state.currency -= amount
            return True
        return False
    
    def get_balance(self):
        """Get current currency balance"""
        return self.pet_state.currency
    
    def get_currency(self):
        """Get current currency balance (alias for get_balance)"""
        return self.get_balance()