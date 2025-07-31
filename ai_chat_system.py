import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
import time
from datetime import datetime
from unified_ui import SimpleButton, COLORS
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
AVAILABLE_MODELS = {
    'gemini-2.5-pro': {
        'name': 'Gemini 2.5 Pro',
        'free': True,
        'description': 'Latest and most capable model',
        'context_window': '2M tokens'
    },
    'gemini-2.5-flash': {
        'name': 'Gemini 2.5 Flash',
        'free': True,
        'description': 'Fast and efficient latest generation',
        'context_window': '1M tokens'
    },
    'gemini-1.5-pro': {
        'name': 'Gemini 1.5 Pro',
        'free': False,
        'description': 'Advanced model with reasoning capabilities',
        'context_window': '2M tokens'
    },
    'gemini-1.5-flash': {
        'name': 'Gemini 1.5 Flash',
        'free': True,
        'description': 'Fast previous generation (free with limits)',
        'context_window': '1M tokens'
    },
    'gemini-1.0-pro': {
        'name': 'Gemini 1.0 Pro',
        'free': False,
        'description': 'Original Pro model',
        'context_window': '32K tokens'
    },
    'gemini-1.5-pro-exp-0801': {
        'name': 'Gemini 1.5 Pro Experimental',
        'free': False,
        'description': 'Experimental version of 1.5 Pro',
        'context_window': '2M tokens'
    },
    'gemini-1.5-flash-exp-0801': {
        'name': 'Gemini 1.5 Flash Experimental',
        'free': True,
        'description': 'Experimental version of 1.5 Flash',
        'context_window': '1M tokens'
    }
}
class AIChatSystem:
    def __init__(self, pet_manager):
        self.pet_manager = pet_manager
        self.api_key = None
        self.model = None
        self.selected_model = 'gemini-2.5-flash'
        self.chat_provider = 'gemini'
        self.ollama_model = None
        self.chat_window = None
        self.is_typing = False
        self.typing_timer = None
        self.response_bubble_active = False
        self.conversation_history = []
        self.current_session_id = None
        self.load_settings()
        self.load_conversation_history()
        if self.chat_provider == 'gemini' and self.api_key:
            self.initialize_gemini_model()
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
            history_path = os.path.join(saves_dir, 'conversation_history.json')
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            self.conversation_history = []
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            history_path = os.path.join(saves_dir, 'conversation_history.json')
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving conversation history: {e}")
    def start_new_conversation_session(self):
        """Start a new conversation session"""
        self.current_session_id = datetime.now().isoformat()
        session = {
            'session_id': self.current_session_id,
            'start_time': self.current_session_id,
            'messages': []
        }
        self.conversation_history.append(session)
        return session
    def add_message_to_history(self, user_message, ai_response):
        """Add a message exchange to the current conversation session"""
        if not self.current_session_id:
            self.start_new_conversation_session()
        current_session = None
        for session in self.conversation_history:
            if session['session_id'] == self.current_session_id:
                current_session = session
                break
        if current_session:
            message_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'ai_response': ai_response
            }
            current_session['messages'].append(message_entry)
            self.save_conversation_history()
    def setup_chat_provider(self):
        """Show the chat provider setup dialog"""
        dialog = ChatProviderDialog(self.pet_manager.root, self)
        dialog.show()
    def load_settings(self):
        """Load AI chat settings from file"""
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
            settings_path = os.path.join(saves_dir, 'ai_chat_settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.api_key = settings.get('api_key')
                self.selected_model = settings.get('selected_model', 'gemini-2.5-flash')
                self.chat_provider = settings.get('chat_provider', 'gemini')
                self.ollama_model = settings.get('ollama_model')
        except Exception as e:
            print(f"Error loading AI chat settings: {e}")
            self.api_key = None
            self.selected_model = 'gemini-2.5-flash'
            self.chat_provider = 'gemini'
            self.ollama_model = None
    def save_settings(self, **kwargs):
        """Save AI chat settings to file"""
        try:
            if 'api_key' in kwargs:
                self.api_key = kwargs['api_key']
            if 'selected_model' in kwargs:
                self.selected_model = kwargs['selected_model']
            if 'chat_provider' in kwargs:
                self.chat_provider = kwargs['chat_provider']
            if 'ollama_model' in kwargs:
                self.ollama_model = kwargs['ollama_model']
            saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            settings_path = os.path.join(saves_dir, 'ai_chat_settings.json')
            settings = {
                'api_key': self.api_key,
                'selected_model': self.selected_model,
                'chat_provider': self.chat_provider,
                'ollama_model': self.ollama_model
            }
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving AI chat settings: {e}")
            return False
    def create_chat_window(self, parent_window=None):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.lift()
            self.chat_window.focus_force()
            return
        self.chat_window = tk.Toplevel()
        self.chat_window.title("Chat with Pet")
        self.chat_window.geometry("450x200")
        self.chat_window.resizable(False, False)
        if parent_window and parent_window.winfo_exists():
            parent_window.update_idletasks()
            x = parent_window.winfo_x() + parent_window.winfo_width()
            y = parent_window.winfo_y()
            self.chat_window.geometry(f"+{x}+{y}")
            self.chat_window.attributes('-topmost', True)
            self.chat_window.after(500, lambda: self.chat_window.attributes('-topmost', False))
        else:
            self.chat_window.attributes('-topmost', True)
            self.chat_window.after(100, lambda: self.chat_window.attributes('-topmost', False))
        main_frame = ttk.Frame(self.chat_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        instructions = ttk.Label(main_frame,
                                 text=f"Chat with {self.pet_manager.name}! Ask anything - from pet care to general questions!\nResponses appear in speech bubbles above your pet.",
                                 font=('Arial', 9),
                                 foreground='#666666')
        instructions.pack(pady=(0, 10))
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        self.message_entry = tk.Text(input_frame, height=2, wrap=tk.WORD, font=('Arial', 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.message_entry.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_entry.config(yscrollcommand=scrollbar.set)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', padx=5, pady=(5, 0))
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side=tk.LEFT)
        settings_button = SimpleButton(left_button_frame, text="Settings", command=self.setup_chat_provider,
                                     bg=COLORS['secondary'], fg="white")
        settings_button.pack(side=tk.LEFT, padx=(0, 5))
        history_button = SimpleButton(left_button_frame, text="History", command=self.show_conversation_history,
                                    bg=COLORS['info'], fg="white")
        history_button.pack(side=tk.LEFT)
        send_button = SimpleButton(button_frame, text="Send Message", command=self.send_message_from_button,
                                 bg=COLORS['primary'], fg="white")
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        self.message_entry.bind('<Return>', self.handle_enter_key)
        self.message_entry.bind('<Shift-Return>', self.handle_shift_enter)
        self.message_entry.focus()
        self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat_window)
        if not self.current_session_id:
            self.start_new_conversation_session()
    def show_conversation_history(self):
        """Show the conversation history window"""
        history_window = ConversationHistoryWindow(self.pet_manager.root, self)
        history_window.show()
    def get_ollama_models(self):
        """Get list of available Ollama models"""
        try:
            if not OLLAMA_AVAILABLE:
                return []
            models = ollama.list()
            if hasattr(models, 'models'):
                return [model.model for model in models.models]
            elif isinstance(models, dict) and 'models' in models:
                return [model['name'] for model in models['models']]
            return []
        except Exception as e:
            print(f"Error getting Ollama models: {e}")
            return []
    def send_message(self, message):
        if self.is_typing:
            return
        message = message.strip()
        if not message:
            return
        self.is_typing = True
        self.message_entry.config(state='disabled')
        if hasattr(self, 'start_thinking_animation'):
            self.start_thinking_animation()
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    def _process_message(self, message):
        try:
            full_prompt = self.get_pet_personality_prompt() + f"\n\nUser: {message}\nPet:"
            ai_response = ""
            if self.chat_provider == 'gemini':
                if not self.model:
                    raise Exception("Gemini model not initialized")
                response = self.model.generate_content(full_prompt)
                ai_response = response.text.strip()
            elif self.chat_provider == 'ollama':
                if not OLLAMA_AVAILABLE:
                    raise Exception("Ollama library not available")
                elif not self.ollama_model:
                    raise Exception("No Ollama model selected")
                else:
                    try:
                        response = ollama.chat(
                            model=self.ollama_model,
                            messages=[{'role': 'user', 'content': full_prompt}],
                            options={'num_ctx': 4096},
                            stream=False
                        )
                        if isinstance(response, dict) and 'message' in response:
                            ai_response = response['message']['content'].strip()
                        elif hasattr(response, 'message'):
                            ai_response = response.message.content.strip()
                        else:
                            raise Exception(f"Unexpected response format: {response}")
                        import re
                        think_pattern = r'<think>.*?</think>'
                        ai_response = re.sub(think_pattern, '', ai_response, flags=re.DOTALL).strip()
                        reasoning_pattern = r'<reasoning>.*?</reasoning>'
                        ai_response = re.sub(reasoning_pattern, '', ai_response, flags=re.DOTALL).strip()
                    except ollama.ResponseError as e:
                        raise Exception(f"Ollama error: {e}")
                    except Exception as e:
                        raise Exception(f"Ollama chat error: {e}")
            else:
                raise Exception(f"Unknown chat provider: {self.chat_provider}")
            if not ai_response.strip():
                raise Exception("Empty response from AI")
            self.add_message_to_history(message, ai_response)
            self.pet_manager.root.after(0, lambda: self.show_ai_response(ai_response))
        except Exception as e:
            import traceback
            error_str = str(e)
            # Only print traceback for unexpected errors, not for Ollama connection errors
            if not ("ollama" in error_str.lower() and ("connect" in error_str.lower() or "connection" in error_str.lower())):
                traceback.print_exc()
            error_msg = self._get_friendly_error_message(error_str)
            self.pet_manager.root.after(0, lambda: self.show_ai_response(error_msg))
        finally:
            self.pet_manager.root.after(0, self.reset_typing_state)
    def continue_conversation_from_history(self, session_id, message_index=None):
        """Continue a conversation from history"""
        target_session = None
        for session in self.conversation_history:
            if session['session_id'] == session_id:
                target_session = session
                break
        if not target_session:
            return
        self.current_session_id = session_id
        if not self.chat_window or not self.chat_window.winfo_exists():
            self.create_chat_window()
        self.chat_window.lift()
        self.chat_window.focus_force()
        self.message_entry.focus()
    def send_message_from_button(self):
        """Send message when Send button is clicked"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            self.message_entry.delete("1.0", tk.END)
            self.send_message(message)
    def handle_enter_key(self, event):
        """Handle Enter key press in message entry"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            self.message_entry.delete("1.0", tk.END)
            self.send_message(message)
        return 'break'
    def handle_shift_enter(self, event):
        """Handle Shift+Enter key press (insert newline)"""
        return None
    def get_pet_personality_prompt(self):
        """Get the pet's personality prompt for AI responses"""
        pet_name = getattr(self.pet_manager, 'name', 'Pet')
        context_info = ""
        if hasattr(self.pet_manager, 'context_awareness'):
            context = self.pet_manager.context_awareness.get_current_context()
            if context:
                app_name = context.get('app_name', 'Unknown')
                window_title = context.get('title', 'Unknown')
                context_info = f"\n\nCurrent context: The user is currently using {app_name} (window title: '{window_title}')."
        return f"You are {pet_name}, a friendly virtual pet. Respond in character as a cute, helpful pet companion. Keep responses conversational and engaging, but not too long.{context_info}"
    def initialize_gemini_model(self):
        """Initialize the Gemini AI model"""
        try:
            if not GENAI_AVAILABLE:
                return False
            if not self.api_key:
                return False
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.selected_model)
            return True
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            return False
    def start_thinking_animation(self):
        """Start the thinking animation"""
        try:
            if hasattr(self.pet_manager, 'speech_bubble'):
                self.pet_manager.speech_bubble.show_bubble('default', 'Thinking...', use_typewriter=False)
            else:
                print("No speech_bubble found on pet_manager")
        except Exception as e:
            print(f"Error starting thinking animation: {e}")
            import traceback
            traceback.print_exc()
    def stop_thinking_animation(self):
        """Stop the thinking animation"""
        if self.response_bubble_active:
            return
        try:
            if hasattr(self.pet_manager, 'speech_bubble'):
                self.pet_manager.speech_bubble.clear_bubble()
            else:
                print("No speech_bubble found on pet_manager")
        except Exception as e:
            print(f"Error stopping thinking animation: {e}")
            import traceback
            traceback.print_exc()
    def _get_friendly_error_message(self, error_str):
        """Convert technical error messages to user-friendly ones"""
        if "API key" in error_str.lower():
            return "Oops! There seems to be an issue with the API key. Please check your settings."
        elif "model" in error_str.lower():
            return "Sorry! I'm having trouble with the AI model. Please try again or check your settings."
        elif "ollama" in error_str.lower() and ("connect" in error_str.lower() or "connection" in error_str.lower()):
            return "Ollama is not running."
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            return "I can't connect to the AI service right now. Please check your internet connection."
        else:
            return "Sorry! I encountered an unexpected error. Please try again."
    def show_ai_response(self, response):
        self.stop_thinking_animation()
        self.is_typing = False
        if response and response.strip():
            try:
                if hasattr(self.pet_manager, 'speech_bubble') and self.pet_manager.speech_bubble:
                    self.pet_manager.speech_bubble.show_bubble('custom', response)
                    self.response_bubble_active = True
                else:
                    print("Speech bubble not found on pet_manager")
            except Exception as e:
                print(f"Failed to display AI response: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No response to display: '{response}'")
    def show_typewriter_response(self, full_text):
        if self.is_typing:
            return
        if not full_text or not full_text.strip():
            self.is_typing = False
            return
        self.show_ai_response(full_text)
    def update_thinking_text(self):
        """Update the thinking bubble with animated dots"""
        if not self.is_typing:
            dots = "." * ((self.thinking_dots % 3) + 1)
            self.pet_manager.speech_bubble.show_bubble('default', f'Thinking{dots}')
            self.thinking_dots += 1
            if hasattr(self, 'thinking_timer'):
                try:
                    self.pet_manager.root.after_cancel(self.thinking_timer)
                except ValueError:
                    pass
            self.thinking_timer = self.pet_manager.root.after(800, self.update_thinking_text)
    def close_chat_window(self):
        self.reset_typing_state()
        if self.chat_window:
            self.chat_window.destroy()
            self.chat_window = None
    def reset_typing_state(self):
        """Reset all typing-related state variables"""
        if self.typing_timer:
            try:
                self.pet_manager.root.after_cancel(self.typing_timer)
            except ValueError:
                pass
            self.typing_timer = None
        if hasattr(self, 'thinking_timer') and self.thinking_timer:
            try:
                self.pet_manager.root.after_cancel(self.thinking_timer)
            except ValueError:
                pass
            self.thinking_timer = None
        self.is_typing = False
        if not self.response_bubble_active:
            self.stop_thinking_animation()
        else:
            self.pet_manager.root.after(self.pet_manager.speech_bubble.bubble_duration,
                                       lambda: setattr(self, 'response_bubble_active', False))
        if hasattr(self, 'message_entry') and self.message_entry:
            try:
                self.message_entry.config(state='normal')
            except tk.TclError:
                pass
class ConversationHistoryWindow:
    def __init__(self, parent, chat_system):
        self.parent = parent
        self.chat_system = chat_system
        self.history_window = None
    def show(self):
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.lift()
            return
        self.history_window = tk.Toplevel(self.parent)
        self.history_window.title("Conversation History")
        self.history_window.geometry("700x500")
        self.history_window.resizable(True, True)
        self.history_window.transient(self.parent)
        self.history_window.grab_set()
        self.history_window.update_idletasks()
        x = (self.history_window.winfo_screenwidth() // 2) - (self.history_window.winfo_width() // 2)
        y = (self.history_window.winfo_screenheight() // 2) - (self.history_window.winfo_height() // 2)
        self.history_window.geometry(f"+{x}+{y}")
        self.create_history_interface()
    def create_history_interface(self):
        main_frame = ttk.Frame(self.history_window, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        title_label = ttk.Label(main_frame, text="Conversation History",
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        sessions_frame = ttk.LabelFrame(main_frame, text="Conversation Sessions", padding=(5, 5))
        sessions_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(sessions_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sessions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate_sessions(scrollable_frame)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        from unified_ui import SimpleButton, COLORS
        clear_button = SimpleButton(buttons_frame, text="Clear All History",
                                  command=self.clear_all_history,
                                  bg=COLORS['error'], fg="white")
        clear_button.pack(side=tk.LEFT)
        close_button = SimpleButton(buttons_frame, text="Close",
                                  command=self.history_window.destroy,
                                  bg=COLORS['secondary'], fg="white")
        close_button.pack(side=tk.RIGHT)
    def populate_sessions(self, parent_frame):
        """Populate the sessions list"""
        if not self.chat_system.conversation_history:
            no_history_label = ttk.Label(parent_frame,
                                        text="No conversation history yet.\nStart chatting with your pet to see conversations here!",
                                        font=('Arial', 10),
                                        foreground='#666666',
                                        justify=tk.CENTER)
            no_history_label.pack(pady=20)
            return
        sorted_sessions = sorted(self.chat_system.conversation_history,
                               key=lambda x: x['start_time'], reverse=True)
        for i, session in enumerate(sorted_sessions):
            self.create_session_widget(parent_frame, session, i)
    def create_session_widget(self, parent, session, index):
        """Create a widget for a single conversation session"""
        session_frame = ttk.LabelFrame(parent, padding=(10, 5))
        session_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        start_time = datetime.fromisoformat(session['start_time'])
        formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        message_count = len(session['messages'])
        header_text = f"Session {index + 1} - {formatted_time} ({message_count} messages)"
        header_label = ttk.Label(session_frame, text=header_text, font=('Arial', 10, 'bold'))
        header_label.pack(anchor=tk.W)
        if session['messages']:
            preview_frame = ttk.Frame(session_frame)
            preview_frame.pack(fill=tk.X, pady=(5, 0))
            first_msg = session['messages'][0]
            preview_text = f"You: {first_msg['user_message'][:100]}{'...' if len(first_msg['user_message']) > 100 else ''}"
            preview_label = ttk.Label(preview_frame, text=preview_text,
                                    font=('Arial', 9), foreground='#666666')
            preview_label.pack(anchor=tk.W)
        buttons_frame = ttk.Frame(session_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        from unified_ui import SimpleButton, COLORS
        view_button = SimpleButton(buttons_frame, text="View Full Conversation",
                                 command=lambda s=session: self.show_full_conversation(s),
                                 bg=COLORS['info'], fg="white")
        view_button.pack(side=tk.LEFT, padx=(0, 5))
        continue_button = SimpleButton(buttons_frame, text="Continue Conversation",
                                     command=lambda s=session: self.continue_conversation(s),
                                     bg=COLORS['primary'], fg="white")
        continue_button.pack(side=tk.LEFT)
    def show_full_conversation(self, session):
        """Show the full conversation in a new window"""
        conv_window = tk.Toplevel(self.history_window)
        conv_window.title(f"Conversation - {datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d %H:%M')}")
        conv_window.geometry("600x400")
        conv_window.resizable(True, True)
        main_frame = ttk.Frame(conv_window, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10),
                             state=tk.DISABLED, bg='#f8f9fa')
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=text_scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        for i, message in enumerate(session['messages']):
            timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')
            text_widget.insert(tk.END, f"[{timestamp}] You: ", 'user_label')
            text_widget.insert(tk.END, f"{message['user_message']}\n\n", 'user_text')
            text_widget.insert(tk.END, f"[{timestamp}] {self.chat_system.pet_manager.name}: ", 'ai_label')
            text_widget.insert(tk.END, f"{message['ai_response']}\n\n", 'ai_text')
        text_widget.tag_configure('user_label', foreground='#2196F3', font=('Arial', 10, 'bold'))
        text_widget.tag_configure('user_text', foreground='#333333')
        text_widget.tag_configure('ai_label', foreground='#4CAF50', font=('Arial', 10, 'bold'))
        text_widget.tag_configure('ai_text', foreground='#333333')
        text_widget.config(state=tk.DISABLED)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        from unified_ui import SimpleButton, COLORS
        copy_button = SimpleButton(buttons_frame, text="Copy All Text",
                                 command=lambda: self.copy_conversation_text(session),
                                 bg=COLORS['secondary'], fg="white")
        copy_button.pack(side=tk.LEFT)
        continue_button = SimpleButton(buttons_frame, text="Continue This Conversation",
                                     command=lambda: [self.continue_conversation(session), conv_window.destroy()],
                                     bg=COLORS['primary'], fg="white")
        continue_button.pack(side=tk.LEFT, padx=(5, 0))
        close_button = SimpleButton(buttons_frame, text="Close",
                                  command=conv_window.destroy,
                                  bg=COLORS['text_light'], fg="white")
        close_button.pack(side=tk.RIGHT)
    def copy_conversation_text(self, session):
        """Copy the entire conversation to clipboard"""
        conversation_text = f"Conversation from {datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for message in session['messages']:
            timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')
            conversation_text += f"[{timestamp}] You: {message['user_message']}\n\n"
            conversation_text += f"[{timestamp}] {self.chat_system.pet_manager.name}: {message['ai_response']}\n\n"
        self.history_window.clipboard_clear()
        self.history_window.clipboard_append(conversation_text)
        messagebox.showinfo("Copied", "Conversation copied to clipboard!")
    def continue_conversation(self, session):
        """Continue the selected conversation"""
        self.chat_system.continue_conversation_from_history(session['session_id'])
        self.history_window.destroy()
    def clear_all_history(self):
        """Clear all conversation history"""
        if messagebox.askyesno("Clear History",
                              "Are you sure you want to delete all conversation history?\nThis action cannot be undone."):
            self.chat_system.conversation_history = []
            self.chat_system.current_session_id = None
            self.chat_system.save_conversation_history()
            self.history_window.destroy()
            self.show()
class ChatProviderDialog:
    def __init__(self, parent, chat_system):
        self.parent = parent
        self.chat_system = chat_system
        self.dialog = None
        self.ollama_model_menu = None
        self.ollama_no_models_label = None
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Choose AI Provider")
        self.dialog.geometry("400x550")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        main_container = ttk.Frame(self.dialog)
        main_container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(main_container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        def _on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        content_frame = ttk.Frame(scrollable_frame, padding=(15, 15))
        content_frame.pack(fill=tk.BOTH, expand=True)
        title_label = ttk.Label(content_frame, text="Choose Your AI Provider", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15), anchor='w')
        provider_frame = ttk.LabelFrame(content_frame, text="Select Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 15))
        self.provider_var = tk.StringVar(value=self.chat_system.chat_provider)
        ttk.Radiobutton(provider_frame, text="Google Gemini (Cloud)", variable=self.provider_var, value='gemini', command=self.on_provider_change).pack(anchor='w', pady=2)
        ttk.Radiobutton(provider_frame, text="Ollama (Local)", variable=self.provider_var, value='ollama', command=self.on_provider_change).pack(anchor='w', pady=2)
        self.gemini_frame = ttk.LabelFrame(content_frame, text="Google Gemini Settings", padding=10)
        self.gemini_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(self.gemini_frame, text="API Key:").pack(anchor='w')
        self.api_key_entry = ttk.Entry(self.gemini_frame, show="*", font=('Courier', 9))
        self.api_key_entry.pack(fill=tk.X, pady=5)
        if self.chat_system.api_key:
            self.api_key_entry.insert(0, self.chat_system.api_key)
        ttk.Label(self.gemini_frame, text="Model:").pack(anchor='w')
        self.model_var = tk.StringVar(value=self.chat_system.selected_model)
        # Create display names for models that include free/paid information
        model_display_names = []
        self.model_key_to_display = {}
        self.model_display_to_key = {}
        for model_key, model_info in AVAILABLE_MODELS.items():
            display_name = f"{model_info['name']} ({'Free' if model_info['free'] else 'Paid'})"
            model_display_names.append(display_name)
            self.model_key_to_display[model_key] = display_name
            self.model_display_to_key[display_name] = model_key
        
        # Set the initial display value
        initial_display = self.model_key_to_display.get(self.chat_system.selected_model, self.chat_system.selected_model)
        self.model_display_var = tk.StringVar(value=initial_display)
        self.gemini_model_menu = ttk.Combobox(self.gemini_frame, textvariable=self.model_display_var, values=model_display_names, state="readonly")
        self.gemini_model_menu.pack(fill=tk.X, pady=5)
        self.ollama_frame = ttk.LabelFrame(content_frame, text="Ollama Settings", padding=10)
        self.ollama_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(self.ollama_frame, text="Make sure Ollama is running locally.", font=('Arial', 9), foreground='#666').pack(anchor='w')
        ttk.Label(self.ollama_frame, text="Available Models:").pack(anchor='w', pady=(5,0))
        self.ollama_models = self.chat_system.get_ollama_models()
        self.ollama_model_var = tk.StringVar(value=self.chat_system.ollama_model)
        if self.chat_system.chat_provider == 'ollama' and self.chat_system.ollama_model:
            if self.chat_system.ollama_model not in self.ollama_models:
                messagebox.showwarning("Model Not Found",
                                     f"The previously selected Ollama model '{self.chat_system.ollama_model}' is no longer available. Please select a different model.")
        if self.ollama_models:
            self.ollama_model_menu = ttk.Combobox(self.ollama_frame, textvariable=self.ollama_model_var, values=self.ollama_models, state="readonly")
            self.ollama_model_menu.pack(fill=tk.X, pady=5)
        else:
            self.ollama_no_models_label = ttk.Label(self.ollama_frame, text="No Ollama models found.", font=('Arial', 9), foreground='#ff6666')
            self.ollama_no_models_label.pack(anchor='w', pady=5)
        self.instructions_label = ttk.Label(content_frame, text="", font=('Arial', 9), justify=tk.LEFT)
        self.instructions_label.pack(fill=tk.X, pady=5)
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        from unified_ui import SimpleButton, COLORS
        save_button = SimpleButton(button_frame, text="Save & Test", command=self.save_and_test, bg=COLORS['success'], fg="white")
        save_button.pack(side=tk.RIGHT)
        cancel_button = SimpleButton(button_frame, text="Cancel", command=self.cancel, bg=COLORS['error'], fg="white")
        cancel_button.pack(side=tk.RIGHT, padx=5)
        if self.chat_system.chat_provider == 'gemini':
            for child in self.gemini_frame.winfo_children():
                child.config(state='normal')
            for child in self.ollama_frame.winfo_children():
                child.config(state='disabled')
        else:
            for child in self.ollama_frame.winfo_children():
                child.config(state='normal')
            for child in self.gemini_frame.winfo_children():
                child.config(state='disabled')
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    def on_provider_change(self):
        provider = self.provider_var.get()
        if provider == 'gemini':
            for child in self.gemini_frame.winfo_children():
                child.config(state='normal')
            for child in self.ollama_frame.winfo_children():
                child.config(state='disabled')
            # Update the model dropdown with current selection
            if hasattr(self, 'model_display_var') and hasattr(self, 'model_key_to_display'):
                current_model = self.chat_system.selected_model
                display_name = self.model_key_to_display.get(current_model, current_model)
                self.model_display_var.set(display_name)
            instructions_text = """For Google Gemini:
1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Paste it above
4. Select your preferred model"""
        else:
            self.ollama_models = self.chat_system.get_ollama_models()
            self.ollama_model_var = tk.StringVar(value=self.chat_system.ollama_model)
            if self.ollama_model_menu:
                self.ollama_model_menu.destroy()
                self.ollama_model_menu = None
            if self.ollama_no_models_label:
                self.ollama_no_models_label.destroy()
                self.ollama_no_models_label = None
            if self.ollama_models:
                self.ollama_model_menu = ttk.Combobox(self.ollama_frame, textvariable=self.ollama_model_var, values=self.ollama_models, state="readonly")
                self.ollama_model_menu.pack(fill=tk.X, pady=5)
                if self.chat_system.ollama_model and self.chat_system.ollama_model not in self.ollama_models:
                    messagebox.showwarning("Model Not Found",
                                         f"The previously selected Ollama model '{self.chat_system.ollama_model}' is no longer available. Please select a different model.")
            else:
                self.ollama_no_models_label = ttk.Label(self.ollama_frame, text="No Ollama models found.", font=('Arial', 9), foreground='#ff6666')
                self.ollama_no_models_label.pack(anchor='w', pady=5)
            for child in self.ollama_frame.winfo_children():
                child.config(state='normal')
            for child in self.gemini_frame.winfo_children():
                child.config(state='disabled')
            instructions_text = """For Ollama:
1. Install Ollama from https://ollama.ai
2. Run: ollama serve
3. Install models: ollama pull llama3.2
4. Select a model above"""
        if hasattr(self, 'instructions_label'):
            self.instructions_label.config(text=instructions_text)
    def cancel(self):
        """Cancel the dialog without saving changes"""
        if self.dialog:
            self.dialog.destroy()
        self.dialog = None
    def save_and_test(self):
        provider = self.provider_var.get()
        self.chat_system.reset_typing_state()
        if provider == 'gemini':
            api_key = self.api_key_entry.get().strip()
            if not api_key:
                messagebox.showerror("Error", "Please enter a Google Gemini API key.")
                return
            selected_model_display = self.model_display_var.get()
            selected_model = self.model_display_to_key.get(selected_model_display, selected_model_display)
            if self.chat_system.save_settings(api_key=api_key, selected_model=selected_model,
                                            chat_provider='gemini'):
                if self.chat_system.initialize_gemini_model():
                    messagebox.showinfo("Success", "Gemini settings saved and tested successfully!")
                    self.dialog.destroy()
                    self.chat_system.create_chat_window()
                else:
                    messagebox.showerror("Error", "Failed to initialize Gemini. Please check your API key.")
        elif provider == 'ollama':
            selected_model = self.ollama_model_var.get()
            if not selected_model:
                messagebox.showerror("Error", "Please select an Ollama model.")
                return
            if self.chat_system.save_settings(chat_provider='ollama', ollama_model=selected_model):
                messagebox.showinfo("Success", "Ollama settings saved successfully!")
                self.dialog.destroy()
                self.chat_system.create_chat_window()