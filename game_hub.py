import tkinter as tk
from tkinter import ttk
import random
import time
class NumberGuesserGame:
    def __init__(self, parent, currency_system, pet_state=None):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.guesses_left = 3
        self.currency_system = currency_system
        self.pet_state = pet_state
        self.last_guess = None
        self.setup_ui()
    def setup_ui(self):
        self.target_number = random.randint(1, 10)
        self.title_label = ttk.Label(self.frame, text="Number Guesser", font=("Arial", 16, "bold"), foreground="#2196F3")
        self.title_label.pack(pady=(10, 5))
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
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
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        self.game_container = ttk.Frame(self.frame, padding=15, relief="groove")
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        self.info_label = ttk.Label(self.game_container,
                                   text=f"Level {self.level}\nGuess a number between 1-{10 + (self.level-1)}",
                                   font=("Arial", 12),
                                   justify="center",
                                   foreground="#333333")
        self.info_label.pack(pady=10)
        self.hint_label = ttk.Label(self.game_container, text="", font=("Arial", 11, "italic"), foreground="#1976D2")
        self.hint_label.pack(pady=8)
        self.input_frame = ttk.Frame(self.game_container)
        self.input_frame.pack(pady=10)
        self.entry = ttk.Entry(self.input_frame, width=10, font=("Arial", 12))
        self.entry.pack(side='left', padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.check_guess())
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
        self.entry.focus()
    def check_guess(self):
        try:
            guess = int(self.entry.get())
            max_number = 10 + (self.level - 1)
            if self.pet_state and hasattr(self.pet_state, 'stats'):
                self.pet_state.stats.modify_stat('energy', -0.5)
            self.entry.delete(0, 'end')
            self.last_guess = guess
            if guess == self.target_number:
                self.hint_label.config(text="Correct! 🎉", foreground="green")
                batch_number = (self.level - 1) // 3
                base_reward = 1 + 2 * batch_number
                self.currency_system.add_currency(base_reward)
                if self.pet_state and hasattr(self.pet_state, 'pet_manager'):
                    self.pet_state.pet_manager.handle_interaction('play')
                self.level += 1
                self.guesses_left = 3 + ((self.level - 1) // 5)
                max_number = 10 + (self.level - 1)
                self.target_number = random.randint(1, max_number)
                self.info_label.config(text=f"Level {self.level}\nGuess 1-{max_number} ({self.guesses_left} guesses)")
                new_batch_number = (self.level - 1) // 3
                new_base_reward = 1 + 2 * new_batch_number
                self.reward_label.config(text=f"Reward: {new_base_reward} coins")
                self.frame.after(1500, lambda: self.hint_label.config(text=""))
            else:
                hint = "Higher ⬆️" if guess < self.target_number else "Lower ⬇️"
                self.hint_label.config(text=hint, foreground="blue")
                self.guesses_left -= 1
                if self.guesses_left <= 0:
                    self.hint_label.config(text=f"The number was {self.target_number}", foreground="red")
                    batch_number = (self.level - 1) // 5
                    self.level = batch_number * 5 + 1
                    self.guesses_left = 3 + batch_number
                    max_number = 10 + (self.level - 1)
                    self.target_number = random.randint(1, max_number)
                    self.frame.after(2000, lambda: self.info_label.config(
                        text=f"Game Over! Restarting at Level {self.level}\nGuess 1-{max_number} ({self.guesses_left} guesses)"))
                    new_batch_number = (self.level - 1) // 3
                    new_base_reward = 1 + 2 * new_batch_number
                    self.reward_label.config(text=f"Reward: {new_base_reward} coins")
                    self.frame.after(2000, lambda: self.hint_label.config(text=""))
                else:
                    self.info_label.config(text=f"Guesses left: {self.guesses_left}\nLevel {self.level} (1-{max_number})")
            self.entry.focus()
        except ValueError:
            self.hint_label.config(text="Please enter a valid number!", foreground="red")
            self.entry.delete(0, 'end')
            self.entry.focus()
class ReactionTestGame:
    def __init__(self, parent, currency_system, pet_state=None):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.currency_system = currency_system
        self.pet_state = pet_state
        self.waiting = False
        self.ready_to_click = False
        self.setup_ui()
    def setup_ui(self):
        self.title_label = ttk.Label(self.frame, text="Reaction Test", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=(10, 5))
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
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
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        self.game_container = ttk.Frame(self.frame, padding=10)
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        self.reaction_button = tk.Button(
            self.game_container,
            text="Start Test",
            command=self.start_test,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.reaction_button.pack(pady=20)
        self.status_label = ttk.Label(self.game_container,
                                     text="Press the button to start!",
                                     font=("Arial", 11),
                                     justify="center",
                                     foreground="#333333")
        self.status_label.pack(pady=10)
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
        self.level_label = ttk.Label(self.game_container,
                                   text=f"Level: {self.level}",
                                   font=("Arial", 11, "bold"),
                                   foreground="#673AB7")
        self.level_label.pack(pady=10)
    def start_test(self):
        if self.waiting or self.ready_to_click:
            return
        self.waiting = True
        self.ready_to_click = False
        self.reaction_button.config(
            text="Wait...",
            bg="#FFC107",
            command=self.too_early
        )
        self.status_label.config(text="Wait for the button to turn red...")
        self.timer_label.config(text="Time: 0.00s")
        wait_time = random.randint(1000, 3000)
        self.frame.after(wait_time, self.enable_button)
    def too_early(self):
        if not self.ready_to_click and self.waiting:
            self.waiting = False
            self.status_label.config(text="Too early! Try again", foreground="red")
            self.reaction_button.config(
                text="Start Test",
                bg="#4CAF50",
                command=self.start_test
            )
            self.frame.after(1500, lambda: self.status_label.config(foreground="black"))
    def enable_button(self):
        if not self.waiting:
            return
        self.start_time = time.time()
        self.waiting = False
        self.ready_to_click = True
        self.reaction_button.config(
            text="CLICK NOW!",
            bg="#F44336",
            command=self.react
        )
        self.status_label.config(text="Click the button NOW!", foreground="red")
        self.update_timer_display()
    def update_timer_display(self):
        if self.ready_to_click:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {elapsed:.2f}s")
            self.frame.after(10, self.update_timer_display)
    def react(self):
        if not self.ready_to_click:
            return
        if self.pet_state and hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.modify_stat('energy', -1.5)
        self.ready_to_click = False
        reaction_time = time.time() - self.start_time
        time_limit = max(0.3, 3.0 - (self.level * 0.1))
        time_diff = time_limit - reaction_time
        if reaction_time <= time_limit:
            base_reward = 1 + 2 * ((self.level - 1) // 3)
            self.currency_system.add_currency(base_reward)
            self.level += 1
            if self.pet_state and hasattr(self.pet_state, 'pet_manager'):
                self.pet_state.pet_manager.handle_interaction('play')
            if time_diff > 0.5:
                feedback = "Amazing speed! 🚀"
            elif time_diff > 0.2:
                feedback = "Great reaction! ⚡"
            else:
                feedback = "Just in time! ✅"
            self.status_label.config(text=f"{feedback}", foreground="#4CAF50")
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level: {self.level}")
            new_time_limit = max(0.3, 3.0 - (self.level * 0.1))
            self.goal_label.config(text=f"Goal: {new_time_limit:.2f}s")
        else:
            self.level = max(1, self.level - 1)
            self.status_label.config(
                text=f"Too slow by {abs(time_diff):.2f}s! Try again",
                foreground="#F44336"
            )
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level: {self.level}")
            new_time_limit = max(0.3, 3.0 - (self.level * 0.1))
            self.goal_label.config(text=f"Goal: {new_time_limit:.2f}s")
        self.reaction_button.config(
            text="Start Test",
            bg="#4CAF50",
            command=self.start_test
        )
        self.timer_label.config(text=f"Time: {reaction_time:.3f}s")
        self.frame.after(2000, lambda: self.status_label.config(
            text="Press the button to start!",
            foreground="#333333"
        ))
class BallClickerGame:
    def __init__(self, parent, currency_system, pet_state=None):
        self.frame = ttk.Frame(parent)
        self.level = 1
        self.score = 0
        self.currency_system = currency_system
        self.pet_state = pet_state
        self.game_running = False
        self.balls = []
        self.black_balls_clicked = 0
        self.required_clicks = 5
        self.ball_spawn_timer = None
        self._last_end_message_text = None
        self._last_end_message_success = False
        self._last_stats_text = None
        self.setup_ui()
    def setup_ui(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.title_label = ttk.Label(self.frame, text="Ball Clicker", font=("Arial", 16, "bold"), foreground="#2196F3")
        self.title_label.grid(row=0, column=0, pady=(10, 5))
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.grid(row=1, column=0, pady=(5, 10))
        batch_number = (self.level - 1) // 3
        base_reward = 1 + 2 * batch_number
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
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        self.reward_label = ttk.Label(self.reward_frame, text=f"Reward: {base_reward} coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        self.game_container = ttk.Frame(self.frame, padding=15, relief="groove")
        self.game_container.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        self.game_container.columnconfigure(0, weight=1)
        self.game_container.rowconfigure(3, weight=1)
        self.info_frame = ttk.Frame(self.game_container)
        self.info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.columnconfigure(1, weight=1)
        self.score_label = ttk.Label(self.info_frame, text=f"Score: {self.score}", font=("Arial", 12, "bold"), foreground="#1976D2")
        self.score_label.grid(row=0, column=0, sticky='w')
        self.progress_label = ttk.Label(self.info_frame, text=f"Clicks: 0/{self.required_clicks}", font=("Arial", 12), foreground="#4CAF50")
        self.progress_label.grid(row=0, column=1, sticky='e')
        self.timer_label = ttk.Label(self.game_container, text="Time: 0.00s", font=("Arial", 12), foreground="#FF9800")
        self.timer_label.grid(row=1, column=0, pady=5)
        self.level_label = ttk.Label(self.game_container, text=f"Level {self.level}", font=("Arial", 11, "bold"), foreground="#673AB7")
        self.level_label.grid(row=2, column=0, pady=5)
        self.canvas = tk.Canvas(self.game_container, bg='#f5f5f5', relief=tk.SUNKEN, bd=2, highlightthickness=0)
        self.canvas.grid(row=3, column=0, sticky='nsew', pady=10)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.start_button = tk.Button(self.game_container, text="Start Round", command=self.start_round, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief=tk.RAISED, borderwidth=2)
        self.start_button.grid(row=4, column=0, pady=15)
    def start_round(self):
        if self.game_running:
            return
        self.game_running = True
        self.score = 0
        self.black_balls_clicked = 0
        self.balls = []
        self.canvas.delete('all')
        self.score_label.config(text=f"Score: {self.score}")
        self.progress_label.config(text=f"Clicks: {self.black_balls_clicked}/{self.required_clicks}")
        self.start_button.config(state='disabled')
        self.start_time = time.time()
        self.round_duration = max(8.0, 15.0 - (self.level * 0.3))
        self.black_balls_spawned = 0
        self.min_black_balls_needed = self.required_clicks * 2
        self.spawn_ball()
        self.update_timer()
    def spawn_ball(self):
        if not self.game_running:
            return
        red_probability = min(0.2 + (self.level * 0.01), 0.4)
        elapsed = time.time() - self.start_time
        force_black = (self.black_balls_spawned < self.min_black_balls_needed and
                      elapsed > (self.round_duration * 0.5))
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = random.randint(15, max(15, canvas_width - 15))
        y = random.randint(15, max(15, canvas_height - 15))
        is_red = random.random() < red_probability and not force_black
        color = 'red' if is_red else 'black'
        if color == 'black':
            self.black_balls_spawned += 1
        ball = self.canvas.create_oval(x-15, y-15, x+15, y+15,
                                     fill=color,
                                     outline='white' if is_red else 'gray',
                                     width=2)
        self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball, c=color: self.handle_click(b, c))
        self.balls.append(ball)
        removal_time = random.randint(2000, 3000) if not is_red else random.randint(1500, 2500)
        self.canvas.after(removal_time, lambda b=ball: self.remove_ball(b))
        spawn_delay = max(300, random.randint(400, 1200) - (self.level * 10))
        self.ball_spawn_timer = self.frame.after(spawn_delay, self.spawn_ball)
    def remove_ball(self, ball):
        if ball in self.balls:
            self.balls.remove(ball)
            self.canvas.delete(ball)
    def handle_click(self, ball, color):
        if not self.game_running or ball not in self.balls:
            return
        if self.pet_state and hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.modify_stat('energy', -0.5)
        self.remove_ball(ball)
        if color == 'black':
            self.score += 1
            self.black_balls_clicked += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.progress_label.config(text=f"Clicks: {self.black_balls_clicked}/{self.required_clicks}")
            if self.black_balls_clicked >= self.required_clicks:
                self.end_round(True)
        else:
            self.score = max(0, self.score - 2)
            self.score_label.config(text=f"Score: {self.score}")
    def _on_canvas_resize(self, event=None):
        if not self.game_running:
            self.canvas.delete("end_message")
            self.canvas.delete("stats_message")
            if hasattr(self, '_last_end_message_text') and self._last_end_message_text is not None:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                fill_color = "green" if self._last_end_message_success else ("orange" if self._last_end_message_text.startswith("Time's up!") else "red")
                self.canvas.create_text(canvas_width / 2, canvas_height / 2,
                                      text=self._last_end_message_text,
                                      font=("Arial", 14, "bold" if self._last_end_message_success else ""),
                                      fill=fill_color,
                                      tags="end_message")
                if hasattr(self, '_last_stats_text') and self._last_stats_text is not None:
                    self.canvas.create_text(canvas_width / 2, canvas_height / 2 + 30,
                                          text=self._last_stats_text,
                                          font=("Arial", 10), fill="blue",
                                          tags="stats_message")
    def update_timer(self):
        if not self.game_running:
            return
        elapsed = time.time() - self.start_time
        self.timer_label.config(text=f"Time: {elapsed:.2f}s")
        remaining_time = self.round_duration - elapsed
        if remaining_time > 0:
            balls_needed = self.min_black_balls_needed - self.black_balls_spawned
            expected_rate = balls_needed / remaining_time if remaining_time > 0 else 0
            if expected_rate > 1.5 and balls_needed > 0 and remaining_time > 3.0:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                x = random.randint(20, canvas_width - 20 if canvas_width > 40 else 20)
                y = random.randint(20, canvas_height - 20 if canvas_height > 40 else 20)
                ball = self.canvas.create_oval(x-15, y-15, x+15, y+15,
                                           fill='black',
                                           outline='gray',
                                           width=2)
                self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball: self.handle_click(b, 'black'))
                self.balls.append(ball)
                self.black_balls_spawned += 1
                self.canvas.after(3000, lambda b=ball: self.remove_ball(b))
            elif remaining_time < 3.0 and balls_needed > 3:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                x = random.randint(20, canvas_width - 20 if canvas_width > 40 else 20)
                y = random.randint(20, canvas_height - 20 if canvas_height > 40 else 20)
                ball = self.canvas.create_oval(x-15, y-15, x+15, y+15,
                                           fill='black',
                                           outline='gray',
                                           width=2)
                self.canvas.tag_bind(ball, '<Button-1>', lambda e, b=ball: self.handle_click(b, 'black'))
                self.balls.append(ball)
                self.black_balls_spawned += 1
                self.canvas.after(4000, lambda b=ball: self.remove_ball(b))
        if elapsed < self.round_duration:
            self.frame.after(50, self.update_timer)
        else:
            self.end_round(False)
    def end_round(self, success=False):
        self.game_running = False
        if self.ball_spawn_timer:
            self.frame.after_cancel(self.ball_spawn_timer)
        self.canvas.delete('all')
        base_reward = 1 + 2 * ((self.level - 1) // 3)
        if success:
            self.currency_system.add_currency(base_reward)
            self.level += 1
            self.required_clicks = 5 + self.level
            if self.pet_state and hasattr(self.pet_state, 'pet_manager'):
                self.pet_state.pet_manager.handle_interaction('play')
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            message_text = f"Level Complete! +{base_reward} coins"
            self._last_end_message_text = message_text
            self._last_end_message_success = True
            self.canvas.create_text(canvas_width / 2, canvas_height / 2,
                                  text=message_text,
                                  font=("Arial", 14, "bold"),
                                  fill="green",
                                  tags="end_message")
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level {self.level}")
            self.start_button.config(
                text=f"Start Level {self.level}",
                state='normal',
                bg="#4CAF50"
            )
        else:
            if self.black_balls_clicked >= self.required_clicks // 2:
                half_reward = max(1, base_reward // 2)
                self.currency_system.add_currency(half_reward)
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                message_text = f"Time's up! +{half_reward} coins"
                self._last_end_message_text = message_text
                self._last_end_message_success = False
                self.canvas.create_text(canvas_width / 2, canvas_height / 2,
                                      text=message_text,
                                      font=("Arial", 14),
                                      fill="orange",
                                      tags="end_message")
            else:
                self.level = max(1, self.level - 1)
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                message_text = "Try again!"
                self._last_end_message_text = message_text
                self._last_end_message_success = False
                self.canvas.create_text(canvas_width / 2, canvas_height / 2,
                                      text=message_text,
                                      font=("Arial", 14),
                                      fill="red",
                                      tags="end_message")
            new_batch_number = (self.level - 1) // 3
            new_base_reward = 1 + 2 * new_batch_number
            self.reward_label.config(text=f"Reward: {new_base_reward} coins")
            self.level_label.config(text=f"Level {self.level}")
            self.start_button.config(
                text="Try Again",
                state='normal',
                bg="#FF9800"
            )
        self.progress_label.config(text=f"Clicks: 0/{self.required_clicks}")
        stats_text = f"Black balls: {self.black_balls_clicked} | Score: {self.score}"
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self._last_stats_text = stats_text
        self.canvas.create_text(canvas_width / 2, canvas_height / 2 + 30, text=stats_text, font=("Arial", 10), fill="blue", tags="stats_message")
class SlotMachineGame:
    def __init__(self, parent, currency_system, pet_state=None):
        self.frame = ttk.Frame(parent)
        self.currency_system = currency_system
        self.pet_state = pet_state
        self.rolling = False
        self.setup_ui()
    def setup_ui(self):
        self.title_label = ttk.Label(self.frame, text="Slot Machine", font=("Arial", 16, "bold"), foreground="#2196F3")
        self.title_label.pack(pady=(10, 5))
        self.reward_frame = ttk.Frame(self.frame)
        self.reward_frame.pack(pady=(5, 10))
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
        if self.currency_icon:
            self.icon_label = ttk.Label(self.reward_frame, image=self.currency_icon)
            self.icon_label.pack(side='left', padx=(0, 5))
        self.reward_label = ttk.Label(self.reward_frame, text="Reward: 0-1000 coins", font=("Arial", 10, "bold"))
        self.reward_label.pack(side='left')
        self.game_container = ttk.Frame(self.frame, padding=15, relief="groove")
        self.game_container.pack(fill='both', expand=True, padx=20, pady=10)
        self.slot_frame = ttk.Frame(self.game_container)
        self.slot_frame.pack(pady=20)
        self.slot_labels = []
        for i in range(3):
            slot_label = tk.Label(self.slot_frame,
                                 text="❓",
                                 font=("Arial", 40, "bold"),
                                 bg="white",
                                 relief=tk.RAISED,
                                 bd=3,
                                 width=3,
                                 height=2)
            slot_label.pack(side='left', padx=5)
            self.slot_labels.append(slot_label)
        self.result_label = ttk.Label(self.game_container,
                                     text="",
                                     font=("Arial", 12, "bold"),
                                     foreground="#1976D2")
        self.result_label.pack(pady=10)
        self.spin_button = tk.Button(self.game_container,
                                   text="Spin (Cost: 5 coins)",
                                   command=self.spin,
                                   font=("Arial", 12, "bold"),
                                   bg="white",
                                   fg="black",
                                   padx=20,
                                   pady=10,
                                   relief=tk.RAISED,
                                   borderwidth=2)
        self.spin_button.pack(pady=20)
        self.instructions_label = ttk.Label(self.game_container,
                                           text="Get 3 💰 for 1000 coins!\nEach 💰 gives 50 coins!\nOther combinations pay 0-20 coins.",
                                           font=("Arial", 10),
                                           justify="center",
                                           foreground="#666666")
        self.instructions_label.pack(pady=10)
    def spin(self):
        if self.rolling:
            return
        if self.currency_system.get_currency() < 5:
            self.result_label.config(text="Not enough coins!", foreground="red")
            return
        self.currency_system.remove_currency(5)
        if hasattr(self.frame.winfo_toplevel(), 'update_currency_display'):
            self.frame.winfo_toplevel().update_currency_display()
        self.rolling = True
        self.spin_button.config(state='disabled', text="Spinning...")
        self.result_label.config(text="", foreground="#1976D2")
        self.roll_count = 0
        self.animate_rolling()
    def animate_rolling(self):
        if not self.rolling:
            return
        emojis = ["🍒", "🍋", "🍊", "🍇", "🍉", "🍎", "🍓", "🍑", "🥝", "🍍", "🥭", "🥥", "🫐", "🍈", "🍌"]
        for label in self.slot_labels:
            label.config(text=random.choice(emojis))
        self.roll_count += 1
        if self.roll_count < random.randint(15, 25):
            self.frame.after(100, self.animate_rolling)
        else:
            self.show_result()
    def show_result(self):
        self.rolling = False
        self.spin_button.config(state='normal', text="Spin (Cost: 5 coins)")
        emojis = ["🍒", "🍋", "🍊", "🍇", "🍉", "🍎", "🍓", "🍑", "🥝", "🍍", "🥭", "🥥", "🫐", "🍈", "🍌", "💰"]
        final_emojis = []
        for i in range(3):
            if random.random() < 0.01:
                final_emojis.append("💰")
            else:
                final_emojis.append(random.choice(emojis[:-1]))
        for i, label in enumerate(self.slot_labels):
            label.config(text=final_emojis[i])
        reward = 0
        money_count = final_emojis.count("💰")
        if final_emojis == ["💰", "💰", "💰"]:
            reward = 1000
            self.result_label.config(text="JACKPOT! 1000 coins! 🎉💰", foreground="gold")
        else:
            reward += money_count * 50
            if len(set(final_emojis)) == 1:
                regular_reward = random.randint(15, 20)
                reward += regular_reward
                self.result_label.config(text=f"Three of a kind! {reward} coins! 🎉", foreground="green")
            elif len(set(final_emojis)) == 2:
                regular_reward = random.randint(15, 20)
                reward += regular_reward
                self.result_label.config(text=f"Two of a kind! {reward} coins!", foreground="#1976D2")
            else:
                regular_reward = random.randint(0, 5)
                reward += regular_reward
                if reward > 0:
                    self.result_label.config(text=f"Nice try! {reward} coins!", foreground="#4CAF50")
                else:
                    self.result_label.config(text="No luck this time!", foreground="#9E9E9E")
        if reward > 0:
            self.currency_system.add_currency(reward)
            if hasattr(self.frame.winfo_toplevel(), 'update_currency_display'):
                self.frame.winfo_toplevel().update_currency_display()
        if self.pet_state and hasattr(self.pet_state, 'pet_manager'):
            self.pet_state.pet_manager.handle_interaction('play')
class GameHub:
    def __init__(self, parent, currency_system, pet_state=None, parent_window=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Game Hub")
        self.pet_state = pet_state
        self.energy_check_active = True
        if pet_state and hasattr(pet_state, 'stats'):
            energy_level = float(pet_state.stats.get_stat('energy'))
            if energy_level <= 5.0:
                self.show_tired_message()
                return
            else:
                pass
        else:
            pass
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = min(700, int(screen_width * 0.5))
        height = min(600, int(screen_height * 0.7))
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(550, 500)
        self.window.configure(bg='#f0f0f0')
        if parent_window and parent_window.winfo_exists():
            parent_window.update_idletasks()
            x = parent_window.winfo_x() + parent_window.winfo_width()
            y = parent_window.winfo_y()
            self.window.geometry(f"+{x}+{y}")
            self.window.attributes('-topmost', True)
            self.window.after(500, lambda: self.window.attributes('-topmost', False))
        try:
            import os
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                self.window.iconphoto(True, ImageTk.PhotoImage(Image.open(img_path)))
        except Exception as e:
            print(f"Error setting window icon: {e}")
        self.currency_system = currency_system
        self.pet_state = getattr(currency_system, 'pet_state', None)
        self.main_frame = ttk.Frame(self.window, padding=15)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.header_frame = tk.Frame(self.main_frame, bg="#2196F3")
        self.header_frame.pack(fill='x', pady=(0, 15))
        self.title_label = tk.Label(self.header_frame,
                                  text="Game Hub",
                                  font=("Arial", 20, "bold"),
                                  bg="#2196F3",
                                  fg="white",
                                  padx=15,
                                  pady=10)
        self.title_label.pack(side='left')
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
        self.currency_frame = tk.Frame(self.header_frame,
                                     bg="#FFD700",
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
        self.notebook = ttk.Notebook(self.main_frame)
        saved_levels = {}
        if self.pet_state and hasattr(self.pet_state, 'game_progress'):
            saved_levels = self.pet_state.game_progress
        self.number_guesser_tab = self.create_number_guesser_game(saved_levels.get('number_guesser', 1))
        self.reaction_test_tab = self.create_reaction_test_game(saved_levels.get('reaction_test', 1))
        self.ball_clicker_tab = self.create_ball_clicker_game(saved_levels.get('ball_clicker', 1))
        self.slot_machine_tab = self.create_slot_machine_game()
        style = ttk.Style()
        style.configure("TNotebook", background="#f0f0f0", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e0e0", padding=[15, 5], font=("Arial", 11))
        style.map("TNotebook.Tab", background=[('selected', '#2196F3'), ('!selected', '#f0f0f0')], foreground=[('selected', '#000000'), ('!selected', '#333333')])
        self.notebook.add(self.number_guesser_tab.frame, text="Number Guesser")
        self.notebook.add(self.reaction_test_tab.frame, text="Reaction Test")
        self.notebook.add(self.ball_clicker_tab.frame, text="Ball Clicker")
        self.notebook.add(self.slot_machine_tab.frame, text="Slot Machine")
        self.notebook.pack(expand=1, fill='both', padx=5, pady=5)
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
        self.update_currency_display()
        self.start_energy_monitoring()
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
    def start_energy_monitoring(self):
        """Start continuous monitoring of pet energy levels""""
        if self.energy_check_active:
            self.check_energy_level()
            self.window.after(2000, self.start_energy_monitoring)
    def check_energy_level(self):
        """Check if pet energy has dropped below 5% and close game hub if so""""
        if not self.energy_check_active:
            return
        if self.pet_state and hasattr(self.pet_state, 'stats'):
            try:
                energy_level = float(self.pet_state.stats.get_stat('energy'))
                if energy_level <= 5.0:
                    self.energy_check_active = False
                    self.disable_all_games()
                    self.show_energy_depleted_message()
            except Exception as e:
                pass
    def disable_all_games(self):
        """Disable all game interactions when energy is too low""""
        try:
            if hasattr(self, 'number_guesser_tab'):
                self.disable_game_tab(self.number_guesser_tab)
            if hasattr(self, 'reaction_test_tab'):
                self.disable_game_tab(self.reaction_test_tab)
            if hasattr(self, 'ball_clicker_tab'):
                self.disable_game_tab(self.ball_clicker_tab)
            if hasattr(self, 'slot_machine_tab'):
                self.disable_game_tab(self.slot_machine_tab)
        except Exception as e:
            pass
    def disable_game_tab(self, game_tab):
        """Disable all interactive elements in a game tab""""
        try:
            if hasattr(game_tab, 'frame'):
                self.disable_widget_children(game_tab.frame)
        except Exception as e:
            pass
    def disable_widget_children(self, widget):
        """Recursively disable all children of a widget""""
        try:
            for child in widget.winfo_children():
                widget_type = child.winfo_class()
                if widget_type in ['Button', 'Entry', 'Text', 'Listbox', 'Scale', 'Spinbox']:
                    try:
                        child.configure(state='disabled')
                    except tk.TclError:
                        pass
                elif widget_type == 'Canvas':
                    try:
                        child.configure(state='disabled')
                    except tk.TclError:
                        child.unbind('<Button-1>')
                        child.unbind('<ButtonPress-1>')
                        child.unbind('<ButtonRelease-1>')
                self.disable_widget_children(child)
        except Exception as e:
            pass
    def show_energy_depleted_message(self):
        """Show message when energy drops below 5% during gameplay and close game hub""""
        pet_name = "Your pet"
        if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'name'):
            pet_name = self.pet_state.pet_manager.name
        message_window = tk.Toplevel(self.window)
        message_window.title("Pet Tired")
        message_window.geometry("500x250")
        message_window.configure(bg='#f0f0f0')
        message_window.resizable(False, False)
        message_window.transient(self.window)
        message_window.grab_set()
        message_window.protocol("WM_DELETE_WINDOW", lambda: None)
        message_window.update_idletasks()
        x = (message_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (message_window.winfo_screenheight() // 2) - (250 // 2)
        message_window.geometry(f"500x250+{x}+{y}")
        main_frame = tk.Frame(message_window, bg='#f0f0f0', padx=30, pady=25)
        main_frame.pack(fill='both', expand=True)
        tired_label = tk.Label(main_frame,
                              text="😴💤",
                              font=("Arial", 48),
                              bg='#f0f0f0')
        tired_label.pack(pady=(10, 20))
        message_text = f"{pet_name} got too tired while playing!\nThe game hub will now close."
        message_label = tk.Label(main_frame,
                                text=message_text,
                                font=("Arial", 16, "bold"),
                                bg='#f0f0f0',
                                fg='#000000',
                                justify='center',
                                wraplength=450)
        message_label.pack(pady=15)
        def close_all():
            message_window.destroy()
            self.window.destroy()
        close_button = tk.Button(main_frame,
                               text="OK",
                               command=close_all,
                               font=("Arial", 14, "bold"),
                               bg="#2196F3",
                               fg="white",
                               padx=25,
                               pady=8,
                               relief=tk.RAISED,
                               borderwidth=2)
        close_button.pack(pady=20)
        message_window.after(5000, close_all)
    def show_tired_message(self):
        """Show a message when the pet is too tired to play games""""
        pet_name = "Your pet"
        if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'name'):
            pet_name = self.pet_state.pet_manager.name
        self.window.geometry("500x300")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(False, False)
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"500x300+{x}+{y}")
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        tired_label = tk.Label(main_frame,
                              text="😴💤",
                              font=("Arial", 40),
                              bg='#f0f0f0')
        tired_label.pack(pady=(5, 15))
        message_text = f"{pet_name} is too tired...\nPlease rest for a little before continuing playing"
        message_label = tk.Label(main_frame,
                                text=message_text,
                                font=("Arial", 14, "bold"),
                                bg='#f0f0f0',
                                fg='#000000',
                                justify='center',
                                wraplength=420)
        message_label.pack(pady=10)
        close_button = tk.Button(main_frame,
                               text="OK",
                               command=self.window.destroy,
                               font=("Arial", 12, "bold"),
                               bg="#2196F3",
                               fg="white",
                               padx=20,
                               pady=6,
                               relief=tk.RAISED,
                               borderwidth=2)
        close_button.pack(pady=15)
    def on_window_close(self):
        """Handle window close event""""
        self.energy_check_active = False
        self.window.destroy()
    def create_number_guesser_game(self, level=1):
        game = NumberGuesserGame(self.notebook, self.currency_system, self.pet_state)
        game.level = level
        max_number = 10 + (game.level - 1)
        game.info_label.config(text=f"Level {game.level}\nGuess a number between 1-{max_number}")
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        game.target_number = random.randint(1, max_number)
        game.guesses_left = 3 + ((game.level - 1) // 5)
        return game
    def create_reaction_test_game(self, level=1):
        game = ReactionTestGame(self.notebook, self.currency_system, self.pet_state)
        game.level = level
        game.level_label.config(text=f"Level: {game.level}")
        time_limit = max(0.3, 3.0 - (game.level * 0.1))
        game.goal_label.config(text=f"Goal: {time_limit:.2f}s")
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        return game
    def create_ball_clicker_game(self, level=1):
        game = BallClickerGame(self.notebook, self.currency_system, self.pet_state)
        game.level = level
        game.level_label.config(text=f"Level {game.level}")
        game.required_clicks = 5 + game.level
        game.progress_label.config(text=f"Clicks: 0/{game.required_clicks}")
        batch_number = (game.level - 1) // 3
        base_reward = 1 + 2 * batch_number
        game.reward_label.config(text=f"Reward: {base_reward} coins")
        return game
    def create_slot_machine_game(self):
        game = SlotMachineGame(self.notebook, self.currency_system, self.pet_state)
        return game
    def update_currency_display(self):
        if hasattr(self, 'currency_label'):
            current_coins = self.currency_system.get_currency()
            self.currency_label.config(text=f"Coins: {current_coins}")
            if hasattr(self, 'last_coins') and self.last_coins != current_coins:
                self.currency_frame.config(bg="#FFFFFF")
                self.window.after(200, lambda: self.currency_frame.config(bg="#FFD700"))
                if hasattr(self, 'icon_label'):
                    self.icon_label.config(bg="#FFFFFF")
                    self.window.after(200, lambda: self.icon_label.config(bg="#FFD700"))
                self.currency_label.config(bg="#FFFFFF")
                self.window.after(200, lambda: self.currency_label.config(bg="#FFD700"))
            self.last_coins = current_coins
        self.window.after(500, self.update_currency_display)