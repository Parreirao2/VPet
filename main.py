import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import math
import shutil
from datetime import datetime
from unified_ui import SimpleStatusPanel
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
from treasure_system import TreasureSystem
class PetState:
    def __init__(self):
        self.growth = PetGrowth(None)
        self.stats = PetStats(self.growth)
        self.growth.stats = self.stats
        self.stage = 'Baby'
        self.current_animation = 'Standing'
        self.direction = 'left'
        self.is_interacting = False
        self.is_sleeping = False
        self.sleep_start_time = None
        self.currency = 100
        self.game_progress = {
            'number_guesser': 1,
            'reaction_test': 1,
            'ball_clicker': 1
        }
        self.poop_system_dirty = False
    def update_pet_display(self):
        if hasattr(self, 'pet_manager') and hasattr(self.pet_manager, 'animation'):
            self.pet_manager.animation.update_pet_image()
class VirtualPet:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("256x256+300+300")
        self.root.attributes('-topmost', True)
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(self.save_path, exist_ok=True)
        self.last_save = None
        self._name = "My Pet"
        self.running = True
        self.settings = {
            'always_on_top': True,
            'start_with_windows': False,
            'volume': 50,
            'pet_size': 100,
            'transparency': 0,
            'movement_speed': 5,
            'activity_level': 5,
            'poop_frequency': 0.2,
            'pet_color': 'black',
            'context_awareness_enabled': True
        }
        self.pet_state = PetState()
        self.pet_state.pet_manager = self
        self.pet_state.stats.pet_state = self.pet_state
        self.canvas = tk.Canvas(root, width=256, height=256,
                              highlightthickness=0, bg='#010101')
        self.canvas.pack()
        self.root.wm_attributes('-transparentcolor', '#010101')
        self.load_settings()
        if self.settings.get('context_awareness_enabled', True):
            try:
                from context_awareness import ContextAwareness
                self.context_awareness = ContextAwareness(self)
            except ImportError as e:
                pass
            except Exception as e:
                pass
        else:
            pass
        self.animation = PetAnimation(root, self.canvas, self.pet_state, self.settings)
        def check_context_awareness():
            if hasattr(self, 'context_awareness') and self.context_awareness:
                try:
                    self.context_awareness.update_context_awareness()
                except Exception as e:
                    pass
            self.root.after(3000, check_context_awareness)
        if self.settings.get('context_awareness_enabled', True):
            self.root.after(5000, check_context_awareness)
        self.speech_bubble = SpeechBubble(self.canvas, self.root)
        self.status_panel = SimpleStatusPanel(root, self)
        self.sleep_timer_label = None
        self.sleep_timer_update_id = None
        print("Initializing poop system...")
        self.poop_system = PoopSystem(self.root, self.canvas, self.pet_state)
        self.pet_state.poop_system = self.poop_system
        print(f"Poop system initialized with realistic pressure-based mechanics")
        self.inventory_system = InventorySystem(self.root, self.canvas, self.pet_state)
        self.treasure_system = TreasureSystem(self.root, self.canvas, self.pet_state, self.inventory_system, self)
        self.pet_state.treasure_system = self.treasure_system
        self.auto_load_pet()
        self.last_click_time = 0
        self.last_happiness_boost_time = 0
        self.happiness_boost_cooldown = 0
        self.movement_timer = None
        self.resume_timer = None
        self.animation_reset_timer = None
        self.canvas.bind('<Button-1>', self.handle_click)
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.bind('<B1-Motion>', self.handle_drag)
        self.canvas.bind('<ButtonRelease-1>', self.handle_drag_end)
        self.canvas.bind('<Double-Button-1>', self.handle_double_click)
        self.update_state()
        if hasattr(self.animation, 'start_random_movement'):
            self.animation.start_random_movement()
        self.setup_system_tray()
        alpha = int(255 * (100 - self.settings['transparency']) / 100)
        self.root.attributes('-alpha', alpha/255)
        if hasattr(self.animation, 'handle_color_change'):
            self.animation.handle_color_change(None, self.settings['pet_color'])
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_name):
        self._name = new_name
        self.check_for_cheat_code()
    def update_state(self):
        self.pet_state.stats.update()
        energy = self.pet_state.stats.get_stat('energy')
        if energy < 15:
            if not self.pet_state.is_sleeping:
                self.pet_state.is_sleeping = True
                self.pet_state.sleep_start_time = datetime.now()
                energy_needed = 100 - energy
                sleep_duration_minutes = energy_needed / 12
                self.pet_state.sleep_duration = int(sleep_duration_minutes * 60 * 1000)
                self.pet_state.current_animation = 'sleeping'
        self.check_sickness_status()
        if hasattr(self.pet_state, 'growth'):
            evolution_occurred = self.pet_state.growth.check_evolution()
            if evolution_occurred:
                self.pet_state.stage = self.pet_state.growth.stage
        if hasattr(self, 'poop_system'):
            self.poop_system.check_poop_generation(
                self.root.winfo_x() + self.canvas.winfo_width() // 2,
                self.root.winfo_y() + self.canvas.winfo_height() // 2
            )
        if hasattr(self, 'icon'):
            if hasattr(self.icon, 'update_icon_menu'):
                self.icon.update_icon_menu()
            elif hasattr(self.icon, 'update_menu'):
                self.icon.update_menu()
        if not hasattr(self, 'update_counter'):
            self.update_counter = 0
        self.update_counter += 1
        if self.update_counter >= 12:
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
            if not self.pet_state.is_sleeping:
                if is_sick:
                    self.animation.show_sickness_overlay()
                else:
                    self.animation.hide_sickness_overlay()
        if self.pet_state.is_sleeping:
            self.pet_state.current_animation = 'sleeping'
            if hasattr(self.animation, 'hide_sickness_overlay'):
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
        if new_stage == "Special" or self.pet_state.stage != new_stage:
            if hasattr(self.pet_state, 'growth') and hasattr(self.pet_state.growth, 'evolve_to'):
                if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
                    self.pet_state.is_sleeping = False
                    self.pet_state.sleep_start_time = None
                success = self.pet_state.growth.evolve_to(new_stage)
                if success:
                    self.root.after(3000, self.ensure_movement_after_evolution)
                return success
        return False
    def ensure_movement_after_evolution(self):
        if hasattr(self.animation, 'force_restart_movement'):
            self.animation.force_restart_movement()
        else:
            self.pet_state.is_interacting = False
            if hasattr(self.animation, 'start_random_movement'):
                self.animation.start_random_movement()
    def handle_click(self, event):
        current_time = datetime.now().timestamp()
        if current_time - self.last_click_time < 0.3:
            if current_time - self.last_happiness_boost_time > self.happiness_boost_cooldown:
                self.pet_state.current_animation = 'happy'
                self.pet_state.stats.modify_stat('happiness', 20)
                self.pet_state.stats.modify_stat('social', 20)
                self.speech_bubble.show_bubble('happy')
                self.happiness_boost_cooldown = 60
                self.last_happiness_boost_time = current_time
                if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                    self.root.after_cancel(self.animation_reset_timer)
                self.animation_reset_timer = self.root.after(2000, self.reset_animation_state)
        self.last_click_time = current_time
    def handle_double_click(self, event):
        """Handle double-click to wake up sleeping pet or increase happiness"""
        pet_x = self.canvas.winfo_width() // 2
        pet_y = self.canvas.winfo_height() // 2
        distance = ((event.x - pet_x) ** 2 + (event.y - pet_y) ** 2) ** 0.5
        if distance < 50:
            if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
                if hasattr(self, 'inventory_system'):
                    self.inventory_system.wake_up_pet()
                    self.pet_state.is_sleeping = False
                    self.pet_state.sleep_start_time = None
                return
            current_time = time.time()
            if not hasattr(self, 'last_double_click_time'):
                self.last_double_click_time = 0
            if current_time - self.last_double_click_time >= 60:
                self.pet_state.stats.modify_stat('happiness', 10)
                self.pet_state.current_animation = 'happy'
                self.pet_state.is_interacting = True
                if hasattr(self, 'speech_bubble'):
                    self.speech_bubble.show_bubble('happy')
                self.last_double_click_time = current_time
                self.schedule_resume_movement(3000)
            else:
                remaining_time = int(60 - (current_time - self.last_double_click_time))
                if hasattr(self, 'speech_bubble'):
                    self.speech_bubble.show_bubble('happy', f"Wait {remaining_time} more seconds!")
    def reset_animation_state(self):
        if getattr(self.pet_state, 'is_sleeping', False):
            return
        if hasattr(self, 'pet_state') and self.pet_state.current_animation == 'happy':
            self.pet_state.current_animation = 'Standing'
            self.pet_state.is_interacting = False
            if hasattr(self, 'animation_reset_timer') and self.animation_reset_timer:
                self.root.after_cancel(self.animation_reset_timer)
                self.animation_reset_timer = None
            if hasattr(self, 'animation') and self.animation:
                if hasattr(self.animation, 'resume_movement'):
                    self.animation.resume_movement()
                elif hasattr(self.animation, 'start_random_movement'):
                    self.animation.start_random_movement()
    def check_for_cheat_code(self):
        if self._name == "UUDDLRLRBA":
            self.pet_state.currency += 10000000
            print("Cheat code activated! 10,000,000 coins added.")
    def reset_pet(self):
        self.pet_state = PetState()
        self.name = "Pet"
        self.pet_state.current_animation = 'Standing'
        self.pet_state.direction = 'left'
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
        summary = {
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
        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping and self.pet_state.sleep_start_time is not None:
            elapsed = datetime.now().timestamp() - self.pet_state.sleep_start_time.timestamp()
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            summary['sleep_timer'] = f"{minutes:02d}:{seconds:02d}"
        return summary
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
            'inventory': {item_id: item.quantity for item_id, item in self.inventory_system.items.items() if not item.unlimited},
            'creation_date': datetime.now().isoformat(),
            'save_date': datetime.now().isoformat(),
            'is_sleeping': self.pet_state.is_sleeping,
            'sleep_start_time': self.pet_state.sleep_start_time.isoformat() if self.pet_state.sleep_start_time else None,
            'sleep_duration': getattr(self.pet_state, 'sleep_duration', None),
            'poop_system_dirty': self.pet_state.poop_system_dirty,
            'treasure_system': self.treasure_system.get_save_data() if hasattr(self, 'treasure_system') else None
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
                if stat in stats_dict:
                    self.pet_state.stats.stats[stat] = max(0, min(100, stats_dict[stat]))
                    print(f"Loaded {stat}: {stats_dict[stat]}")
            if 'age' in stats_dict:
                self.pet_state.stats.stats['age'] = stats_dict['age']
                self.pet_state.stats.age = stats_dict['age']
            if 'decay_rates' in save_data:
                for key, value in save_data['decay_rates'].items():
                    if key in self.pet_state.stats.decay_rates:
                        self.pet_state.stats.decay_rates[key] = value
            if 'stage' in save_data:
                self.pet_state.stage = save_data['stage']
                if hasattr(self.pet_state, 'growth'):
                    self.pet_state.growth.stage = save_data['stage']
            if 'currency' in save_data:
                self.pet_state.currency = save_data['currency']
                print(f"Loaded currency: {save_data['currency']}")
            if 'inventory' in save_data:
                for item_id, quantity in save_data['inventory'].items():
                    if item_id in self.inventory_system.items:
                        self.inventory_system.items[item_id].quantity = quantity
                print(f"Loaded inventory: {len(save_data['inventory'])} items")
            if 'game_progress' in save_data:
                self.pet_state.game_progress = save_data['game_progress']
            self.pet_state.is_sleeping = save_data.get('is_sleeping', False)
            if 'sleep_start_time' in save_data and save_data['sleep_start_time']:
                self.pet_state.sleep_start_time = datetime.fromisoformat(save_data['sleep_start_time'])
            else:
                self.pet_state.sleep_start_time = None
            if 'sleep_duration' in save_data:
                self.pet_state.sleep_duration = save_data['sleep_duration']
            if 'poop_system_dirty' in save_data:
                self.pet_state.poop_system_dirty = save_data['poop_system_dirty']
            self.last_save = os.path.basename(filepath)
            if 'treasure_system' in save_data and hasattr(self, 'treasure_system'):
                self.treasure_system.load_save_data(save_data['treasure_system'])
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
            if hasattr(self, 'poop_system'):
                self.poop_system.add_food_consumed(1)
            self.schedule_resume_movement(5000)
            return result
        elif interaction_type == 'play':
            if self.pet_state.is_sleeping:
                if hasattr(self, 'inventory_system'):
                    self.inventory_system.wake_up_pet()
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
        elif interaction_type == 'clean':
            self.pet_state.current_animation = 'happy'
            self.pet_state.stats.modify_stat('cleanliness', 15)
            self.pet_state.stats.modify_stat('happiness', 5)
            result['message'] = 'Your pet feels fresh and clean!'
            result['stat_changes'].update({'cleanliness': 15, 'happiness': 5})
            self.speech_bubble.show_bubble('clean')
        elif interaction_type == 'sleep':
            if not self.pet_state.is_sleeping:
                self.pet_state.current_animation = 'sleeping'
                self.pet_state.is_sleeping = True
                self.pet_state.sleep_start_time = datetime.now()
                energy_needed = 100 - self.pet_state.stats.get_stat('energy')
                sleep_duration_minutes = max(0.1, energy_needed / 12)
                self.pet_state.sleep_duration = int(sleep_duration_minutes * 60 * 1000)
                result['message'] = 'Your pet is now sleeping to recover energy!'
                self.speech_bubble.show_bubble('sleep')
                return result
        self.schedule_resume_movement(3000)
        return result
    def schedule_resume_movement(self, delay_ms):
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
        self.resume_timer = self.root.after(delay_ms, self.resume_movement)
    def resume_movement(self):
        self.pet_state.is_interacting = False
        if hasattr(self.animation, 'resume_movement'):
            self.animation.resume_movement()
        else:
            if hasattr(self.animation, 'force_restart_movement'):
                self.animation.force_restart_movement()
    def handle_right_click(self, event):
        self.pause_movement()
        x = self.root.winfo_x() + event.x
        y = self.root.winfo_y() + event.y
        self.status_panel.show_panel(x, y)
        self.schedule_resume_movement(5000)
        self.root.after(100, self.update_sleep_timer_display)
    def on_stats_panel_closed(self):
        self.schedule_resume_movement(200)
        if self.sleep_timer_update_id:
            self.root.after_cancel(self.sleep_timer_update_id)
            self.sleep_timer_update_id = None
        if self.sleep_timer_label:
            self.sleep_timer_label.destroy()
            self.sleep_timer_label = None
    def show_inventory(self, parent_window=None):
        self.inventory_system.show_inventory(parent_window=parent_window)
    def update_sleep_timer_display(self):
        """Update the sleep timer in the status panel to show remaining time"""
        if not self.status_panel or not self.status_panel.panel_window or not self.status_panel.panel_window.winfo_exists():
            return
        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
            if self.pet_state.sleep_start_time is None:
                self.pet_state.sleep_start_time = datetime.now()
            if not hasattr(self.pet_state, 'sleep_duration') or self.pet_state.sleep_duration is None:
                self.pet_state.sleep_duration = 180000
            sleep_duration_sec = self.pet_state.sleep_duration / 1000
            elapsed = datetime.now().timestamp() - self.pet_state.sleep_start_time.timestamp()
            remaining = max(0, sleep_duration_sec - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            timer_text = f"Sleeping: {minutes:02d}:{seconds:02d} left"
            if not self.sleep_timer_label:
                self.sleep_timer_label = tk.Label(self.status_panel.panel_window,
                                                text=timer_text,
                                                font=("Arial", 12, "bold"),
                                                fg="white",
                                                bg="#4a86e8",
                                                padx=10,
                                                pady=5)
                self.sleep_timer_label.pack(side="top", fill=tk.X, pady=(0, 10))
            else:
                if self.sleep_timer_label.winfo_exists():
                    self.sleep_timer_label.config(text=timer_text)
                else:
                    self.sleep_timer_label = None
            self.sleep_timer_update_id = self.root.after(1000, self.update_sleep_timer_display)
        elif self.sleep_timer_label:
            self.sleep_timer_label.destroy()
            self.sleep_timer_label = None
    def show_game_hub(self, parent_window=None):
        from game_hub import GameHub
        from currency_system import CurrencySystem
        if not hasattr(self, 'currency_system'):
            self.currency_system = CurrencySystem(self.pet_state)
        game_hub = GameHub(self.root, self.currency_system, self.pet_state, parent_window=parent_window)
    def handle_drag(self, event):
        self.pause_movement()
        x = self.root.winfo_x() + event.x - 128
        y = self.root.winfo_y() + event.y - 128
        self.root.geometry(f'+{x}+{y}')
    def handle_drag_end(self, event):
        self.schedule_resume_movement(500)
    def pause_movement(self):
        self.pet_state.is_interacting = True
        if hasattr(self.animation, 'pause_movement'):
            self.animation.pause_movement()
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
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.name = "SystemTrayThread"
        self.tray_thread.start()
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
        try:
            success, message = self.save_pet()
            if success:
                print("Pet data saved successfully!")
            else:
                print(f"Failed to save pet data: {message}")
        except Exception as e:
            print(f"Error saving pet data on exit: {e}")
        if hasattr(self, 'treasure_system'):
            self.treasure_system.cleanup()
        if hasattr(self, 'poop_system'):
            self.poop_system.cleanup()
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        self.running = False
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
        elif setting_name == 'pet_size':
            if hasattr(self.animation, 'handle_size_change'):
                self.animation.handle_size_change(old_value, value)
            else:
                self.handle_size_change(old_value, value)
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
    def auto_load_pet(self):
        """Automatically load the most recent save file on startup"""
        try:
            standard_save = os.path.join(self.save_path, f"{self.name.replace(' ', '_')}_save.json")
            if os.path.exists(standard_save):
                print(f"Loading existing pet save: {standard_save}")
                pet, error = self.load_pet(standard_save)
                if pet:
                    print("Pet loaded successfully!")
                    if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
                        print(f"[LOAD] Loaded sleep state: is_sleeping={self.pet_state.is_sleeping}, sleep_start_time={self.pet_state.sleep_start_time}")
                    return True
                else:
                    print(f"Failed to load pet: {error}")
            save_files = self.get_save_files()
            if save_files:
                most_recent = None
                most_recent_time = 0
                for save_file in save_files:
                    if save_file.endswith('_save.json') or save_file.startswith('autosave_'):
                        file_path = os.path.join(self.save_path, save_file)
                        try:
                            mod_time = os.path.getmtime(file_path)
                            if mod_time > most_recent_time:
                                most_recent_time = mod_time
                                most_recent = save_file
                        except:
                            continue
                if most_recent:
                    print(f"Loading most recent save: {most_recent}")
                    pet, error = self.load_pet(most_recent)
                    if pet:
                        print("Pet loaded successfully!")
                        if hasattr(self.pet_state, 'is_sleeping') and self.pet_state.is_sleeping:
                            print(f"[LOAD] Loaded sleep state: is_sleeping={self.pet_state.is_sleeping}, sleep_start_time={self.pet_state.sleep_start_time}")
                        return True
                    else:
                        print(f"Failed to load pet: {error}")
            print("No existing save file found, starting with new pet")
            return False
        except Exception as e:
            print(f"Error during auto-load: {e}")
            return False
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
    pet = VirtualPet(root)
    root.protocol("WM_DELETE_WINDOW", pet.exit_app)
    root.mainloop()