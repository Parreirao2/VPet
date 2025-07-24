import tkinter as tk
import math
import random
from PIL import Image, ImageDraw, ImageTk
from unified_ui import COLORS

class SpeechBubble:
    
    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.parent = parent
        self.bubble_window = None
        self.bubble_duration = 5000
        self._bubble_timer = None
        self._update_position_timer = None
        self._repositioning_pet = False  # Flag to prevent repositioning loops
        self._last_reposition_time = 0  # Track when we last repositioned
        self._bubble_positioned = False  # Flag to prevent positioning loops
        self._last_bubble_position = None  # Track last bubble position
        
        self.responses = {
            'feed': [
                "Yum yum!", 
                "Delicious!", 
                "More please!", 
                "Tasty!",
                "*happy munching*",
                "This is so good!",
                "My favorite food!",
                "Nom nom nom!",
                "I was so hungry!",
                "Food makes me happy!",
                "Can I have seconds?",
                "*licks lips*",
                "Best meal ever!",
                "So satisfying!",
                "*contented sigh*"
            ],
            'play': [
                "This is fun!", 
                "Wheee!", 
                "Let's play more!", 
                "*excited noises*",
                "I love playing!",
                "Again, again!",
                "You're the best playmate!",
                "*jumps with joy*",
                "Playing is my favorite!",
                "I could do this all day!",
                "So much fun!",
                "*playful spin*",
                "This game is awesome!",
                "I'm having a blast!",
                "Let's never stop playing!"
            ],
            'clean': [
                "So fresh!", 
                "Squeaky clean!", 
                "*happy splashing*", 
                "I feel renewed!",
                "Bubbles!",
                "I love bath time!",
                "*shakes off water*",
                "Clean and shiny now!",
                "That was refreshing!",
                "I feel like new!",
                "*enjoys the scrubbing*",
                "Sparkling clean!",
                "Bath time is the best!",
                "I needed that wash!",
                "No more dirt on me!"
            ],
            'medicine': [
                "Feeling better!", 
                "*gulp*", 
                "Tastes weird...", 
                "Thank you!",
                "I needed that",
                "That's helping already!",
                "*makes a face but takes it*",
                "Medicine makes me stronger!",
                "I can feel it working!",
                "Not so sick anymore!",
                "The taste is worth feeling better!",
                "*reluctant but grateful*",
                "Health is returning!",
                "That wasn't so bad!",
                "I'll be better in no time!"
            ],
            'pet': [
                "*purrs*", 
                "I love attention!", 
                "More pets please!", 
                "*happy noises*",
                "That feels nice!",
                "Right there, perfect!",
                "*leans into the pets*",
                "I could get used to this!",
                "Attention is the best!",
                "You give the best pets!",
                "*closes eyes in contentment*",
                "This is so relaxing!",
                "Don't stop, please!",
                "Pets make everything better!",
                "*melts with happiness*"
            ],
            'sleep': [
                "*yawns*", 
                "Zzz...", 
                "Nap time...", 
                "*sleepy noises*",
                "So cozy...",
                "*curls up*",
                "Sweet dreams...",
                "Need some rest...",
                "*peaceful sleeping*",
                "Goodnight...",
                "*soft snoring*",
                "Time to recharge...",
                "Sleep is bliss...",
                "*dreams of adventures*",
                "Wake me up later..."
            ],
            'happy': [
                "I'm so happy!", 
                "*excited bouncing*", 
                "Best day ever!", 
                "Yay!",
                "*happy dance*",
                "Life is wonderful!",
                "*radiates joy*",
                "Couldn't be happier!",
                "This is perfect!",
                "*beams with delight*",
                "So much happiness!",
                "I love everything right now!",
                "*jumps with excitement*",
                "Pure joy!",
                "This is what happiness feels like!"
            ],
            'sad': [
                "*sniffles*", 
                "I'm sad...", 
                "*sighs*", 
                "Need hugs...",
                "*sad face*",
                "Feeling blue...",
                "*droops sadly*",
                "Not having a good day...",
                "Could use some cheering up...",
                "*quiet whimper*",
                "Everything feels gray...",
                "Just want to be alone...",
                "*looks down sadly*",
                "Having a rough time...",
                "Need some comfort..."
            ],
            'hungry': [
                "I'm hungry!", 
                "Feed me please!", 
                "*stomach growls*", 
                "Need food...",
                "Starving!",
                "My tummy is empty!",
                "*looks at food bowl*",
                "Anything to eat?",
                "So hungry I could eat anything!",
                "*dramatic hunger pose*",
                "Food? Food? Food?",
                "Haven't eaten in forever!",
                "*dreams of snacks*",
                "My stomach is talking to me!",
                "Feed me or I'll waste away!"
            ],
            'sick': [
                "Not feeling well...", 
                "*coughs*", 
                "I need medicine...", 
                "*sneezes*",
                "I'm sick...",
                "Feeling awful...",
                "*weak voice*",
                "Need to get better...",
                "*shivers slightly*",
                "Under the weather...",
                "*looks pale*",
                "Could use some care...",
                "Feeling feverish...",
                "*groans softly*",
                "Just want to feel better..."
            ],
            'tired': [
                "*yawns*", 
                "So sleepy...", 
                "Need rest...", 
                "Can barely keep eyes open...",
                "Tired...",
                "*struggles to stay awake*",
                "Need a nap badly...",
                "Energy all gone...",
                "*droopy eyelids*",
                "Too exhausted...",
                "Just five minutes of rest...",
                "*slow movements*",
                "Running on empty...",
                "Need to recharge...",
                "No energy left..."
            ],
            'dirty': [
                "I need a bath!", 
                "*scratches*", 
                "Feeling icky...", 
                "Too dirty...",
                "Clean me please!",
                "*tries to clean self*",
                "Dirt everywhere...",
                "Need to be fresh again...",
                "*uncomfortable wiggle*",
                "Feeling grimy...",
                "Bath time, please?",
                "*looks at dirt with disgust*",
                "Can't stand being dirty!",
                "Need to be spotless again!",
                "*shakes off some dirt*"
            ],
            'lonely': [
                "I miss you...", 
                "Play with me?", 
                "*lonely sigh*", 
                "Need company...",
                "Where is everyone?",
                "Been alone too long...",
                "*looks around for friends*",
                "Feeling forgotten...",
                "Just want someone to talk to...",
                "*waits by the window*",
                "The silence is too much...",
                "Anyone there?",
                "*perks up at any sound*",
                "Loneliness hurts...",
                "Wish you were here..."
            ],
            'default': [
                "Hello!", 
                "*happy noises*", 
                "I'm here!", 
                "Notice me!",
                "Hi there!",
                "What's happening?",
                "*curious look*",
                "Good to see you!",
                "*friendly greeting*",
                "Hey friend!",
                "*waves excitedly*",
                "Ready for adventure!",
                "What shall we do today?",
                "*tilts head curiously*",
                "I've been waiting for you!"
            ]
        }
    
    def show_bubble(self, message_type, custom_message=None, use_typewriter=True):
        responses = self.responses.get(message_type, self.responses['default'])
        message = custom_message if custom_message else random.choice(responses)
        
        self.clear_bubble() # Always clear previous bubble before showing a new one
        
        if use_typewriter and len(message.split()) > 2:  # Use typewriter for longer messages
            self.show_typewriter_bubble(message)
        else:
            # Pass message_type as first parameter and message as second parameter
            self._create_bubble(message_type, message)
    
    def _create_bubble(self, message_type, message=None, use_typewriter=False, is_complete=True):
        # Clear any existing bubble before creating a new one
        self.clear_bubble()
        
        # Handle the case where message is None
        if message is None:
            message = message_type
        
        try:
            pet_x = self.parent.winfo_x() + self.parent.winfo_width() // 2 # Use parent's width for pet_x
            pet_y = self.parent.winfo_y() + 100
            
            # Store pet position for tail direction calculation
            self.pet_x = pet_x
            self.pet_y = pet_y
            
            self.bubble_window = tk.Toplevel(self.parent)
            
            self.bubble_window.overrideredirect(True)
            self.bubble_window.attributes('-topmost', True)
            self.bubble_window.attributes('-transparentcolor', 'white')
            
            self.bubble_window.configure(bg='white')
            
        except Exception as e:
            print(f"Error in _create_bubble setup: {e}")
            import traceback
            traceback.print_exc()
            return
        
        try:
            padding = 12
            
            # Calculate dynamic size based on message length
            temp_label = tk.Label(self.bubble_window, text=message, font=("Comic Sans MS", 11, "bold"), wraplength=250)
            temp_label.update_idletasks()
            
            text_width = temp_label.winfo_reqwidth()
            text_height = temp_label.winfo_reqheight()
            temp_label.destroy()
            
            # Dynamic sizing - grow with content but have reasonable limits
            min_width = 120
            max_width = 300
            bubble_width = max(min_width, min(text_width + padding * 2, max_width))
            bubble_height = max(40, text_height + padding * 2)
            
            canvas_width = bubble_width + 40
            canvas_height = bubble_height + 40
            
            bubble_canvas = tk.Canvas(
                self.bubble_window,
                width=canvas_width,
                height=canvas_height,
                bg='white',
                highlightthickness=0
            )
            bubble_canvas.pack()
            
            corner_radius = 15
            
            # Create bubble shape with rounded corners
            bubble_canvas.create_arc(15, 15, 15 + corner_radius*2, 15 + corner_radius*2,
                                    start=90, extent=90, fill="#FFFFCC", outline="#FFFFCC", width=0, style=tk.PIESLICE)
            bubble_canvas.create_arc(bubble_width + 15 - corner_radius*2, 15, bubble_width + 15, 15 + corner_radius*2,
                                    start=0, extent=90, fill="#FFFFCC", outline="#FFFFCC", width=0, style=tk.PIESLICE)
            bubble_canvas.create_arc(15, bubble_height + 15 - corner_radius*2, 15 + corner_radius*2, bubble_height + 15,
                                    start=180, extent=90, fill="#FFFFCC", outline="#FFFFCC", width=0, style=tk.PIESLICE)
            bubble_canvas.create_arc(bubble_width + 15 - corner_radius*2, bubble_height + 15 - corner_radius*2,
                                    bubble_width + 15, bubble_height + 15,
                                    start=270, extent=90, fill="#FFFFCC", outline="#FFFFCC", width=0, style=tk.PIESLICE)
            
            bubble_canvas.create_rectangle(15 + corner_radius, 15, bubble_width + 15 - corner_radius, 15 + corner_radius,
                                          fill="#FFFFCC", outline="#FFFFCC")
            bubble_canvas.create_rectangle(15 + corner_radius, bubble_height + 15 - corner_radius,
                                          bubble_width + 15 - corner_radius, bubble_height + 15,
                                          fill="#FFFFCC", outline="#FFFFCC")
            bubble_canvas.create_rectangle(15, 15 + corner_radius, 15 + corner_radius, bubble_height + 15 - corner_radius,
                                          fill="#FFFFCC", outline="#FFFFCC")
            bubble_canvas.create_rectangle(bubble_width + 15 - corner_radius, 15 + corner_radius,
                                          bubble_width + 15, bubble_height + 15 - corner_radius,
                                          fill="#FFFFCC", outline="#FFFFCC")
            bubble_canvas.create_rectangle(15 + corner_radius, 15 + corner_radius,
                                          bubble_width + 15 - corner_radius, bubble_height + 15 - corner_radius,
                                          fill="#FFFFCC", outline="#FFFFCC")
            
            border_points = [
                15 + corner_radius, 15,
                bubble_width + 15 - corner_radius, 15,
                bubble_width + 15, 15 + corner_radius,
                bubble_width + 15, bubble_height + 15 - corner_radius,
                bubble_width + 15 - corner_radius, bubble_height + 15,
                15 + corner_radius, bubble_height + 15,
                15, bubble_height + 15 - corner_radius,
                15, 15 + corner_radius,
                15 + corner_radius, 15
            ]
            
            bubble_canvas.create_polygon(border_points, fill="#FFFFCC", outline="", width=0)
            
            # Store canvas reference and dimensions for tail creation
            self.bubble_canvas = bubble_canvas
            self.bubble_width = bubble_width
            self.bubble_height = bubble_height
            self.canvas_width = canvas_width
            self.canvas_height = canvas_height
            
            # Create tail - will be positioned correctly in _update_bubble_position
            self._create_bubble_tail()
            
            self._update_bubble_position(canvas_width, canvas_height)
            
            self._start_position_updates(canvas_width, canvas_height)
            
            # Store text widget reference for typewriter updates
            self.bubble_text_id = bubble_canvas.create_text(
                (bubble_width + 30) // 2,
                (bubble_height + 30) // 2,
                text=message,
                font=("Comic Sans MS", 11, "bold"),
                fill="black",
                width=bubble_width - padding,
                justify=tk.CENTER,
                anchor="center"
            )
            
            # Set display duration - longer for typewriter effect or longer messages
            if use_typewriter:
                # For typewriter effects, use a longer base duration since text appears gradually
                display_time = max(8000, len(message) * 150)  # Increased base time for typewriter
            else:
                display_time = max(self.bubble_duration, len(message) * 100)
            
            # Only set auto-clear timer if this is a complete message (not mid-typewriter)
            if not use_typewriter or is_complete:
                self._bubble_timer = self.parent.after(display_time, self.clear_bubble)
            
            # Force window to show and update
            self.bubble_window.update_idletasks()
            self.bubble_window.deiconify()
            # Force window to show and update (add after the existing deiconify line)
            self.bubble_window.update_idletasks()
            self.bubble_window.deiconify()
            self.bubble_window.lift()  # Bring to front
            self.bubble_window.focus_force()  # Force focus
            self.bubble_window.attributes('-topmost', True)  # Ensure it stays on top
            
        except Exception as e:
            print(f"Error creating speech bubble: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_bubble_position(self, canvas_width, canvas_height):
        if not self.bubble_window:
            return
            
        pet_x = self.parent.winfo_x() + self.canvas.winfo_width() // 2
        pet_y = self.parent.winfo_y() + 100
        
        # Calculate ideal bubble position (above pet)
        bubble_x = pet_x - canvas_width // 2
        bubble_y = pet_y - canvas_height - 10  # 10px gap between pet and bubble
        
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # Adjust horizontal position to stay on screen
        if bubble_x < 0:
            bubble_x = 0
        elif bubble_x + canvas_width > screen_width:
            bubble_x = screen_width - canvas_width
        
        # Check if bubble would be cut off at the top
        if bubble_y < 0:
            # Not enough space above pet - place bubble below pet instead
            bubble_y = pet_y + 50  # Place below pet with upward-pointing tail
        
        # Determine if bubble is above or below pet
        bubble_window_y = bubble_y
        is_below_pet = bubble_window_y > pet_y
        
        # Only update tail direction if position actually changed
        current_position = (bubble_x, bubble_y, is_below_pet)
        if not self._bubble_positioned or self._last_bubble_position != current_position:
            self._update_bubble_tail(is_below_pet)
            self._last_bubble_position = current_position
            self._bubble_positioned = True
        
        self.bubble_window.geometry(f"+{bubble_x}+{bubble_y}")
    
    def _adjust_pet_position_for_bubble(self, new_y):
        """Naturally move the pet down to accommodate speech bubble using normal movement speed"""
        if not hasattr(self.parent, 'winfo_exists') or not self.parent.winfo_exists():
            return
            
        current_x = self.parent.winfo_x()
        current_y = self.parent.winfo_y()
        
        # Only move if the adjustment is reasonable (not too far) and pet isn't already moving
        if abs(new_y - current_y) < 150:  # Max 150px adjustment
            
            # Double-check that pet isn't moving before we start our own movement
            if (hasattr(self.parent, 'pet_manager') and 
                hasattr(self.parent.pet_manager, 'pet_state') and 
                self.parent.pet_manager.pet_state.is_interacting):
                print("DEBUG: Pet became busy during bubble positioning, aborting movement")
                return
            # Try to use the pet's animation system for natural movement
            if hasattr(self.parent, 'pet_manager') and hasattr(self.parent.pet_manager, 'pet_animation'):
                pet_animation = self.parent.pet_manager.pet_animation
                pet_state = self.parent.pet_manager.pet_state
                settings = self.parent.pet_manager.settings
                
                print("DEBUG: Using pet's natural movement system for bubble positioning")
                
                # Pause current movement
                pet_animation.pause_movement()
                
                # Set target position (keep same X, move to new Y)
                pet_animation.target_x = current_x
                pet_animation.target_y = new_y
                
                # Set walking animation and direction (no direction change needed for vertical movement)
                pet_state.current_animation = 'Walking'
                
                # Start natural movement
                pet_animation.move_step()
                
                # Schedule resuming normal behavior after reaching position
                def check_arrival():
                    if not self.parent.winfo_exists():
                        return
                        
                    curr_y = self.parent.winfo_y()
                    distance = abs(new_y - curr_y)
                    
                    if distance < 10:  # Close enough
                        print("DEBUG: Natural bubble positioning movement completed")
                        pet_state.current_animation = 'Standing'
                        pet_animation.schedule_resume_movement(1000)  # Resume after 1 second
                        # Reset repositioning flag when movement is complete
                        if hasattr(self.parent, 'pet_manager') and hasattr(self.parent.pet_manager, 'speech_bubble'):
                            self.parent.pet_manager.speech_bubble._repositioning_pet = False
                    else:
                        # Check again
                        self.parent.after(200, check_arrival)
                
                self.parent.after(500, check_arrival)
                
            else:
                # Fallback to slower, more natural movement
                print("DEBUG: Using fallback natural movement for bubble positioning")
                
                # Use much slower movement that mimics normal pet speed
                total_distance = abs(new_y - current_y)
                # Simulate normal pet movement speed (similar to pet_animation.py)
                speed = 5  # Default movement speed
                step_size = speed * 0.5
                steps = int(total_distance / step_size)
                steps = max(steps, 10)  # Minimum steps for smoothness
                
                step_y = (new_y - current_y) / steps
                
                def move_step(step):
                    if step >= steps or not self.parent.winfo_exists():
                        self.parent.geometry(f'+{current_x}+{new_y}')
                        return
                    
                    intermediate_y = int(current_y + step_y * step)
                    self.parent.geometry(f'+{current_x}+{intermediate_y}')
                    # Use same timing as normal pet movement (50ms)
                    self.parent.after(50, lambda: move_step(step + 1))
                
                move_step(1)
    
    def _start_position_updates(self, canvas_width, canvas_height):
        if self._update_position_timer:
            self.parent.after_cancel(self._update_position_timer)
        
        def update_loop():
            if self.bubble_window:
                self._update_bubble_position(canvas_width, canvas_height)
                self._update_position_timer = self.parent.after(50, update_loop)
        
        self._update_position_timer = self.parent.after(50, update_loop)
    
    def _update_bubble_text(self, new_text, is_complete=False):
        """Update the text in an existing bubble (for typewriter effect)"""
        if not self.bubble_window or not hasattr(self, 'bubble_canvas') or not hasattr(self, 'bubble_text_id'):
            return
        
        try:
            # Update the text
            self.bubble_canvas.itemconfig(self.bubble_text_id, text=new_text)
            
            # If typing is complete, set a timer to clear the bubble
            if is_complete:
                display_time = max(self.bubble_duration, len(new_text) * 100)
                self._bubble_timer = self.parent.after(display_time, self.clear_bubble)
        except tk.TclError:
            # Bubble was destroyed, ignore
            pass
    
    def show_typewriter_bubble(self, text, is_complete=False):
        """Show a speech bubble with typewriter effect (for AI chat)"""
        if is_complete:
            # If the message is complete, just show it normally
            self._create_bubble('ai_response', message=text, use_typewriter=True, is_complete=True)
        else:
            # Start the typewriter animation
            self._start_typewriter_animation(text)
    
    def _start_typewriter_animation(self, full_text):
        """Start word-by-word typewriter animation"""
        if not full_text or not full_text.strip():
            return
        
        self.clear_bubble()  # Clear any existing bubble
        
        # Create initial bubble with empty text
        self._create_bubble("", message="", use_typewriter=True, is_complete=False)
        
        words = full_text.split()
        self.typewriter_words = words
        self.typewriter_current_text = ""
        self.typewriter_index = 0
        self.typewriter_timer = None
        
        # Start the animation
        self._typewriter_next_word()
    
    def _typewriter_next_word(self):
        """Add the next word to the bubble"""
        if not hasattr(self, 'typewriter_words') or not self.bubble_window:
            return
            
        if self.typewriter_index < len(self.typewriter_words):
            # Add next word
            if self.typewriter_current_text:
                self.typewriter_current_text += " "
            self.typewriter_current_text += self.typewriter_words[self.typewriter_index]
            
            # Update the bubble text
            self._update_bubble_text(self.typewriter_current_text, is_complete=False)
            
            self.typewriter_index += 1
            
            # Calculate delay - longer after punctuation
            current_word = self.typewriter_words[self.typewriter_index - 1]
            delay = 400 if current_word.endswith(('.', '!', '?')) else 200
            
            # Schedule next word
            self.typewriter_timer = self.parent.after(delay, self._typewriter_next_word)
        else:
            # Animation complete
            self._update_bubble_text(self.typewriter_current_text, is_complete=True)
            self._cleanup_typewriter()
    
    def _cleanup_typewriter(self):
        """Clean up typewriter animation state"""
        if hasattr(self, 'typewriter_timer') and self.typewriter_timer:
            self.parent.after_cancel(self.typewriter_timer)
            self.typewriter_timer = None
        
        # Clean up animation state
        if hasattr(self, 'typewriter_words'):
            del self.typewriter_words
        if hasattr(self, 'typewriter_current_text'):
            del self.typewriter_current_text
        if hasattr(self, 'typewriter_index'):
            del self.typewriter_index
    
    def show_dynamic_typewriter_bubble(self, text, is_complete=False):
        """Show a speech bubble that dynamically resizes as text appears"""
        # Clear existing bubble and create new one with current text
        self.clear_bubble()
        self._create_bubble(text, is_typewriter=False, is_complete=is_complete)
    
    def clear_bubble(self):
        if self._bubble_timer:
            self.parent.after_cancel(self._bubble_timer)
            self._bubble_timer = None
            
        if self._update_position_timer:
            self.parent.after_cancel(self._update_position_timer)
            self._update_position_timer = None
        
        # Clean up typewriter animation
        self._cleanup_typewriter()
        
        if self.bubble_window:
            self.bubble_window.destroy()
            self.bubble_window = None
            
        # Reset repositioning flag when bubble is cleared
        self._repositioning_pet = False
        self._bubble_positioned = False
        self._last_bubble_position = None
    
    def _create_bubble_tail(self):
        """Create the initial bubble tail (pointing down by default)"""
        if not hasattr(self, 'bubble_canvas'):
            return
            
        # Create tail pointing down (default)
        tail_points = [
            (self.bubble_width + 15) // 2 + 5, self.bubble_height + 30,
            (self.bubble_width + 15) // 2 - 5, self.bubble_height + 15,
            (self.bubble_width + 15) // 2 + 15, self.bubble_height + 15
        ]
        
        self.bubble_tail_id = self.bubble_canvas.create_polygon(
            tail_points,
            fill="#FFFFCC",
            outline="",
            width=0,
            tags="bubble_tail"
        )
    
    def _update_bubble_tail(self, is_below_pet):
        """Update the bubble tail direction based on bubble position relative to pet"""
        if not hasattr(self, 'bubble_canvas') or not hasattr(self, 'bubble_tail_id'):
            return
            
        try:
            # Delete existing tail
            self.bubble_canvas.delete(self.bubble_tail_id)
            
            if is_below_pet:
                # Bubble is below pet - tail should point up (triangle pointing upward)
                tail_points = [
                    (self.bubble_width + 15) // 2, 0,        # Top point (pointing up)
                    (self.bubble_width + 15) // 2 - 10, 15,  # Bottom left
                    (self.bubble_width + 15) // 2 + 10, 15   # Bottom right
                ]
            else:
                # Bubble is above pet - tail should point down (default)
                tail_points = [
                    (self.bubble_width + 15) // 2 + 5, self.bubble_height + 30,  # Bottom point
                    (self.bubble_width + 15) // 2 - 5, self.bubble_height + 15,  # Top left
                    (self.bubble_width + 15) // 2 + 15, self.bubble_height + 15  # Top right
                ]
            
            # Create new tail with correct direction
            self.bubble_tail_id = self.bubble_canvas.create_polygon(
                tail_points,
                fill="#FFFFCC",
                outline="",
                width=0,
                tags="bubble_tail"
            )
        except tk.TclError:
            # Canvas was destroyed, ignore
            pass