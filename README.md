<div align="center">

# 🐾 **Virtual Pet (VPet)** 
### *Your AI-Powered Desktop Companion*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Ollama-purple.svg)](#-ai-chat-system)

</div>

---

<div align="center">
  
![VPet Banner](img_assets/VPet_Demo.apng)

</div>

## 🌟 **Overview**

**VPet** is a revolutionary desktop virtual pet that combines classic Tamagotchi gameplay with cutting-edge AI technology. Your pet evolves through life stages, learns from interactions, and even chats with you using advanced AI models like **Google Gemini** and **Ollama**. It's not just a pet—it's your intelligent desktop companion.

---

## 🎭 **Pet Evolution Journey**

<div align="center">

| **Baby** | **Child** | **Teen** | **Adult** | **Special** |
|:--------:|:---------:|:--------:|:---------:|:-----------:|
| ![Baby](frames/Baby_Happy.png) | ![Child](frames/Child_Happy.png) | ![Teen](frames/Teen_Happy.png) | ![Adult](frames/Adult_Happy.png) | ??? |
| *Day 1-30* | *Day 31-60* | *Day 61-90* | *Day 91+* | *Secret* |

</div>

---

## ✨ **Core Features**

### 🤖 **AI Chat System** *(NEW: Ollama Support!)*
- **🧠 Multiple AI Models**: 
  - **Google Gemini** (7 models: Pro, Flash, Lite)
  - **🆕 Ollama** (Local AI - no internet required!)
- **🎯 Context-Aware**: Pet knows your apps and responds intelligently
- **💬 Natural Conversations**: Typewriter-style responses with personality
- **🔒 Privacy-First**: Local Ollama models keep your data private
- **🎭 Personality-Driven**: Responses adapt to your pet's mood and life stage

### 🎮 **Interactive Gameplay**
- **📊 6 Core Stats**: Hunger, Happiness, Energy, Health, Cleanliness, Social
- **🍔 80+ Food Items**: From bread to sushi, each with unique effects
- **🎲 3 Mini-Games**: Number Guesser, Reaction Test, Ball Clicker
- **💰 Economy System**: Earn coins through games and care activities
- **🧹 Realistic Care**: Clean up after your pet, manage hygiene

### 🏆 **Advanced Features**
- **👁️ Context Awareness**: Pet monitors your apps and comments intelligently
- **🎨 Customization**: Colors, sizes, transparency, behavior settings
- **💾 Auto-Save**: Never lose progress with 5-minute auto-saves
- **🖥️ Desktop Integration**: Always-on-top, multi-monitor support
- **🔄 Smart Evolution**: Natural aging or instant evolution items

---

## 🚀 **Quick Start**

### 📥 **Installation**
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/VPet.git
cd VPet

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run VPet
python main.py
```

### 🔑 **AI Setup**

#### **Option 1: Google Gemini** *(Cloud)*
1. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Enter key in VPet settings
3. Choose from 7 Gemini models

#### **Option 2: Ollama** *(Local - NEW!)*
1. Install [Ollama](https://ollama.ai) on your system
2. Download a model: `ollama pull llama2` or `ollama pull mistral`
3. Select "Ollama" in VPet AI settings
4. **Zero configuration needed** - works offline!

---

## 🎮 **How to Play**

### **Basic Controls**
| **Action** | **Result** |
|------------|------------|
| **Left Click** | Select pet |
| **Double Click** | Happiness boost (+10%) |
| **Right Click** | Open context menu |
| **Drag** | Move pet anywhere |

### **Daily Care Routine**
1. **🍽️ Feed** your pet when hungry
2. **🎮 Play** mini-games for coins and happiness
3. **🧹 Clean** up waste to maintain hygiene
4. **💬 Chat** with AI for social interaction
5. **😴 Let rest** when energy is low

---

## 🛒 **Shop & Items**

### **Food Categories**
| **Category** | **Price Range** | **Best For** |
|:-------------|:----------------|:-------------|
| **🥖 Bakery** | 15-35 coins | Quick hunger fix |
| **🍰 Desserts** | 20-60 coins | Happiness boost |
| **🍖 Main Dishes** | 30-70 coins | Full meals |
| **🍜 International** | 35-50 coins | Balanced stats |

### **Special Items**
- **🧻 Toilet Paper**: Clean waste (FREE)
- **🚿 Shower**: +15% cleanliness (FREE)
- **🧬 Evo1**: Instant evolution (10,000 coins)
- **✨ Evo2**: Secret special form (1,000,000 coins)

---

## 🎯 **Mini-Games**

<div align="center">

| **Game** | **Skill** | **Reward** | **Max Coins** |
|:---------|:----------|:-----------|:--------------|
| **🎲 Number Guesser** | Logic | 1-7+ coins | 7+ per level |
| **⚡ Reaction Test** | Speed | 1-7+ coins | 7+ per level |
| **🎯 Ball Clicker** | Precision | 1-7+ coins | 7+ per level |

</div>

---

## 🎨 **Customization Options**

### **Visual Settings**
- **🎨 Colors**: Black, Blue, Pink
- **📏 Sizes**: Tiny to Large
- **👻 Transparency**: 10% to 100%
- **🎭 Personality**: Active, Calm, Playful

### **Behavior Settings**
- **⚡ Speed**: Slow to Fast movement
- **💩 Poop Frequency**: Rare to Frequent
- **💬 Chat Frequency**: Minimal to Chatty
- **🔄 Auto-Start**: Launch with Windows

---

## 🏗️ **Technical Architecture**

### **Core Technologies**
```python
Python 3.8+          # Core language
Tkinter             # GUI framework
Pillow (PIL)        # Image processing
Pystray             # System tray integration
Google GenerativeAI # Gemini API
Ollama              # Local AI models
```

### **Project Structure**
```
VPet/
├── 📁 frames/               # Pet animations & sprites
├── 📁 img_assets/           # Food, items, UI graphics
├── 🐍 main.py              # Application entry point
├── 🧠 ai_chat_system.py    # AI chat with Gemini & Ollama
├── 🎮 game_hub.py          # Mini-games & currency
├── 💾 pet_components.py    # Core pet logic & stats
├── 🎬 pet_animation.py     # Animation & movement
├── 🛒 inventory_system.py  # Shop & items
├── 💰 currency_system.py   # Economy management
├── 🧹 poop_system.py       # Waste management & cleaning
├── 💬 speech_bubble.py     # Pet communication system
├── 🖥️ system_tray.py      # System tray integration
├── ⚙️ unified_ui.py        # Modern UI components & settings
├── 🎨 ui_components.py     # UI utilities & helpers
├── 🚀 startup_manager.py   # Windows startup integration
├── 🏗️ build_exe.py        # Executable builder
├── 📋 build_vpet.spec     # PyInstaller specification
├── 📝 requirements.txt    # Python dependencies
├── 📄 LICENSE             # MIT License
└── 📖 README.md           # This file
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

### **🐛 Bug Reports**
- Check existing [issues](https://github.com/yourusername/VPet/issues)
- Include steps to reproduce
- Add screenshots if possible

### **✨ Feature Requests**
- Open a new [issue](https://github.com/yourusername/VPet/issues)
- Describe the feature and its benefits
- Check if similar requests exist

### **🔧 Development**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Google AI Studio** for Gemini API
- **Ollama Team** for local AI capabilities
- **Python Community** for amazing libraries
- **Tamagotchi** for the original inspiration

---

<div align="center">

### ⭐ **Star this repo if you love VPet!** ⭐

**Made with ❤️ by the VPet Community**

</div>
