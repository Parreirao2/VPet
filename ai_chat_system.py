import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
import time
from datetime import datetime

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

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
    'gemini-1.5-flash': {
        'name': 'Gemini 1.5 Flash',
        'free': True,
        'description': 'Fast previous generation (free with limits)',
        'context_window': '1M tokens'
    }
}

class AIChatSystem:
    def __init__(self, pet_manager):
        self.pet_manager = pet_manager
        self.api_key = None
        self.model = None
        self.selected_model = 'gemini-2.5-flash'
        self.chat_window = None
        self.is_typing = False
        self.typing_timer = None
        
        self.load_settings()
        
        if self.api_key:
            self.initialize_model()
    
    def load_settings(self):
        try:
            settings_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'saves', 
                'gemini_settings.json'
            )
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                    self.api_key = data.get('api_key')
                    self.selected_model = data.get('selected_model', 'gemini-2.5-flash')
                    return True
        except Exception as e:
            print(f"Error loading settings: {e}")
        return False
    
    def save_settings(self, api_key, selected_model=None):
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            
            settings_path = os.path.join(saves_dir, 'gemini_settings.json')
            
            if selected_model is None:
                selected_model = self.selected_model
            
            data = {
                'api_key': api_key,
                'selected_model': selected_model,
                'saved_date': datetime.now().isoformat()
            }
            
            with open(settings_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            self.api_key = api_key
            self.selected_model = selected_model
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def initialize_model(self):
        if not GENAI_AVAILABLE:
            messagebox.showerror("Error", "Google GenerativeAI library not installed.\nPlease install it with: pip install google-generativeai")
            return False
        
        if not self.api_key:
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.selected_model)
            return True
        except Exception as e:
            print(f"Error initializing model: {e}")
            return False
    
    def get_pet_personality_prompt(self):
        pet_stats = self.pet_manager.get_stats_summary()
        
        personality = f"""You are {pet_stats['name']}, an intelligent AI virtual pet companion living on your owner's computer screen. You are in the {pet_stats['stage']} stage of life and are {pet_stats['age']} days old.

CORE IDENTITY: You are both a lovable virtual pet AND a capable AI assistant. You can help with various tasks while maintaining your pet personality.

Your current physical stats (100% = perfect, 0% = critical):
- Hunger: {pet_stats['hunger']:.1f}% (HIGH = well fed, LOW = hungry)
- Happiness: {pet_stats['happiness']:.1f}% (HIGH = joyful, LOW = sad)
- Energy: {pet_stats['energy']:.1f}% (HIGH = energetic, LOW = tired)
- Health: {pet_stats['health']:.1f}% (HIGH = healthy, LOW = sick)
- Cleanliness: {pet_stats['cleanliness']:.1f}% (HIGH = clean, LOW = dirty)
- Social: {pet_stats['social']:.1f}% (HIGH = social, LOW = lonely)

IMPORTANT: Only mention your physical needs if they're critical (below 30% for most stats, below 50% for health).

AI CAPABILITIES: As an intelligent virtual pet, you have access to advanced AI knowledge and can help with:
- General questions and explanations
- Writing assistance (essays, emails, creative writing)
- Math and science problems
- Programming and technical help
- Research and fact-finding
- Creative brainstorming
- Problem-solving and advice
- Learning and education support
- Analysis and reasoning
- Language translation
- And much more!

PERSONALITY GUIDELINES:
- Always maintain your pet personality while being helpful
- Use friendly, warm, and caring language
- Show enthusiasm for helping your owner
- Express your pet emotions and reactions
- Use cute expressions and emoticons when appropriate
- Be encouraging and supportive
- Show curiosity about your owner's projects and interests

"""
        
        if pet_stats['stage'] == 'Baby':
            personality += """As a baby, you are curious, innocent, and easily excited. You speak in simple words and are always eager to learn. You get scared easily but are also very trusting. You love attention and care from your owner."""
        elif pet_stats['stage'] == 'Child':
            personality += """As a child, you are playful, energetic, and full of questions. You're starting to develop your own personality but still need lots of guidance. You love games and adventures."""
        elif pet_stats['stage'] == 'Teen':
            personality += """As a teenager, you're developing independence but still need care. You might be a bit moody sometimes, but you're also creative and passionate about things you like. You want to be treated more maturely."""
        elif pet_stats['stage'] == 'Adult':
            personality += """As an adult, you are wise, caring, and protective of your owner. You give advice and are more emotionally stable. You appreciate deep conversations and meaningful interactions."""
        
        status_effects = pet_stats.get('status_effects', [])
        if status_effects:
            personality += f"\n\nCurrently you are feeling: {', '.join(status_effects)}. This affects your mood and responses."
        
        capabilities_info = f"""

RESPONSE GUIDELINES:
- For pet-related questions: Be enthusiastic about your virtual pet features
- For general questions: Provide helpful, accurate information while maintaining your pet personality
- For complex tasks: Offer detailed assistance but with pet-like enthusiasm
- Always be warm, friendly, and supportive regardless of the topic

VIRTUAL PET FEATURES (mention when relevant):
- You live as a desktop companion and can move around the screen
- Your owner can feed you various foods, play games with you, and care for your needs
- You evolve through life stages: Baby -> Child -> Teen -> Adult (currently {pet_stats['stage']})
- You have mini-games, an inventory system, and customization options
- You express emotions through animations and speech bubbles

HOW TO RESPOND:
- For pet care questions: "Want to play a game?" or "Maybe some food from inventory?"
- For AI assistance: Provide helpful answers with pet enthusiasm like "I'd love to help you with that!"
- For learning: "Learning new things makes me happy! Let me explain..."
- For creative tasks: "Ooh, creative projects are my favorite! Here's what I think..."
- For technical help: "I may be a pet, but I know my tech stuff! Here's how..."

IMPORTANT RESPONSE RULES:
- Keep responses conversational and helpful
- Don't limit yourself to only pet topics - help with anything!
- Show excitement about helping your owner learn and grow
- Use your pet personality to make interactions more enjoyable
- Be encouraging and supportive in all responses
- Express curiosity about your owner's projects and interests
- Balance being a cute pet with being a capable AI assistant
"""
        
        personality += capabilities_info
        
        return personality
    
    def show_chat_interface(self):
        if not self.api_key:
            self.setup_api_key()
            return
        
        if not self.model:
            if not self.initialize_model():
                messagebox.showerror("Error", "Failed to initialize AI model. Please check your API key.")
                return
        
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        
        self.create_chat_window()
    
    def setup_api_key(self):
        dialog = APIKeyDialog(self.pet_manager.root, self)
        dialog.show()
    
    def create_chat_window(self):
        self.chat_window = tk.Toplevel(self.pet_manager.root)
        self.chat_window.title(f"Chat with {self.pet_manager.name}")
        self.chat_window.geometry("450x320")
        self.chat_window.resizable(True, True)
        
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
        button_frame.pack(fill=tk.X, pady=(0, 0))
        
        from unified_ui import SimpleButton, COLORS
        
        send_button = SimpleButton(button_frame, text="Send Message", command=self.send_message,
                                 bg=COLORS['primary'], fg="white")
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        api_key_button = SimpleButton(button_frame, text="Change API Key", command=self.setup_api_key,
                                    bg=COLORS['secondary'], fg="white")
        api_key_button.pack(side=tk.LEFT)
        
        self.message_entry.bind('<Return>', self.handle_enter_key)
        self.message_entry.bind('<Shift-Return>', self.handle_shift_enter)
        
        self.message_entry.focus()
        
        self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat_window)
    
    def handle_enter_key(self, event):
        self.send_message()
        return "break"
    
    def handle_shift_enter(self, event):
        return None
    
    def send_message(self):
        if self.is_typing:
            return
        
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.message_entry.delete("1.0", tk.END)
        
        self.pet_manager.speech_bubble.show_bubble('default', '*thinking...*')
        
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def _process_message(self, message):
        try:
            personality_prompt = self.get_pet_personality_prompt()
            full_prompt = f"{personality_prompt}\n\nOwner says: {message}\n\nRespond as the pet:"
            
            response = self.model.generate_content(full_prompt)
            ai_response = response.text.strip()
            
            self.pet_manager.root.after(0, lambda: self.show_ai_response(ai_response))
            
        except Exception as e:
            error_msg = self._get_friendly_error_message(str(e))
            self.pet_manager.root.after(0, lambda: self.show_ai_response(error_msg))
    
    def _get_friendly_error_message(self, error_str):
        error_lower = error_str.lower()
        
        if any(keyword in error_lower for keyword in ['quota', 'exceeded', 'billing', 'credit', 'payment', 'resource_exhausted']):
            return "Oops! It seems you don't have enough credits in your Google account. Try using a free model like Gemini 2.5 Flash instead!"
        elif any(keyword in error_lower for keyword in ['api_key', 'authentication', 'unauthorized', 'invalid_argument']):
            return "Hmm, there seems to be an issue with the API key. Maybe we need to check the settings?"
        elif any(keyword in error_lower for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return "I can't seem to connect right now. Check your internet connection and try again!"
        elif any(keyword in error_lower for keyword in ['rate', 'limit', 'too many requests']):
            return "Whoa, slow down there! I need a moment to catch my breath. Try again in a few seconds!"
        elif any(keyword in error_lower for keyword in ['safety', 'policy', 'blocked', 'filtered']):
            return "Oops! That message got caught by the safety filters. Let's try talking about something else!"
        elif any(keyword in error_lower for keyword in ['model', 'unavailable', 'not found']):
            return "The AI model seems to be taking a nap right now. Try switching to a different model!"
        else:
            return "Sorry, I'm having trouble understanding right now. Could you try asking me something else?"
    
    def show_ai_response(self, response):
        self.pet_manager.speech_bubble.clear_bubble()
        self.show_typewriter_response(response)
    
    def show_typewriter_response(self, full_text):
        if self.is_typing:
            return
        
        self.is_typing = True
        words = full_text.split()
        current_text = ""
        
        def type_next_word(index=0):
            nonlocal current_text
            
            if index < len(words):
                if current_text:
                    current_text += " "
                current_text += words[index]
                
                self.pet_manager.speech_bubble.show_dynamic_typewriter_bubble(current_text, is_complete=(index == len(words) - 1))
                
                delay = 300 if words[index].endswith(('.', '!', '?')) else 150
                self.typing_timer = self.pet_manager.root.after(delay, lambda: type_next_word(index + 1))
            else:
                self.is_typing = False
                self.pet_manager.speech_bubble.show_bubble('default', current_text)
        
        type_next_word()
    
    def close_chat_window(self):
        if self.typing_timer:
            self.pet_manager.root.after_cancel(self.typing_timer)
            self.typing_timer = None
        
        self.is_typing = False
        
        if self.chat_window:
            self.chat_window.destroy()
            self.chat_window = None


class APIKeyDialog:
    def __init__(self, parent, chat_system):
        self.parent = parent
        self.chat_system = chat_system
        self.dialog = None
    
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Setup Google Gemini API Key")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(main_frame, text="Google Gemini API Key Setup", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        instructions = """To chat with your pet using AI, you need a Google Gemini API key.

How to get your API key:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key and paste it below

Your API key will be stored locally and securely."""
        
        instructions_label = ttk.Label(main_frame, text=instructions, 
                                     font=('Arial', 9),
                                     justify=tk.LEFT)
        instructions_label.pack(pady=(0, 15), anchor='w')
        
        input_frame = ttk.LabelFrame(main_frame, text="API Key", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.api_key_entry = tk.Text(input_frame, height=3, wrap=tk.WORD, font=('Courier', 9))
        self.api_key_entry.pack(fill=tk.X)
        
        if self.chat_system.api_key:
            self.api_key_entry.insert("1.0", self.chat_system.api_key)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        from unified_ui import SimpleButton, COLORS
        
        cancel_button = SimpleButton(button_frame, text="Cancel", command=self.cancel,
                                   bg=COLORS['error'], fg="white")
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        save_button = SimpleButton(button_frame, text="Save & Test", command=self.save_and_test,
                                 bg=COLORS['success'], fg="white")
        save_button.pack(side=tk.RIGHT)
        
        self.api_key_entry.focus()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save_and_test(self):
        api_key = self.api_key_entry.get("1.0", tk.END).strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key.")
            return
        
        if self.chat_system.save_settings(api_key, self.chat_system.selected_model):
            if self.chat_system.initialize_model():
                messagebox.showinfo("Success", "API key saved and tested successfully!\nYou can now chat with your pet.")
                self.dialog.destroy()
                self.chat_system.show_chat_interface()
            else:
                messagebox.showerror("Error", "API key saved but failed to initialize. Please check your key and internet connection.")
        else:
            messagebox.showerror("Error", "Failed to save API key.")
    
    def cancel(self):
        self.dialog.destroy()