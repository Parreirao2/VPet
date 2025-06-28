"""Poop System Module

This module handles the pet's pooping behavior, including:
- Random poop generation during pet movement
- Displaying poops on the screen
- Cleaning mechanism for removing poops
- Effects of uncleaned poops on pet stats
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import random
from datetime import datetime, timedelta

class PoopSystem:
    """Manages pet poop generation, display and cleaning"""
    
    def __init__(self, root, canvas, pet_state):
        self.root = root
        self.canvas = canvas
        self.pet_state = pet_state
        
        # List to track all poops on screen
        self.poops = []
        
        # Load poop images
        self.poop_images = []
        self.toilet_paper_image = None
        self.load_images()
        
        # Poop generation settings
        # Get poop frequency from pet_manager settings if available
        if hasattr(pet_state, 'pet_manager') and hasattr(pet_state.pet_manager, 'settings'):
            self.poop_chance = pet_state.pet_manager.settings.get('poop_frequency', 0.1)  # Increased default from 0.1 to 5.0
        else:
            self.poop_chance = 0.1  # Increased default from 0.1 to 5.0
        self.last_poop_time = datetime.now()
        self.min_poop_interval = random.randint(300, 900)  # Reduced from 300-900 to 10-30 seconds
        
        # Food consumption tracking for poop generation
        self.food_consumed = 0
        self.food_poop_multiplier = 0.05  # Each food item increases poop chance by 5%
        
        # Cleaning mode variables
        self.cleaning_mode = False
        self.original_cursor = None
        
        # Track uncleaned poops effect
        self.poop_check_timer = None
        
        # Animation timer for poops
        self.poop_animation_timer = None
        self.start_poop_animation()
        
    def add_food_consumed(self, amount=1):
        """Increase the food consumed counter to affect poop generation chance"""
        self.food_consumed += amount
        print(f"Food consumed increased to {self.food_consumed}")
        
        self.start_poop_check_timer()
        
        # Debug message to confirm initialization
        print(f"Poop system initialized with chance: {self.poop_chance}%, interval: {self.min_poop_interval}s")
    
    def load_images(self):
        """Load poop and toilet paper images"""
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets')
            
            # Load poop images
            poop1 = Image.open(os.path.join(img_path, 'poop1.png')).convert("RGBA")
            poop2 = Image.open(os.path.join(img_path, 'poop2.png')).convert("RGBA")
            
            # Resize poop images (adjust size as needed)
            size = (32, 32)
            poop1 = poop1.resize(size, Image.LANCZOS)
            poop2 = poop2.resize(size, Image.LANCZOS)
            
            # Create a transparent background
            # This ensures proper transparency handling in Tkinter
            for img in [poop1, poop2]:
                # Create a fully transparent background
                background = Image.new("RGBA", img.size, (0, 0, 0, 0))
                # Composite the image onto the transparent background
                background.paste(img, (0, 0), img)
                img = background
            
            # Convert to PhotoImage
            self.poop_images = [
                ImageTk.PhotoImage(poop1),
                ImageTk.PhotoImage(poop2)
            ]
            
            # Load and prepare toilet paper image for cursor
            toilet_paper = Image.open(os.path.join(img_path, 'toilet_paper.png')).convert("RGBA")
            toilet_paper = toilet_paper.resize((32, 32), Image.LANCZOS)
            
            # Create transparent background for toilet paper
            background = Image.new("RGBA", toilet_paper.size, (0, 0, 0, 0))
            background.paste(toilet_paper, (0, 0), toilet_paper)
            toilet_paper = background
            
            self.toilet_paper_image = ImageTk.PhotoImage(toilet_paper)
            
        except Exception as e:
            print(f'Error loading poop images: {e}')
    
    def check_poop_generation(self, x, y):
        """Check if a poop should be generated at the current position"""
        # Don't generate poop if pet is interacting or in cleaning mode
        if self.pet_state.is_interacting or self.cleaning_mode:
            return
        
        # Check if enough time has passed since last poop
        now = datetime.now()
        if (now - self.last_poop_time).total_seconds() < self.min_poop_interval:
            return
        
        # Random chance to generate poop based on cleanliness stat and poop_frequency setting
        # Lower cleanliness increases poop chance, but with a more significant effect from the slider
        cleanliness = self.pet_state.stats.get_stat('cleanliness') if hasattr(self.pet_state, 'stats') else 100
        
        # Calculate poop chance based on cleanliness, poop_frequency setting, and food consumed
        # Lower cleanliness increases poop chance
        adjusted_chance = self.poop_chance * (1 + (100 - cleanliness) / 100)
        
        # Add food consumption effect to poop chance
        if self.food_consumed > 0:
            food_effect = self.food_consumed * self.food_poop_multiplier
            adjusted_chance += food_effect
            print(f"Food effect on poop chance: +{food_effect:.2f}% from {self.food_consumed} food items")
        
        # Debug print to check poop generation
        print(f"Poop check: chance={adjusted_chance:.2f}%, random={random.random() * 100:.2f}%, interval={self.min_poop_interval}s")
        
        # Significantly increase the chance to make poops appear more frequently for testing
        random_value = random.random()
        if random_value <= (adjusted_chance):
            print(f"GENERATING POOP! Random value: {random_value} <= {adjusted_chance}")
            # Get absolute screen coordinates for the poop
            # Use the root window's position plus the canvas center coordinates
            screen_x = self.root.winfo_x() + 128  # Center of pet canvas
            screen_y = self.root.winfo_y() + 128  # Center of pet canvas
            self.generate_poop(screen_x, screen_y)
            self.last_poop_time = now
            
            # Reduce the minimum interval between poops when frequency is high
            self.min_poop_interval = max(10, 300 - (self.poop_chance * 1000))  # Reduced minimum interval
            
            # Reduce food consumed counter after generating a poop
            if self.food_consumed > 0:
                self.food_consumed = 0  # Reset to 0 instead of reducing by 1
                print(f"Food consumed reset to {self.food_consumed} after generating poop")
    
    def generate_poop(self, screen_x, screen_y):
        """Generate a poop at the specified absolute screen position"""
        # Start with the first poop image
        poop_img = self.poop_images[0]
        
        # Add small random offset so poop isn't directly under pet
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        
        # Store absolute screen coordinates
        abs_x = screen_x + offset_x
        abs_y = screen_y + offset_y
        
        # Create a separate toplevel window for the poop
        poop_window = tk.Toplevel(self.root)
        poop_window.overrideredirect(True)  # Remove window decorations
        poop_window.attributes('-topmost', True)  # Keep on top
        
        # Make window transparent - use a consistent approach for Windows
        # Use a specific color for transparency that works well on Windows
        transparent_color = '#010101'
        poop_window.config(bg=transparent_color)
        poop_window.attributes('-transparentcolor', transparent_color)
        
        # Create canvas for poop with transparent background
        poop_canvas = tk.Canvas(poop_window, width=32, height=32, 
                              highlightthickness=0, bg=transparent_color)
        poop_canvas.pack()
        
        # Create poop on canvas
        poop_id = poop_canvas.create_image(16, 16, image=poop_img)
        
        # Position the poop window at the absolute coordinates
        poop_window.geometry(f'32x32+{abs_x}+{abs_y}')
        
        # Store poop info with reference to the image, window and canvas
        self.poops.append({
            'id': poop_id,
            'window': poop_window,
            'canvas': poop_canvas,
            'image': poop_img,  # Keep reference to prevent garbage collection
            'time': datetime.now(),
            'abs_x': abs_x,  # Store absolute screen coordinates
            'abs_y': abs_y,
            'frame': 0  # Track current animation frame (0 or 1)
        })
        
        # Decrease cleanliness stat
        if hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.modify_stat('cleanliness', -5)
            print(f"Poop generated! Cleanliness reduced to {self.pet_state.stats.get_stat('cleanliness')}")

    
    def start_cleaning_mode(self):
        """Enter cleaning mode with toilet paper cursor"""
        if not self.cleaning_mode:
            self.cleaning_mode = True
            self.original_cursor = self.canvas.cget('cursor')
            
            # Check if we're using the inventory system
            if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'inventory_system'):
                # Let the inventory system handle the cursor and cleaning
                # We just set the cleaning mode flag for coordination
                pass
            else:
                # Legacy mode - direct cursor handling
                try:
                    # Try to set custom cursor (this may not work on all platforms)
                    self.canvas.config(cursor='hand2')  # Fallback cursor
                    
                    # Show toilet paper image following mouse
                    self.canvas.bind('<Motion>', self.move_toilet_paper)
                    self.toilet_paper_id = self.canvas.create_image(0, 0, image=self.toilet_paper_image)
                    
                    # Bind click to clean poop
                    self.canvas.bind('<Button-1>', self.clean_poop)
                except Exception as e:
                    print(f"Error setting custom cursor: {e}")
                    # Fallback to simple cursor change
                    self.canvas.config(cursor='hand2')
                    self.canvas.bind('<Button-1>', self.clean_poop)
    
    def move_toilet_paper(self, event):
        """Move toilet paper image with cursor"""
        if hasattr(self, 'toilet_paper_id'):
            # Get absolute screen coordinates
            abs_x = self.root.winfo_pointerx()
            abs_y = self.root.winfo_pointery()
            self.canvas.coords(self.toilet_paper_id, abs_x, abs_y)
            
            # Update collision detection with global position
            self.check_poop_cleaning(abs_x, abs_y)

    def check_poop_cleaning(self, x, y):
        """Check if toilet paper is touching any poops using screen coordinates"""
        for poop in self.poops[:]:
            # Get poop window position (center of poop)
            poop_x = poop['window'].winfo_x() + 16
            poop_y = poop['window'].winfo_y() + 16
            
            if abs(x - poop_x) < 32 and abs(y - poop_y) < 32:
                # Destroy poop window
                poop['window'].destroy()
                # Remove from list
                self.poops.remove(poop)
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', 15)
                    print(f"Poop cleaned! Cleanliness increased to {self.pet_state.stats.get_stat('cleanliness')}")
    
    def stop_cleaning_mode(self):
        """Exit cleaning mode"""
        if self.cleaning_mode:
            self.cleaning_mode = False
            
            # Restore original cursor
            self.canvas.config(cursor=self.original_cursor)
            
            # Remove toilet paper image and unbind events
            if hasattr(self, 'toilet_paper_id'):
                self.canvas.delete(self.toilet_paper_id)
                delattr(self, 'toilet_paper_id')
            
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Button-1>')
    
    def clean_poop(self, event):
        """Clean poop when clicked in cleaning mode"""
        if not self.cleaning_mode:
            return
        
        # Get absolute mouse coordinates
        abs_x = self.root.winfo_x() + event.x
        abs_y = self.root.winfo_y() + event.y
        
        cleaned = False
        
        # Check if click is on any poop
        for i, poop in enumerate(self.poops[:]):
            # Get poop window position
            poop_x = poop['window'].winfo_x() + 16  # Center of poop
            poop_y = poop['window'].winfo_y() + 16  # Center of poop
            
            # Simple distance-based hit detection
            distance = ((poop_x - abs_x) ** 2 + (poop_y - abs_y) ** 2) ** 0.5
            if distance < 20:  # 20 pixel radius for hit detection
                # Destroy poop window
                poop['window'].destroy()
                # Remove from list
                self.poops.pop(i)
                cleaned = True
                
                # Improve cleanliness stat slightly for each cleaned poop
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', 2)
                    print(f"Poop cleaned! Cleanliness increased to {self.pet_state.stats.get_stat('cleanliness')}")
                break
        
        # Exit cleaning mode if all poops are cleaned
        if not self.poops:
            self.stop_cleaning_mode()
            return cleaned
    
    def start_poop_check_timer(self):
        """Start timer to check for old poops and apply effects"""
        self.check_old_poops()
        # Check every 30 seconds
        self.poop_check_timer = self.root.after(30000, self.start_poop_check_timer)
    
    def check_old_poops(self):
        now = datetime.now()
        has_old_poops = False

        # Check each poop's age
        for poop in self.poops:
            # If poop is older than 5 minutes (300 seconds)
            if (now - poop['time']).total_seconds() > 300:
                has_old_poops = True
                # Gradually decrease cleanliness for each old poop
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', -3)
                    print(f"Old poop found! Cleanliness reduced to {self.pet_state.stats.get_stat('cleanliness')}")

        # Apply effects if there are old poops
        if has_old_poops:
            # Decrease happiness and health
            if hasattr(self.pet_state, 'stats'):
                self.pet_state.stats.modify_stat('happiness', -0.5)
                self.pet_state.stats.modify_stat('health', -0.2)
                print(f"Old poops affecting pet! Happiness: {self.pet_state.stats.get_stat('happiness')}, Health: {self.pet_state.stats.get_stat('health')}")

            # Make pet sad if there are too many old poops
            if len(self.poops) > 3 and self.pet_state.current_animation != 'sad':
                self.pet_state.current_animation = 'sad'

    
    def start_poop_animation(self):
        """Start animation timer for poops"""
        self.animate_poops()
        # Animate every 500ms (2 frames per second)
        self.poop_animation_timer = self.root.after(500, self.start_poop_animation)
    
    def animate_poops(self):
        """Update poop animations by cycling between frames"""
        if not self.poops:
            return
            
        for poop in self.poops:
            # Toggle between frame 0 and 1
            poop['frame'] = 1 - poop['frame']
            # Update image
            poop_img = self.poop_images[poop['frame']]
            poop['image'] = poop_img  # Update reference
            # Update canvas item
            poop['canvas'].itemconfig(poop['id'], image=poop_img)
            
            # Ensure window transparency settings are maintained
            transparent_color = '#010101'
            poop['window'].config(bg=transparent_color)
            poop['window'].attributes('-transparentcolor', transparent_color)
            poop['canvas'].config(bg=transparent_color)
            poop['window'].update()
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        if self.poop_check_timer:
            self.root.after_cancel(self.poop_check_timer)
            self.poop_check_timer = None
            
        if hasattr(self, 'poop_animation_timer') and self.poop_animation_timer:
            self.root.after_cancel(self.poop_animation_timer)
            self.poop_animation_timer = None
        
        # Destroy all poop windows
        for poop in self.poops:
            if 'window' in poop and poop['window'].winfo_exists():
                poop['window'].destroy()
        
        self.poops = []
    
    def clean_all_poops(self):
        """Remove all existing poops"""
        for poop in self.poops:
            poop['window'].destroy()
        self.poops = []
    
    def remove_poop(self, index):
        """Remove a specific poop by index"""
        if 0 <= index < len(self.poops):
            # Destroy the poop window
            self.poops[index]['window'].destroy()
            # Remove from the list
            removed_poop = self.poops.pop(index)
            return True
        return False
    
