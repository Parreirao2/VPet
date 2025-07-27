import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import time
from datetime import datetime, timedelta
from unified_ui import COLORS

class TreasureSystem:
    def __init__(self, root, canvas, pet_state, inventory_system, pet_manager=None):
        self.root = root
        self.canvas = canvas
        self.pet_state = pet_state
        self.inventory_system = inventory_system
        self.pet_manager = pet_manager  # Add this line
        
        # Treasure chest state
        self.chest_window = None
        self.chest_active = False
        self.last_chest_hour = -1
        self.chest_timer_id = None
        self.chest_disappear_timer_id = None
        self.last_chest_spawn_date = None  # Add this line
        
        # Load treasure chest image
        self.chest_image = None
        self.load_chest_image()
        
        # Define item tiers
        self.item_tiers = {
            'basic': ['apple', 'donut', 'croissant'],
            'mid': ['hotdog', 'sandwich', 'bacon', 'cupcake'],
            'good': ['cheese', 'burger', 'ice_cream'],
            'premium': ['chocolate_bar', 'cooked_fish', 'sushi'],
            'exotic': ['enchanted_apple', 'first_aid']  # Special items
        }
        
        # Start the treasure system
        self.start_treasure_system()
    
    def load_chest_image(self):
        """Load the treasure chest image with proper aspect ratio"""
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'Treasure.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate scaling factor to fit within max size while preserving aspect ratio
                max_size = 80
                scale_factor = min(max_size / original_width, max_size / original_height)
                
                # Calculate new dimensions
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                # Resize with proper aspect ratio
                img = img.resize((new_width, new_height), Image.LANCZOS)
                self.chest_image = ImageTk.PhotoImage(img)
                self.chest_width = new_width
                self.chest_height = new_height
                return True
        except Exception as e:
            print(f"Error loading treasure chest image: {e}")
        return False
    
    def start_treasure_system(self):
        """Start the treasure chest system with frequent checks for testing"""
        self.check_treasure_spawn()
        # Schedule next check in 1 minute (reverted from 10 seconds testing)
        self.chest_timer_id = self.root.after(60000, self.start_treasure_system)
    
    def check_treasure_spawn(self):
        """Check if a treasure chest should spawn"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_date = current_time.date()
        
        # Check if we already spawned a chest today
        if (self.last_chest_spawn_date == current_date or 
            current_hour == self.last_chest_hour or 
            self.chest_active):
            return
        
        # Random chance to spawn (15-25% chance per hour)
        if random.random() < 0.2:  # 20% chance every hour
            self.spawn_treasure_chest()
            self.last_chest_hour = current_hour
            self.last_chest_spawn_date = current_date  # Add this line
    
    def get_save_data(self):
        """Get treasure system data for saving"""
        return {
            'last_chest_hour': self.last_chest_hour,
            'last_chest_spawn_date': self.last_chest_spawn_date.isoformat() if self.last_chest_spawn_date else None,
            'chest_active': self.chest_active
        }
    
    def load_save_data(self, data):
        """Load treasure system data from save"""
        if data:
            self.last_chest_hour = data.get('last_chest_hour', -1)
            if data.get('last_chest_spawn_date'):
                from datetime import date
                self.last_chest_spawn_date = date.fromisoformat(data['last_chest_spawn_date'])
            self.chest_active = data.get('chest_active', False)
    
    def spawn_treasure_chest(self):
        """Spawn a treasure chest at a random position on screen"""
        if self.chest_active or not self.chest_image:
            return
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use actual chest dimensions
        chest_w = getattr(self, 'chest_width', 64)
        chest_h = getattr(self, 'chest_height', 64)
        
        # Random position on screen (avoiding edges)
        chest_x = random.randint(100, screen_width - chest_w - 100)
        chest_y = random.randint(100, screen_height - chest_h - 100)
        
        # Store position for popup message
        self.chest_x = chest_x
        self.chest_y = chest_y
        
        # Create treasure chest window with proper dimensions
        self.chest_window = tk.Toplevel(self.root)
        self.chest_window.overrideredirect(True)
        self.chest_window.attributes('-topmost', True)
        self.chest_window.geometry(f"{chest_w + 40}x{chest_h + 40}+{chest_x}+{chest_y}")
        
        # Create chest canvas with padding for glow effect
        # Use a different background color that won't interfere with transparency
        chest_canvas = tk.Canvas(self.chest_window, width=chest_w + 40, height=chest_h + 40, 
                                highlightthickness=0, bg='#000001')  # Changed from #010101
        chest_canvas.pack()
        
        # Make background transparent (use the new background color)
        self.chest_window.wm_attributes('-transparentcolor', '#000001')
        
        # Add chest image at center
        chest_canvas.create_image((chest_w + 40) // 2, (chest_h + 40) // 2, image=self.chest_image)
        
        # Store canvas reference for glow effect
        self.chest_canvas = chest_canvas
        
        # Add glow effect
        self.add_glow_effect(chest_canvas, chest_w, chest_h)
        
        # Bind click event
        chest_canvas.bind('<Button-1>', self.on_chest_clicked)
        self.chest_window.bind('<Button-1>', self.on_chest_clicked)
        
        # Set chest as active
        self.chest_active = True
        
        # Schedule chest disappearance after 5 minutes (reverted from 30 seconds testing)
        self.chest_disappear_timer_id = self.root.after(300000, self.remove_treasure_chest)
        
        print("Treasure chest spawned!")
    
    def add_glow_effect(self, canvas, chest_w, chest_h):
        """Add a visible pulsing glow effect to the chest"""
        self.glow_phase = 0
        
        def pulse_glow():
            if not self.chest_active or not canvas.winfo_exists():
                return
            
            # Remove previous glow
            canvas.delete("glow")
            
            # Calculate pulsing intensity (0.4 to 1.0)
            import math
            intensity = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self.glow_phase))
            self.glow_phase += 0.15
            
            # Create multiple glow rings using filled ovals with stipple for transparency effect
            center_x = (chest_w + 60) // 2
            center_y = (chest_h + 60) // 2
            
            # Outer glow (largest, most transparent)
            glow_size_outer = max(chest_w, chest_h) // 2 + 25
            canvas.create_oval(
                center_x - glow_size_outer, center_y - glow_size_outer,
                center_x + glow_size_outer, center_y + glow_size_outer,
                fill="#FFD700", outline="#FFD700", width=2,
                stipple="gray25", tags="glow"
            )
            
            # Middle glow
            glow_size_mid = max(chest_w, chest_h) // 2 + 18
            canvas.create_oval(
                center_x - glow_size_mid, center_y - glow_size_mid,
                center_x + glow_size_mid, center_y + glow_size_mid,
                fill="#FFFF00", outline="#FFFF00", width=2,
                stipple="gray50", tags="glow"
            )
            
            # Inner glow (smaller, more intense)
            glow_size_inner = max(chest_w, chest_h) // 2 + 12
            canvas.create_oval(
                center_x - glow_size_inner, center_y - glow_size_inner,
                center_x + glow_size_inner, center_y + glow_size_inner,
                outline="#FFFFFF", width=int(3 * intensity), tags="glow"
            )
            
            # Core glow (bright outline around chest)
            glow_size_core = max(chest_w, chest_h) // 2 + 5
            canvas.create_oval(
                center_x - glow_size_core, center_y - glow_size_core,
                center_x + glow_size_core, center_y + glow_size_core,
                outline="#FFFF88", width=int(2 * intensity), tags="glow"
            )
            
            # Schedule next pulse
            if self.chest_active:
                self.root.after(80, pulse_glow)
        
        pulse_glow()
    
    def on_chest_clicked(self, event):
        """Handle treasure chest click"""
        if not self.chest_active:
            return
        
        # Generate rewards
        rewards = self.generate_rewards()
        
        # Apply rewards
        self.apply_rewards(rewards)
        
        # Show reward message
        self.show_reward_message(rewards)
        
        # Remove chest
        self.remove_treasure_chest()
    
    def generate_rewards(self):
        """Generate random rewards based on the specified probabilities"""
        rewards = {
            'coins': 0,
            'items': []
        }
        
        # Generate coin reward (50-300)
        rewards['coins'] = random.randint(50, 300)
        
        # Generate item rewards based on probabilities
        rand = random.random() * 100
        
        if rand <= 60:  # 60% chance - Basic Tier
            item_count = random.randint(1, 5)
            for _ in range(item_count):
                item = random.choice(self.item_tiers['basic'])
                rewards['items'].append(item)
        
        elif rand <= 80:  # 20% chance - Mid-Tier
            item_count = random.randint(1, 3)
            for _ in range(item_count):
                item = random.choice(self.item_tiers['mid'])
                rewards['items'].append(item)
        
        elif rand <= 90:  # 10% chance - Good Tier
            item_count = random.randint(1, 3)
            for _ in range(item_count):
                item = random.choice(self.item_tiers['good'])
                rewards['items'].append(item)
        
        elif rand <= 95:  # 5% chance - Premium Tier
            item = random.choice(self.item_tiers['premium'])
            rewards['items'].append(item)
        
        else:  # 5% chance - Exotic Tier (changed from 1% to 5% for better balance)
            item = random.choice(self.item_tiers['exotic'])
            rewards['items'].append(item)
        
        return rewards
    
    def apply_rewards(self, rewards):
        """Apply the generated rewards to the player"""
        # Add coins
        self.pet_state.currency += rewards['coins']
        
        # Add items to inventory
        for item_id in rewards['items']:
            if item_id in self.inventory_system.items:
                self.inventory_system.items[item_id].add(1)
        
        # Update currency display if inventory is open
        if hasattr(self.pet_state, 'currency_label') and self.pet_state.currency_label:
            try:
                # Check if the widget still exists before updating
                if self.pet_state.currency_label.winfo_exists():
                    self.pet_state.currency_label.config(
                        text=f"Coins: {self.pet_state.currency}"
                    )
            except tk.TclError:
                # Widget has been destroyed, ignore the update
                pass
        
        # Update inventory UI if open
        if hasattr(self.inventory_system, 'update_ui'):
            try:
                self.inventory_system.update_ui()
            except tk.TclError:
                # UI has been destroyed, ignore the update
                pass
        
        # Auto-save the game to prevent loss of rewards
        try:
            if self.pet_manager and hasattr(self.pet_manager, 'save_pet'):
                success, message = self.pet_manager.save_pet(is_autosave=True)
                if success:
                    print("Game auto-saved after treasure chest opened")
                else:
                    print(f"Auto-save failed: {message}")
            else:
                print("Warning: Could not auto-save - pet_manager not available")
        except Exception as e:
            print(f"Error during auto-save: {e}")
    
    def show_reward_message(self, rewards):
        """Show a message displaying the rewards received above the treasure chest"""
        # Create reward message
        message_parts = ["🎉 Treasure Found! 🎉"]
        message_parts.append(f"💰 +{rewards['coins']} coins")
        
        if rewards['items']:
            # Count items
            item_counts = {}
            for item_id in rewards['items']:
                if item_id in self.inventory_system.items:
                    item_name = self.inventory_system.items[item_id].name
                    item_counts[item_name] = item_counts.get(item_name, 0) + 1
            
            message_parts.append("\n📦 Items received:")
            for item_name, count in item_counts.items():
                message_parts.append(f"  • {item_name} x{count}")
        
        reward_text = "\n".join(message_parts)
        
        # Only show the popup window (remove speech bubble to avoid duplicates)
        self.show_popup_message(reward_text)
    
    def show_popup_message(self, message):
        """Show popup message above treasure chest"""
        # Create popup window above treasure chest
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        
        # Calculate position above treasure chest
        popup_x = getattr(self, 'chest_x', 200)
        popup_y = getattr(self, 'chest_y', 200) - 150  # 150 pixels above chest
        
        # Ensure popup stays on screen
        if popup_y < 50:
            popup_y = getattr(self, 'chest_y', 200) + getattr(self, 'chest_height', 64) + 20
        
        # Create styled message frame
        frame = tk.Frame(popup, bg='#2C3E50', relief='raised', bd=2)
        frame.pack(padx=5, pady=5)
        
        # Create message label with better styling
        msg_label = tk.Label(frame, text=message, 
                            font=("Arial", 11, "bold"), 
                            bg='#2C3E50', 
                            fg='#F1C40F',  # Gold color
                            justify=tk.LEFT,
                            padx=15, pady=10)
        msg_label.pack()
        
        # Update popup to get proper size
        popup.update_idletasks()
        popup_width = popup.winfo_reqwidth()
        popup_height = popup.winfo_reqheight()
        
        # Center popup horizontally relative to chest
        chest_center_x = popup_x + getattr(self, 'chest_width', 64) // 2
        final_x = chest_center_x - popup_width // 2
        
        # Ensure popup stays on screen horizontally
        screen_width = self.root.winfo_screenwidth()
        if final_x < 10:
            final_x = 10
        elif final_x + popup_width > screen_width - 10:
            final_x = screen_width - popup_width - 10
        
        popup.geometry(f"+{final_x}+{popup_y}")
        
        # Auto-close after 4 seconds
        popup.after(4000, popup.destroy)
        
    def remove_treasure_chest(self):
        """Remove the treasure chest from screen"""
        if self.chest_window and self.chest_window.winfo_exists():
            self.chest_window.destroy()
        
        self.chest_window = None
        self.chest_active = False
        
        # Cancel disappear timer if it exists
        if self.chest_disappear_timer_id:
            self.root.after_cancel(self.chest_disappear_timer_id)
            self.chest_disappear_timer_id = None
        
        print("Treasure chest removed")
    
    def cleanup(self):
        """Clean up the treasure system"""
        # Cancel timers
        if self.chest_timer_id:
            self.root.after_cancel(self.chest_timer_id)
        
        if self.chest_disappear_timer_id:
            self.root.after_cancel(self.chest_disappear_timer_id)
        
        # Remove chest if active
        self.remove_treasure_chest()