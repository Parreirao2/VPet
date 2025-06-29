import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from unified_ui import COLORS

class InventoryItem:
    
    def __init__(self, name, image_path, description, quantity=1, max_quantity=99):
        self.name = name
        self.image_path = image_path
        self.description = description
        self.quantity = quantity
        self.max_quantity = max_quantity
        self.image = None
        self.icon = None
        self.selected = False
        
    def load_image(self, size=(32, 32)):
        try:
            img = Image.open(self.image_path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            self.image = ImageTk.PhotoImage(img)
            return True
        except Exception as e:
            print(f"Error loading item image {self.image_path}: {e}")
            return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")
    
    def use(self):
        if self.quantity > 0:
            self.quantity -= 1
            return True
        return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")
    
    def add(self, amount=1):
        self.quantity = min(self.max_quantity, self.quantity + amount)

class InventorySystem:
    
    def __init__(self, root, canvas, pet_state):
        self.root = root
        self.canvas = canvas
        self.pet_state = pet_state
        
        self.items = {}
        
        self.selected_item = None
        
        self.inventory_window = None
        self.item_buttons = []
        
        self.item_cursor_id = None
        self.original_cursor = None
        
        self.load_default_items()
    
    def load_default_items(self):
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets')
            
            toilet_paper_path = os.path.join(img_path, 'toilet_paper.png')
            if os.path.exists(toilet_paper_path):
                toilet_paper = InventoryItem(
                    name="Toilet Paper",
                    image_path=toilet_paper_path,
                    description="Used to clean up messes",
                    quantity=5
                )
                toilet_paper.load_image()
                self.items["toilet_paper"] = toilet_paper
            
            shower_path = os.path.join(img_path, 'shower.png')
            if os.path.exists(shower_path):
                shower = InventoryItem(
                    name="Shower",
                    image_path=shower_path,
                    description="Increases cleanliness by 15%",
                    quantity=5
                )
                shower.load_image()
                self.items["shower"] = shower

            food_items = [
                ("baguette", "Baguette", "Hunger: +4, Happiness: +2, Energy: +3, Health: +1, Cleanliness: -1", 35),
                ("bread", "Bread", "Hunger: +3, Happiness: +1, Energy: +2, Health: 0, Cleanliness: 0", 20),
                ("bun", "Bun", "Hunger: +2, Happiness: +1, Energy: +1, Health: 0, Cleanliness: 0", 15),
                ("burger", "Burger", "Hunger: +5, Happiness: +4, Energy: +3, Health: -2, Cleanliness: -2", 45),
                ("burrito", "Burrito", "Hunger: +4, Happiness: +3, Energy: +3, Health: -1, Cleanliness: -2", 40),
                ("cheesecake", "Cheesecake", "Hunger: +3, Happiness: +5, Energy: +2, Health: -2, Cleanliness: -1", 50),
                ("cheesepuff_bowl", "Cheesepuff Bowl", "Hunger: +2, Happiness: +4, Energy: +1, Health: -2, Cleanliness: -3", 30),
                ("chocolate", "Chocolate", "Hunger: +1, Happiness: +5, Energy: +3, Health: -1, Cleanliness: -1", 35),
                ("chocolatecake", "Chocolate Cake", "Hunger: +3, Happiness: +5, Energy: +2, Health: -3, Cleanliness: -2", 55),
                ("cookies", "Cookies", "Hunger: +2, Happiness: +4, Energy: +2, Health: -1, Cleanliness: -1", 25),
                ("curry", "Curry", "Hunger: +4, Happiness: +3, Energy: +3, Health: +2, Cleanliness: -2", 50),
                ("donut", "Donut", "Hunger: +2, Happiness: +4, Energy: +2, Health: -2, Cleanliness: -1", 20),
                ("dumplings", "Dumplings", "Hunger: +3, Happiness: +2, Energy: +2, Health: +1, Cleanliness: -1", 35),
                ("eggsalad_bowl", "Egg Salad Bowl", "Hunger: +3, Happiness: +1, Energy: +2, Health: +2, Cleanliness: -1", 40),
                ("eggtart", "Egg Tart", "Hunger: +2, Happiness: +3, Energy: +1, Health: 0, Cleanliness: -1", 25),
                ("frenchfries", "French Fries", "Hunger: +3, Happiness: +4, Energy: +2, Health: -2, Cleanliness: -2", 30),
                ("friedegg", "Fried Egg", "Hunger: +2, Happiness: +1, Energy: +2, Health: +1, Cleanliness: -1", 20),
                ("fruitcake", "Fruitcake", "Hunger: +3, Happiness: +2, Energy: +2, Health: +1, Cleanliness: -1", 40),
                ("garlicbread", "Garlic Bread", "Hunger: +3, Happiness: +2, Energy: +2, Health: 0, Cleanliness: -2", 25),
                ("giantgummybear", "Giant Gummy Bear", "Hunger: +2, Happiness: +5, Energy: +3, Health: -3, Cleanliness: -2", 60),
                ("gingerbreadman", "Gingerbread Man", "Hunger: +2, Happiness: +4, Energy: +2, Health: -1, Cleanliness: -1", 35),
                ("hotdog", "Hot Dog", "Hunger: +3, Happiness: +3, Energy: +2, Health: -2, Cleanliness: -2", 30),
                ("icecream_bowl", "Ice Cream Bowl", "Hunger: +2, Happiness: +5, Energy: +1, Health: -2, Cleanliness: -2", 45),
                ("jam", "Jam", "Hunger: +1, Happiness: +3, Energy: +1, Health: 0, Cleanliness: -1", 15),
                ("jelly", "Jelly", "Hunger: +1, Happiness: +3, Energy: +1, Health: -1, Cleanliness: -1", 20),
                ("lemonpie", "Lemon Pie", "Hunger: +3, Happiness: +4, Energy: +2, Health: -1, Cleanliness: -2", 45),
                ("loafbread", "Loaf Bread", "Hunger: +3, Happiness: +1, Energy: +2, Health: +1, Cleanliness: 0", 25),
                ("macncheese", "Mac and Cheese", "Hunger: +4, Happiness: +3, Energy: +3, Health: -1, Cleanliness: -2", 40),
                ("meatball", "Meatball", "Hunger: +3, Happiness: +2, Energy: +3, Health: +1, Cleanliness: -1", 35),
                ("nacho", "Nacho", "Hunger: +2, Happiness: +4, Energy: +1, Health: -2, Cleanliness: -3", 30),
                ("omlet", "Omelet", "Hunger: +3, Happiness: +2, Energy: +3, Health: +2, Cleanliness: -1", 40),
                ("pancakes", "Pancakes", "Hunger: +3, Happiness: +3, Energy: +2, Health: -1, Cleanliness: -1", 35),
                ("pizza", "Pizza", "Hunger: +4, Happiness: +4, Energy: +3, Health: -2, Cleanliness: -2", 50),
                ("popcorn_bowl", "Popcorn Bowl", "Hunger: +2, Happiness: +3, Energy: +1, Health: -1, Cleanliness: -2", 25),
                ("potatochips_bowl", "Potato Chips Bowl", "Hunger: +2, Happiness: +3, Energy: +1, Health: -2, Cleanliness: -2", 20),
                ("pudding", "Pudding", "Hunger: +2, Happiness: +4, Energy: +1, Health: -1, Cleanliness: -1", 30),
                ("ramen", "Ramen", "Hunger: +4, Happiness: +3, Energy: +3, Health: 0, Cleanliness: -2", 35),
                ("roastedchicken", "Roasted Chicken", "Hunger: +5, Happiness: +3, Energy: +4, Health: +2, Cleanliness: -2", 60),
                ("salmon", "Salmon", "Hunger: +4, Happiness: +2, Energy: +3, Health: +3, Cleanliness: -1", 55),
                ("sandwich", "Sandwich", "Hunger: +3, Happiness: +2, Energy: +3, Health: +1, Cleanliness: -1", 30),
                ("spaghetti", "Spaghetti", "Hunger: +4, Happiness: +3, Energy: +3, Health: +1, Cleanliness: -2", 45),
                ("steak", "Steak", "Hunger: +5, Happiness: +4, Energy: +4, Health: +2, Cleanliness: -2", 70),
                ("strawberrycake", "Strawberry Cake", "Hunger: +3, Happiness: +5, Energy: +2, Health: -2, Cleanliness: -2", 55),
                ("sushi", "Sushi", "Hunger: +3, Happiness: +3, Energy: +2, Health: +3, Cleanliness: -1", 50),
                ("taco", "Taco", "Hunger: +3, Happiness: +3, Energy: +2, Health: 0, Cleanliness: -2", 35),
                ("waffle", "Waffle", "Hunger: +3, Happiness: +3, Energy: +2, Health: -1, Cleanliness: -1", 30),
                ("applepie", "Apple Pie", "Hunger: +3, Happiness: +4, Energy: +2, Health: 0, Cleanliness: -2", 45),
                ("bacon", "Bacon", "Hunger: +2, Happiness: +3, Energy: +2, Health: -1, Cleanliness: -2", 25),
                ("bagel", "Bagel", "Hunger: +3, Happiness: +2, Energy: +2, Health: +1, Cleanliness: -1", 25)
            ]
            
            new_recipes_path = os.path.join(img_path, 'New_recipes')
            for item_id, name, desc, price in food_items:
                item_path = os.path.join(new_recipes_path, f"{item_id}.png")
                if os.path.exists(item_path):
                    item = InventoryItem(
                        name=name,
                        image_path=item_path,
                        description=desc,
                        quantity=0
                    )
                    item.load_image()
                    self.items[item_id] = item
                    
        except Exception as e:
            print(f"Error loading default inventory items: {e}")
    
    def show_inventory(self):
        if hasattr(self.pet_state, 'stats_menu') and self.pet_state.stats_menu.winfo_exists():
            self.pet_state.stats_menu.destroy()
        
        if self.inventory_window and self.inventory_window.winfo_exists():
            self.inventory_window.destroy()
        
        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.attributes('-topmost', True)
        self.inventory_window.title("Inventory")
        self.inventory_window.geometry("450x600")
        self.inventory_window.resizable(False, False)
        
        x = self.root.winfo_x() + self.root.winfo_width()
        y = self.root.winfo_y()
        self.inventory_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(self.inventory_window, bg=COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = tk.Label(main_frame, text="Inventory", font=("Arial", 14, "bold"),
                         bg=COLORS['background'], fg=COLORS['primary'])
        title_label.pack(pady=(0, 10))
        
        currency_frame = tk.Frame(main_frame, bg=COLORS['background'])
        currency_frame.pack(fill=tk.X, pady=(0, 10))
        
        currency_icon = None
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((16, 16), Image.LANCZOS)
                currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading currency icon: {e}")
        
        if currency_icon:
            icon_label = tk.Label(currency_frame, image=currency_icon, bg=COLORS['background'])
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
            icon_label.image = currency_icon
        
        currency_label = tk.Label(currency_frame, text=f"Coins: {self.pet_state.currency}", 
                                font=("Arial", 10, "bold"),
                                bg=COLORS['background'], fg=COLORS['secondary'])
        currency_label.pack(side=tk.LEFT)
        self.pet_state.currency_label = currency_label
        
        canvas = tk.Canvas(main_frame, bg=COLORS['background'], width=420)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        grid_frame = tk.Frame(canvas, bg=COLORS['background'])
        grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        def _on_closing():
            if canvas.winfo_exists():
                canvas.unbind("<MouseWheel>")
            self.inventory_window.destroy()
        
        self.inventory_window.protocol("WM_DELETE_WINDOW", _on_closing)
        
        self.item_buttons = []
        row, col = 0, 0
        max_cols = 4
        
        for item_id, item in self.items.items():
            item_frame = tk.Frame(grid_frame, bg=COLORS['surface'],
                                highlightbackground=COLORS['primary_light'],
                                highlightthickness=1 if item.selected else 0,
                                width=70, height=120)
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            item_frame.grid_propagate(False)
            
            if item.image:
                img_label = tk.Label(item_frame, image=item.image, bg=COLORS['surface'])
                img_label.pack(pady=(5, 0))
            
            name_label = tk.Label(item_frame, text=item.name, font=("Arial", 8),
                                bg=COLORS['surface'], fg=COLORS['text'])
            name_label.pack(pady=(2, 0))
            
            qty_label = tk.Label(item_frame, text=f"x{item.quantity}", font=("Arial", 8),
                              bg=COLORS['surface'], fg=COLORS['text_light'])
            qty_label.pack(pady=(0, 2))
            
            price = self.get_item_price(item_id)
            price_label = tk.Label(item_frame, text=f"{price} coins", 
                                 font=('Arial', 7), bg=COLORS['surface'], fg=COLORS['secondary'])
            price_label.pack(pady=(0, 2))
            
            button_container = tk.Frame(item_frame, bg=COLORS['surface'])
            button_container.pack(side=tk.BOTTOM, pady=(0, 3))
            
            use_btn = tk.Button(button_container, text="Use", command=lambda i=item_id: self.use_item(i),
                          bg=COLORS['primary'], fg='white', font=('Arial', 7))
            use_btn.pack(side=tk.TOP, pady=1)
            use_btn.config(width=6)
            
            if item_id not in ["shower", "toilet_paper"]:
                buy_btn = tk.Button(button_container, text="Buy", command=lambda i=item_id: self.buy_item(i),
                              bg=COLORS['secondary'], fg='white', font=('Arial', 7))
                buy_btn.pack(side=tk.TOP)
                buy_btn.config(width=6)
            
            tooltip_text = self.get_item_description(item_id)
            
            from unified_ui import ModernTooltip
            
            tooltip = ModernTooltip(item_frame, tooltip_text, 
                         bg=COLORS['primary_dark'], 
                         fg='white', 
                         delay=300)
            
            if tooltip.tooltip_window:
                tooltip.tooltip_window.lift()
            
            if item.image:
                ModernTooltip(img_label, tooltip_text, 
                             bg=COLORS['primary_dark'], 
                             fg='white', 
                             delay=300)
            
            ModernTooltip(name_label, tooltip_text, 
                         bg=COLORS['primary_dark'], 
                         fg='white', 
                         delay=300)
            
            item_tooltip = tooltip_text
            
            self.item_buttons.append({
                "id": item_id,
                "frame": item_frame,
                "qty_label": qty_label,
                "tooltip": item_tooltip
            })
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        close_button = tk.Button(main_frame, text="Close", bg=COLORS['primary'],
                              fg="white", font=("Arial", 10), bd=0,
                              command=self.inventory_window.destroy)
        close_button.pack(pady=(10, 0))
        
        self.inventory_window.attributes('-topmost', True)
        
        self.inventory_window.protocol("WM_DELETE_WINDOW", self.inventory_window.destroy)
    
    def select_item(self, item_id):
        if self.selected_item:
            self.selected_item.selected = False
            
            for button in self.item_buttons:
                if button["id"] == self.get_item_id(self.selected_item):
                    button["frame"].config(highlightthickness=0)
        
        item = self.items.get(item_id)
        if item and item.quantity > 0:
            self.selected_item = item
            self.selected_item.selected = True
            
            for button in self.item_buttons:
                if button["id"] == item_id:
                    button["frame"].config(highlightthickness=2)
                else:
                    button["frame"].config(highlightthickness=0)
        else:
            if item and item.quantity <= 0:
                print(f"Out of {item.name}")
            self.selected_item = None
    
    def use_item(self, item_id):
        if item_id in self.items and self.items[item_id].quantity > 0:
            item = self.items[item_id]
            initial_stats = {}
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                initial_stats[stat] = self.pet_state.stats[stat]
            
            self.apply_item_effects(item)
            
            changes = []
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if stat in initial_stats:
                    change = self.pet_state.stats[stat] - initial_stats[stat]
                    if change != 0:
                        changes.append(f"{stat.title()}: {'+' if change > 0 else ''}{change:.0f}%")
            
            if changes:
                feedback = tk.Label(self.inventory_window, 
                                  text="\n".join(changes),
                                  bg=COLORS['success'],
                                  fg="white",
                                  font=("Arial", 10, "bold"),
                                  padx=10, pady=5)
                feedback.place(relx=0.5, rely=0.1, anchor="center")
                self.inventory_window.after(2000, feedback.destroy)
            
            item.quantity -= 1
            self.update_ui()
            return True
        return False

    def buy_item(self, item_id):
        price = self.get_item_price(item_id)
        
        if self.pet_state.currency >= price:
            self.pet_state.currency -= price
            self.items[item_id].add(1)
            self.update_ui()
            self.update_currency_display()
            self.show_buy_feedback(item_id)
            return True
        else:
            self.show_not_enough_coins_message()
            return False
            
    def show_buy_feedback(self, item_id):
        if not self.inventory_window or not self.inventory_window.winfo_exists():
            return
            
        for button in self.item_buttons:
            if button["id"] == item_id:
                feedback = tk.Label(button["frame"], text="Bought!", 
                                  bg=COLORS['success'], fg="white",
                                  font=("Arial", 8, "bold"))
                feedback.place(relx=0.5, rely=0.5, anchor="center")
                
                self.inventory_window.after(1000, feedback.destroy)
                
    def show_not_enough_coins_message(self):
        if not self.inventory_window or not self.inventory_window.winfo_exists():
            return
            
        message = tk.Label(self.inventory_window, text="Not enough coins!", 
                          bg=COLORS['error'], fg="white",
                          font=("Arial", 10, "bold"),
                          padx=10, pady=5)
        message.place(relx=0.5, rely=0.1, anchor="center")
        
        self.inventory_window.after(2000, message.destroy)

    def update_ui(self):
        for button in self.item_buttons:
            item_id = button["id"]
            if item_id in self.items:
                button["qty_label"].config(text=f"x{self.items[item_id].quantity}")
        
        self.update_currency_display()
    
    def apply_item_effects(self, item):
        stats = self.pet_state.stats.stats
        
        is_food_item = False
        
        effects = {}
        if item.description:
            for effect in item.description.split(", "):
                if ": " in effect:
                    stat, value = effect.split(": ")
                    effects[stat.lower()] = int(value.strip("+"))
        
        if effects:
            for stat, value in effects.items():
                if stat == 'hunger':
                    stats['hunger'] = min(100, stats['hunger'] + value)
                elif stat == 'happiness':
                    stats['happiness'] = min(100, stats['happiness'] + value)
                elif stat == 'energy':
                    stats['energy'] = min(100, stats['energy'] + value)
                elif stat == 'health':
                    stats['health'] = max(0, min(100, stats['health'] + value))
                elif stat == 'cleanliness':
                    stats['cleanliness'] = max(0, min(100, stats['cleanliness'] + value))
            
            is_food_item = True
            if hasattr(self.pet_state, 'pet_manager'):
                self.pet_state.pet_manager.handle_interaction('feed')
        elif item.name == "Toilet Paper":
            if hasattr(self.pet_state, 'poop_system'):
                num_poops = len(self.pet_state.poop_system.poops)
                if num_poops > 0:
                    import random
                    poop_index = random.randint(0, num_poops - 1)
                    self.pet_state.poop_system.remove_poop(poop_index)
                    
                    stats['cleanliness'] = min(100, stats['cleanliness'] + 15)
                    return True
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        message = tk.Label(self.inventory_window, text="No poops to clean!", 
                                          bg=COLORS['warning'], fg="white",
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=5)
                        message.place(relx=0.5, rely=0.1, anchor="center")
                        self.inventory_window.after(2000, message.destroy)
                    item.quantity += 1
                    return False
        elif item.name == "Shower":
            stats['cleanliness'] = min(100, stats['cleanliness'] + 15)
            
            if self.inventory_window and self.inventory_window.winfo_exists():
                message = tk.Label(self.inventory_window, text="Cleanliness +15%!", 
                                  bg=COLORS['success'], fg="white",
                                  font=("Arial", 10, "bold"),
                                  padx=10, pady=5)
                message.place(relx=0.5, rely=0.1, anchor="center")
                self.inventory_window.after(2000, message.destroy)
                
            if hasattr(self.pet_state, 'pet_manager'):
                self.pet_state.pet_manager.handle_interaction('clean')
                
            return True
        
        if is_food_item and hasattr(self.pet_state, 'poop_system'):
            self.pet_state.poop_system.add_food_consumed(1)
        
        if hasattr(self.pet_state, 'update_stats_display'):
            self.pet_state.update_stats_display()
        
        for stat in ['health', 'happiness', 'energy', 'hunger', 'cleanliness', 'social']:
            if stat in stats:
                stats[stat] = max(0, stats[stat])

    def start_item_use_mode(self):
        if not self.selected_item:
            print("No item selected")
            return
            
        if not self.selected_item.image:
            if not self.selected_item.load_image():
                print(f"Could not load image for {self.selected_item.name}")
                return
                
        self.original_cursor = self.canvas.cget('cursor')
        self.root.config(cursor='hand2')
        
        self.original_cursor = self.canvas.cget('cursor')
        
        self.canvas.config(cursor='hand2')
        
        self.original_bindings = {
            'motion': self.canvas.bind('<Motion>'),
            'button1': self.canvas.bind('<Button-1>'),
            'button1_motion': self.canvas.bind('<B1-Motion>'),
            'buttonrelease1': self.canvas.bind('<ButtonRelease-1>')
        }
        
        self.canvas.bind('<Motion>', self.move_item_cursor)
        self.item_cursor_id = self.canvas.create_image(0, 0, image=self.selected_item.image)
        
        self.dragging = False
        
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.move_item_cursor)
        self.canvas.bind('<ButtonRelease-1>', self.drop_item)
        
        if self.selected_item and self.selected_item.name == "Toilet Paper":
            if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
                self.pet_state.pet_manager.poop_system.cleaning_mode = True
    
    def move_item_cursor(self, event):
        if hasattr(self, 'item_cursor_id'):
            self.canvas.coords(self.item_cursor_id, event.x, event.y)
            
            if hasattr(self, 'dragging') and self.dragging:
                self.canvas.itemconfig(self.item_cursor_id, state='normal')
                self.canvas.tag_raise(self.item_cursor_id)
                
    def move_drag_window(self, event):
        if hasattr(self, 'drag_window') and self.dragging:
            abs_x = self.root.winfo_x() + event.x - 20
            abs_y = self.root.winfo_y() + event.y - 20
            
            self.drag_window.geometry(f'+{abs_x}+{abs_y}')
            
            self.current_drag_x = abs_x + 20
            self.current_drag_y = abs_y + 20
    
    def start_drag(self, event):
        self.root.bind('<B1-Motion>', self.handle_drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def handle_drag(self, event):
        if hasattr(self, 'drag_window') and self.drag_window:
            x = event.x_root - 16
            y = event.y_root - 16
            self.drag_window.geometry(f'+{x}+{y}')
            self.check_pet_collision(event.x_root, event.y_root)
            if hasattr(self.pet_state, 'poop_system'):
                self.check_poop_collision(event.x_root, event.y_root)

    def drop_item(self, event):
        if not hasattr(self, 'drag_window') or not self.drag_window:
            return
        
        self.drag_window.destroy()
        delattr(self, 'drag_window')
        self.root.unbind('<Motion>')
        self.root.unbind('<Button-1>')
        
        if self.selected_item:
            item_id = next(id for id, item in self.items.items() if item == self.selected_item)
            
            if self.pet_state.check_collision(event.x_root, event.y_root):
                self.use_item(item_id)
            
            elif self.selected_item.name == "Toilet Paper" and hasattr(self.pet_state, 'poop_system'):
                if self.check_poop_collision(event.x_root, event.y_root):
                    self.use_item(item_id)
        
        self.selected_item = None
    
    def check_poop_collision(self, x, y):
        for poop in self.pet_state.poop_system.poops:
            poop_x = poop['abs_x']
            poop_y = poop['abs_y']
            if abs(x - poop_x) < 32 and abs(y - poop_y) < 32:
                self.clean_poop(poop)
                self.pet_state.stats['cleanliness'] = min(100, self.pet_state.stats['cleanliness'] + 15)
                return True
        return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")

    def check_pet_collision(self, x, y):
        if not hasattr(self, 'drag_window'):
            return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")
        
        for item_id in self.items:
            self.update_item_quantity_display(item_id)
        
        self.update_currency_display()
        
        win_x = self.drag_window.winfo_x()
        win_y = self.drag_window.winfo_y()
        
        item_center_x = win_x + 15
        item_center_y = win_y + 15
        
        pet_x = self.root.winfo_x() + 128
        pet_y = self.root.winfo_y() + 128
        
        distance = ((item_center_x - pet_x) ** 2 + (item_center_y - pet_y) ** 2) ** 0.5
        if distance < 100:
            self.feed_pet()
            return True
        return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")

    def feed_pet(self):
        if self.selected_item and self.selected_item.quantity > 0:
            self.pet_state.stats['hunger'] = min(100, self.pet_state.stats['hunger'] + 20)
            self.selected_item.use()
            self.update_quantity_display()
        
    def move_independent_toilet_paper(self, event):
        if hasattr(self, 'drag_window'):
            abs_x = self.root.winfo_pointerx()
            abs_y = self.root.winfo_pointery()
            self.drag_window.geometry(f'32x32+{abs_x-16}+{abs_y-16}')
            
            self.current_drag_x = abs_x
            self.current_drag_y = abs_y
    
    def start_drag(self, event):
        self.root.bind('<B1-Motion>', self.handle_drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def handle_drag(self, event):
        if hasattr(self, 'drag_window') and self.drag_window:
            x = event.x_root - 16
            y = event.y_root - 16
            self.drag_window.geometry(f'+{x}+{y}')
            self.check_pet_collision(event.x_root, event.y_root)
            if hasattr(self.pet_state, 'poop_system'):
                self.check_poop_collision(event.x_root, event.y_root)

    def drop_item(self, event):
        if not hasattr(self, 'drag_window') or not self.drag_window:
            return
        
        self.drag_window.destroy()
        delattr(self, 'drag_window')
        self.root.unbind('<Motion>')
        self.root.unbind('<Button-1>')
        
        if self.selected_item:
            item_id = next(id for id, item in self.items.items() if item == self.selected_item)
            
            if self.pet_state.check_collision(event.x_root, event.y_root):
                self.use_item(item_id)
            
            elif self.selected_item.name == "Toilet Paper" and hasattr(self.pet_state, 'poop_system'):
                if self.check_poop_collision(event.x_root, event.y_root):
                    self.use_item(item_id)
        
        self.selected_item = None
    
    def check_poop_collision(self, x, y):
        for poop in self.pet_state.poop_system.poop_instances:
            poop_x = poop.canvas.coords(poop.poop_id)[0] + self.root.winfo_x()
            poop_y = poop.canvas.coords(poop.poop_id)[1] + self.root.winfo_y()
            distance = ((poop_x - x) ** 2 + (poop_y - y) ** 2) ** 0.5
            if distance < 30:
                self.clean_poop(poop)
        
    def check_pet_collision(self, x, y):
        if not hasattr(self, 'drag_window'):
            return False

    def update_currency_display(self):
        if hasattr(self.pet_state, 'currency_label'):
            self.pet_state.currency_label.config(
                text=f"Coins: {self.pet_state.currency}"
            )

    def update_item_quantity_display(self, item_id):
        for btn in self.item_buttons:
            if btn['id'] == item_id:
                btn["qty_label"].config(text=f"x{self.items[item_id].quantity}")

    def feed_pet(self):
        if self.selected_item and self.selected_item.quantity > 0:
            self.pet_state.stats['hunger'] = min(100, self.pet_state.stats['hunger'] + 20)
            self.selected_item.use()
            self.update_quantity_display()
        
    def start_drag_mode(self, item_id):
        item = self.items.get(item_id)
        if not item:
            return
        
        drag_window = tk.Toplevel(self.root)
        drag_window.overrideredirect(True)
        drag_window.attributes('-topmost', True)
        drag_window.attributes('-alpha', 0.7)
        
        if item.image:
            label = tk.Label(drag_window, image=item.image, bg='white')
            label.pack()
            
            drag_window.geometry(f"{item.image.width()}x{item.image.height()}")
        
        def update_position(event):
            x = self.root.winfo_pointerx() - drag_window.winfo_width()//2
            y = self.root.winfo_pointery() - drag_window.winfo_height()//2
            drag_window.geometry(f"+{x}+{y}")
        
        self.root.bind('<Motion>', update_position)
        
        def use_dragged_item(event):
            if self.selected_item:
                self.use_item(item_id)
            drag_window.destroy()
            self.root.unbind('<Motion>')
            self.root.unbind('<Button-1>')
        
        self.root.bind('<Button-1>', use_dragged_item)
        
        update_position(None)
        
    def drop_item(self, event):
        if not self.selected_item or not self.dragging:
            return "break"
        
        self.dragging = False
        item_used = False
        
        if hasattr(self, 'drag_window'):
            abs_x = self.current_drag_x
            abs_y = self.current_drag_y
        else:
            abs_x = self.root.winfo_x() + event.x
            abs_y = self.root.winfo_y() + event.y
        
        if self.selected_item.name == "Toilet Paper":
            if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
                poop_system = self.pet_state.pet_manager.poop_system
                
                for i, poop in enumerate(poop_system.poops[:]):
                    poop_x = poop['window'].winfo_x() + 16
                    poop_y = poop['window'].winfo_y() + 16
                    
                    distance = ((poop_x - abs_x) ** 2 + (poop_y - abs_y) ** 2) ** 0.5
                    if distance < 40:
                        try:
                            poop['canvas'].itemconfig(poop['id'], state='hidden')
                            poop['window'].update()
                            self.root.after(100)
                            poop['canvas'].itemconfig(poop['id'], state='normal')
                            poop['window'].update()
                            self.root.after(100)
                        except Exception:
                            pass
                            
                        poop['window'].destroy()
                        poop_system.poops.pop(i)
                        item_used = True
                        
                        if 'cleanliness' in self.pet_state.stats:
                            self.pet_state.stats['cleanliness'] = min(100, self.pet_state.stats['cleanliness'] + 15)
                        break
        
        elif self.selected_item.name in ["Bread", "Milk", "Chocolate"]:
            if hasattr(self.pet_state, 'pet_manager'):
                pet_x = self.root.winfo_x() + 128
                pet_y = self.root.winfo_y() + 128
                
                distance = ((abs_x - pet_x) ** 2 + (abs_y - pet_y) ** 2) ** 0.5
                if distance < 60:
                    self.pet_state.pet_manager.handle_interaction('feed')
                    item_used = True
        
        if item_used:
            self.selected_item.use()
            
            for button in self.item_buttons:
                if button["id"] == self.get_item_id(self.selected_item):
                    button["qty_label"].config(text=f"x{self.selected_item.quantity}")
            
            if self.selected_item.quantity <= 0:
                self.stop_item_use_mode()
        else:
            if hasattr(self, 'drag_window'):
                original_x = self.drag_window.winfo_x()
                original_y = self.drag_window.winfo_y()
                for offset in [3, -6, 6, -3]:
                    self.drag_window.geometry(f'+{original_x + offset}+{original_y}')
                    self.drag_window.update()
                    self.root.after(50)
                self.drag_window.geometry(f'+{original_x}+{original_y}')
        
        if hasattr(self, 'drag_window'):
            self.drag_window.destroy()
            delattr(self, 'drag_window')
            delattr(self, 'drag_canvas')
            
        if self.selected_item and self.selected_item.quantity > 0:
            self.item_cursor_id = self.canvas.create_image(event.x, event.y, image=self.selected_item.image)
        
        return "break"
    
    def use_selected_item(self, event):
        pass
    
    def stop_item_use_mode(self):
        self.canvas.config(cursor=self.original_cursor)
        
        if hasattr(self, 'item_cursor_id'):
            self.canvas.delete(self.item_cursor_id)
            delattr(self, 'item_cursor_id')
        
        if hasattr(self, 'drag_window') and self.drag_window.winfo_exists():
            self.drag_window.destroy()
            delattr(self, 'drag_window')
            if hasattr(self, 'drag_canvas'):
                delattr(self, 'drag_canvas')
        
        if hasattr(self, 'drag_image'):
            delattr(self, 'drag_image')
        
        self.dragging = False
        
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        
        if hasattr(self, 'original_bindings'):
            for event, binding in self.original_bindings.items():
                if binding:
                    if event == 'motion':
                        self.canvas.bind('<Motion>', binding)
                    elif event == 'button1':
                        self.canvas.bind('<Button-1>', binding)
                    elif event == 'button1_motion':
                        self.canvas.bind('<B1-Motion>', binding)
                    elif event == 'buttonrelease1':
                        self.canvas.bind('<ButtonRelease-1>', binding)
            delattr(self, 'original_bindings')
        
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item = None
        
        if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
            self.pet_state.pet_manager.poop_system.cleaning_mode = False
    
    def get_item_id(self, item):
        for item_id, inv_item in self.items.items():
            if inv_item == item:
                return item_id
        return None

    def cleanup(self):
        if self.inventory_window and self.inventory_window.winfo_exists():
            self.inventory_window.destroy()
        
        self.stop_item_use_mode()

    def get_item_description(self, item_id):
        """Get detailed description for an item with its attributes"""
        if item_id in self.items:
            item = self.items[item_id]
            
            # Define effects based on item type
            effects = ""
            if item_id == "toilet_paper":
                effects = "\n\nEffects:\n- Cleans 1 poop\n- +15% Cleanliness"
            elif item_id == "shower":
                effects = "\n\nEffects:\n- +15% Cleanliness"
            # For all food items, use their stored description
            else:
                effects = "\n\nEffects:\n" + item.description
                
            # Format price information
            price_info = ""
            if item_id not in ["toilet_paper", "shower"]:
                price = self.get_item_price(item_id)
                price_info = f"\n\nPrice: {price} coins"
            
            # Add usage instructions based on item type
            usage_info = ""
            if item_id == 'toilet_paper':
                usage_info = "\n\nUse: Cleans one poop at a time"
            elif item_id == 'shower':
                usage_info = "\n\nUse: Increases cleanliness by 15%"
            
            # Format the tooltip with better spacing and organization
            return f"{item.name}\n{'-' * len(item.name)}\n{effects}{price_info}{usage_info}"
        
        return "Item not found"
            
    def get_item_price(self, item_id):
        """Get the price of an item based on its ID"""
        # Special case for free items
        if item_id in ["toilet_paper", "shower"]:
            return 0
            
        # Get price from food items list
        food_items = [
            ("baguette", 35), ("bread", 20), ("bun", 15), ("burger", 45),
            ("burrito", 40), ("cheesecake", 50), ("cheesepuff_bowl", 30),
            ("chocolate", 35), ("chocolatecake", 55), ("cookies", 25),
            ("curry", 50), ("donut", 20), ("dumplings", 35),
            ("eggsalad_bowl", 40), ("eggtart", 25), ("frenchfries", 30),
            ("friedegg", 20), ("fruitcake", 40), ("garlicbread", 25),
            ("giantgummybear", 60), ("gingerbreadman", 35), ("hotdog", 30),
            ("icecream_bowl", 45), ("jam", 15), ("jelly", 20),
            ("lemonpie", 45), ("loafbread", 25), ("macncheese", 40),
            ("meatball", 35), ("nacho", 30), ("omlet", 40),
            ("pancakes", 35), ("pizza", 50), ("popcorn_bowl", 25),
            ("potatochips_bowl", 20), ("pudding", 30), ("ramen", 35),
            ("roastedchicken", 60), ("salmon", 55), ("sandwich", 30),
            ("spaghetti", 45), ("steak", 70), ("strawberrycake", 55),
            ("sushi", 50), ("taco", 35), ("waffle", 30),
            ("applepie", 45), ("bacon", 25), ("bagel", 25)
        ]
        
        # Find matching item and return its price
        for food_id, price in food_items:
            if item_id == food_id:
                return price
                
        # Default price if not found
        return 10

    def start_drag_mode(self, item_id):
        """Start drag mode for selected item"""
        item = self.items.get(item_id)
        if not item:
            return
        
        # Create drag window
        drag_window = tk.Toplevel(self.root)
        drag_window.overrideredirect(True)
        drag_window.attributes('-topmost', True)
        drag_window.attributes('-alpha', 0.7)
        
        # Create label with item image
        if item.image:
            label = tk.Label(drag_window, image=item.image, bg='white')
            label.pack()
            
            # Update window size based on image
            drag_window.geometry(f"{item.image.width()}x{item.image.height()}")
        
        # Track mouse movement
        def update_position(event):
            x = self.root.winfo_pointerx() - drag_window.winfo_width()//2
            y = self.root.winfo_pointery() - drag_window.winfo_height()//2
            drag_window.geometry(f"+{x}+{y}")
        
        # Bind mouse movement
        self.root.bind('<Motion>', update_position)
        
        # Handle item use on click
        def use_dragged_item(event):
            if self.selected_item:
                self.use_item(item_id)
            drag_window.destroy()
            self.root.unbind('<Motion>')
            self.root.unbind('<Button-1>')
        
        self.root.bind('<Button-1>', use_dragged_item)
        
        # Initial position
        update_position(None)
        
    def drop_item(self, event):
        """Handle dropping the item at the current position"""
        if not self.selected_item or not self.dragging:
            return "break"  # Prevent event from propagating even if not dragging
        
        self.dragging = False
        item_used = False
        
        # Get absolute coordinates from the drag window position
        if hasattr(self, 'drag_window'):
            # Use the center of the drag window for collision detection
            abs_x = self.current_drag_x
            abs_y = self.current_drag_y
        else:
            # Fallback to mouse coordinates if drag window doesn't exist
            abs_x = self.root.winfo_x() + event.x
            abs_y = self.root.winfo_y() + event.y
        
        # Handle different item types
        if self.selected_item.name == "Toilet Paper":
            # Clean poop if poop system is available
            if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
                poop_system = self.pet_state.pet_manager.poop_system
                
                # Check if dropped on any poop
                for i, poop in enumerate(poop_system.poops[:]):
                    # Get poop window position
                    poop_x = poop['window'].winfo_x() + 16  # Center of poop
                    poop_y = poop['window'].winfo_y() + 16  # Center of poop
                    
                    # Simple distance-based hit detection
                    distance = ((poop_x - abs_x) ** 2 + (poop_y - abs_y) ** 2) ** 0.5
                    if distance < 40:  # Increased radius for easier hit detection
                        # Visual feedback - flash effect before removing
                        try:
                            poop['canvas'].itemconfig(poop['id'], state='hidden')
                            poop['window'].update()
                            self.root.after(100)
                            poop['canvas'].itemconfig(poop['id'], state='normal')
                            poop['window'].update()
                            self.root.after(100)
                        except Exception:
                            pass  # In case window was already destroyed
                            
                        # Destroy poop window
                        poop['window'].destroy()
                        # Remove from list
                        poop_system.poops.pop(i)
                        item_used = True
                        
                        # Improve cleanliness stat slightly for each cleaned poop
                        if 'cleanliness' in self.pet_state.stats:
                            # ...
                            # In drop_item method where poop is cleaned:
                            self.pet_state.stats['cleanliness'] = min(100, self.pet_state.stats['cleanliness'] + 15)
                        break
        
        # Handle food items
        elif self.selected_item.name in ["Bread", "Milk", "Chocolate"]:
            # Feed pet if within range
            if hasattr(self.pet_state, 'pet_manager'):
                # Get pet window position and center
                pet_x = self.root.winfo_x() + 128  # Assuming pet is centered in canvas
                pet_y = self.root.winfo_y() + 128  # Assuming pet is centered in canvas
                
                # Simple distance check to pet center using absolute coordinates
                distance = ((abs_x - pet_x) ** 2 + (abs_y - pet_y) ** 2) ** 0.5
                if distance < 60:  # Increased radius for easier feeding
                    # Visual feedback before feeding
                    self.pet_state.pet_manager.handle_interaction('feed')
                    item_used = True
        
        # Reduce quantity if item was used
        if item_used:
            self.selected_item.use()
            
            # Update quantity label if inventory is open
            for button in self.item_buttons:
                if button["id"] == self.get_item_id(self.selected_item):
                    button["qty_label"].config(text=f"x{self.selected_item.quantity}")
            
            # Stop using item if quantity is zero
            if self.selected_item.quantity <= 0:
                self.stop_item_use_mode()
        else:
            # Provide visual feedback that item couldn't be used here
            # Shake effect for the drag window
            if hasattr(self, 'drag_window'):
                original_x = self.drag_window.winfo_x()
                original_y = self.drag_window.winfo_y()
                for offset in [3, -6, 6, -3]:
                    self.drag_window.geometry(f'+{original_x + offset}+{original_y}')
                    self.drag_window.update()
                    self.root.after(50)
                # Reset to original position
                self.drag_window.geometry(f'+{original_x}+{original_y}')
        
        # Clean up the drag window
        if hasattr(self, 'drag_window'):
            self.drag_window.destroy()
            delattr(self, 'drag_window')
            delattr(self, 'drag_canvas')
            
        # Restore item cursor for continued use if item wasn't fully used up
        if self.selected_item and self.selected_item.quantity > 0:
            self.item_cursor_id = self.canvas.create_image(event.x, event.y, image=self.selected_item.image)
        
        # Prevent event from propagating to other handlers
        return "break"
    
    def use_selected_item(self, event):
        """Legacy method for backward compatibility"""
        # This is now handled by drop_item
        pass
    
    def stop_item_use_mode(self):
        """Stop using the selected item"""
        # Restore original cursor
        self.canvas.config(cursor=self.original_cursor)
        
        # Remove item cursor image
        if hasattr(self, 'item_cursor_id'):
            self.canvas.delete(self.item_cursor_id)
            delattr(self, 'item_cursor_id')
        
        # Clean up drag window if it exists
        if hasattr(self, 'drag_window') and self.drag_window.winfo_exists():
            self.drag_window.destroy()
            delattr(self, 'drag_window')
            if hasattr(self, 'drag_canvas'):
                delattr(self, 'drag_canvas')
        
        # Clean up drag image reference
        if hasattr(self, 'drag_image'):
            delattr(self, 'drag_image')
        
        # Reset dragging state
        self.dragging = False
        
        # Unbind all events related to item use
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        
        # Restore original bindings if they were saved
        if hasattr(self, 'original_bindings'):
            # Only restore bindings that were previously saved
            for event, binding in self.original_bindings.items():
                if binding:
                    if event == 'motion':
                        self.canvas.bind('<Motion>', binding)
                    elif event == 'button1':
                        self.canvas.bind('<Button-1>', binding)
                    elif event == 'button1_motion':
                        self.canvas.bind('<B1-Motion>', binding)
                    elif event == 'buttonrelease1':
                        self.canvas.bind('<ButtonRelease-1>', binding)
            delattr(self, 'original_bindings')
        
        # Reset selected item
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item = None
        
        # Reset cleaning mode if toilet paper was being used
        if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
            self.pet_state.pet_manager.poop_system.cleaning_mode = False
    
    def get_item_id(self, item):
        """Get the ID of an item object"""
        for item_id, inv_item in self.items.items():
            if inv_item == item:
                return item_id
        return None

    def cleanup(self):
        """Clean up resources when shutting down"""
        # Close inventory window if open
        if self.inventory_window and self.inventory_window.winfo_exists():
            self.inventory_window.destroy()
        
        # Stop item use mode
        self.stop_item_use_mode()