class CurrencySystem:
    def __init__(self, pet_state):
        self.pet_state = pet_state
        if not hasattr(self.pet_state, 'currency'):
            self.pet_state.currency = 100  # Starting amount
    
    def add_currency(self, amount):
        self.pet_state.currency += amount
        return self.pet_state.currency
    
    def remove_currency(self, amount):
        if self.pet_state.currency >= amount:
            self.pet_state.currency -= amount
            return True
        return False
    
    def get_balance(self):
        return self.pet_state.currency
    
    def get_currency(self):
        return self.get_balance()