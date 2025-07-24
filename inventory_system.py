import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
from unified_ui import COLORS

class InventoryItem:
    
    def __init__(self, name, image_path, description, quantity=1, max_quantity=99, unlimited=False, cost=0):
        self.name = name
        self.image_path = image_path
        self.description = description
        self.quantity = quantity
        self.max_quantity = max_quantity
        self.unlimited = unlimited
        self.cost = cost
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
                    quantity=1,
                    unlimited=True
                )
                toilet_paper.load_image()
                self.items["toilet_paper"] = toilet_paper
            
            shower_path = os.path.join(img_path, 'shower.png')
            if os.path.exists(shower_path):
                shower = InventoryItem(
                    name="Shower",
                    image_path=shower_path,
                    description="Increases cleanliness by 15%",
                    quantity=1,
                    unlimited=True
                )
                shower.load_image()
                self.items["shower"] = shower
    
                sleeping_path = os.path.join(img_path, 'sleeping.png')
                if os.path.exists(sleeping_path):
                    sleeping = InventoryItem(
                        name="Sleep",
                        image_path=sleeping_path,
                        description="Put your pet to sleep to recover energy gradually",
                        quantity=1,
                        unlimited=True,
                        cost=0
                    )
                    sleeping.load_image()
                    self.items["sleeping"] = sleeping
    
            evo1_path = os.path.join(img_path, 'Evo1.png')
            if os.path.exists(evo1_path):
                evo1 = InventoryItem(
                    name="Evo1",
                    image_path=evo1_path,
                    description="Evolves your pet to the next stage.",
                    quantity=0,
                    max_quantity=1
                )
                evo1.load_image()
                self.items["evo1"] = evo1

            evo2_path = os.path.join(img_path, 'Evo2.png')
            if os.path.exists(evo2_path):
                evo2 = InventoryItem(
                    name="Evo2",
                    image_path=evo2_path,
                    description="Evolves your pet to a special stage.",
                    quantity=0,
                    max_quantity=1
                )
                evo2.load_image()
                self.items["evo2"] = evo2

            food_items = [
    # Basic/Cheap Items
    ("bun", "Bun", "Hunger: +5, Happiness: +2, Energy: +2, Health: +1, Cleanliness: 0", 15),
    ("jam", "Jam", "Hunger: +6, Happiness: +4, Energy: +3, Health: +1, Cleanliness: -1", 18),
    ("bread", "Bread", "Hunger: +8, Happiness: +3, Energy: +4, Health: +2, Cleanliness: 0", 20),
    ("donut", "Donut", "Hunger: +7, Happiness: +6, Energy: +4, Health: 0, Cleanliness: -2", 22),
    ("friedegg", "Fried Egg", "Hunger: +9, Happiness: +4, Energy: +5, Health: +2, Cleanliness: -1", 24),
    ("jelly", "Jelly", "Hunger: +7, Happiness: +6, Energy: +4, Health: +1, Cleanliness: -2", 23),
    ("potatochips_bowl", "Potato Chips Bowl", "Hunger: +8, Happiness: +6, Energy: +3, Health: 0, Cleanliness: -2", 22),

    # Mid-tier Items
    ("bagel", "Bagel", "Hunger: +12, Happiness: +5, Energy: +5, Health: +3, Cleanliness: -1", 30),
    ("bacon", "Bacon", "Hunger: +13, Happiness: +6, Energy: +6, Health: +2, Cleanliness: -2", 34),
    ("cookies", "Cookies", "Hunger: +12, Happiness: +7, Energy: +6, Health: +1, Cleanliness: -1", 36),
    ("eggtart", "Egg Tart", "Hunger: +13, Happiness: +6, Energy: +5, Health: +2, Cleanliness: -1", 33),
    ("garlicbread", "Garlic Bread", "Hunger: +12, Happiness: +6, Energy: +5, Health: +3, Cleanliness: -2", 32),
    ("loafbread", "Loaf Bread", "Hunger: +14, Happiness: +4, Energy: +5, Health: +3, Cleanliness: 0", 35),
    ("popcorn_bowl", "Popcorn Bowl", "Hunger: +13, Happiness: +6, Energy: +4, Health: +2, Cleanliness: -2", 33),
    ("cheesepuff_bowl", "Cheesepuff Bowl", "Hunger: +17, Happiness: +7, Energy: +5, Health: +1, Cleanliness: -3", 45),
    ("frenchfries", "French Fries", "Hunger: +18, Happiness: +7, Energy: +4, Health: +1, Cleanliness: -3", 47),
    ("hotdog", "Hot Dog", "Hunger: +19, Happiness: +6, Energy: +5, Health: +1, Cleanliness: -2", 48),
    ("nacho", "Nacho", "Hunger: +18, Happiness: +7, Energy: +4, Health: +1, Cleanliness: -3", 46),
    ("pudding", "Pudding", "Hunger: +16, Happiness: +7, Energy: +5, Health: +2, Cleanliness: -1", 42),
    ("sandwich", "Sandwich", "Hunger: +20, Happiness: +6, Energy: +6, Health: +4, Cleanliness: -1", 50),
    ("waffle", "Waffle", "Hunger: +19, Happiness: +7, Energy: +5, Health: +2, Cleanliness: -2", 48),

    # Good Items
    ("baguette", "Baguette", "Hunger: +23, Happiness: +6, Energy: +6, Health: +4, Cleanliness: -1", 55),
    ("chocolate", "Chocolate", "Hunger: +22, Happiness: +10, Energy: +6, Health: +2, Cleanliness: -1", 58),
    ("dumplings", "Dumplings", "Hunger: +24, Happiness: +6, Energy: +6, Health: +4, Cleanliness: -1", 60),
    ("gingerbreadman", "Gingerbread Man", "Hunger: +22, Happiness: +9, Energy: +6, Health: +2, Cleanliness: -2", 58),
    ("meatball", "Meatball", "Hunger: +25, Happiness: +7, Energy: +7, Health: +5, Cleanliness: -1", 62),
    ("pancakes", "Pancakes", "Hunger: +24, Happiness: +9, Energy: +6, Health: +3, Cleanliness: -1", 60),
    ("ramen", "Ramen", "Hunger: +26, Happiness: +8, Energy: +7, Health: +4, Cleanliness: -2", 65),
    ("taco", "Taco", "Hunger: +24, Happiness: +7, Energy: +6, Health: +3, Cleanliness: -2", 60),
    ("burrito", "Burrito", "Hunger: +30, Happiness: +7, Energy: +7, Health: +3, Cleanliness: -2", 70),
    ("eggsalad_bowl", "Egg Salad Bowl", "Hunger: +28, Happiness: +6, Energy: +6, Health: +5, Cleanliness: -1", 72),
    ("fruitcake", "Fruitcake", "Hunger: +29, Happiness: +7, Energy: +6, Health: +4, Cleanliness: -1", 74),
    ("macncheese", "Mac and Cheese", "Hunger: +30, Happiness: +9, Energy: +6, Health: +3, Cleanliness: -2", 76),
    ("omlet", "Omelet", "Hunger: +28, Happiness: +6, Energy: +7, Health: +5, Cleanliness: -1", 72),
    ("burger", "Burger", "Hunger: +34, Happiness: +8, Energy: +8, Health: +3, Cleanliness: -3", 85),
    ("icecream_bowl", "Ice Cream Bowl", "Hunger: +32, Happiness: +10, Energy: +5, Health: +2, Cleanliness: -2", 80),
    ("lemonpie", "Lemon Pie", "Hunger: +33, Happiness: +10, Energy: +6, Health: +3, Cleanliness: -2", 82),
    ("applepie", "Apple Pie", "Hunger: +34, Happiness: +10, Energy: +6, Health: +4, Cleanliness: -2", 86),
    ("spaghetti", "Spaghetti", "Hunger: +35, Happiness: +8, Energy: +7, Health: +5, Cleanliness: -2", 88),

    # Premium Items (now stronger)
    ("cheesecake", "Cheesecake", "Hunger: +45, Happiness: +18, Energy: +12, Health: +8, Cleanliness: -2", 105),
    ("curry", "Curry", "Hunger: +48, Happiness: +15, Energy: +14, Health: +12, Cleanliness: -3", 110),
    ("pizza", "Pizza", "Hunger: +50, Happiness: +17, Energy: +14, Health: +10, Cleanliness: -3", 115),
    ("sushi", "Sushi", "Hunger: +47, Happiness: +16, Energy: +13, Health: +14, Cleanliness: -1", 108),
    ("chocolatecake", "Chocolate Cake", "Hunger: +52, Happiness: +20, Energy: +12, Health: +9, Cleanliness: -2", 120),
    ("salmon", "Salmon", "Hunger: +55, Happiness: +15, Energy: +15, Health: +14, Cleanliness: -1", 130),
    ("strawberrycake", "Strawberry Cake", "Hunger: +50, Happiness: +19, Energy: +13, Health: +10, Cleanliness: -2", 118),
    ("giantgummybear", "Giant Gummy Bear", "Hunger: +52, Happiness: +24, Energy: +16, Health: +8, Cleanliness: -3", 135),
    ("roastedchicken", "Roasted Chicken", "Hunger: +56, Happiness: +17, Energy: +17, Health: +13, Cleanliness: -2", 140),

    # Luxury Item (maxed)
    ("steak", "Steak", "Hunger: +60, Happiness: +60, Energy: +60, Health: +60, Cleanliness: +60", 200)
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
    
    def show_inventory(self, parent_window=None):
        print(f"[DEBUG] InventorySystem.show_inventory: parent_window={'valid' if parent_window else 'None'}")
        if hasattr(self.pet_state, 'stats_menu') and self.pet_state.stats_menu.winfo_exists():
            self.pet_state.stats_menu.destroy()
        
        if self.inventory_window and self.inventory_window.winfo_exists():
            self.inventory_window.destroy()
        
        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.title("Inventory")
        self.inventory_window.geometry("450x600")
        self.inventory_window.resizable(False, False)
        
        # Position the window relative to the parent window if provided, otherwise use default positioning
        if parent_window and parent_window.winfo_exists():
            # Force update to ensure geometry info is up to date
            parent_window.update_idletasks()
            # Position to the right of the parent window
            x = parent_window.winfo_x() + parent_window.winfo_width()
            y = parent_window.winfo_y()
            print(f"[DEBUG] Positioning inventory window relative to parent: x={x}, y={y}")
            print(f"[DEBUG] Parent window geometry: x={parent_window.winfo_x()}, y={parent_window.winfo_y()}, width={parent_window.winfo_width()}, height={parent_window.winfo_height()}")
            self.inventory_window.geometry(f"+{x}+{y}")
            # Ensure the inventory window is on top of the parent window
            self.inventory_window.attributes('-topmost', True)
            # After a short delay, reset topmost to allow proper window layering
            self.inventory_window.after(500, lambda: self.inventory_window.attributes('-topmost', False))
        else:
            # Default positioning to the right of the main window
            x = self.root.winfo_x() + self.root.winfo_width()
            y = self.root.winfo_y()
            print(f"[DEBUG] Positioning inventory window with default positioning: x={x}, y={y}")
            self.inventory_window.geometry(f"+{x}+{y}")
            self.inventory_window.attributes('-topmost', True)
        
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
        
        # Create scrollable frame for inventory items
        scrollable_frame = tk.Frame(main_frame, bg=COLORS['background'])
        scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with fixed height to ensure scrolling
        canvas = tk.Canvas(scrollable_frame, bg=COLORS['background'], width=380, height=300, highlightthickness=0)
        
        # Create scrollbar - always visible with explicit styling
        scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview, width=20, bg=COLORS['background'])
        
        # Create the frame that will hold all inventory items
        grid_frame = tk.Frame(canvas, bg=COLORS['background'])
        
        # Configure scrolling behavior
        def configure_scroll_region(event=None):
            # Update scroll region to encompass all items
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            
            if bbox:
                # Always ensure there's enough content to scroll
                canvas_height = canvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                
                # If content is smaller than canvas, create minimum scroll region
                min_scroll_height = max(content_height, canvas_height + 50)
                canvas.configure(scrollregion=(0, 0, 0, min_scroll_height))
            else:
                # No items yet, set a default scroll region to show scrollbar
                canvas.configure(scrollregion=(0, 0, 0, 400))
        
        def configure_canvas_width(event):
            # Make the grid frame match the canvas width
            canvas_width = event.width - scrollbar.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        # Bind events for dynamic resizing
        grid_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # Create window in canvas for the grid frame
        canvas_window = canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        
        # Link canvas and scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid configuration - 4 columns
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references for later use
        self.inventory_canvas = canvas
        self.inventory_scrollbar = scrollbar
        self.inventory_grid_frame = grid_frame
        
        # Mouse wheel scrolling function
        def _on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to canvas and main frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        main_frame.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Also bind to the inventory window for better mouse wheel support
        self.inventory_window.bind("<MouseWheel>", _on_mousewheel)
        
        # Force initial scroll region update
        self.inventory_window.after(100, configure_scroll_region)
        
        def _on_closing():
            if canvas.winfo_exists():
                canvas.unbind("<MouseWheel>")
            self.inventory_window.destroy()
        
        self.inventory_window.protocol("WM_DELETE_WINDOW", _on_closing)
        
        self.item_buttons = []
        row, col = 0, 0
        max_cols = 4

        sorted_items = sorted(self.items.items(), key=lambda item: self.get_item_price(item[0]))

        for item_id, item in sorted_items:
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
            
            qty_label = None
            if not item.unlimited:
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
            
            if item_id not in ["shower", "toilet_paper", "sleeping"]:
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
        
        # Import SimpleButton for prettier close button
        from unified_ui import SimpleButton
        
        close_button = SimpleButton(main_frame, text="Close", 
                                   bg=COLORS['primary'], fg="white",
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
        if item_id in self.items and (self.items[item_id].quantity > 0 or item_id in ['toilet_paper', 'shower', 'sleeping']):
            item = self.items[item_id]
            initial_stats = {}
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                initial_stats[stat] = self.pet_state.stats[stat]
            
            print(f"[DEBUG] Using item: {item.name} (ID: {item_id})")
            print(f"[DEBUG] Initial stats: {initial_stats}")
            
            # Check if this is a food item before applying effects
            is_food_item = False
            if item.description:
                for effect in item.description.split(", "):
                    if ": " in effect:
                        stat, value = effect.split(": ")
                        if stat.lower() == 'hunger':
                            is_food_item = True
                            break
                        
            self.apply_item_effects(item)
            
            changes = []
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if stat in initial_stats:
                    change = self.pet_state.stats[stat] - initial_stats[stat]
                    if change != 0:
                        changes.append(f"{stat.title()}: {'+' if change > 0 else ''}{change:.0f}%")
            
            # Skip immediate stat display for sleeping item (handled separately)
            if item.name == "Sleep":
                print("[DEBUG] Skipping immediate stat display for sleeping item")
                pass
            elif changes and not is_food_item:  # Don't show speech bubble for food items (handled by handle_interaction)
                # Use speech bubble system instead of inventory window pop-ups
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    change_text = "\n".join(changes)
                    self.pet_state.speech_bubble.show_bubble('custom', f"Used {item.name}!\n{change_text}")
                    print(f"[DEBUG] Displayed speech bubble with changes: {change_text}")
                else:
                    # Fallback to inventory window if speech bubble not available
                    feedback = tk.Label(self.inventory_window,
                                      text="\n".join(changes),
                                      bg=COLORS['success'],
                                      fg="white",
                                      font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
                    feedback.place(relx=0.5, rely=0.1, anchor="center")
                    self.inventory_window.after(2000, feedback.destroy)
                    print("[DEBUG] Used fallback inventory window pop-up")
            
            if not item.unlimited:
                item.quantity -= 1
            self.update_ui()
            return True
        return False

    def buy_item(self, item_id):
        if item_id == "evo1" and (self.pet_state.stage == "Adult" or self.pet_state.stage == "Special"):
            if self.inventory_window and self.inventory_window.winfo_exists():
                message = tk.Label(self.inventory_window, text="Pet is already at max stage!",
                                  bg=COLORS['warning'], fg="white",
                                  font=("Arial", 10, "bold"),
                                  padx=10, pady=5)
                message.place(relx=0.5, rely=0.1, anchor="center")
                self.inventory_window.after(2000, message.destroy)
            return False

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
        if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
            self.pet_state.speech_bubble.show_bubble('custom', "Item purchased!")
        else:
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
        if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
            self.pet_state.speech_bubble.show_bubble('custom', "Not enough coins!")
        else:
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
            if item_id in self.items and button["qty_label"]:
                button["qty_label"].config(text=f"x{self.items[item_id].quantity}")
        
        self.update_currency_display()
    
    def apply_item_effects(self, item):
        stats = self.pet_state.stats.stats
        
        is_food_item = False
        
        effects = {}
        
        print(f"[DEBUG] Applying effects for item: {item.name}")
        if item.description:
            for effect in item.description.split(", "):
                if ": " in effect:
                    stat, value = effect.split(": ")
                    effects[stat.lower()] = int(value.strip("+"))
        
        if effects:
            # Check if this is a food item (has hunger effect)
            is_food_item = 'hunger' in effects
            
            if is_food_item:
                # Trigger feeding animation through handle_interaction
                if hasattr(self.pet_state, 'pet_manager'):
                    # Calculate total hunger increase for the interaction
                    hunger_increase = effects.get('hunger', 0)
                    # Temporarily store the effects to apply after animation
                    self.pending_food_effects = effects
                    # Trigger the feeding animation
                    self.pet_state.pet_manager.handle_interaction('feed')
                    # Apply the specific item effects (overriding the default +20 hunger)
                    self.apply_pending_food_effects()
                else:
                    # Fallback to direct stat modification if no pet_manager
                    self.apply_direct_food_effects(effects)
            else:
                # Non-food items, apply effects directly
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
            
            # Increase poop pressure for food items
            if is_food_item and hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'poop_system'):
                self.pet_state.pet_manager.poop_system.add_food_consumed(1)
                print(f"[DEBUG] Food item used - increased poop pressure")
        elif item.name == "Toilet Paper":
            if hasattr(self.pet_state, 'poop_system'):
                num_poops = len(self.pet_state.poop_system.poops)
                if num_poops > 0:
                    import random
                    poop_index = random.randint(0, num_poops - 1)
                    self.pet_state.poop_system.remove_poop(poop_index)
                    
                    stats['cleanliness'] = min(100, stats['cleanliness'] + 15)
                    self.pet_state.stats.modify_stat('social', 3) # Increase social for toilet paper
                    return True
                else:
                    # Use speech bubble for "no poops" message
                    if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                        self.pet_state.speech_bubble.show_bubble('custom', "No poops to clean!")
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
            # Trigger clean interaction for animation
            if hasattr(self.pet_state, 'pet_manager'):
                self.pet_state.pet_manager.handle_interaction('clean')
            else:
                # Fallback to direct stat modification
                self.pet_state.stats['cleanliness'] = min(100, self.pet_state.stats['cleanliness'] + 15)
                self.pet_state.stats['happiness'] = min(100, self.pet_state.stats['happiness'] + 5)
            
            # Use speech bubble for shower effect
            if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                self.pet_state.speech_bubble.show_bubble('custom', "Cleanliness +15%!" )
            else:
                if self.inventory_window and self.inventory_window.winfo_exists():
                    message = tk.Label(self.inventory_window, text="Cleanliness +15%!",
                                      bg=COLORS['success'], fg="white",
                                      font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
                    message.place(relx=0.5, rely=0.1, anchor="center")
                    self.inventory_window.after(2000, message.destroy)
                
            # Don't call handle_interaction to avoid duplicate pop-ups
            # The inventory system already displays the speech bubble
            return True
        
        elif item.name == "Evo1":
            if self.pet_state.stage != "Adult":
                if self.pet_state.stage == "Baby":
                    self.pet_state.growth.evolve_to("Child")
                elif self.pet_state.stage == "Child":
                    self.pet_state.growth.evolve_to("Teen")
                elif self.pet_state.stage == "Teen":
                    self.pet_state.growth.evolve_to("Adult")
            else:
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    self.pet_state.speech_bubble.show_bubble('custom', "Pet is already at max stage!")
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        message = tk.Label(self.inventory_window, text="Pet is already at max stage!",
                                          bg=COLORS['warning'], fg="white",
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=5)
                        message.place(relx=0.5, rely=0.1, anchor="center")
                        self.inventory_window.after(2000, message.destroy)
                item.quantity += 1
                return False
        elif item.name == "Evo2":
            if self.pet_state.stage != "Special":
                self.pet_state.growth.evolve_to("Special")
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    self.pet_state.speech_bubble.show_bubble('custom', "Your pet evolved to Special stage!")
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        message = tk.Label(self.inventory_window, text="Your pet evolved to Special stage!",
                                          bg=COLORS['success'], fg="white",
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=5)
                        message.place(relx=0.5, rely=0.1, anchor="center")
                        self.inventory_window.after(2000, message.destroy)
                if hasattr(self.pet_state, 'update_pet_display'): # Assuming this method exists or will be added
                    self.pet_state.update_pet_display()
            else:
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    self.pet_state.speech_bubble.show_bubble('custom', "Pet is already in Special stage!")
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                            self.pet_state.speech_bubble.show_bubble('custom', "Pet is already in Special stage!")
                        else:
                            message = tk.Label(self.inventory_window, text="Pet is already in Special stage!",
                                              bg=COLORS['warning'], fg="white",
                                              font=("Arial", 10, "bold"),
                                              padx=10, pady=5)
                            message.place(relx=0.5, rely=0.1, anchor="center")
                            self.inventory_window.after(2000, message.destroy)
                item.quantity += 1 # Refund item if already in special stage
                return False
        elif item.name == "Sleep":
            # Check if pet is already sleeping
            if hasattr(self.pet_state, 'current_animation') and self.pet_state.current_animation == 'sleeping':
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    self.pet_state.speech_bubble.show_bubble('custom', "Pet is already sleeping!")
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        message = tk.Label(self.inventory_window, text="Pet is already sleeping!",
                                          bg=COLORS['warning'], fg="white",
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=5)
                        message.place(relx=0.5, rely=0.1, anchor="center")
                        self.inventory_window.after(2000, message.destroy)
                item.quantity += 1  # Refund item
                return False
            
            # Calculate sleep time based on missing energy
            current_energy = self.pet_state.stats.stats.get('energy', 100)
            missing_energy = 100 - current_energy
            if missing_energy <= 0:
                if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                    self.pet_state.speech_bubble.show_bubble('custom', "Pet already has full energy!")
                else:
                    if self.inventory_window and self.inventory_window.winfo_exists():
                        message = tk.Label(self.inventory_window, text="Pet already has full energy!",
                                          bg=COLORS['info'], fg="white",
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=5)
                        message.place(relx=0.5, rely=0.1, anchor="center")
                        self.inventory_window.after(2000, message.destroy)
                item.quantity += 1  # Refund item
                return False
            
            # Calculate sleep duration (max 5 minutes = 300000ms, scaled by missing energy)
            max_sleep_time = 300000  # 5 minutes in milliseconds
            sleep_duration = int(max_sleep_time * (missing_energy / 100))
            min_sleep_time = 5000  # Minimum 5 seconds
            sleep_duration = max(min_sleep_time, sleep_duration)
            
            # Calculate stat changes for display
            energy_gain = missing_energy
            happiness_loss = -5  # Small happiness decrease for sleeping
            social_gain = 0
            
            # Starting sleep: missing_energy={missing_energy}, sleep_duration={sleep_duration}
            
            # Start sleeping
            self.pet_state.current_animation = 'sleeping'
            self.pet_state.is_interacting = True
            self.pet_state.is_sleeping = True
            self.pet_state.sleep_start_time = datetime.now()
            self.pet_state.sleep_duration = sleep_duration
            self.pet_state.sleep_end_time = datetime.now().timestamp() + (sleep_duration / 1000)
            
            # Set animation to sleeping: {self.pet_state.current_animation}
            
            # Create sleep timer display
            self.create_sleep_timer()
            
            # Start energy recovery
            self.start_energy_recovery()
            
            # Show sleeping message
            print(f"[DEBUG] Pet attributes: {dir(self.pet_state)}")
            print(f"[DEBUG] Has speech_bubble: {hasattr(self.pet_state, 'speech_bubble')}")
            print(f"[DEBUG] Has canvas: {hasattr(self.pet_state, 'canvas')}")
            
            # Try multiple ways to show the message
            message_text = f"Pet is now sleeping! ({int(missing_energy)}% energy to recover)"
            
            # Method 1: Speech bubble
            if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                print("[DEBUG] Showing sleep message via speech bubble")
                self.pet_state.speech_bubble.show_bubble('custom', message_text)
            # Method 2: Canvas text
            elif hasattr(self.pet_state, 'canvas'):
                print("[DEBUG] Showing sleep message via canvas")
                if hasattr(self.pet_state, 'sleep_message_id'):
                    self.pet_state.canvas.delete(self.pet_state.sleep_message_id)
                self.pet_state.sleep_message_id = self.pet_state.canvas.create_text(
                    128, 30, text=message_text,
                    font=("Arial", 12, "bold"), fill="white"
                )
                self.parent.after(3000, lambda: self.pet_state.canvas.delete(self.pet_state.sleep_message_id))
            # Method 3: Inventory window fallback
            else:
                print("[DEBUG] No speech bubble or canvas, using inventory window")
                if self.inventory_window and self.inventory_window.winfo_exists():
                    message = tk.Label(self.inventory_window, text=message_text,
                                      bg=COLORS['success'], fg="white",
                                      font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
                    message.place(relx=0.5, rely=0.1, anchor="center")
                    self.inventory_window.after(3000, message.destroy)
            
            # The sleeping item messages are handled within this block
            # Return True to indicate the item was used successfully
            return True
        
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

    def create_sleep_timer(self):
        """Create and display sleep timer countdown"""
        print("[DEBUG] Creating sleep timer")
        if not hasattr(self.pet_state, 'canvas'):
            print("[DEBUG] No canvas found for sleep timer")
            return
            
        # Remove existing timer if any
        if hasattr(self.pet_state, 'sleep_timer_id'):
            self.pet_state.canvas.delete(self.pet_state.sleep_timer_id)
            
        # Create timer text
        self.pet_state.sleep_timer_id = self.pet_state.canvas.create_text(
            128, 50,  # Position above pet
            text="Sleeping...",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="sleep_timer"
        )
        
        print("[DEBUG] Sleep timer created successfully")
        self.update_sleep_timer()

    def update_sleep_timer(self):
        """Update the sleep timer display"""
        if not hasattr(self.pet_state, 'sleep_timer_id') or not hasattr(self.pet_state, 'sleep_end_time'):
            return
            
        current_time = datetime.now().timestamp()
        remaining = self.pet_state.sleep_end_time - current_time
        
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            timer_text = f"Sleep: {minutes:02d}:{seconds:02d}"
            
            self.canvas.itemconfig(self.pet_state.sleep_timer_id, text=timer_text)
            
            # Schedule next update
            if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
                self.root.after(1000, self.update_sleep_timer)
        else:
            # Sleep finished
            self.clear_sleep_timer()

    def clear_sleep_timer(self):
        """Clear the sleep timer display"""
        if hasattr(self.pet_state, 'sleep_timer_id'):
            self.canvas.delete(self.pet_state.sleep_timer_id)
            delattr(self.pet_state, 'sleep_timer_id')

    def start_energy_recovery(self):
        """Start gradual energy recovery during sleep"""
        if not hasattr(self.pet_state, 'is_sleeping') or not self.pet_state.is_sleeping:
            print("[DEBUG] Energy recovery stopped - not sleeping")
            return
            
        current_energy = self.pet_state.stats.stats.get('energy', 100)
        print(f"[DEBUG] Energy recovery: current={current_energy}, sleeping={self.pet_state.is_sleeping}")
        
        if current_energy >= 100:
            print("[DEBUG] Energy full, waking up pet")
            self.wake_up_pet()
            return
            
        # Calculate energy to add (scaled by missing energy)
        missing_energy = 100 - current_energy
        recovery_rate = max(1, missing_energy // 50)  # Recover 1-2% per tick
        
        # Add energy
        self.pet_state.stats.modify_stat('energy', recovery_rate)
        
        # Reduce hunger: 1% per 5% energy gain
        hunger_drop = recovery_rate // 5
        if hunger_drop > 0:
            self.pet_state.stats.modify_stat('hunger', -hunger_drop)
        
        print(f"[DEBUG] Recovery: +{recovery_rate}% energy, -{hunger_drop}% hunger")
        
        # Update stats display
        if hasattr(self.pet_state, 'update_stats_display'):
            self.pet_state.update_stats_display()
        
        # Continue recovery if still sleeping
        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
            print("[DEBUG] Scheduling next energy recovery")
            self.root.after(2000, self.start_energy_recovery)

    def wake_up_pet(self):
        """Wake up the pet from sleep"""
        print("[DEBUG] wake_up_pet called")
        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
            print("[DEBUG] Waking up pet")
            self.pet_state.is_sleeping = False
            self.pet_state.sleep_start_time = None  # Reset sleep_start_time
            self.pet_state.current_animation = 'Standing'
            self.pet_state.is_interacting = False
            print(f"[DEBUG] Set is_sleeping to {self.pet_state.is_sleeping}, sleep_start_time to None, current_animation to {self.pet_state.current_animation}")

            # Clear sleep timer
            self.clear_sleep_timer()
            
            # Cancel any pending sleep timers
            if hasattr(self.pet_state, 'sleep_timer'):
                print("[DEBUG] Canceling pending sleep timers")
                self.root.after_cancel(self.pet_state.sleep_timer)
            
            # Show wake up message
            if hasattr(self.pet_state, 'speech_bubble') and self.pet_state.speech_bubble:
                print("[DEBUG] Showing wake up message via speech bubble")
                self.pet_state.speech_bubble.show_bubble('custom', "Pet woke up!")
            else:
                print("[DEBUG] Showing wake up message in inventory window")
                if self.inventory_window and self.inventory_window.winfo_exists():
                    message = tk.Label(self.inventory_window, text="Pet woke up!",
                                      bg=COLORS['info'], fg="white",
                                      font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
                    message.place(relx=0.5, rely=0.1, anchor="center")
                    self.inventory_window.after(2000, message.destroy)
        else:
            print("[DEBUG] wake_up_pet called but pet is not sleeping")
            
    def apply_pending_food_effects(self):
        """Apply the specific food item effects after the feeding animation starts"""
        if hasattr(self, 'pending_food_effects'):
            stats = self.pet_state.stats.stats
            for stat, value in self.pending_food_effects.items():
                if stat == 'hunger':
                    # Override the default +20 from handle_interaction
                    stats['hunger'] = min(100, stats['hunger'] - 20 + value)  # Remove default, add item value
                elif stat == 'happiness':
                    stats['happiness'] = min(100, stats['happiness'] + value)
                elif stat == 'energy':
                    stats['energy'] = min(100, stats['energy'] + value)
                elif stat == 'health':
                    stats['health'] = max(0, min(100, stats['health'] + value))
                elif stat == 'cleanliness':
                    stats['cleanliness'] = max(0, min(100, stats['cleanliness'] + value))
            
            self.pet_state.stats.modify_stat('social', 5)  # Increase social for food items
            del self.pending_food_effects

    def apply_direct_food_effects(self, effects):
        """Fallback method to apply food effects directly without animation"""
        stats = self.pet_state.stats.stats
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
        
        self.pet_state.stats.modify_stat('social', 5)  # Increase social for food items

    def handle_double_click(self, event):
        """Handle double-click to wake up sleeping pet"""
        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
            # Check if click is on the pet area
            pet_x, pet_y = 128, 128  # Center of pet
            distance = ((event.x - pet_x) ** 2 + (event.y - pet_y) ** 2) ** 0.5
            
            if distance < 50:  # Click within pet area
                self.wake_up_pet()

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
            if item_id not in ["toilet_paper", "shower", "sleeping"]:
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
        if item_id in ["toilet_paper", "shower", "sleeping"]:
            return 0
        if item_id == "evo1":
            return 10000
        if item_id == "evo2":
            return 1000000
            
        # Get price from food items list (organized by price tiers)
        food_items = [
            # Basic/Cheap Items (15-25 coins)
            ("bun", 15), ("jam", 15), ("bread", 20), ("donut", 20),
            ("friedegg", 20), ("jelly", 20), ("potatochips_bowl", 20),
            ("bagel", 25), ("bacon", 25), ("cookies", 25), ("eggtart", 25),
            ("garlicbread", 25), ("loafbread", 25), ("popcorn_bowl", 25),
            
            # Mid-tier Items (30-35 coins)
            ("cheesepuff_bowl", 30), ("frenchfries", 30), ("hotdog", 30),
            ("nacho", 30), ("pudding", 30), ("sandwich", 30), ("waffle", 30),
            ("baguette", 35), ("chocolate", 35), ("dumplings", 35),
            ("gingerbreadman", 35), ("meatball", 35), ("pancakes", 35),
            ("ramen", 35), ("taco", 35),
            
            # Good Items (40-45 coins)
            ("burrito", 40), ("eggsalad_bowl", 40), ("fruitcake", 40),
            ("macncheese", 40), ("omlet", 40), ("burger", 45),
            ("icecream_bowl", 45), ("lemonpie", 45), ("applepie", 45),
            ("spaghetti", 45),
            
            # Premium Items (50-60 coins)
            ("cheesecake", 50), ("curry", 50), ("pizza", 50), ("sushi", 50),
            ("chocolatecake", 55), ("salmon", 55), ("strawberrycake", 55),
            ("giantgummybear", 60), ("roastedchicken", 60),
            
            # Luxury Item (70 coins)
            ("steak", 70)
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