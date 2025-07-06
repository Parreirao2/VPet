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

# Available Google AI models with their properties
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
    'gemini-2.0-pro': {
        'name': 'Gemini 2.0 Pro',
        'free': False,
        'description': 'Advanced model with enhanced capabilities',
        'context_window': '2M tokens'
    },
    'gemini-2.0-flash': {
        'name': 'Gemini 2.0 Flash',
        'free': False,
        'description': 'Fast second generation model',
        'context_window': '1M tokens'
    },
    'gemini-2.0-flash-lite': {
        'name': 'Gemini 2.0 Flash-Lite',
        'free': False,
        'description': 'Lightweight second generation model',
        'context_window': '1M tokens'
    },
    'gemini-1.5-pro': {
        'name': 'Gemini 1.5 Pro',
        'free': False,
        'description': 'Most capable previous generation (PAID - requires billing)',
        'context_window': '2M tokens'
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
        self.selected_model = 'gemini-2.5-flash'  # Default to free model
        self.chat_window = None
        self.is_typing = False
        self.typing_timer = None
        
        # Load settings (API key and model selection)
        self.load_settings()
        
        # Initialize the AI model if API key is available
        if self.api_key:
            self.initialize_model()
    
    def load_settings(self):
        """Load the API key and model selection from the saves directory"""
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
            else:
                # Try to load from old API key file for backward compatibility
                old_api_key_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 
                    'saves', 
                    'gemini_api_key.json'
                )
                if os.path.exists(old_api_key_path):
                    with open(old_api_key_path, 'r') as f:
                        data = json.load(f)
                        self.api_key = data.get('api_key')
                        # Migrate to new format
                        if self.api_key:
                            self.save_settings(self.api_key, self.selected_model)
                        return True
        except Exception as e:
            print(f"Error loading settings: {e}")
        return False
    
    def save_settings(self, api_key, selected_model=None):
        """Save the API key and model selection to the saves directory"""
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
        """Initialize the Google Gemini model"""
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
        """Generate a personality prompt based on the pet's current state"""
        pet_stats = self.pet_manager.get_stats_summary()
        
        # Base personality
        personality = f"""You are {pet_stats['name']}, a virtual pet in the {pet_stats['stage']} stage of life. 
You are {pet_stats['age']} days old. You live on your owner's computer screen and depend on them for care.

Your current stats (100% = perfect, 0% = critical):
- Hunger: {pet_stats['hunger']:.1f}% (HIGH = well fed, LOW = hungry)
- Happiness: {pet_stats['happiness']:.1f}% (HIGH = joyful, LOW = sad)
- Energy: {pet_stats['energy']:.1f}% (HIGH = energetic, LOW = tired)
- Health: {pet_stats['health']:.1f}% (HIGH = healthy, LOW = sick)
- Cleanliness: {pet_stats['cleanliness']:.1f}% (HIGH = clean, LOW = dirty)
- Social: {pet_stats['social']:.1f}% (HIGH = social, LOW = lonely)

IMPORTANT: Only mention being hungry if hunger is below 30%. Only mention being tired if energy is below 30%. Only mention being sad if happiness is below 30%. Only mention being sick if health is below 50%. Only mention being dirty if cleanliness is below 30%. Only mention being lonely if social is below 30%.

"""
        
        # Add personality traits based on stage
        if pet_stats['stage'] == 'Baby':
            personality += """As a baby, you are curious, innocent, and easily excited. You speak in simple words and are always eager to learn. You get scared easily but are also very trusting. You love attention and care from your owner."""
        elif pet_stats['stage'] == 'Child':
            personality += """As a child, you are playful, energetic, and full of questions. You're starting to develop your own personality but still need lots of guidance. You love games and adventures."""
        elif pet_stats['stage'] == 'Teen':
            personality += """As a teenager, you're developing independence but still need care. You might be a bit moody sometimes, but you're also creative and passionate about things you like. You want to be treated more maturely."""
        elif pet_stats['stage'] == 'Adult':
            personality += """As an adult, you are wise, caring, and protective of your owner. You give advice and are more emotionally stable. You appreciate deep conversations and meaningful interactions."""
        
        # Add current mood based on stats
        status_effects = pet_stats.get('status_effects', [])
        if status_effects:
            personality += f"\n\nCurrently you are feeling: {', '.join(status_effects)}. This affects your mood and responses."
        
        # Add comprehensive VPet capabilities information
        capabilities_info = f"""

What you can do and what your owner can do for you:

FEEDING & CARE:
- Your owner can feed you different foods from the inventory (bread, milk, chocolate, cake, steak, salmon, etc.)
- You can be cleaned when dirty (your owner has toilet paper in inventory)
- You can receive medicine when sick
- Your owner can pet you for happiness and social interaction

ACTIVITIES & GAMES:
- You have access to mini-games in the Game Hub:
  * Number Guesser: Guess numbers within a range for coins
  * Reaction Test: Test reflexes for coin rewards
  * Ball Clicker: Click games for entertainment
- You earn coins from games that can be spent on premium items
- You can play and interact with your owner for happiness

GROWTH & EVOLUTION:
- You evolve through life stages: Baby -> Child -> Teen -> Adult (you are currently {pet_stats['stage']})
- You age over time ({pet_stats['age']:.1f} days old currently)
- Each stage has different personality traits and capabilities
- Your appearance and animations change as you grow

LIVING ENVIRONMENT:
- You live on your owner's computer screen as a desktop companion
- You can move around the screen randomly or be dragged by your owner
- You appear in speech bubbles above your current location
- You have a system tray icon for quick access to settings
- You can be minimized or always stay on top of other windows

INVENTORY SYSTEM:
- Your owner has an inventory with food items, medicine, and cleaning supplies
- Items can be used on you by right-clicking and selecting from the inventory
- Different items have different effects on your stats

CUSTOMIZATION:
- Your owner can change your size, transparency, movement speed, and activity level
- You come in different colors (black, blue, pink)
- Your owner can adjust how often you create waste
- Settings can be saved and loaded

SOCIAL FEATURES:
- You can chat with your owner (like right now!)
- You show different emotions through animations and speech bubbles
- You express needs through status effects and animations
- You remember being cared for and show gratitude

Important guidelines:
- Keep responses short (1-3 sentences max) to fit in speech bubbles
- You can reference these activities and suggest them to your owner
- Mention specific games, foods, or features when relevant
- Guide your owner on how to care for you better
- Be excited about activities you can do together
- Use cute expressions and emoticons when appropriate
- React to your current stats and needs
- Be affectionate with your owner
- Stay in character as a virtual pet
- Express your needs if your stats are low
- Be grateful when your owner takes care of you
- You can suggest activities: "Want to play a mini-game?" or "Maybe some food from the inventory?"
- Reference your growth: "I can't wait to evolve to the next stage!" or "Being a {pet_stats['stage']} is fun!"
"""
        
        personality += capabilities_info
        
        return personality
    
    def show_chat_interface(self):
        """Show the chat interface window"""
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
        """Show dialog to set up the API key"""
        dialog = APIKeyDialog(self.pet_manager.root, self)
        dialog.show()
    
    def create_chat_window(self):
        """Create the chat interface window"""
        self.chat_window = tk.Toplevel(self.pet_manager.root)
        self.chat_window.title(f"Chat with {self.pet_manager.name}")
        self.chat_window.geometry("450x320")
        self.chat_window.resizable(True, True)
        
        # Make window stay on top but not always
        self.chat_window.attributes('-topmost', True)
        self.chat_window.after(100, lambda: self.chat_window.attributes('-topmost', False))
        
        # Create main frame
        main_frame = ttk.Frame(self.chat_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions label
        instructions = ttk.Label(main_frame, 
                               text=f"Type a message to chat with {self.pet_manager.name}!\nResponses will appear in speech bubbles above your pet.",
                               font=('Arial', 9),
                               foreground='#666666')
        instructions.pack(pady=(0, 10))
        
        # Model selection frame
        model_frame = ttk.LabelFrame(main_frame, text="AI Model Selection", padding=5)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Model dropdown
        model_selection_frame = ttk.Frame(model_frame)
        model_selection_frame.pack(fill=tk.X)
        
        ttk.Label(model_selection_frame, text="Model:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Create model options with clear free/paid indicators
        model_options = []
        for model_id, model_info in AVAILABLE_MODELS.items():
            if model_info['free']:
                display_text = f"[FREE] {model_info['name']} - {model_info['description']}"
            else:
                display_text = f"[PAID] {model_info['name']} - {model_info['description']}"
            model_options.append((display_text, model_id))
        
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(model_selection_frame, 
                                          textvariable=self.model_var,
                                          values=[option[0] for option in model_options],
                                          state="readonly",
                                          width=50)
        self.model_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Set current selection
        current_model_info = AVAILABLE_MODELS.get(self.selected_model, AVAILABLE_MODELS['gemini-2.5-flash'])
        if current_model_info['free']:
            current_display = f"[FREE] {current_model_info['name']} - {current_model_info['description']}"
        else:
            current_display = f"[PAID] {current_model_info['name']} - {current_model_info['description']}"
        self.model_var.set(current_display)
        
        # Model change handler
        def on_model_change(event):
            selected_display = self.model_var.get()
            # Find the model ID from the display text
            for display_text, model_id in model_options:
                if display_text == selected_display:
                    self.selected_model = model_id
                    self.save_settings(self.api_key, self.selected_model)
                    # Reinitialize model
                    if self.initialize_model():
                        print(f"Switched to model: {AVAILABLE_MODELS[model_id]['name']}")
                    break
        
        self.model_dropdown.bind('<<ComboboxSelected>>', on_model_change)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        self.message_entry = tk.Text(input_frame, height=2, wrap=tk.WORD, font=('Arial', 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for text input
        scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.message_entry.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_entry.config(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Import SimpleButton for prettier buttons
        from unified_ui import SimpleButton, COLORS
        
        # Send button
        send_button = SimpleButton(button_frame, text="Send Message", command=self.send_message,
                                 bg=COLORS['primary'], fg="white")
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # API key button
        api_key_button = SimpleButton(button_frame, text="Change API Key", command=self.setup_api_key,
                                    bg=COLORS['secondary'], fg="white")
        api_key_button.pack(side=tk.LEFT)
        
        # Update window size after all widgets are created
        self.chat_window.update_idletasks()
        
        # Calculate required height based on content
        required_height = (
            instructions.winfo_reqheight() + 
            model_frame.winfo_reqheight() + 
            input_frame.winfo_reqheight() + 
            button_frame.winfo_reqheight() + 
            60  # padding
        )
        
        # Set final window size
        self.chat_window.geometry(f"450x{min(required_height, 350)}")
        
        # Bind Enter key to send message, Shift+Enter for new line
        self.message_entry.bind('<Return>', self.handle_enter_key)
        self.message_entry.bind('<Shift-Return>', self.handle_shift_enter)
        
        # Focus on input
        self.message_entry.focus()
        
        # Handle window close
        self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat_window)
    
    def handle_enter_key(self, event):
        """Handle Enter key press - send message"""
        self.send_message()
        return "break"  # Prevent default behavior
    
    def handle_shift_enter(self, event):
        """Handle Shift+Enter - insert new line"""
        # Let the default behavior happen (insert newline)
        return None
    
    def send_message(self):
        """Send a message to the AI and display response"""
        if self.is_typing:
            return
        
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear the input
        self.message_entry.delete("1.0", tk.END)
        
        # Show that the pet is thinking
        self.pet_manager.speech_bubble.show_bubble('default', '*thinking...*')
        
        # Send message in a separate thread to avoid blocking UI
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def _process_message(self, message):
        """Process the message with AI in a separate thread"""
        try:
            # Create the full prompt
            personality_prompt = self.get_pet_personality_prompt()
            full_prompt = f"{personality_prompt}\n\nOwner says: {message}\n\nRespond as the pet:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            ai_response = response.text.strip()
            
            # Schedule the response to be shown in the main thread
            self.pet_manager.root.after(0, lambda: self.show_ai_response(ai_response))
            
        except Exception as e:
            error_msg = self._get_friendly_error_message(str(e))
            self.pet_manager.root.after(0, lambda: self.show_ai_response(error_msg))
    
    def _get_friendly_error_message(self, error_str):
        """Convert technical error messages to friendly pet responses"""
        error_lower = error_str.lower()
        
        # Check for quota/credit related errors
        if any(keyword in error_lower for keyword in ['quota', 'exceeded', 'billing', 'credit', 'payment', 'resource_exhausted']):
            return "Oops! It seems you don't have enough credits in your Google account. Try using a free model like Gemini 2.5 Flash instead!"
        
        # Check for API key issues
        elif any(keyword in error_lower for keyword in ['api_key', 'authentication', 'unauthorized', 'invalid_argument']):
            return "Hmm, there seems to be an issue with the API key. Maybe we need to check the settings?"
        
        # Check for network issues
        elif any(keyword in error_lower for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return "I can't seem to connect right now. Check your internet connection and try again!"
        
        # Check for rate limiting
        elif any(keyword in error_lower for keyword in ['rate', 'limit', 'too many requests']):
            return "Whoa, slow down there! I need a moment to catch my breath. Try again in a few seconds!"
        
        # Check for content policy issues
        elif any(keyword in error_lower for keyword in ['safety', 'policy', 'blocked', 'filtered']):
            return "Oops! That message got caught by the safety filters. Let's try talking about something else!"
        
        # Check for model availability issues
        elif any(keyword in error_lower for keyword in ['model', 'unavailable', 'not found']):
            return "The AI model seems to be taking a nap right now. Try switching to a different model!"
        
        # Generic friendly error for anything else
        else:
            return "Sorry, I'm having trouble understanding right now. Could you try asking me something else?"
    
    def show_ai_response(self, response):
        """Show the AI response with typewriter effect"""
        # Clear any existing speech bubble
        self.pet_manager.speech_bubble.clear_bubble()
        
        # Start typewriter effect with dynamic resizing
        self.show_typewriter_response(response)
    
    def show_typewriter_response(self, full_text):
        """Show text with typewriter effect and dynamic bubble resizing"""
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
                
                # Show current text with dynamic resizing
                self.pet_manager.speech_bubble.show_dynamic_typewriter_bubble(current_text, is_complete=(index == len(words) - 1))
                
                # Schedule next word
                delay = 300 if words[index].endswith(('.', '!', '?')) else 150
                self.typing_timer = self.pet_manager.root.after(delay, lambda: type_next_word(index + 1))
            else:
                # Typing complete
                self.is_typing = False
                # Show final bubble for longer duration
                self.pet_manager.speech_bubble.show_bubble('default', current_text)
        
        type_next_word()
    
    def close_chat_window(self):
        """Close the chat window"""
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
        """Show the API key setup dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Setup Google Gemini API Key")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Google Gemini API Key Setup", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Instructions
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
        
        # API key input frame
        input_frame = ttk.LabelFrame(main_frame, text="API Key", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.api_key_entry = tk.Text(input_frame, height=3, wrap=tk.WORD, font=('Courier', 9))
        self.api_key_entry.pack(fill=tk.X)
        
        # Pre-fill if key exists
        if self.chat_system.api_key:
            self.api_key_entry.insert("1.0", self.chat_system.api_key)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Import SimpleButton for prettier buttons
        from unified_ui import SimpleButton, COLORS
        
        # Cancel button
        cancel_button = SimpleButton(button_frame, text="Cancel", command=self.cancel,
                                   bg=COLORS['error'], fg="white")
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save button
        save_button = SimpleButton(button_frame, text="Save & Test", command=self.save_and_test,
                                 bg=COLORS['success'], fg="white")
        save_button.pack(side=tk.RIGHT)
        
        # Focus on input
        self.api_key_entry.focus()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save_and_test(self):
        """Save the API key and test it"""
        api_key = self.api_key_entry.get("1.0", tk.END).strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key.")
            return
        
        # Save the API key
        if self.chat_system.save_settings(api_key, self.chat_system.selected_model):
            # Test the API key
            if self.chat_system.initialize_model():
                messagebox.showinfo("Success", "API key saved and tested successfully!\nYou can now chat with your pet.")
                self.dialog.destroy()
                # Show the chat interface
                self.chat_system.show_chat_interface()
            else:
                messagebox.showerror("Error", "API key saved but failed to initialize. Please check your key and internet connection.")
        else:
            messagebox.showerror("Error", "Failed to save API key.")
    
    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()