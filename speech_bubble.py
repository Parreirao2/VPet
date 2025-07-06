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
    
    def show_bubble(self, message_type, custom_message=None):
        responses = self.responses.get(message_type, self.responses['default'])
        
        message = custom_message if custom_message else random.choice(responses)
        
        self._create_bubble(message)
    
    def _create_bubble(self, message, is_typewriter=False, is_complete=False):
        # Only clear bubble if this is not a typewriter update
        if not is_typewriter:
            self.clear_bubble()
        elif self.bubble_window:
            # For typewriter effect, just update the existing bubble
            self._update_bubble_text(message, is_complete)
            return
        
        pet_x = self.parent.winfo_x() + self.canvas.winfo_width() // 2
        pet_y = self.parent.winfo_y() + 100
        
        self.bubble_window = tk.Toplevel(self.parent)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.attributes('-topmost', True)
        self.bubble_window.attributes('-transparentcolor', 'white')
        
        self.bubble_window.configure(bg='white')
        
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
        
        tail_points = [
            (bubble_width + 15) // 2 + 5, bubble_height + 30,
            (bubble_width + 15) // 2 - 5, bubble_height + 15,
            (bubble_width + 15) // 2 + 15, bubble_height + 15
        ]
        bubble_canvas.create_polygon(
            tail_points,
            fill="#FFFFCC",
            outline="",
            width=0
        )
        
        # This will be replaced by the stored text reference below
        
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
        
        # Store canvas reference for updates
        self.bubble_canvas = bubble_canvas
        
        # Set display duration - longer for typewriter effect or longer messages
        if is_typewriter and not is_complete:
            # Don't auto-clear during typewriter effect
            pass
        else:
            display_time = max(self.bubble_duration, len(message) * 100)
            self._bubble_timer = self.parent.after(display_time, self.clear_bubble)
    
    def _update_bubble_position(self, canvas_width, canvas_height):
        if not self.bubble_window:
            return
            
        pet_x = self.parent.winfo_x() + self.canvas.winfo_width() // 2
        pet_y = self.parent.winfo_y() + 100
        
        bubble_x = max(0, pet_x - canvas_width // 2)
        bubble_y = max(0, pet_y - canvas_height)
        
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        if bubble_x + canvas_width > screen_width:
            bubble_x = screen_width - canvas_width
        if bubble_y < 0:
            bubble_y = 0
        
        self.bubble_window.geometry(f"+{bubble_x}+{bubble_y}")
    
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
        self._create_bubble(text, is_typewriter=True, is_complete=is_complete)
    
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
        
        if self.bubble_window:
            self.bubble_window.destroy()
            self.bubble_window = None