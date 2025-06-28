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
        

        self.sickness_icon = None
        self.sickness_icon_id = None
        self.sickness_blink_timer = None
        self.sickness_visible = True
        

        if hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.on_sickness_changed = self.update_sickness_display
        

        if hasattr(self.pet_state, 'growth'):
            self.pet_state.growth.on_stage_changed = self.handle_stage_change
        

        self.load_animations()
        

        self.animate()
        
    def handle_stage_change(self, old_stage, new_stage):

        print(f"Pet evolved from {old_stage} to {new_stage}, reloading animations")

        self.animations = {}

        self.load_animations()
    
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
        

        fallback_map = {
            'Sleep2': 'Sleep1',  # Use Sleep1 as fallback for Sleep2
            'Refuse': 'Angry'    # Use Angry as fallback for Refuse
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
                            # Don't print fallback message to reduce console spam
                            break
                

                if img_path and os.path.exists(img_path):
                    image = Image.open(img_path)

                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized_image = image.resize((int(image.width * size_factor), int(image.height * size_factor)), Image.LANCZOS)
                    

                    # Direction flipping will be handled in the animate method
                    self.animations[state] = ImageTk.PhotoImage(resized_image)
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
                img = img.resize((32, 32), Image.LANCZOS)  # Increased size for better visibility
                self.sickness_icon = ImageTk.PhotoImage(img)
                return True
            else:
                print(f"Sickness icon not found at {img_path}")
                return False
        except Exception as e:
            print(f"Error loading sickness icon: {e}")
            return False
    
    def update_sickness_display(self, is_sick):
        """Update the sickness icon display based on pet's sickness status"""
        # Load sickness icon if not already loaded
        if not self.sickness_icon and not self.load_sickness_icon():
            return  # Can't display if icon can't be loaded
            
        # Remove existing sickness icon if any
        if self.sickness_icon_id:
            self.canvas.delete(self.sickness_icon_id)
            self.sickness_icon_id = None
            
        # If pet is sick and we have the icon, display it
        if is_sick and self.sickness_icon:
            # Position the icon at the top right of the pet, but still near it
            self.sickness_icon_id = self.canvas.create_image(
                160, 100,  # Positioned at top right of pet
                image=self.sickness_icon,
                tags='sickness_icon'
            )
            
    def show_sickness_overlay(self):
        """Show the sickness overlay when pet is sick"""
        # Load sickness icon if not already loaded
        if not self.sickness_icon and not self.load_sickness_icon():
            return  # Can't display if icon can't be loaded
            
        # Display the sickness icon
        if self.sickness_icon and not self.sickness_icon_id:
            self.sickness_icon_id = self.canvas.create_image(
                160, 100,  # Positioned at top right of pet
                image=self.sickness_icon,
                tags='sickness_icon'
            )
            # Set pet animation to sick
            self.pet_state.current_animation = 'sick'
            
            # Start blinking the sickness icon
            self.start_sickness_icon_blinking()
    
    def start_sickness_icon_blinking(self):
        """Start blinking the sickness icon"""
        def blink_icon():
            if self.sickness_icon_id:
                if self.sickness_visible:
                    self.canvas.itemconfigure(self.sickness_icon_id, state='hidden')
                    self.sickness_visible = False
                else:
                    self.canvas.itemconfigure(self.sickness_icon_id, state='normal')
                    self.sickness_visible = True
                
                # Continue blinking if the pet is still sick
                if hasattr(self.pet_state.stats, 'is_sick') and self.pet_state.stats.is_sick:
                    self.sickness_blink_timer = self.root.after(500, blink_icon)
        
        # Cancel any existing blink timer
        if self.sickness_blink_timer:
            self.root.after_cancel(self.sickness_blink_timer)
        
        # Start blinking
        self.sickness_visible = True
        self.sickness_blink_timer = self.root.after(500, blink_icon)
    
    def hide_sickness_overlay(self):
        """Hide the sickness overlay when pet recovers"""
        # Stop blinking timer
        if self.sickness_blink_timer:
            self.root.after_cancel(self.sickness_blink_timer)
            self.sickness_blink_timer = None
        
        # Remove the sickness icon
        if self.sickness_icon_id:
            self.canvas.delete(self.sickness_icon_id)
            self.sickness_icon_id = None
            
        # Reset animation if it was set to sick
        if self.pet_state.current_animation == 'sick':
            self.pet_state.current_animation = 'Standing'
            
    def check_sickness_status(self):
        """Check if pet should be sick based on stats"""
        is_sick = False
        
        # Check if any stat is below 25%
        if hasattr(self.pet_state, 'stats'):
            for stat_name in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social']:
                if self.pet_state.stats.get_stat(stat_name) < 25:
                    is_sick = True
                    break
            
            # Update sickness status in pet stats
            if hasattr(self.pet_state.stats, 'is_sick'):
                self.pet_state.stats.is_sick = is_sick
            
            # Update pet animation and overlay based on sickness status
            if is_sick:
                if self.pet_state.current_animation != 'sick':
                    self.pet_state.current_animation = 'sick'
                if not self.sickness_icon_id:
                    self.show_sickness_overlay()
            else:
                if self.sickness_icon_id:
                    self.hide_sickness_overlay()
            
            # Update sickness status
            if hasattr(self.pet_state.stats, 'is_sick'):
                self.pet_state.stats.is_sick = is_sick
                
            # Force immediate update of sickness display
            if is_sick and not self.sickness_icon_id:
                self.load_sickness_icon()
                self.show_sickness_overlay()
            elif not is_sick and self.sickness_icon_id:
                self.hide_sickness_overlay()
    
    def animate(self):
        """Update pet animation frame"""
        try:
            # Get current animation sequence
            animation_sequences = {
                'Standing': ['Walk1', 'Walk2'],  # Changed to use the same animation as Walking
                'Walking': ['Walk1', 'Walk2'],
                'happy': ['Happy', 'Walk1'],
                'sleeping': ['Sleep1'],  # Changed to only use Sleep1 to avoid fallback messages
                'eating': ['Eat1', 'Eat2'],
                'playing': ['Attack', 'Walk1'],
                'special': ['Happy', 'Walk1', 'Walk2', 'Happy'],
                'angry': ['Angry', 'Walk1'],
                'sad': ['Lose1', 'Walk1'],
                'sick': ['Walk1', 'Lose1']  # Fixed to cycle between Walk1 and Lose1
            }
            
            sequence = animation_sequences[self.pet_state.current_animation]
            frame = sequence[int(datetime.now().timestamp() * 2) % len(sequence)]
            
            # Update canvas with current frame
            self.canvas.delete('pet')  # Only delete the pet image, not everything
            if frame in self.animations:
                # Get the original image path to reload with proper direction
                base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
                pet_color = self.settings.get('pet_color', 'black').lower()
                
                # Try to find the image path
                img_path = None
                if pet_color == 'black':
                    # Default black pet (no suffix)
                    possible_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}.png'),
                        os.path.join(base_path, f'{self.pet_state.stage.lower()}_{frame}.png')
                    ]
                else:
                    # Try multiple filename patterns for colored pets
                    possible_paths = [
                        os.path.join(base_path, f'{self.pet_state.stage}_{frame}_{pet_color}.png'),
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
                
                # If we found a valid image path, load and display it with proper direction
                if img_path and os.path.exists(img_path):
                    # Load the image
                    image = Image.open(img_path)
                    # Resize the image based on pet_size setting (100 = 4x original size)
                    size_factor = 4 * (self.settings['pet_size'] / 100)
                    resized_image = image.resize((int(image.width * size_factor), int(image.height * size_factor)), Image.LANCZOS)
                    
                    # Always apply direction flip based on current direction
                    # This ensures direction is maintained regardless of color/stage changes
                    if self.pet_state.direction == 'right':
                        resized_image = resized_image.transpose(Image.FLIP_LEFT_RIGHT)
                    
                    # Convert to PhotoImage and display
                    self.animations[frame] = ImageTk.PhotoImage(resized_image)
                    self.canvas.create_image(128, 128, image=self.animations[frame], tags='pet')
                else:
                    # Use the preloaded animation if we couldn't reload it
                    photoimage = self.animations[frame]
                    self.canvas.create_image(128, 128, image=photoimage, tags='pet')
                    print(f"Warning: Could not reload animation frame for {self.pet_state.stage}_{frame}")
                
                # Check if pet is sick and update sickness icon if needed
                self.check_sickness_status()
            else:
                print(f"Warning: Animation frame {frame} not found in preloaded animations")
        
        except Exception as e:
            print(f'Animation error: {e}')
        
        # Schedule next frame
        self.root.after(100, self.animate)
    
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
                    # Stay idle for a while but keep animating
                    idle_time = random.randint(5000, 15000)  # 5-15 seconds of idle time
                    self.pet_state.current_animation = 'Standing'  # Still uses Walking animation frames
                    self.movement_timer = self.root.after(idle_time, move_randomly)
                    return
                
                # Set random target position within screen bounds
                self.target_x = random.randint(0, screen_width - 256)
                self.target_y = random.randint(0, screen_height - 256)
                
                # Update pet direction based on target
                current_x = self.root.winfo_x()
                self.pet_state.direction = 'right' if self.target_x > current_x else 'left'
                
                # Set walking animation
                self.pet_state.current_animation = 'Walking'
                
                # Start movement steps
                self.move_step()
                
                # Schedule next random movement based on activity level
                # Higher activity level means more frequent movements (1-10 scale)
                # Convert to milliseconds: 10000ms (low activity) to 2000ms (high activity)
                delay = int(10000 - (activity_level * 800))
                self.movement_timer = self.root.after(delay, move_randomly)
        
        # Start initial movement
        move_randomly()
    
    def move_step(self):
        """Move one step toward target position"""
        if not hasattr(self, 'target_x') or not hasattr(self, 'target_y'):
            return
            
        # Get current position
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        # Calculate distance to target
        dx = self.target_x - current_x
        dy = self.target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # If we're close enough, stop moving
        if distance < 5:
            self.pet_state.current_animation = 'Standing'
            return
        
        # Calculate movement speed based on settings
        speed = self.settings.get('movement_speed', 5)
        step_size = speed * 0.5  # Adjust step size based on speed setting
        
        # Calculate step
        if distance > 0:
            step_x = dx * step_size / distance
            step_y = dy * step_size / distance
        else:
            step_x = 0
            step_y = 0
        
        # Update position
        new_x = current_x + step_x
        new_y = current_y + step_y
        self.root.geometry(f'+{int(new_x)}+{int(new_y)}')
        
        # Check for poop generation at each step
        if hasattr(self.pet_state, 'poop_system'):
            self.pet_state.poop_system.check_poop_generation(128, 128)  # Center of pet
        
        # Schedule next step
        if not self.pet_state.is_interacting:
            self.movement_timer = self.root.after(50, self.move_step)
    
    def pause_movement(self):
        """Pause pet movement for interactions"""
        self.pet_state.is_interacting = True
        
        # Cancel any ongoing movement timers
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
        """Resume pet movement after interaction"""
        self.pet_state.is_interacting = False
        
        # Start random movement again
        if not self.movement_timer:
            self.start_random_movement()
    
    def schedule_resume_movement(self, delay_ms):
        """Schedule resuming movement after a delay"""
        if self.resume_timer:
            self.root.after_cancel(self.resume_timer)
        self.resume_timer = self.root.after(delay_ms, self.resume_movement)
    
    def handle_drag(self, event):
        """Handle dragging the pet with the mouse"""
        self.pause_movement()
        x = self.root.winfo_x() + event.x - 128  # Center offset
        y = self.root.winfo_y() + event.y - 128  # Center offset
        self.root.geometry(f'+{x}+{y}')
    
    def create_tray_icon(self):
        """Create an icon for the system tray"""
        from PIL import ImageDraw
        
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