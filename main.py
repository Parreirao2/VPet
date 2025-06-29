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
import time
from PIL import Image, ImageTk, ImageDraw
from speech_bubble import SpeechBubble
from system_tray import create_context_menu, setup_system_tray
from poop_system import PoopSystem
from inventory_system import InventorySystem
from pet_animation import PetAnimation
from pet_components import PetStats, PetGrowth


class PetState:
    def __init__(self):
        self.growth = PetGrowth(None)
        self.stats = PetStats(self.growth)
        self.growth.stats = self.stats
        self.stage = 'Baby'
        self.current_animation = 'Standing'
        self.direction = 'left'
        self.is_interacting = False
        self.currency = 100
        self.game_progress = {
            'number_guesser': 1,
            'reaction_test': 1,
            'ball_clicker': 1
        }

class VirtualPet:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(self.save_path, exist_ok=True)
        self.last_save = None
        self.name = "My Pet"
        
        self.settings = {
            'always_on_top': True,
            'start_with_windows': False,
            'volume': 50,
            'pet_size': 100,
            'transparency': 0,
            'movement_speed': 5,
            'activity_level': 5,
            'poop_frequency': 0.2,
            'pet_color': 'black'
        }
        
        self.pet_state = PetState()
        
        self.canvas = tk.Canvas(root, width=256, height=256,
                              highlightthickness=0, bg='#010101')
        self.canvas.pack()
        
        self.root.wm_attributes('-transparentcolor', '#010101')
        
        self.animation = PetAnimation(root, self.canvas, self.pet_state, self.settings)

        self.combined_panel = CombinedPanel(root, self, self.canvas)
        self.speech_bubble = SpeechBubble(self.canvas, self.root)
        self.status_panel = SimpleStatusPanel(root, self)
        
        print("Initializing poop system...")
        self.poop_system = PoopSystem(self.root, self.canvas, self.pet_state)
        self.pet_state.poop_system = self.poop_system
        print(f"Poop system initialized with frequency: {self.settings['poop_frequency']}%")
        
        print("Forcing initial poop generation for testing...")
        self.poop_system.check_poop_generation(128, 128)
        
        self.inventory_system = InventorySystem(self.root, self.canvas, self.pet_state)
        
        self.pet_state.pet_manager = self
        
        self.load_animations()
        
        
        self.last_click_time = 0
        self.last_happiness_boost_time = 0
        self.happiness_boost_cooldown = 0
        
        self.movement_timer = None
        self.resume_timer = None
        self.animation_reset_timer = None
        
        self.canvas.bind('<Button-1>', self.handle_click)
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.bind('<B1-Motion>', self.handle_drag)
        
        self.animate()
        self.update_state()
        
        self.animation.start_random_movement()
        
        self.setup_system_tray()
        
        self.load_settings()
        
        alpha = int(255 * (100 - self.settings['transparency']) / 100)
        self.root.attributes('-alpha', alpha/255)
        
        if hasattr(self.animation, 'handle_color_change'):
            self.animation.handle_color_change(None, self.settings['pet_color'])
    
    def load_animations(self):
        self.animations = {}
        base_path = os.path.join(os.path.dirname(__file__), 'frames')
        
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
        try:
            animation_sequences = {
                'Standing': ['Walk1', 'Walk2'],
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
            
            self.canvas.delete('pet')
            if frame in self.animations:
                pet_color = self.settings.get('pet_color', 'black').lower()
                
                img_path = None
                base_path = os.path.join(os.path.dirname(__file__), 'frames')
                
                if pet_color == 'black':
                    img_path = os.path.join(base_path, f'{self.pet_state.stage}_{frame}.png')
                    if not os.path.exists(img_path):
                        img_path = os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}.png')
                else:
                    possible_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}_{pet_color}.png')
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                if img_path is None or not os.path.exists(img_path):
                    fallback_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}.png')
                    ]
                    
                    for path in fallback_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                if img_path and os.path.exists(img_path):
                    image = Image.open(img_path)
                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized_image = image.resize((int(image.width * size_factor), int(image.height * size_factor)), Image.LANCZOS)
                    if self.pet_state.direction == 'right':
                        resized_image = resized_image.transpose(Image.FLIP_LEFT_RIGHT)
                    self.animations[frame] = ImageTk.PhotoImage(resized_image)
                    self.canvas.create_image(128, 128, image=self.animations[frame], tags='pet')
        
        except Exception as e:
            print(f'Animation error: {e}')
        
        self.root.after(100, self.animate)
    
    def update_state(self):
        self.pet_state.stats.update()
        
        self.check_sickness_status()
        
        if hasattr(self.pet_state, 'growth'):
            self.pet_state.growth.check_evolution()
        
        if hasattr(self, 'icon'):
            if hasattr(self.icon, 'update_icon_menu'):
                self.icon.update_icon_menu()
            elif hasattr(self.icon, 'update_menu'):
                self.icon.update_menu()
        
        if not hasattr(self, 'update_counter'):
            self.update_counter = 0
        self.update_counter += 1
        
        if self.update_counter >= 60:
            print("Auto-saving pet data...")
            self.save_pet()
            self.save_settings()
            self.update_counter = 0
        
        self.root.after(5000, self.update_state)
        
    def check_sickness_status(self):
        is_sick = False
        for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
            if self.pet_state.stats.get_stat(stat) < 25:
                is_sick = True
                break
                
        if is_sick != self.pet_state.stats.is_sick:
            self.pet_state.stats.is_sick = is_sick
            
            if is_sick:
                self.animation.show_sickness_overlay()
            else:
                self.animation.hide_sickness_overlay()
    
    def check_evolution(self):
        age = self.pet_state.stats.age
        if age >= 30 and self.pet_state.stage == 'Baby':
            self.evolve_to('Child')
        elif age >= 60 and self.pet_state.stage == 'Child':
            self.evolve_to('Teen')
        elif age >= 90 and self.pet_state.stage == 'Teen':
            self.evolve_to('Adult')
    
    def evolve_to(self, new_stage):
        self.pet_state.stage = new_stage
        self.load_animations()
        self.pet_state.current_animation = 'special'
        return True
    
    def handle_click(self, event):
        current_time = datetime.now().timestamp()
        
        if current_time - self.last_click_time < 0.3:
            if current_time - self.last_happiness_boost_time > self.happiness_boost_cooldown:
                self.pet_state.current_animation = 'happy'
                self.pet_state.stats.modify_stat('happiness', 10)
                self.speech_bubble.show_bubble('happy')
                
                self.happiness_boost_cooldown = random.randint(180, 600)
                self.last_happiness_boost_time = current_time
                
                if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                    self.root.after_cancel(self.animation_reset_timer)
                
                self.animation_reset_timer = self.root.after(2000, self.reset_animation_state)
        
        self.last_click_time = current_time
        
    def reset_animation_state(self):
        if hasattr(self, 'pet_state') and self.pet_state.current_animation == 'happy':
            self.pet_state.current_animation = 'Standing'
            self.pet_state.is_interacting = False
            
            if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                self.root.after_cancel(self.animation_reset_timer)
                self.animation_reset_timer = None
                
            if hasattr(self, 'animation') and self.animation:
                self.animation.start_random_movement()
    
    def reset_pet(self):
        self.pet_state = PetState()
        self.name = "Pet"
        
        self.pet_state.current_animation = 'Standing'
        self.pet_state.direction = 'left'
        self.load_animations()
        
        self.pet_state.pet_manager = self
        
        return True, "Pet has been reset to initial state."
        
        if hasattr(self, 'poop_system'):
            self.poop_system.pet_state = self.pet_state
            self.pet_state.poop_system = self.poop_system
        
        if hasattr(self, 'inventory_system'):
            self.inventory_system.pet_state = self.pet_state
        
        if hasattr(self, 'animation'):
            self.animation.pet_state = self.pet_state
        
        self.save_settings()
        
        if hasattr(self, 'icon') and hasattr(self.icon, 'update_menu'):
            self.icon.update_menu()
    
    def get_stats_summary(self):
        status_effects = []
        
        if self.pet_state.stats.get_stat('hunger') <= 20:
            status_effects.append('hungry')
        
        if self.pet_state.stats.get_stat('energy') <= 30:
            status_effects.append('tired')
        
        if self.pet_state.stats.get_stat('health') <= 30:
            status_effects.append('sick')
        
        if self.pet_state.stats.get_stat('happiness') <= 30:
            status_effects.append('sad')
        
        if self.pet_state.stats.get_stat('cleanliness') <= 30:
            status_effects.append('dirty')
        
        if self.pet_state.stats.get_stat('social') <= 30:
            status_effects.append('lonely')
        
        return {
            'name': self.name,
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
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(save_path, exist_ok=True)
        
        stats_dict = {
            'hunger': self.pet_state.stats.get_stat('hunger'),
            'happiness': self.pet_state.stats.get_stat('happiness'),
            'energy': self.pet_state.stats.get_stat('energy'),
            'health': self.pet_state.stats.get_stat('health'),
            'cleanliness': self.pet_state.stats.get_stat('cleanliness'),
            'social': self.pet_state.stats.get_stat('social'),
            'age': self.pet_state.stats.get_stat('age')
        }
        
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
        
        filename = f"{self.name.replace(' ', '_')}_save.json"
        
        backup_path = os.path.join(save_path, f"{self.name.replace(' ', '_')}_backup.json")
        if os.path.exists(os.path.join(save_path, filename)):
            try:
                shutil.copy2(os.path.join(save_path, filename), backup_path)
            except Exception as e:
                print(f"Failed to create backup: {e}")
            
        filepath = os.path.join(save_path, filename)
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=4)
            
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
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(save_path, exist_ok=True)
        
        try:
            files = [f for f in os.listdir(save_path) if f.endswith('.json')]
            return files
        except Exception as e:
            print(f"Error getting save files: {e}")
            return []
    
    def delete_save(self, save_file):
        try:
            save_path = os.path.join(self.save_path, save_file)
            
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            else:
                print(f"Save file not found: {save_path}")
                return False
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False
    
    def load_pet(self, filepath):
        try:
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.save_path, filepath)
                
            if not os.path.exists(filepath):
                return None, f"Save file not found: {filepath}"
                
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            self.name = save_data.get('name', 'Pet')
            
            stats_dict = save_data.get('stats', {})
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                self.pet_state.stats.modify_stat(stat, -100)
            
            for stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if stat in stats_dict:
                    self.pet_state.stats.modify_stat(stat, stats_dict[stat])
            
            if 'age' in stats_dict:
                self.pet_state.stats.stats['age'] = stats_dict['age']
                self.pet_state.stats.age = stats_dict['age']
            
            if 'decay_rates' in save_data:
                for key, value in save_data['decay_rates'].items():
                    if key in self.pet_state.stats.decay_rates:
                        self.pet_state.stats.decay_rates[key] = value
            
            if 'stage' in save_data:
                self.pet_state.stage = save_data['stage']
            
            if 'currency' in save_data:
                self.pet_state.currency = save_data['currency']
            
            if 'game_progress' in save_data:
                self.pet_state.game_progress = save_data['game_progress']
            
            self.load_animations()
            
            self.pet_state.current_animation = 'special'
            
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
        self.pause_movement()
        
        result = {
            'success': True,
            'message': '',
            'stat_changes': {}
        }
        
        if interaction_type == 'feed':
            self.pet_state.current_animation = 'eating'
            self.pet_state.stats.modify_stat('hunger', 20)
            result['message'] = 'Your pet enjoyed the food!'
            result['stat_changes']['hunger'] = 20
            self.speech_bubble.show_bubble('feed')
        elif interaction_type == 'play':
            self.pet_state.current_animation = 'playing'
            self.pet_state.stats.modify_stat('happiness', 15)
            self.pet_state.stats.modify_stat('energy', -10)
            result['message'] = 'Your pet had fun playing!'
            result['stat_changes'].update({'happiness': 15, 'energy': -10})
            self.speech_bubble.show_bubble('play')

        elif interaction_type == 'medicine':
            if self.pet_state.stats.get_stat('health') < 50:
                self.pet_state.current_animation = 'happy'
                self.pet_state.stats.modify_stat('health', 30)
                result['message'] = 'Your pet is feeling better!'
                result['stat_changes']['health'] = 30
                self.speech_bubble.show_bubble('medicine')
            else:
                self.pet_state.current_animation = 'angry'
                result['message'] = 'Your pet doesn\'t need medicine right now!'
                self.speech_bubble.show_bubble('medicine', 'I don\'t need medicine!')
        elif interaction_type == 'pet':
            self.pet_state.current_animation = 'happy'
            self.pet_state.stats.modify_stat('happiness', 10)
            self.pet_state.stats.modify_stat('social', 15)
            result['message'] = 'Your pet enjoyed the attention!'
            result['stat_changes'].update({'happiness': 10, 'social': 15})
            self.speech_bubble.show_bubble('pet')
        elif interaction_type == 'sleep':
            self.pet_state.current_animation = 'sleeping'
            self.pet_state.stats.modify_stat('energy', 30)
            result['message'] = 'Your pet is sleeping peacefully.'
            result['stat_changes']['energy'] = 30
            self.speech_bubble.show_bubble('sleep')
            
        self.schedule_resume_movement(3000)
        
        return result
    
    def schedule_resume_movement(self, delay_ms):
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
        self.resume_timer = self.root.after(delay_ms, self.resume_movement)
    
    def resume_movement(self):
        self.pet_state.is_interacting = False
        
        if not self.movement_timer:
            self.animation.start_random_movement()
    
    def handle_right_click(self, event):
        x = self.root.winfo_x() + event.x
        y = self.root.winfo_y() + event.y
        
        self.status_panel.show_panel(x, y)
    
    def show_inventory(self):
        self.inventory_system.show_inventory()
        
    def show_game_hub(self):
        from game_hub import GameHub
        from currency_system import CurrencySystem
        
        if not hasattr(self, 'currency_system'):
            self.currency_system = CurrencySystem(self.pet_state)
        
        game_hub = GameHub(self.root, self.currency_system, self.pet_state)
    
    def handle_drag(self, event):
        self.pause_movement()
        x = self.root.winfo_x() + event.x - 128
        y = self.root.winfo_y() + event.y - 128
        self.root.geometry(f'+{x}+{y}')
    
    def start_random_movement(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        def move_randomly():
            if not self.pet_state.is_interacting:
                activity_level = self.settings['activity_level']
                idle_chance = (11 - activity_level) * 10
                
                if random.randint(1, 100) <= idle_chance:
                    idle_time = random.randint(5000, 15000)
                    self.pet_state.current_animation = 'Standing'
                    self.movement_timer = self.root.after(idle_time, move_randomly)
                    return
                
                target_x = random.randint(0, screen_width - 256)
                target_y = random.randint(0, screen_height - 256)
                
                current_x = self.root.winfo_x()
                self.pet_state.direction = 'right' if target_x > current_x else 'left'
                
                self.pet_state.current_animation = 'Walking'
                
                self.animation.target_x = target_x
                self.animation.target_y = target_y
                self.animation.move_step()
                
                delay = int(10000 - (activity_level * 800))
                self.movement_timer = self.root.after(delay, move_randomly)
        
        move_randomly()
    
    def pause_movement(self):
        self.pet_state.is_interacting = True
        
        if self.movement_timer:
            self.root.after_cancel(self.movement_timer)
            self.movement_timer = None
            
            
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
            self.resume_timer = None
    
    def setup_system_tray(self):
        from system_tray import setup_system_tray
        
        self.icon = setup_system_tray(self, self.show_settings, self.exit_app)
        
        try:
            dummy = self.icon.menu
            
            if hasattr(self.icon, '_update_menu'):
                self.icon._update_menu()
        except Exception as e:
            pass
        
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.name = "SystemTrayThread"
        tray_thread.start()
        
        time.sleep(0.5)
    
    def create_tray_icon(self):
        icon_size = 64
        icon_image = Image.new('RGB', (icon_size, icon_size), color=(73, 109, 137))
        
        try:
            base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
            img_path = os.path.join(base_path, f'{self.pet_state.stage}_Walk1.png')
            if os.path.exists(img_path):
                pet_image = Image.open(img_path)
                pet_image = pet_image.resize((icon_size, icon_size), Image.LANCZOS)
                icon_image = pet_image
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            draw = ImageDraw.Draw(icon_image)
            draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
            draw.ellipse((24, 24, 30, 30), fill=(0, 0, 0))
            draw.ellipse((38, 24, 44, 30), fill=(0, 0, 0))
            draw.arc((24, 32, 44, 42), start=0, end=180, fill=(0, 0, 0), width=2)
        
        return icon_image
    
    def show_pet(self):
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', self.settings['always_on_top'])
    
    def minimize_to_tray(self):
        self.root.withdraw()
    
    def show_settings(self):
        from unified_ui import SimpleUI
        settings_window = SimpleUI(self.root)
        settings_window.show_settings(self)
    
    def exit_app(self):
        print("Saving pet data before exit...")
        self.save_pet()
        
        if hasattr(self, 'poop_system'):
            self.poop_system.cleanup()
            
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        self.root.quit()
        
    def update_setting(self, setting_name, value):
        old_value = self.settings.get(setting_name)
        
        self.settings[setting_name] = value
        
        if setting_name == 'always_on_top':
            self.root.attributes('-topmost', value)
        elif setting_name == 'transparency':
            alpha = int(255 * (100 - value) / 100)
            self.root.attributes('-alpha', alpha/255)
        elif setting_name == 'pet_color':
            if hasattr(self.animation, 'handle_color_change'):
                self.animation.handle_color_change(old_value, value)
            else:
                self.handle_color_change(old_value, value)
        
        self.save_settings()
        
    def handle_color_change(self, old_color, new_color):
        print(f"Pet color changed from {old_color} to {new_color}")
        
        current_direction = self.pet_state.direction
        
        if hasattr(self.animation, 'handle_color_change'):
            self.animation.handle_color_change(old_color, new_color)
        else:
            if hasattr(self.animation, 'load_animations'):
                self.animation.animations = {}
                self.animation.load_animations()
        
        self.pet_state.direction = current_direction
    
    def save_settings(self):
        import json
        import os
        
        settings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def load_settings(self):
        import json
        import os
        
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves', 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
            except Exception as e:
                print(f"Error loading settings: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Virtual Pet")
    
    from unified_ui import SimpleUI
    simple_ui = SimpleUI(root)
    
    pet = VirtualPet(root)
    
    root.protocol("WM_DELETE_WINDOW", pet.exit_app)
    
    root.mainloop()