import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class CurrencyDisplay:
    def __init__(self, parent, initial_coins=0):
        self.frame = ttk.Frame(parent)
        self.coins = initial_coins
        

        try:
            self.currency_img = ImageTk.PhotoImage(
                Image.open('img_assets/currency.png').resize((24, 24))
            )
        except FileNotFoundError:
            self.currency_img = ImageTk.PhotoImage(Image.new('RGBA', (24,24)))
        
        self.icon_label = ttk.Label(self.frame, image=self.currency_img)
        self.value_label = ttk.Label(self.frame, text=f'{self.coins}¢')
        
        self.icon_label.pack(side='left', padx=5)
        self.value_label.pack(side='left')

    def update_display(self, new_value):
        self.coins = max(0, new_value)
        self.value_label.config(text=f'{self.coins}¢')

    def get_current_balance(self):
        return self.coins

def create_status_bar(parent):
    status_frame = ttk.Frame(parent)
    

    currency = CurrencyDisplay(status_frame)
    currency.frame.pack(side='right', padx=10)
    

    return status_fram