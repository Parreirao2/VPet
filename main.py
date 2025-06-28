import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import math
import shutil
from datetime import datetime
from unified_ui import CombinedPanel, SimpleSpeechBubble, SimpleStatusPanel
import pystray
import random
import threading
import time  # Added import for time module
from PIL import Image, ImageTk, ImageDraw
from speech_bubble import SpeechBubble
from system_tray import create_context_menu, setup_system_tray
from poop_system import PoopSystem
from inventory_system import InventorySystem
from pet_animation import PetAnimation
from pet_components import PetStats, PetGrowth

# PetStats class is now imported from pet_components.py

class PetState:
    def __init__(self):
        # Create PetGrowth instance first
        self.growth = PetGrowth(None)
        # Create PetStats with reference to growth
        self.stats = PetStats(self.growth)
        # Connect stats back to growth
        self.growth.stats = self.stats
        self.stage = 'Baby'  # Baby, Child, Teen, Adult
        self.current_animation = 'Standing'
        self.direction = 'left'
        self.is_interacting = False  # Flag to track if pet is in an interaction
        self.currency = 100  # Initialize currency with starting amount
        # Dictionary to track game progress (highest level reached for each game)
        self.game_progress = {
            'number_guesser': 1,
            'reaction_test': 1,
            'ball_clicker': 1
        }

class VirtualPet:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Removes window decorations
        self.root.attributes('-topmost', True)  # Keep window on top
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(self.save_path, exist_ok=True)
        self.last_save = None
        self.name = "My Pet"  # Initialize name with default value
        
        # Initialize settings
        self.settings = {
            'always_on_top': True,
            'start_with_windows': False,
            'volume': 50,
            'pet_size': 100,
            'transparency': 0,
            'movement_speed': 5,
            'activity_level': 5,
            'poop_frequency': 0.2,  # Increased poop frequency (5.0%)
            'pet_color': 'black'  # Default pet color (black, blue, pink)
        }
        
        # Initialize pet state
        self.pet_state = PetState()
        
        # Create canvas for pet rendering with transparent background
        self.canvas = tk.Canvas(root, width=256, height=256,
                              highlightthickness=0, bg='#010101')
        self.canvas.pack()
        
        # Make the window transparent
        self.root.wm_attributes('-transparentcolor', '#010101')
        
        # Initialize animation system
        self.animation = PetAnimation(root, self.canvas, self.pet_state, self.settings)

        # Initialize UI components
        self.combined_panel = CombinedPanel(root, self, self.canvas)
        self.speech_bubble = SpeechBubble(self.canvas, self.root)
        self.status_panel = SimpleStatusPanel(root, self)
        
        # Initialize poop system
        print("Initializing poop system...")
        self.poop_system = PoopSystem(self.root, self.canvas, self.pet_state)
        self.pet_state.poop_system = self.poop_system  # Add reference to PetState
        print(f"Poop system initialized with frequency: {self.settings['poop_frequency']}%")
        
        # Force a poop generation for testing
        print("Forcing initial poop generation for testing...")
        self.poop_system.check_poop_generation(128, 128)
        
        # Initialize inventory system
        self.inventory_system = InventorySystem(self.root, self.canvas, self.pet_state)
        
        # Connect pet_state to pet_manager for inventory system to access
        self.pet_state.pet_manager = self
        
        # Load initial animation frames
        self.load_animations()
        
        # Initialize movement variables
        # Movement handling moved to PetAnimation class
        
        # Variables for double-click detection and cooldown
        self.last_click_time = 0
        self.last_happiness_boost_time = 0
        self.happiness_boost_cooldown = 0  # Will be set randomly
        
        # Initialize movement and resume timers
        self.movement_timer = None
        self.resume_timer = None  # Add missing resume_timer attribute
        self.animation_reset_timer = None  # Initialize animation reset timer
        
        # Bind events
        self.canvas.bind('<Button-1>', self.handle_click)  # Left click
        self.canvas.bind('<Button-3>', self.handle_right_click)  # Right click
        self.canvas.bind('<B1-Motion>', self.handle_drag)  # Drag
        
        # Start animation and state updates
        self.animate()
        self.update_state()
        
        # Start random movement
        self.animation.start_random_movement()
        
        # Setup system tray
        self.setup_system_tray()
        
        # Load settings
        self.load_settings()
        
        # Apply transparency setting
        alpha = int(255 * (100 - self.settings['transparency']) / 100)
        self.root.attributes('-alpha', alpha/255)
        
        # Ensure animation system is properly initialized with current settings
        if hasattr(self.animation, 'handle_color_change'):
            self.animation.handle_color_change(None, self.settings['pet_color'])
    
    def load_animations(self):
        """Load animation frames for current pet stage"""
        self.animations = {}
        base_path = os.path.join(os.path.dirname(__file__), 'frames')
        
        # Load all animations for current stage
        for state in ['Walk1', 'Walk2', 'Happy', 'Sleep1', 'Sleep2',
                     'Eat1', 'Eat2', 'Attack', 'Angry', 'Lose1']:
            try:
                img_path = os.path.join(base_path, f'{self.pet_state.stage}_{state}.png')
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    self.animations[state] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f'Error loading animation frame: {e}')
    
    def animate(self):
        """Update pet animation frame"""
        try:
            # Get current animation sequence
            animation_sequences = {
                'Standing': ['Walk1', 'Walk2'],  # Changed to use the same animation as Walking
                'Walking': ['Walk1', 'Walk2'],
                'happy': ['Happy', 'Walk1'],
                'sleeping': ['Sleep1', 'Sleep2'],
                'eating': ['Eat1', 'Eat2'],
                'playing': ['Attack', 'Walk1'],
                'special': ['Happy', 'Walk1', 'Walk2', 'Happy'],
                'angry': ['Angry', 'Walk1'],
                'sad': ['Lose1', 'Walk1'],
                'sick': ['Lose1', 'Sleep2']
            }
            
            sequence = animation_sequences[self.pet_state.current_animation]
            frame = sequence[int(datetime.now().timestamp() * 2) % len(sequence)]
            
            # Update canvas with current frame
            self.canvas.delete('pet')  # Only delete the pet image, not everything
            if frame in self.animations:
                # Get pet color from settings
                pet_color = self.settings.get('pet_color', 'black').lower()
                
                # Determine file path based on color
                img_path = None
                base_path = os.path.join(os.path.dirname(__file__), 'frames')
                
                if pet_color == 'black':
                    # Default black pet (no suffix)
                    img_path = os.path.join(base_path, f'{self.pet_state.stage}_{frame}.png')
                    if not os.path.exists(img_path):
                        # Try alternate case for black pet
                        img_path = os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}.png')
                else:
                    # Try multiple filename patterns for colored pets
                    possible_paths = [
                        # Original case with stage as is
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}_{pet_color}.png'),
                        # Lowercase stage
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}_{pet_color}.png')
                    ]
                    
                    # Find the first path that exists
                    for path in possible_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                # If no specific variant found, try fallbacks to black
                if img_path is None or not os.path.exists(img_path):
                    fallback_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}.png')
                    ]
                    
                    for path in fallback_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                # Load the image if a valid path was found
                if img_path and os.path.exists(img_path):
                    # Load the image
                    image = Image.open(img_path)
                    # Resize the image based on pet_size setting (100 = 4x original size)
                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized_image = image.resize((int(image.width * size_factor), int(image.height * size_factor)), Image.LANCZOS)
                    # Flip image if pet is moving right
                    if self.pet_state.direction == 'right':
                        resized_image = resized_image.transpose(Image.FLIP_LEFT_RIGHT)
                    # Convert to PhotoImage and store
                    self.animations[frame] = ImageTk.PhotoImage(resized_image)
                    # Center in the canvas
                    self.canvas.create_image(128, 128, image=self.animations[frame], tags='pet')
        
        except Exception as e:
            print(f'Animation error: {e}')
        
        # Schedule next frame
        self.root.after(100, self.animate)
    
    def update_state(self):
        """Update pet state based on elapsed time"""
        # Use the update method from the PetStats class in pet_components.py
        self.pet_state.stats.update()
        
        # Check if pet is sick
        self.check_sickness_status()
        
        # Check for evolution
        if hasattr(self.pet_state, 'growth'):
            self.pet_state.growth.check_evolution()
        
        # Update system tray menu to reflect current stats
        if hasattr(self, 'icon'):
            if hasattr(self.icon, 'update_icon_menu'):
                # Use the new real-time update method
                self.icon.update_icon_menu()
            elif hasattr(self.icon, 'update_menu'):
                # Fallback to the old method
                self.icon.update_menu()
        
        # Auto-save pet data every 5 minutes (60 updates * 5 seconds = 300 seconds)
        if not hasattr(self, 'update_counter'):
            self.update_counter = 0
        self.update_counter += 1
        
        if self.update_counter >= 60:
            print("Auto-saving pet data...")
            self.save_pet()
            self.save_settings()
            self.update_counter = 0
        
        # Schedule next update
        self.root.after(5000, self.update_state)  # Update every 5 seconds
        
    def check_sickness_status(self):
        """Check if pet should be sick based on stats"""
        # Pet is sick if any stat is below 25%
        is_sick = False
        for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
            if self.pet_state.stats.get_stat(stat) < 25:
                is_sick = True
                break
                
        # Update sickness status if changed
        if is_sick != self.pet_state.stats.is_sick:
            self.pet_state.stats.is_sick = is_sick
            
            # Update animation if pet is sick
            if is_sick:
                self.animation.show_sickness_overlay()
            else:
                self.animation.hide_sickness_overlay()
    
    def check_evolution(self):
        """Check and handle pet evolution"""
        age = self.pet_state.stats.age
        if age >= 30 and self.pet_state.stage == 'Baby':
            self.evolve_to('Child')
        elif age >= 60 and self.pet_state.stage == 'Child':
            self.evolve_to('Teen')
        elif age >= 90 and self.pet_state.stage == 'Teen':
            self.evolve_to('Adult')
    
    def evolve_to(self, new_stage):
        """Handle evolution to new stage"""
        self.pet_state.stage = new_stage
        self.load_animations()
        self.pet_state.current_animation = 'special'
        return True  # Return True to indicate successful stage change
    
    def handle_click(self, event):
        """Handle left mouse click on pet"""
        current_time = datetime.now().timestamp()
        
        # Check if this is a double-click (two clicks within 0.3 seconds)
        if current_time - self.last_click_time < 0.3:
            # This is a double-click - check if we're in cooldown period
            if current_time - self.last_happiness_boost_time > self.happiness_boost_cooldown:
                # Not in cooldown, so apply happiness boost
                self.pet_state.current_animation = 'happy'
                self.pet_state.stats.modify_stat('happiness', 10)
                # Show a happy speech bubble
                self.speech_bubble.show_bubble('happy')
                
                # Set a new random cooldown period (between 3-10 minutes)
                self.happiness_boost_cooldown = random.randint(180, 600)  # seconds
                self.last_happiness_boost_time = current_time
                
                # Cancel any existing animation reset timer
                if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                    self.root.after_cancel(self.animation_reset_timer)
                
                # Set a timer to reset animation state after 2 seconds
                self.animation_reset_timer = self.root.after(2000, self.reset_animation_state)
        
        # Update the last click time for double-click detection
        self.last_click_time = current_time
        
    def reset_animation_state(self):
        """Reset the pet's animation state back to normal"""
        if hasattr(self, 'pet_state') and self.pet_state.current_animation == 'happy':
            self.pet_state.current_animation = 'Standing'
            self.pet_state.is_interacting = False
            
            # Cancel any existing animation reset timer
            if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                self.root.after_cancel(self.animation_reset_timer)
                self.animation_reset_timer = None
                
            # Resume random movement
            if hasattr(self, 'animation') and self.animation:
                self.animation.start_random_movement()
    
    def reset_pet(self):
        """Reset pet to initial state (Baby stage, 0 days, default stats)"""
        # Create a new pet state
        self.pet_state = PetState()
        self.name = "Pet"  # Reset to default name
        
        # Reset animation and load new frames
        self.pet_state.current_animation = 'Standing'
        self.pet_state.direction = 'left'
        self.load_animations()
        
        # Connect pet_state to pet_manager for inventory system to access
        self.pet_state.pet_manager = self
        
        # Return success status and message
        return True, "Pet has been reset to initial state."
        
        # Initialize poop system reference
        if hasattr(self, 'poop_system'):
            self.poop_system.pet_state = self.pet_state
            self.pet_state.poop_system = self.poop_system
        
        # Reset inventory system
        if hasattr(self, 'inventory_system'):
            self.inventory_system.pet_state = self.pet_state
        
        # Reset animation system
        if hasattr(self, 'animation'):
            self.animation.pet_state = self.pet_state
        
        # Save the reset state
        self.save_settings()
        
        # Update the UI
        if hasattr(self, 'icon') and hasattr(self.icon, 'update_menu'):
            self.icon.update_menu()
    
    def get_stats_summary(self):
        """Get a summary of pet stats for display"""
        # Determine status effects based on current stats
        status_effects = []
        
        # Check for hunger
        if self.pet_state.stats.get_stat('hunger') <= 20:
            status_effects.append('hungry')
        
        # Check for energy
        if self.pet_state.stats.get_stat('energy') <= 30:
            status_effects.append('tired')
        
        # Check for health
        if self.pet_state.stats.get_stat('health') <= 30:
            status_effects.append('sick')
        
        # Check for happiness
        if self.pet_state.stats.get_stat('happiness') <= 30:
            status_effects.append('sad')
        
        # Check for cleanliness
        if self.pet_state.stats.get_stat('cleanliness') <= 30:
            status_effects.append('dirty')
        
        # Check for social
        if self.pet_state.stats.get_stat('social') <= 30:
            status_effects.append('lonely')
        
        return {
            'name': self.name,  # Use the pet's name
            'stage': self.pet_state.stage,
            'age': round(self.pet_state.stats.get_stat('age'), 1),
            'hunger': self.pet_state.stats.get_stat('hunger'),
            'happiness': self.pet_state.stats.get_stat('happiness'),
            'energy': self.pet_state.stats.get_stat('energy'),
            'health': self.pet_state.stats.get_stat('health'),
            'cleanliness': self.pet_state.stats.get_stat('cleanliness'),
            'social': self.pet_state.stats.get_stat('social'),
            'status_effects': status_effects
        }
        
    def save_pet(self, is_autosave=False):
        """Save pet state to file"""
        # Create saves directory if it doesn't exist
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(save_path, exist_ok=True)
        
        # Convert PetStats object to dictionary for saving
        stats_dict = {
            'hunger': self.pet_state.stats.get_stat('hunger'),
            'happiness': self.pet_state.stats.get_stat('happiness'),
            'energy': self.pet_state.stats.get_stat('energy'),
            'health': self.pet_state.stats.get_stat('health'),
            'cleanliness': self.pet_state.stats.get_stat('cleanliness'),
            'social': self.pet_state.stats.get_stat('social'),
            'age': self.pet_state.stats.get_stat('age')
        }
        
        # Include decay rates in the save data
        decay_rates_dict = {}
        if hasattr(self.pet_state.stats, 'decay_rates'):
            for key, value in self.pet_state.stats.decay_rates.items():
                decay_rates_dict[key] = value
        
        save_data = {
            'name': self.name,
            'stats': stats_dict,
            'decay_rates': decay_rates_dict,
            'stage': self.pet_state.stage,
            'currency': self.pet_state.currency,
            'game_progress': self.pet_state.game_progress,
            'creation_date': datetime.now().isoformat(),
            'save_date': datetime.now().isoformat()
        }
        
        # Use a single save file for both manual saves and autosaves
        filename = f"{self.name.replace(' ', '_')}_save.json"
        
        # Create backup of existing save if it exists
        backup_path = os.path.join(save_path, f"{self.name.replace(' ', '_')}_backup.json")
        if os.path.exists(os.path.join(save_path, filename)):
            try:
                shutil.copy2(os.path.join(save_path, filename), backup_path)
            except Exception as e:
                print(f"Failed to create backup: {e}")
                # Continue with save even if backup fails
            
        filepath = os.path.join(save_path, filename)
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write the save file
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=4)
            
            # Store the last save filename and timestamp
            self.last_save = filename
            
            return True, "Pet saved successfully!"
        except Exception as e:
            print(f"Failed to save pet: {e}")
            return False, f"Failed to save pet: {e}"
            
            return True, filename
        except Exception as e:
            print(f"Error saving pet: {e}")
            return False, str(e)
    
    def get_save_files(self):
        """Get list of available save files"""
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(save_path, exist_ok=True)
        
        try:
            files = [f for f in os.listdir(save_path) if f.endswith('.json')]
            return files
        except Exception as e:
            print(f"Error getting save files: {e}")
            return []
    
    def delete_save(self, save_file):
        """Delete a save file"""
        try:
            # Construct the full path to the save file
            save_path = os.path.join(self.save_path, save_file)
            
            # Check if the file exists
            if os.path.exists(save_path):
                # Delete the file
                os.remove(save_path)
                return True
            else:
                print(f"Save file not found: {save_path}")
                return False
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False
    
    def load_pet(self, filepath):
        """Load pet from save file"""
        try:
            # Check if filepath is just a filename or a full path
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.save_path, filepath)
                
            # Check if file exists
            if not os.path.exists(filepath):
                return None, f"Save file not found: {filepath}"
                
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Update pet properties
            self.name = save_data.get('name', 'Pet')
            
            # Restore stats
            stats_dict = save_data.get('stats', {})
            # Reset all stats to 0 first
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                self.pet_state.stats.modify_stat(stat, -100)  # Set to 0
            
            # Then set to the saved values
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if stat in stats_dict:
                    self.pet_state.stats.modify_stat(stat, stats_dict[stat])
            
            # For age, we need to directly modify the stats dictionary
            if 'age' in stats_dict:
                self.pet_state.stats.stats['age'] = stats_dict['age']
                # Update the direct attribute for age
                self.pet_state.stats.age = stats_dict['age']
            
            # Restore decay rates if available
            if 'decay_rates' in save_data:
                for key, value in save_data['decay_rates'].items():
                    if key in self.pet_state.stats.decay_rates:
                        self.pet_state.stats.decay_rates[key] = value
            
            # Restore growth stage
            if 'stage' in save_data:
                self.pet_state.stage = save_data['stage']
            
            # Restore currency if available
            if 'currency' in save_data:
                self.pet_state.currency = save_data['currency']
            
            # Restore game progress if available
            if 'game_progress' in save_data:
                self.pet_state.game_progress = save_data['game_progress']
            
            # Reload animations for the current stage
            self.load_animations()
            
            # Set a special animation to indicate successful loading
            self.pet_state.current_animation = 'special'
            
            # Store the loaded filename
            self.last_save = os.path.basename(filepath)
            
            return self, None
        except json.JSONDecodeError as e:
            print(f"Error parsing save file: {e}")
            return None, f"Invalid save file format: {e}"
        except KeyError as e:
            print(f"Missing required data in save file: {e}")
            return None, f"Save file is missing required data: {e}"
        except Exception as e:
            print(f"Error loading pet: {e}")
            return None, str(e)

    def handle_interaction(self, interaction_type):
        """Handle user interaction"""
        # Pause movement during interaction
        self.pause_movement()
        
        result = {
            'success': True,
            'message': '',
            'stat_changes': {}
        }
        
        # Set appropriate animation based on interaction type
        if interaction_type == 'feed':
            self.pet_state.current_animation = 'eating'
            self.pet_state.stats.modify_stat('hunger', 20)
            result['message'] = 'Your pet enjoyed the food!'
            result['stat_changes']['hunger'] = 20
            # Show speech bubble for this interaction
            self.speech_bubble.show_bubble('feed')
        elif interaction_type == 'play':
            self.pet_state.current_animation = 'playing'
            self.pet_state.stats.modify_stat('happiness', 15)
            self.pet_state.stats.modify_stat('energy', -10)
            result['message'] = 'Your pet had fun playing!'
            result['stat_changes'].update({'happiness': 15, 'energy': -10})
            # Show speech bubble for this interaction
            self.speech_bubble.show_bubble('play')

        elif interaction_type == 'medicine':
            if self.pet_state.stats.get_stat('health') < 50:
                self.pet_state.current_animation = 'happy'
                self.pet_state.stats.modify_stat('health', 30)
                result['message'] = 'Your pet is feeling better!'
                result['stat_changes']['health'] = 30
                # Show speech bubble for this interaction
                self.speech_bubble.show_bubble('medicine')
            else:
                self.pet_state.current_animation = 'angry'
                result['message'] = 'Your pet doesn\'t need medicine right now!'
                # Show speech bubble for this interaction
                self.speech_bubble.show_bubble('medicine', 'I don\'t need medicine!')
        elif interaction_type == 'pet':
            self.pet_state.current_animation = 'happy'
            self.pet_state.stats.modify_stat('happiness', 10)
            self.pet_state.stats.modify_stat('social', 15)
            result['message'] = 'Your pet enjoyed the attention!'
            result['stat_changes'].update({'happiness': 10, 'social': 15})
            # Show speech bubble for this interaction
            self.speech_bubble.show_bubble('pet')
        elif interaction_type == 'sleep':
            self.pet_state.current_animation = 'sleeping'
            self.pet_state.stats.modify_stat('energy', 30)
            result['message'] = 'Your pet is sleeping peacefully.'
            result['stat_changes']['energy'] = 30
            # Show speech bubble for this interaction
            self.speech_bubble.show_bubble('sleep')
            
        # Schedule resuming movement after animation completes
        self.schedule_resume_movement(3000)  # Resume movement after 3 seconds
        
        return result
    
    def schedule_resume_movement(self, delay_ms):
        """Schedule resuming movement after a delay"""
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
        self.resume_timer = self.root.after(delay_ms, self.resume_movement)
    
    def resume_movement(self):
        """Resume pet movement after interaction"""
        self.pet_state.is_interacting = False
        
        # Start random movement again
        if not self.movement_timer:
            self.animation.start_random_movement()
    
    def handle_right_click(self, event):
        """Handle right mouse click on pet"""
        # Show status panel near the pet
        x = self.root.winfo_x() + event.x
        y = self.root.winfo_y() + event.y
        
        # Show the status panel which has proper positioning logic
        self.status_panel.show_panel(x, y)
    
    def show_inventory(self):
        """Show the pet's inventory"""
        self.inventory_system.show_inventory()
        
    def show_game_hub(self):
        """Show the game hub with minigames"""
        # Import the GameHub class
        from game_hub import GameHub
        from currency_system import CurrencySystem
        
        # Initialize currency system if not already done
        if not hasattr(self, 'currency_system'):
            self.currency_system = CurrencySystem(self.pet_state)
        
        # Create and show the game hub with pet_state
        game_hub = GameHub(self.root, self.currency_system, self.pet_state)
    
    def handle_drag(self, event):
        """Handle dragging the pet with the mouse"""
        self.pause_movement()
        x = self.root.winfo_x() + event.x - 128  # Center offset
        y = self.root.winfo_y() + event.y - 128  # Center offset
        self.root.geometry(f'+{x}+{y}')
    
    def start_random_movement(self):
        """Start random movement of the pet on the desktop"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        def move_randomly():
            if not self.pet_state.is_interacting:
                # Decide whether to move or stay idle
                # Lower activity level means higher chance to stay idle
                activity_level = self.settings['activity_level']
                idle_chance = (11 - activity_level) * 10  # 10% to 100% chance to stay idle
                
                if random.randint(1, 100) <= idle_chance:
                    # Stay idle for a while
                    idle_time = random.randint(5000, 15000)  # 5-15 seconds of idle time
                    self.pet_state.current_animation = 'Standing'
                    self.movement_timer = self.root.after(idle_time, move_randomly)
                    return
                
                # Set random target position within screen bounds
                target_x = random.randint(0, screen_width - 256)
                target_y = random.randint(0, screen_height - 256)
                
                # Update pet direction based on target
                current_x = self.root.winfo_x()
                self.pet_state.direction = 'right' if target_x > current_x else 'left'
                
                # Set walking animation
                self.pet_state.current_animation = 'Walking'
                
                # Start movement steps - pass target coordinates to animation
                self.animation.target_x = target_x
                self.animation.target_y = target_y
                self.animation.move_step()
                
                # Schedule next random movement based on activity level
                # Higher activity level means more frequent movements (1-10 scale)
                # Convert to milliseconds: 10000ms (low activity) to 2000ms (high activity)
                delay = int(10000 - (activity_level * 800))
                self.movement_timer = self.root.after(delay, move_randomly)
        
        # Start initial movement
        move_randomly()
    
    def pause_movement(self):
        """Pause pet movement for interactions"""
        self.pet_state.is_interacting = True
        
        # Cancel any ongoing movement timers
        if self.movement_timer:
            self.root.after_cancel(self.movement_timer)
            self.movement_timer = None
            
        # Movement timer cleanup handled by PetAnimation class
            
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
            self.resume_timer = None
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Use the consolidated system tray implementation
        from system_tray import setup_system_tray
        
        # Create the icon using the system tray module
        self.icon = setup_system_tray(self, self.show_settings, self.exit_app)
        
        # Force menu initialization before starting the thread
        try:
            # Access menu property to trigger initialization
            dummy = self.icon.menu
            
            # Force menu handle initialization
            if hasattr(self.icon, '_update_menu'):
                self.icon._update_menu()
        except Exception as e:
            pass
        
        # Start the icon in a separate thread with higher priority
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.name = "SystemTrayThread"
        tray_thread.start()
        
        # Give the thread a moment to initialize
        time.sleep(0.5)
    
    def create_tray_icon(self):
        """Create an icon for the system tray"""
        # Create a simple colored square icon
        icon_size = 64
        icon_image = Image.new('RGB', (icon_size, icon_size), color=(73, 109, 137))
        
        # Try to use the pet's current image if available
        try:
            base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
            img_path = os.path.join(base_path, f'{self.pet_state.stage}_Walk1.png')
            if os.path.exists(img_path):
                pet_image = Image.open(img_path)
                # Resize to fit in the icon
                pet_image = pet_image.resize((icon_size, icon_size), Image.LANCZOS)
                icon_image = pet_image
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            # Draw a simple pet-like shape if image loading fails
            draw = ImageDraw.Draw(icon_image)
            draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
            draw.ellipse((24, 24, 30, 30), fill=(0, 0, 0))  # Eye
            draw.ellipse((38, 24, 44, 30), fill=(0, 0, 0))  # Eye
            draw.arc((24, 32, 44, 42), start=0, end=180, fill=(0, 0, 0), width=2)  # Smile
        
        return icon_image
    
    def show_pet(self):
        """Show pet window from system tray"""
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', self.settings['always_on_top'])
    
    def minimize_to_tray(self):
        """Minimize pet to system tray"""
        self.root.withdraw()
    
    def show_settings(self):
        """Show settings window"""
        # Create and show the settings window using SimpleUI
        from unified_ui import SimpleUI
        settings_window = SimpleUI(self.root)
        settings_window.show_settings(self)
    
    def exit_app(self):
        """Exit the application"""
        # Save pet data before exiting
        print("Saving pet data before exit...")
        self.save_pet()
        
        # Clean up poop system resources
        if hasattr(self, 'poop_system'):
            self.poop_system.cleanup()
            
        # Stop system tray icon
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        self.root.quit()
        
    def update_setting(self, setting_name, value):
        """Update a setting and apply any necessary changes"""
        # Store old value for comparison
        old_value = self.settings.get(setting_name)
        
        # Update the setting
        self.settings[setting_name] = value
        
        # Apply specific changes based on setting
        if setting_name == 'always_on_top':
            self.root.attributes('-topmost', value)
        elif setting_name == 'transparency':
            alpha = int(255 * (100 - value) / 100)
            self.root.attributes('-alpha', alpha/255)
        elif setting_name == 'pet_color':
            # If animation system has a color change handler, use it
            if hasattr(self.animation, 'handle_color_change'):
                self.animation.handle_color_change(old_value, value)
            else:
                # Use our own color change handler
                self.handle_color_change(old_value, value)
        
        # Save settings
        self.save_settings()
        
    def handle_color_change(self, old_color, new_color):
        """Handle pet color change by ensuring animation system is updated"""
        print(f"Pet color changed from {old_color} to {new_color}")
        
        # Store current direction
        current_direction = self.pet_state.direction
        
        # If animation system has a color change handler, use it
        if hasattr(self.animation, 'handle_color_change'):
            self.animation.handle_color_change(old_color, new_color)
        else:
            # Fallback: reload animations manually
            if hasattr(self.animation, 'load_animations'):
                self.animation.animations = {}
                self.animation.load_animations()
        
        # Ensure direction is preserved
        self.pet_state.direction = current_direction
    
    def save_settings(self):
        """Save current settings to a file"""
        import json
        import os
        
        # Create settings directory if it doesn't exist
        settings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(settings_dir, exist_ok=True)
        
        # Save settings to file
        settings_file = os.path.join(settings_dir, 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def load_settings(self):
        """Load settings from file"""
        import json
        import os
        
        # Check if settings file exists
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves', 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
            except Exception as e:
                print(f"Error loading settings: {e}")

# Main entry point
if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Virtual Pet")
    
    # Initialize the SimpleUI class to configure styles
    from unified_ui import SimpleUI
    # Initialize simple UI first
    simple_ui = SimpleUI(root)
    
    # Create the virtual pet
    pet = VirtualPet(root)
    
    # Set up protocol handler for window close button
    root.protocol("WM_DELETE_WINDOW", pet.exit_app)
    
    # Start the main event loop
    root.mainloop()