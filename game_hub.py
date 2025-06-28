import tkinter as tk
from tkinter import ttk
import random
import time

class NumberGuesserGame:
    def __init__(self, parent, currency_system):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.guesses_left = 3
        self.currency_system = currency_system
        self.last_guess = None  # Track the last guess for hints
        self.setup_ui()

    def setup_ui(self):
        self.target_number = random.randint(1, 10)
        
        # Create game title with improved styling
        self.title_label = ttk.Label(self.frame, text="Number Guesser", font=("Arial", 16, "bold"), foreground="#2196F3")
        self.title_label.pack(pady=(10, 5))
        
        # Create reward display with coin icon and improved styling
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
        
        # Calculate current reward
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        
        # Try to load currency icon
        self.currency_icon = None
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((16, 16), Image.LANCZOS)
                self.currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading currency icon: {e}")
        
        # Create reward label with icon
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        
        # Create game container with border and improved styling
        self.game_container = ttk.Frame(self.frame, padding=15, relief="groove")
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Level and instruction label with improved styling
        self.info_label = ttk.Label(self.game_container, 
                                   text=f"Level {self.level}\nGuess a number between 1-{10 + (self.level-1)}",
                                   font=("Arial", 12),
                                   justify="center",
                                   foreground="#333333")
        self.info_label.pack(pady=10)
        
        # Hint label with improved styling
        self.hint_label = ttk.Label(self.game_container, text="", font=("Arial", 11, "italic"), foreground="#1976D2")
        self.hint_label.pack(pady=8)
        
        # Input frame
        self.input_frame = ttk.Frame(self.game_container)
        self.input_frame.pack(pady=10)
        
        # Entry and button side by side with improved styling
        self.entry = ttk.Entry(self.input_frame, width=10, font=("Arial", 12))
        self.entry.pack(side='left', padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.check_guess())  # Allow Enter key to submit
        
        # Custom styled button
        self.guess_button = tk.Button(self.input_frame, 
                                   text="Guess", 
                                   command=self.check_guess,
                                   font=("Arial", 11, "bold"),
                                   bg="#4CAF50",
                                   fg="white",
                                   padx=10,
                                   pady=2,
                                   relief=tk.RAISED,
                                   borderwidth=2)
        self.guess_button.pack(side='left')
        
        # Set focus on entry
        self.entry.focus()

    def check_guess(self):
        try:
            guess = int(self.entry.get())
            max_number = 10 + (self.level - 1)
            
            # Clear the entry field
            self.entry.delete(0, 'end')
            
            # Store the current guess for comparison
            self.last_guess = guess
            
            if guess == self.target_number:
                # Success animation/feedback
                self.hint_label.config(text="Correct! 🎉", foreground="green")
                
                # Calculate reward based on level batches
                batch_number = (self.level - 1) // 3
                base_reward = 1 + 2 * batch_number
                self.currency_system.add_currency(base_reward)
                
                # Level progression
                self.level += 1
                self.guesses_left = 3 + ((self.level - 1) // 5)
                max_number = 10 + (self.level - 1)
                self.target_number = random.randint(1, max_number)
                
                # Update UI
                self.info_label.config(text=f"Level {self.level}\nGuess 1-{max_number} ({self.guesses_left} guesses)")
                
                # Update reward display
                new_batch_number = (self.level - 1) // 3
                new_base_reward = 1 + 2 * new_batch_number
                self.reward_label.config(text=f"Reward: {new_base_reward} coins")
                
                # Clear hint after a delay
                self.frame.after(1500, lambda: self.hint_label.config(text=""))
            else:
                # Provide hint
                hint = "Higher ⬆️" if guess < self.target_number else "Lower ⬇️"
                self.hint_label.config(text=hint, foreground="blue")
                
                # Decrease guesses
                self.guesses_left -= 1
                
                if self.guesses_left <= 0:
                    # Game over
                    self.hint_label.config(text=f"The number was {self.target_number}", foreground="red")
                    batch_number = (self.level - 1) // 5
                    self.level = batch_number * 5 + 1
                    self.guesses_left = 3 + batch_number
                    max_number = 10 + (self.level - 1)
                    self.target_number = random.randint(1, max_number)
                    
                    # Update UI with delay to show the correct number first
                    self.frame.after(2000, lambda: self.info_label.config(
                        text=f"Game Over! Restarting at Level {self.level}\nGuess 1-{max_number} ({self.guesses_left} guesses)"))
                    
                    # Update reward display
                    new_batch_number = (self.level - 1) // 3
                    new_base_reward = 1 + 2 * new_batch_number
                    self.reward_label.config(text=f"Reward: {new_base_reward} coins")
                    
                    # Clear hint after a delay
                    self.frame.after(2000, lambda: self.hint_label.config(text=""))
                else:
                    # Update remaining guesses
                    self.info_label.config(text=f"Guesses left: {self.guesses_left}\nLevel {self.level} (1-{max_number})")
            
            # Set focus back to entry
            self.entry.focus()
            
        except ValueError:
            self.hint_label.config(text="Please enter a valid number!", foreground="red")
            self.entry.delete(0, 'end')
            self.entry.focus()

class ReactionTestGame:
    def __init__(self, parent, currency_system):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.currency_system = currency_system
        self.waiting = False
        self.ready_to_click = False
        self.setup_ui()

    def setup_ui(self):
        # Create game title
        self.title_label = ttk.Label(self.frame, text="Reaction Test", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=(10, 5))
        
        # Create reward display with coin icon
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
        
        # Calculate current reward
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        
        # Try to load currency icon
        self.currency_icon = None
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((16, 16), Image.LANCZOS)
                self.currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading currency icon: {e}")
        
        # Create reward label with icon
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        
        # Create game container
        self.game_container = ttk.Frame(self.frame, padding=10)
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create reaction button - using tk.Button instead of ttk.Button for better styling
        self.reaction_button = tk.Button(
            self.game_container, 
            text="Start Test", 
            command=self.start_test,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",  # Green background
            fg="white",    # White text
            width=15,
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.reaction_button.pack(pady=20)
        
        # Status and timer labels
        self.status_label = ttk.Label(self.game_container, 
                                     text="Press the button to start!", 
                                     font=("Arial", 11),
                                     justify="center",
                                     foreground="#333333")
        self.status_label.pack(pady=10)
        
        # Timer frame to hold both current and goal time
        self.timer_frame = ttk.Frame(self.game_container)
        self.timer_frame.pack(pady=5)
        
        self.timer_label = ttk.Label(self.timer_frame, 
                                    text="Time: 0.00s", 
                                    font=("Arial", 12, "bold"),
                                    foreground="#1976D2")
        self.timer_label.pack(side='left', padx=5)
        
        self.goal_label = ttk.Label(self.timer_frame,
                                   text=f"Goal: {max(0.3, 3.0 - (self.level * 0.1)):.2f}s",
                                   font=("Arial", 12),
                                   foreground="#4CAF50")
        self.goal_label.pack(side='left', padx=5)
        
        # Level indicator with custom style
        self.level_label = ttk.Label(self.game_container, 
                                   text=f"Level: {self.level}", 
                                   font=("Arial", 11, "bold"),
                                   foreground="#673AB7")
        self.level_label.pack(pady=10)

    def start_test(self):
        if self.waiting or self.ready_to_click:
            return  # Prevent multiple clicks during test
            
        self.waiting = True
        self.ready_to_click = False
        
        # Change button appearance to waiting state
        self.reaction_button.config(
            text="Wait...",
            bg="#FFC107",  # Amber/yellow for waiting
            command=self.too_early
        )
        
        self.status_label.config(text="Wait for the button to turn red...")
        self.timer_label.config(text="Time: 0.00s")
        
        # Random delay between 1-3 seconds
        wait_time = random.randint(1000, 3000)
        self.frame.after(wait_time, self.enable_button)

    def too_early(self):
        """Called if user clicks button too early"""
        if not self.ready_to_click and self.waiting:
            self.waiting = False
            self.status_label.config(text="Too early! Try again", foreground="red")
            
            # Reset button
            self.reaction_button.config(
                text="Start Test",
                bg="#4CAF50",  # Green
                command=self.start_test
            )
            
            # Reset text color after delay
            self.frame.after(1500, lambda: self.status_label.config(foreground="black"))

    def enable_button(self):
        if not self.waiting:  # If user already clicked too early
            return
            
        self.start_time = time.time()
        self.waiting = False
        self.ready_to_click = True
        
        # Change button appearance to "click now" state
        self.reaction_button.config(
            text="CLICK NOW!",
            bg="#F44336",  # Red for action
            command=self.react
        )
        
        self.status_label.config(text="Click the button NOW!", foreground="red")
        
        # Start the timer display update
        self.update_timer_display()

    def update_timer_display(self):
        """Update the timer display while waiting for click"""
        if self.ready_to_click:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {elapsed:.2f}s")
            self.frame.after(10, self.update_timer_display)  # Update every 10ms for smooth display

    def react(self):
        if not self.ready_to_click:  # Safety check
            return
            
        self.ready_to_click = False
        reaction_time = time.time() - self.start_time
        time_limit = max(0.3, 3.0 - (self.level * 0.1))
        
        # Calculate time difference from limit for feedback
        time_diff = time_limit - reaction_time
        
        if reaction_time <= time_limit:
            # Success!
            base_reward = 1 + 2 * ((self.level - 1) // 3)
            self.currency_system.add_currency(base_reward)
            self.level += 1
            
            # Feedback based on how fast they were
            if time_diff > 0.5:
                feedback = "Amazing speed! 🚀"
            elif time_diff > 0.2:
                feedback = "Great reaction! ⚡"
            else:
                feedback = "Just in time! ✅"
                
            self.status_label.config(text=f"{feedback}", foreground="#4CAF50")
            
            # Update reward display
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level: {self.level}")
            
            # Update goal time display for next level
            new_time_limit = max(0.3, 3.0 - (self.level * 0.1))
            self.goal_label.config(text=f"Goal: {new_time_limit:.2f}s")
        else:
            # Too slow
            self.level = max(1, self.level - 1)
            self.status_label.config(
                text=f"Too slow by {abs(time_diff):.2f}s! Try again", 
                foreground="#F44336"
            )
            
            # Update reward display
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level: {self.level}")
            
            # Update goal time display
            new_time_limit = max(0.3, 3.0 - (self.level * 0.1))
            self.goal_label.config(text=f"Goal: {new_time_limit:.2f}s")
        
        # Reset button
        self.reaction_button.config(
            text="Start Test",
            bg="#4CAF50",  # Green
            command=self.start_test
        )
        
        # Display final time
        self.timer_label.config(text=f"Time: {reaction_time:.3f}s")
        
        # Reset status label color after delay
        self.frame.after(2000, lambda: self.status_label.config(
            text="Press the button to start!",
            foreground="#333333"
        ))

class BallClickerGame:
    def __init__(self, parent, currency_system):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.score = 0
        self.currency_system = currency_system
        self.game_running = False
        self.balls = []
        self.black_balls_clicked = 0
        self.required_clicks = 5  # Base number of required clicks
        self.ball_spawn_timer = None
        self.setup_ui()
        
        # Force the parent window to resize to fit the game
        self.frame.update_idletasks()
        parent_window = self.frame.winfo_toplevel()
        parent_window.geometry(f"600x850")  # Increased height to ensure all elements are visible
        parent_window.minsize(600, 850)  # Increased minimum size to prevent resizing smaller
        parent_window.update_idletasks()
        
        # Schedule multiple size checks to ensure proper sizing
        self.frame.after(100, self._ensure_window_size)
        self.frame.after(500, self._ensure_window_size)  # Additional check after half second
        self.frame.after(1000, self._ensure_window_size)  # Final check after a second

    def _ensure_window_size(self):
        """Ensure the window is large enough to display all components"""
        parent_window = self.frame.winfo_toplevel()
        
        # Set fixed size that we know works for all components
        parent_window.geometry("600x850")
        parent_window.minsize(600, 850)  # Enforce minimum size
        parent_window.update_idletasks()
        
        # Check if start button is visible, if not force another resize
        if hasattr(self, 'start_button') and not self.start_button.winfo_viewable():
            parent_window.geometry("650x900")  # Try even larger size if button not visible
            parent_window.update_idletasks()
    
    def setup_ui(self):
        # Create game title with improved styling
        self.title_label = ttk.Label(self.frame, text="Ball Clicker", font=("Arial", 16, "bold"), foreground="#2196F3")
        self.title_label.pack(pady=(10, 5))
        
        # Create reward display with coin icon and improved styling
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
        
        # Calculate current reward
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        
        # Try to load currency icon
        self.currency_icon = None
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((16, 16), Image.LANCZOS)
                self.currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading currency icon: {e}")
        
        # Create reward label with icon
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        
        # Game container with improved styling - INCREASED SIZE
        self.game_container = ttk.Frame(self.frame, padding=15, relief="groove")
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Info frame for score and timer with improved styling
        self.info_frame = ttk.Frame(self.game_container)
        self.info_frame.pack(fill='x', pady=(0, 10))
        
        # Score and progress labels with improved styling
        self.score_label = ttk.Label(self.info_frame, 
                                   text=f"Score: {self.score}", 
                                   font=("Arial", 12, "bold"),
                                   foreground="#1976D2")
        self.score_label.pack(side='left', padx=10)
        
        self.progress_label = ttk.Label(self.info_frame, 
                                      text=f"Clicks: 0/{self.required_clicks}", 
                                      font=("Arial", 12),
                                      foreground="#4CAF50")
        self.progress_label.pack(side='right', padx=10)
        
        # Timer and level labels with improved styling
        self.timer_label = ttk.Label(self.game_container, 
                                   text="Time: 0.00s", 
                                   font=("Arial", 12),
                                   foreground="#FF9800")
        self.timer_label.pack(pady=5)
        
        self.level_label = ttk.Label(self.game_container, 
                                    text=f"Level {self.level}", 
                                    font=("Arial", 11, "bold"),
                                    foreground="#673AB7")
        self.level_label.pack(pady=5)
        
        # Canvas for the game with proper expansion settings - INCREASED SIZE
        self.canvas_frame = ttk.Frame(self.game_container)
        self.canvas_frame.pack(pady=10, expand=True, fill='both')
        
        # Make sure the frame expands properly
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        # Canvas with proper expansion settings - INCREASED SIZE
        self.canvas = tk.Canvas(self.canvas_frame, 
                              width=450, 
                              height=400, 
                              bg='#f5f5f5',
                              relief=tk.SUNKEN,
                              bd=2)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Make sure the canvas expands with the window
        self.game_container.pack_propagate(False)
        
        # Ensure the canvas frame has a minimum size - INCREASED SIZE
        self.canvas_frame.config(width=450, height=400)
        self.canvas_frame.grid_propagate(False)
        
        # Set a minimum size for the game container to ensure all elements fit - INCREASED SIZE
        self.game_container.config(width=500, height=600)
        
        # Start button with improved styling - ENSURE VISIBILITY
        self.start_button = tk.Button(self.game_container, 
                                    text="Start Round", 
                                    command=self.start_round,
                                    font=("Arial", 12, "bold"),
                                    bg="#4CAF50",
                                    fg="white",
                                    width=15,
                                    height=2,
                                    relief=tk.RAISED,
                                    borderwidth=2)
        self.start_button.pack(pady=15)

    def start_round(self):
        if self.game_running:
            return
            
        # Reset game state
        self.game_running = True
        self.score = 0
        self.black_balls_clicked = 0
        self.balls = []
        self.canvas.delete('all')
        
        # Update UI
        self.score_label.config(text=f"Score: {self.score}")
        self.progress_label.config(text=f"Clicks: {self.black_balls_clicked}/{self.required_clicks}")
        self.start_button.config(state='disabled')
        
        # Set up round parameters
        self.start_time = time.time()
        # Adjust round duration to be more generous at higher levels
        self.round_duration = max(8.0, 15.0 - (self.level * 0.3))
        
        # Track the number of black balls spawned to ensure enough are available
        self.black_balls_spawned = 0
        self.min_black_balls_needed = self.required_clicks * 2  # Ensure at least twice the required clicks
        
        # Start ball spawning
        self.spawn_ball()
        self.update_timer()

    def spawn_ball(self):
        """Spawn a new ball if the game is still running"""
        if not self.game_running:
            return
            
        # Calculate probabilities based on level - make it more balanced
        red_probability = min(0.2 + (self.level * 0.01), 0.4)  # Reduced red ball probability
        
        # Force black ball if we haven't spawned enough to complete the level
        # and we're more than halfway through the round
        elapsed = time.time() - self.start_time
        force_black = (self.black_balls_spawned < self.min_black_balls_needed and 
                      elapsed > (self.round_duration * 0.5))
        
        # Create new ball
        x = random.randint(20, 380)
        y = random.randint(20, 280)  # Adjusted for canvas height
        
        # Determine ball color with adjusted probability
        is_red = random.random() < red_probability and not force_black
        color = 'red' if is_red else 'black'
        
        # Track black balls spawned
        if color == 'black':
            self.black_balls_spawned += 1
        
        # Create ball with gradient effect
        ball = self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                     fill=color,
                                     outline='white' if is_red else 'gray',
                                     width=2)
        
        # Bind click event
        self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball, c=color: self.handle_click(b, c))
        self.balls.append(ball)
        
        # Set ball removal timer - longer for black balls, shorter for red balls
        removal_time = random.randint(2000, 3000) if not is_red else random.randint(1500, 2500)
        self.canvas.after(removal_time, lambda b=ball: self.remove_ball(b))
        
        # Schedule next ball spawn - faster spawning at higher levels
        spawn_delay = max(300, random.randint(400, 1200) - (self.level * 10))
        self.ball_spawn_timer = self.frame.after(spawn_delay, self.spawn_ball)

    def remove_ball(self, ball):
        """Safely remove a ball from the canvas"""
        if ball in self.balls:
            self.balls.remove(ball)
            self.canvas.delete(ball)

    def handle_click(self, ball, color):
        """Handle ball click events"""
        if not self.game_running or ball not in self.balls:
            return
            
        # Remove the clicked ball
        self.remove_ball(ball)
        
        if color == 'black':
            self.score += 1
            self.black_balls_clicked += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.progress_label.config(text=f"Clicks: {self.black_balls_clicked}/{self.required_clicks}")
            
            # Check if level complete
            if self.black_balls_clicked >= self.required_clicks:
                self.end_round(True)
        else:
            # Penalty for clicking red ball
            self.score = max(0, self.score - 2)
            self.score_label.config(text=f"Score: {self.score}")

    def update_timer(self):
        """Update the timer display and check for time-out"""
        if not self.game_running:
            return
            
        elapsed = time.time() - self.start_time
        self.timer_label.config(text=f"Time: {elapsed:.2f}s")
        
        # Calculate the expected rate of black balls needed per second
        remaining_time = self.round_duration - elapsed
        if remaining_time > 0:
            # Calculate how many more black balls we need
            balls_needed = self.min_black_balls_needed - self.black_balls_spawned
            
            # Calculate the expected rate (balls per second) needed to meet the target
            expected_rate = balls_needed / remaining_time if remaining_time > 0 else 0
            
            # If we're behind schedule and need to catch up (but not in the last 3 seconds)
            if expected_rate > 1.5 and balls_needed > 0 and remaining_time > 3.0:
                # Spawn a single black ball to help catch up gradually
                x = random.randint(20, 380)
                y = random.randint(20, 280)
                ball = self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                           fill='black',
                                           outline='gray',
                                           width=2)
                self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball: self.handle_click(b, 'black'))
                self.balls.append(ball)
                self.black_balls_spawned += 1
                
                # Set a reasonable removal time for these catch-up balls
                self.canvas.after(3000, lambda b=ball: self.remove_ball(b))
            
            # Only in critical situations (last 3 seconds) and if severely behind, it adds a single emergency ball
            elif remaining_time < 3.0 and balls_needed > 3:
                # Emergency spawn of a single black ball if we're running out of time
                x = random.randint(20, 380)
                y = random.randint(20, 280)
                ball = self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                           fill='black',
                                           outline='gray',
                                           width=2)
                self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball: self.handle_click(b, 'black'))
                self.balls.append(ball)
                self.black_balls_spawned += 1
                
                # Set a longer removal time for these emergency balls
                self.canvas.after(4000, lambda b=ball: self.remove_ball(b))
        
        if elapsed < self.round_duration:
            self.frame.after(50, self.update_timer)
        else:
            self.end_round(False)

    def end_round(self, success=False):
        """End the current round and update game state"""
        self.game_running = False
        
        # Stop ball spawning
        if self.ball_spawn_timer:
            self.frame.after_cancel(self.ball_spawn_timer)
        
        # Clear canvas
        self.canvas.delete('all')
        
        # Calculate rewards and update level
        base_reward = 1 + 2 * ((self.level - 1) // 3)
        
        # Display round result on canvas
        if success:
            # Success - level up and reward
            self.currency_system.add_currency(base_reward)
            self.level += 1
            self.required_clicks = 5 + self.level  # Increase required clicks
            
            # Display success message
            self.canvas.create_text(200, 150, 
                                  text=f"Level Complete! +{base_reward} coins", 
                                  font=("Arial", 14, "bold"), 
                                  fill="green")
            
            # Update reward display
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level {self.level}")
            
            # Update button
            self.start_button.config(
                text=f"Start Level {self.level}",
                state='normal',
                bg="#4CAF50"
            )
        else:
            # Time ran out - check if enough balls were clicked
            if self.black_balls_clicked >= self.required_clicks // 2:
                # Partial success - give half reward
                half_reward = max(1, base_reward // 2)
                self.currency_system.add_currency(half_reward)
                
                self.canvas.create_text(200, 150, 
                                      text=f"Time's up! +{half_reward} coins", 
                                      font=("Arial", 14), 
                                      fill="orange")
            else:
                # Failure - level down
                self.level = max(1, self.level - 1)
                
                self.canvas.create_text(200, 150, 
                                      text="Try again!", 
                                      font=("Arial", 14), 
                                      fill="red")
            
            # Update reward display
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level {self.level}")
            
            # Update button
            self.start_button.config(
                text="Try Again",
                state='normal',
                bg="#FF9800"
            )
        
        # Reset progress display
        self.progress_label.config(text=f"Clicks: 0/{self.required_clicks}")
        
        # Show stats
        stats_text = f"Black balls: {self.black_balls_clicked} | Score: {self.score}"
        self.canvas.create_text(200, 180, text=stats_text, font=("Arial", 10), fill="blue")

class GameHub:
    def __init__(self, parent, currency_system):
        self.window = tk.Toplevel(parent)
        self.window.title("Game Hub")
        self.window.geometry("700x600")
        self.window.minsize(600, 550)
        self.window.configure(bg='#f0f0f0')
        
        # Set window icon if available
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                self.window.iconphoto(True, ImageTk.PhotoImage(Image.open(img_path)))
        except Exception as e:
            print(f"Error setting window icon: {e}")
        
        self.currency_system = currency_system
        
        # Get pet state reference for game progress tracking
        self.pet_state = getattr(currency_system, 'pet_state', None)
        
        # Create main frame with padding and styling
        self.main_frame = ttk.Frame(self.window, padding=15)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create header with title and currency
        self.header_frame = tk.Frame(self.main_frame, bg="#2196F3")
        self.header_frame.pack(fill='x', pady=(0, 15))
        
        # Game Hub title with improved styling
        self.title_label = tk.Label(self.header_frame, 
                                  text="Game Hub", 
                                  font=("Arial", 20, "bold"),
                                  bg="#2196F3",
                                  fg="white",
                                  padx=15,
                                  pady=10)
        self.title_label.pack(side='left')
        
        # Load currency icon
        self.currency_icon = None
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((24, 24), Image.LANCZOS)
                self.currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading currency icon: {e}")
        
        # Create currency display with custom styling
        self.currency_frame = tk.Frame(self.header_frame, 
                                     bg="#FFD700",  # Gold background
                                     relief=tk.RAISED,
                                     bd=2)
        self.currency_frame.pack(side='right', padx=5, pady=5)
        
        if self.currency_icon:
            self.icon_label = tk.Label(self.currency_frame, 
                                     image=self.currency_icon,
                                     bg="#FFD700")
            self.icon_label.pack(side='left', padx=(5, 2), pady=3)
        
        self.currency_label = tk.Label(self.currency_frame, 
                                     text=f"Coins: {self.currency_system.get_currency()}", 
                                     font=("Arial", 12, "bold"),
                                     bg="#FFD700",
                                     fg="#000000")
        self.currency_label.pack(side='left', padx=(0, 5), pady=3)
        
        # Create notebook with tabs and custom styling
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Get saved game progress levels
        saved_levels = {}
        if self.pet_state and hasattr(self.pet_state, 'game_progress'):
            saved_levels = self.pet_state.game_progress
        
        # Create game tabs with saved progress levels
        self.number_guesser_tab = self.create_number_guesser_game(saved_levels.get('number_guesser', 1))
        self.reaction_test_tab = self.create_reaction_test_game(saved_levels.get('reaction_test', 1))
        self.ball_clicker_tab = self.create_ball_clicker_game(saved_levels.get('ball_clicker', 1))
        
        # Style the notebook tabs
        style = ttk.Style()
        style.configure("TNotebook", background="#f0f0f0", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e0e0", padding=[15, 5], font=("Arial", 11))
        style.map("TNotebook.Tab", background=[('selected', '#2196F3')], foreground=[('selected', 'white')])
        
        # Add tabs with descriptive text
        self.notebook.add(self.number_guesser_tab.frame, text="Number Guesser")
        self.notebook.add(self.reaction_test_tab.frame, text="Reaction Test")
        self.notebook.add(self.ball_clicker_tab.frame, text="Ball Clicker")
        
        self.notebook.pack(expand=1, fill='both', padx=5, pady=5)
        
        # Add footer with instructions and improved styling
        self.footer_frame = tk.Frame(self.main_frame, bg="#E1F5FE", relief=tk.GROOVE, bd=1)
        self.footer_frame.pack(fill='x', pady=(15, 0))
        
        self.instructions_label = tk.Label(self.footer_frame, 
                                        text="Play games to earn coins! Each game gets harder as you level up.",
                                        font=("Arial", 10, "italic"),
                                        bg="#E1F5FE",
                                        fg="#0277BD",
                                        padx=10,
                                        pady=8)
        self.instructions_label.pack(fill='x')
        
        # Set up currency update timer
        self.update_currency_display()
    
    def create_number_guesser_game(self, level=1):
        """Create a number guesser game with the specified starting level"""
        game = NumberGuesserGame(self.notebook, self.currency_system)
        game.level = level
        # Update UI to reflect the level
        max_number = 10 + (game.level - 1)
        game.info_label.config(text=f"Level {game.level}\nGuess a number between 1-{max_number}")
        # Update reward display
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        # Update target number for the current level
        game.target_number = random.randint(1, max_number)
        # Set guesses based on level
        game.guesses_left = 3 + ((game.level - 1) // 5)
        return game
    
    def create_reaction_test_game(self, level=1):
        """Create a reaction test game with the specified starting level"""
        game = ReactionTestGame(self.notebook, self.currency_system)
        game.level = level
        # Update UI to reflect the level
        game.level_label.config(text=f"Level: {game.level}")
        # Update goal time display
        time_limit = max(0.3, 3.0 - (game.level * 0.1))
        game.goal_label.config(text=f"Goal: {time_limit:.2f}s")
        # Update reward display
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        return game
    
    def create_ball_clicker_game(self, level=1):
        """Create a ball clicker game with the specified starting level"""
        game = BallClickerGame(self.notebook, self.currency_system)
        game.level = level
        # Update UI to reflect the level
        game.level_label.config(text=f"Level {game.level}")
        # Update required clicks based on level
        game.required_clicks = 5 + game.level
        game.progress_label.config(text=f"Clicks: 0/{game.required_clicks}")
        # Update reward display
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        return game
    
    def update_currency_display(self):
        """Update the currency display"""
        if hasattr(self, 'currency_label'):
            current_coins = self.currency_system.get_currency()
            self.currency_label.config(text=f"Coins: {current_coins}")
            
            # Flash effect when coins change
            if hasattr(self, 'last_coins') and self.last_coins != current_coins:
                self.currency_frame.config(bg="#FFFFFF")
                self.window.after(200, lambda: self.currency_frame.config(bg="#FFD700"))
                if hasattr(self, 'icon_label'):
                    self.icon_label.config(bg="#FFFFFF")
                    self.window.after(200, lambda: self.icon_label.config(bg="#FFD700"))
                self.currency_label.config(bg="#FFFFFF")
                self.window.after(200, lambda: self.currency_label.config(bg="#FFD700"))
            
            self.last_coins = current_coins
            
        self.window.after(500, self.update_currency_display)  # Update twice per second