import tkinter as tk
from PIL import Image, ImageTk
import os
import math
import random
from datetime import datetime

class PetAnimation:
    
    def __init__(self, root, canvas, pet_state, settings):
        self.root = root
        self.canvas = canvas
        self.pet_state = pet_state
        self.settings = settings
        
        self.animations = {}
        
        self.movement_timer = None
        self.movement_step_timer = None
        self.resume_timer = None
        self.target_x = None
        self.target_y = None
        self.last_sleep_time = datetime.now()  
        
        self.sickness_icon = None
        self.sickness_icon_id = None
        self.sickness_blink_timer = None
        self.sickness_visible = True
        
        self.load_animations()
        if hasattr(self.pet_state, 'growth'):
            self.pet_state.growth.on_stage_changed = self.handle_stage_change
        self.root.after(0, self.animate)
    
    def _apply_sleep_effects(self):
        if hasattr(self.pet_state, 'stats'):
            energy_gain = random.randint(15, 25)  
            hunger_loss = random.randint(3, 8)    
            social_loss = random.randint(2, 5)    
            
            self.pet_state.stats.modify_stat('energy', energy_gain)
            self.pet_state.stats.modify_stat('hunger', -hunger_loss)
            self.pet_state.stats.modify_stat('social', -social_loss)
            
        
        if hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.on_sickness_changed = self.update_sickness_display
        
        
        self.pet_state.current_animation = 'Standing'
        
        self.start_movement_watchdog()
        
    def handle_stage_change(self, old_stage, new_stage):
        print(f"Pet evolved from {old_stage} to {new_stage}, playing evolution animation")
        self.play_evolution_animation()
        
    def play_evolution_animation(self):
        self.pet_state.is_interacting = True
        self.pet_state.current_animation = 'Evolving'
        self.root.after(2400, self.load_new_stage_animations) 

    def load_new_stage_animations(self):
        print("Evolution animation finished, reloading animations for new stage")
        self.animations = {}
        self.load_animations()
        self.pet_state.is_interacting = False
        self.pet_state.current_animation = 'Standing'
        self.force_restart_movement()

    def update_pet_image(self):
        """Forces the pet's image to update based on its current stage and animation."""
        self.load_animations()
        # Immediately trigger a re-render of the pet
        self.animate()
    
    def handle_color_change(self, old_color, new_color):
        print(f"Pet color changed from {old_color} to {new_color}, reloading animations")
        current_direction = self.pet_state.direction
        
        self.animations = {}
        
        self.load_animations()
        
        self.pet_state.direction = current_direction
    
    def load_animations(self):
        self.animations = {}
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
        
        pet_color = self.settings.get('pet_color', 'black').lower()
        
        all_states = ['Walk1', 'Walk2', 'Happy', 'Sleep1', 'Sleep2',
                     'Eat1', 'Eat2', 'Attack', 'Angry', 'Lose1', 'Refuse']
        
        base_path_evo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames', 'Evolution')
        evolution_frames = []
        for i in range(1, 9):
            try:
                img_path = os.path.join(base_path_evo, f'Evo{i}.png')
                if os.path.exists(img_path):
                    pil_img = Image.open(img_path)
                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized = pil_img.resize((int(pil_img.width * size_factor), int(pil_img.height * size_factor)), Image.LANCZOS)
                    evolution_frames.append(ImageTk.PhotoImage(resized))
            except Exception as e:
                print(f'Error loading evolution frame {i}: {e}')
        self.animations['Evolving'] = evolution_frames
        
        fallback_map = {
            'Sleep2': 'Sleep1',
            'Refuse': 'Angry'
        }
        
        for state in all_states:
            try:
                img_path = None
                
                if pet_color == 'black':
                    img_path = os.path.join(base_path, f'{self.pet_state.stage}_{state}.png')
                    if not os.path.exists(img_path):
                        img_path = os.path.join(base_path, f'{self.pet_state.stage.lower()}_{state}.png')
                else:
                    possible_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{state}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{state}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.upper()}_{state}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage}_{state.lower()}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage}_{state.upper()}_{pet_color}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{state.lower()}_{pet_color}.png')
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                if img_path is None or not os.path.exists(img_path):
                    fallback_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{state}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{state}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.upper()}_{state}.png')
                    ]
                    
                    for path in fallback_paths:
                        if os.path.exists(path):
                            img_path = path
                            if pet_color != 'black':
                                print(f"Using default black variant for {state} as {pet_color} variant not found")
                            break
                
                if (img_path is None or not os.path.exists(img_path)) and state in fallback_map:
                    fallback_state = fallback_map[state]
                    if pet_color != 'black':
                        fallback_paths = [
                            os.path.join(base_path, f'{self.pet_state.stage}_{fallback_state}_{pet_color}.png'),
                            os.path.join(base_path, f'{self.pet_state.stage.lower()}_{fallback_state}_{pet_color}.png')
                        ]
                    else:
                        fallback_paths = [
                            os.path.join(base_path, f'{self.pet_state.stage}_{fallback_state}.png'),
                            os.path.join(base_path, f'{self.pet_state.stage.lower()}_{fallback_state}.png')
                        ]
                    
                    for path in fallback_paths:
                        if os.path.exists(path):
                            img_path = path
                            break
                
                if img_path and os.path.exists(img_path):
                    pil_img = Image.open(img_path)
                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized = pil_img.resize((int(pil_img.width * size_factor), int(pil_img.height * size_factor)), Image.LANCZOS)
                    
                    photo_normal = ImageTk.PhotoImage(resized)
                    
                    flipped = resized.transpose(Image.FLIP_LEFT_RIGHT)
                    photo_flipped = ImageTk.PhotoImage(flipped)
                    
                    self.animations[state] = photo_normal
                    self.animations[f"{state}_flip"] = photo_flipped
                else:
                    essential_frames = ['Walk1', 'Walk2', 'Happy']
                    if state in essential_frames:
                        print(f"Warning: Essential animation frame not found for {self.pet_state.stage}_{state}")
            except Exception as e:
                print(f'Error loading animation frame {state}: {e}')
    
    def load_sickness_icon(self):
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'sickness.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((32, 32), Image.LANCZOS)
                self.sickness_icon = ImageTk.PhotoImage(img)
                return True
            else:
                print(f"Sickness icon not found at {img_path}")
                return False
        except Exception as e:
            print(f"Error loading sickness icon: {e}")
            return False
    
    def update_sickness_display(self, is_sick):
        if not self.sickness_icon and not self.load_sickness_icon():
            return
            
        if self.sickness_icon_id:
            self.canvas.delete(self.sickness_icon_id)
            self.sickness_icon_id = None
            
        if is_sick and self.sickness_icon:
            self.sickness_icon_id = self.canvas.create_image(
                160, 100,
                image=self.sickness_icon,
                tags='sickness_icon'
            )
            
    def show_sickness_overlay(self):
        if not self.sickness_icon and not self.load_sickness_icon():
            return
            
        if self.sickness_icon and not self.sickness_icon_id:
            self.sickness_icon_id = self.canvas.create_image(
                160, 100,
                image=self.sickness_icon,
                tags='sickness_icon'
            )
            self.pet_state.current_animation = 'sick'
            
            self.start_sickness_icon_blinking()
    
    def start_sickness_icon_blinking(self):
        def blink_icon():
            if self.sickness_icon_id:
                if self.sickness_visible:
                    self.canvas.itemconfigure(self.sickness_icon_id, state='hidden')
                    self.sickness_visible = False
                else:
                    self.canvas.itemconfigure(self.sickness_icon_id, state='normal')
                    self.sickness_visible = True
                
                if hasattr(self.pet_state.stats, 'is_sick') and self.pet_state.stats.is_sick:
                    self.sickness_blink_timer = self.root.after(500, blink_icon)
        
        if self.sickness_blink_timer:
            self.root.after_cancel(self.sickness_blink_timer)
        
        self.sickness_visible = True
        self.sickness_blink_timer = self.root.after(500, blink_icon)
    
    def hide_sickness_overlay(self):
        if self.sickness_blink_timer:
            self.root.after_cancel(self.sickness_blink_timer)
            self.sickness_blink_timer = None
        
        if self.sickness_icon_id:
            self.canvas.delete(self.sickness_icon_id)
            self.sickness_icon_id = None
            
        if self.pet_state.current_animation == 'sick':
            self.pet_state.current_animation = 'Standing'
            
    def check_sickness_status(self):
        is_sick = False
        
        if hasattr(self.pet_state, 'stats'):
            for stat_name in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if self.pet_state.stats.get_stat(stat_name) < 25:
                    is_sick = True
                    break
            
            if hasattr(self.pet_state.stats, 'is_sick'):
                self.pet_state.stats.is_sick = is_sick
            
            if is_sick:
                if self.pet_state.current_animation != 'sick':
                    self.pet_state.current_animation = 'sick'
                if not self.sickness_icon_id:
                    self.show_sickness_overlay()
            else:
                if self.sickness_icon_id:
                    self.hide_sickness_overlay()
            
            if hasattr(self.pet_state.stats, 'is_sick'):
                self.pet_state.stats.is_sick = is_sick
                
            if is_sick and not self.sickness_icon_id:
                self.load_sickness_icon()
                self.show_sickness_overlay()
            elif not is_sick and self.sickness_icon_id:
                self.hide_sickness_overlay()
    
    def animate(self):
        try:
            animation_sequences = {
                'Standing': ['Walk1', 'Walk2'],
                'Walking': ['Walk1', 'Walk2'],
                'happy': ['Happy', 'Walk1'],
                'sleeping': ['Sleep1'],
                'eating': ['Eat1', 'Eat2'],
                'playing': ['Attack', 'Walk1'],
                'special': ['Happy', 'Walk1', 'Walk2', 'Happy'],
                'angry': ['Angry', 'Walk1'],
                'sad': ['Lose1', 'Walk1'],
                'sick': ['Walk1', 'Lose1']
            }
            
            if self.pet_state.current_animation == 'Evolving':
                sequence = self.animations.get('Evolving', [])
                if not sequence:
                    self.root.after(100, self.animate)
                    return
                frame = sequence[int(datetime.now().timestamp() * 4) % len(sequence)]
                self.canvas.delete('pet')
                self.canvas.create_image(128, 128, image=frame, tags='pet')
            else:
                sequence = animation_sequences.get(self.pet_state.current_animation, [])
                if not sequence:
                    self.root.after(100, self.animate)
                    return
                frame = sequence[int(datetime.now().timestamp() * 2) % len(sequence)]
                self.canvas.delete('pet')
                
                # Select the appropriate frame based on direction
                key = frame
                flip_key = f"{frame}_flip"
                photoimage = None
                
                if self.pet_state.direction == 'right' and flip_key in self.animations:
                    photoimage = self.animations[flip_key]
                elif key in self.animations:
                    photoimage = self.animations[key]
                
                if photoimage:
                    self.canvas.create_image(128, 128, image=photoimage, tags='pet')
                    self.check_sickness_status()
                else:
                    print(f"Warning: Animation frame {frame} not found in preloaded animations")
                    print(f"Available frames: {list(self.animations.keys())}")
                    print(f"Current animation: {self.pet_state.current_animation}")
                    print(f"Animation sequences: {animation_sequences}")
                    # Fallback to Walk1 if available, otherwise any available frame
                    if 'Walk1' in self.animations:
                        photoimage = self.animations['Walk1']
                        self.canvas.create_image(128, 128, image=photoimage, tags='pet')
                        self.check_sickness_status()
                    elif len(self.animations) > 0:
                        # Use any available frame as last resort
                        available_frame = list(self.animations.keys())[0]
                        photoimage = self.animations[available_frame]
                        self.canvas.create_image(128, 128, image=photoimage, tags='pet')
                        self.check_sickness_status()
        
        except Exception as e:
            print(f'Animation error: {e}')
        
        self.root.after(100, self.animate)
    
    def start_random_movement(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        def move_randomly():
            if not self.pet_state.is_interacting:
                activity_level = self.settings['activity_level']
                idle_chance = (11 - activity_level) * 10
                
                if random.randint(1, 100) <= idle_chance:
                    # Decide between standing idle or sleeping
                    time_since_sleep = (datetime.now() - self.last_sleep_time).total_seconds()
                    
                    # Increase sleep chance if pet hasn't slept in a while
                    base_sleep_chance = 15  # 15% base chance (reduced from 25%)
                    if time_since_sleep > 600:  # 10 minutes since last sleep (increased from 5)
                        sleep_chance = min(35, base_sleep_chance + (time_since_sleep - 600) / 120 * 5)  # Max 35% (reduced from 60%)
                    else:
                        sleep_chance = base_sleep_chance
                    
                    if random.randint(1, 100) <= sleep_chance:
                        # Pet decides to take a nap
                        sleep_time = random.randint(8000, 20000)  # 8-20 seconds sleep
                        self.pet_state.current_animation = 'sleeping'
                        self.pet_state.is_interacting = True  # Prevent movement during sleep
                        self.last_sleep_time = datetime.now()
                        
                        # Apply sleep stat effects
                        self._apply_sleep_effects()
                        
                        # Schedule wake up
                        def wake_up():
                            if self.pet_state.current_animation == 'sleeping':
                                self.pet_state.current_animation = 'Standing'
                                self.pet_state.is_interacting = False
                        
                        self.root.after(sleep_time, wake_up)
                        self.movement_timer = self.root.after(sleep_time + 1000, move_randomly)  # Resume movement after waking
                    else:
                        # Pet just stands idle
                        idle_time = random.randint(5000, 15000)
                        self.pet_state.current_animation = 'Standing'
                        self.movement_timer = self.root.after(idle_time, move_randomly)
                    return
                
                # Avoid the top area if context awareness is active to prevent conflicts with speech bubbles
                min_y = 0
                if (hasattr(self.pet_state, 'context_awareness') and 
                    hasattr(self.pet_state.context_awareness, 'monitoring_enabled') and
                    self.pet_state.context_awareness.monitoring_enabled):
                    min_y = 150  # Keep pet away from top 150px when context awareness is active
                
                self.target_x = random.randint(0, screen_width - 256)
                self.target_y = random.randint(min_y, screen_height - 256)
                
                current_x = self.root.winfo_x()
                self.pet_state.direction = 'right' if self.target_x > current_x else 'left'
                
                self.pet_state.current_animation = 'Walking'
                
                self.move_step()
                
                delay = int(10000 - (activity_level * 800))
                self.movement_timer = self.root.after(delay, move_randomly)
        
        move_randomly()
    
    def move_step(self):
        if not hasattr(self, 'target_x') or not hasattr(self, 'target_y'):
            return
            
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        dx = self.target_x - current_x
        dy = self.target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 5:
            self.pet_state.current_animation = 'Standing'
            return
        
        # Update direction based on current movement (fix for direction inconsistency)
        if abs(dx) > 2:  # Only update direction for significant horizontal movement
            new_direction = 'right' if dx > 0 else 'left'
            if new_direction != self.pet_state.direction:
                self.pet_state.direction = new_direction
        
        speed = self.settings.get('movement_speed', 5)
        step_size = speed * 0.5
        
        if distance > 0:
            step_x = dx * step_size / distance
            step_y = dy * step_size / distance
        else:
            step_x = 0
            step_y = 0
        
        new_x = current_x + step_x
        new_y = current_y + step_y
        self.root.geometry(f'+{int(new_x)}+{int(new_y)}')
        
        if hasattr(self.pet_state, 'poop_system'):
            self.pet_state.poop_system.check_poop_generation(128, 128)
        
        if not self.pet_state.is_interacting:
            self.movement_timer = self.root.after(50, self.move_step)
    
    def pause_movement(self):
        self.pet_state.is_interacting = True
        
        if self.movement_timer:
            self.root.after_cancel(self.movement_timer)
            self.movement_timer = None
            
        if self.movement_step_timer:
            self.root.after_cancel(self.movement_step_timer)
            self.movement_step_timer = None
            
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
            self.resume_timer = None
    
    def resume_movement(self):
        self.pet_state.is_interacting = False
        
        if not self.movement_timer:
            self.start_random_movement()
    
    def force_restart_movement(self):
        if self.movement_timer:
            self.root.after_cancel(self.movement_timer)
            self.movement_timer = None
            
        if self.movement_step_timer:
            self.root.after_cancel(self.movement_step_timer)
            self.movement_step_timer = None
            
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
            self.resume_timer = None
        
        self.pet_state.is_interacting = False
        self.pet_state.current_animation = 'Standing'
        
        self.root.after(1000, self.start_random_movement)
    
    def start_movement_watchdog(self):
        def check_movement():
            if (not self.pet_state.is_interacting and 
                self.pet_state.current_animation == 'Standing' and 
                not self.movement_timer):
                
                self.force_restart_movement()
            
            self.root.after(15000, check_movement)
        
        self.root.after(15000, check_movement)
    
    def schedule_resume_movement(self, delay_ms):
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
        self.resume_timer = self.root.after(delay_ms, self.resume_movement)
    
    def handle_drag(self, event):
        self.pause_movement()
        x = self.root.winfo_x() + event.x - 128
        y = self.root.winfo_y() + event.y - 128
        self.root.geometry(f'+{x}+{y}')
    
    def create_tray_icon(self):
        from PIL import ImageDraw
        
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