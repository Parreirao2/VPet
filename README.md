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
| ![Baby](frames/Baby_Happy.png) | ![Child](frames/Child_Happy.png) | ![Teen](frames/Teen_Happy.png) | ![Adult](frames/Adult_Happy.png) | ![Special](frames/Special_Happy.png) |
| *Day 1-30* | *Day 31-60* | *Day 61-90* | *Day 91+* | *Special Evo Spirit* |

</div>

---

## ✨ **Core Features**

### 🤖 **AI Chat System** *(NEW: Ollama Support!)*
- **🧠 Multiple AI Models**: 
  - **Google Gemini** (7 models: Pro, Flash, Lite)
  - **🆕 Ollama** (Local AI - no internet required!)
- **🎯 Context-Aware Positioning**: Pet intelligently avoids overlapping your active windows and responds to your applications
- **💬 Natural Conversations**: Typewriter-style responses with personality
- **🔒 Privacy-First**: Local Ollama models keep your data private
- **🎭 Personality-Driven**: Responses adapt to your pet's mood and life stage

### 🎮 **Interactive Gameplay**
- **📊 6 Core Stats**: Hunger, Happiness, Energy, Health, Cleanliness, Social
- **🍔 13 Food Items**: From apple to sushi, each with unique stat effects
- **🎲 3 Mini-Games**: Number Guesser, Reaction Test, Ball Clicker
- **💰 Economy System**: Earn coins through games and care activities
- **🧹 Realistic Care**: Clean up after your pet, manage hygiene
- **🏆 Treasure Chests**: Hourly treasure spawns with valuable rewards

### 🏆 **Advanced Features**
- **👁️ Context Awareness**: Pet monitors your apps and comments intelligently
- **🎨 Customization**: Colors, sizes, transparency, behavior settings
- **💾 Auto-Save**: Never lose progress with 5-minute auto-saves
- **🖥️ Desktop Integration**: Always-on-top, multi-monitor support
- **🧵 Multi-Threaded System Tray**: Runs in background without blocking main application
- **🔄 Smart Evolution**: Natural aging or instant evolution items

---

## 🚀 **Quick Start**

### 📥 **Installation**
```bash
# 1. Clone the repository
git clone https://github.com/Parreirao2/VPet.git
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
6. **🏆 Find** treasure chests that spawn hourly

---

## 📊 **Pet Stat Mechanics**

### ⚖️ **Core Stats**
| Stat | Effect | Decay Rate |
|------|--------|------------|
| **Hunger** | Affects health when low | Baby: 0.15%/min → Adult: 0.35%/min |
| **Happiness** | Impacts willingness to play | Baby: 0.1%/min → Adult: 0.3%/min |
| **Energy** | Required for activities | Baby: 0.08%/min → Adult: 0.2%/min |
| **Health** | Critical for survival | Doesn't decay |
| **Cleanliness** | Prevents sickness | Baby: 0.1%/min → Adult: 0.25%/min |
| **Social** | Affects chat engagement | Baby: 0.08%/min → Adult: 0.22%/min |

### ⚠️ **Critical Thresholds**
- **Health ≤30%**: Pet gets sick (loses 1% health/22-45s)
- **Energy=0**: Pet falls asleep automatically
- **Cleanliness≤30**: Higher poop chance
- **Any stat=0**: Accelerates sickness

---

## 🤒 **Sickness System**

### 🦠 **Causes**
- Health ≤30% 
- Any stat reaching 0%
- Leaving poop uncleaned

### 💊 **Treatment**
1. Use **First Aid** item (+50% health)
2. Use **Enchanted Apple** (full recovery)
3. Keep cleanliness high

### ⚠️ **Effects**
- Continuous health drain
- Reduced activity
- Sad mood animations

---

## 🧹 **Poop Management**

### 💩 **Mechanics**
- **🍽️ Pressure-Based System**:
  - Each food consumed adds "poop pressure" (0.5-2.0 points based on food type)
  - Poop chance = (current hunger %) × (poop pressure / 10)
  - Pressure resets after each poop

### 🧻 **Cleaning**
1. Click **Toilet Paper** in inventory
2. Drag and drop on poop
3. Each cleanup increases cleanliness by 15%

### ⏳ **Consequences**
- Poops older than 5 minutes:
  - Reduce cleanliness by 3%
  - Lower happiness by 0.5%
  - Decrease health by 0.2%

---

## 🛒 **Shop & Items**

### **Food Items** *(Complete Inventory)*

#### **🥖 Basic Tier** *(15-35 coins)*
| **Item** | **Price** | **Effects** |
|:---------|:----------|:------------|
| **🍎 Apple** | 15 coins | Hunger: +8, Happiness: +3, Energy: +4, Health: +6, Cleanliness: +1 |
| **🍩 Donut** | 25 coins | Hunger: +6, Happiness: +8, Energy: +10, Health: -4, Cleanliness: -3 |
| **🥐 Croissant** | 35 coins | Hunger: +12, Happiness: +5, Energy: +6, Health: +2, Cleanliness: -2 |

#### **🍔 Mid-Tier** *(45-75 coins)*
| **Item** | **Price** | **Effects** |
|:---------|:----------|:------------|
| **🌭 Hotdog** | 45 coins | Hunger: +15, Happiness: +6, Energy: +8, Health: -2, Cleanliness: -4 |
| **🥪 Sandwich** | 55 coins | Hunger: +18, Happiness: +7, Energy: +10, Health: +4, Cleanliness: -1 |
| **🥓 Bacon** | 65 coins | Hunger: +10, Happiness: +8, Energy: +12, Health: -3, Cleanliness: -5 |
| **🧁 Cupcake** | 75 coins | Hunger: +8, Happiness: +12, Energy: +15, Health: -5, Cleanliness: -4 |

#### **🍕 Good Tier** *(85-125 coins)*
| **Item** | **Price** | **Effects** |
|:---------|:----------|:------------|
| **🧀 Cheese** | 85 coins | Hunger: +20, Happiness: +8, Energy: +6, Health: +8, Cleanliness: -2 |
| **🍔 Burger** | 95 coins | Hunger: +25, Happiness: +10, Energy: +12, Health: -1, Cleanliness: -6 |
| **🍦 Ice Cream** | 105 coins | Hunger: +12, Happiness: +15, Energy: +18, Health: -2, Cleanliness: -3 |

#### **🍰 Premium Tier** *(135-200 coins)*
| **Item** | **Price** | **Effects** |
|:---------|:----------|:------------|
| **🍫 Chocolate Bar** | 135 coins | Hunger: +6, Happiness: +20, Energy: +25, Health: -6, Cleanliness: -4 |
| **🐟 Cooked Fish** | 165 coins | Hunger: +28, Happiness: +12, Energy: +15, Health: +15, Cleanliness: -3 |
| **🍣 Sushi** | 200 coins | Hunger: +30, Happiness: +18, Energy: +20, Health: +18, Cleanliness: +2 |

### **Special Items**
| **Item** | **Price** | **Description** |
|:---------|:----------|:----------------|
| **🧻 Toilet Paper** | FREE | Clean up waste (unlimited use) |
| **🚿 Shower** | FREE | Increases cleanliness by 15% (unlimited use) |
| **😴 Sleep** | FREE | Put your pet to sleep to recover energy gradually |
| **🩹 First Aid** | 100 coins | Heals your pet by 50% |
| **🍎✨ Enchanted Apple** | 250 coins | Restores all stats to 100% and sets Poop Chance to 0% |
| **🧬 Evo Spirit** | 10,000 coins | Instant evolution to next stage |
| **✨ Special Evo Spirit** | 1,000,000 coins | Evolution to secret special form |

---

## 🏆 **Treasure Chest System** *(NEW!)*

### **🎁 Hourly Rewards**
Treasure chests spawn randomly every hour (20% chance) and disappear after 5 minutes if not found!

#### **💰 Coin Rewards**
- **Base Reward**: 50-300 coins per chest

#### **📦 Item Rewards** *(Probability-Based)*

| **Tier** | **Chance** | **Items** | **Quantity** |
|:---------|:-----------|:----------|:-------------|
| **🔵 Basic** | 60% | Apple, Donut, Croissant | 1-5 items |
| **🟢 Mid-Tier** | 20% | Hotdog, Sandwich, Bacon, Cupcake | 1-3 items |
| **🟡 Good** | 10% | Cheese, Burger, Ice Cream | 1-3 items |
| **🔴 Premium** | 5% | Chocolate Bar, Cooked Fish, Sushi | 1 item |
| **🟣 Exotic** | 5% | Enchanted Apple, First Aid | 1 item |

### **🔍 How to Find Treasures**
1. **👀 Watch** for glowing treasure chests on your screen
2. **⚡ Act Fast** - chests disappear after 5 minutes
3. **💎 Click** the chest to claim your rewards
4. **💾 Auto-Save** - progress is automatically saved after each treasure

---

## 🎯 **Mini-Games**

<div align="center">

| **Game** | **Skill** | **Reward** | **Max Coins** |
|:---------|:----------|:-----------|:--------------|
| **🎲 Number Guesser** | Logic | 1-7+ coins | 7+ per level |
| **⚡ Reaction Test** | Speed | 1-7+ coins | 7+ per level |
| **🎯 Ball Clicker** | Precision | 1-7+ coins | 7+ per level |
| **🎰 Slot Machine** | Luck | 0-1000 coins | 1000 (Jackpot) |

</div>

### **🎰 Slot Machine Details**
- **Cost**: 5 coins per spin
- **💰 Jackpot**: Three 💰 symbols = 1000 coins
- **💰 Money Symbols**: Each 💰 = 50 coins (1% spawn chance)
- **🍎 Three of a Kind**: 15-20 coins
- **🍎 Two of a Kind**: 15-20 coins  
- **🍎 No Match**: 0-5 coins
- **Symbols**: Various fruit emojis (🍒🍋🍊🍇🍉🍎🍓🍑🥝🍍🥭🥥🫐🍈🍌) + rare 💰

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
├── 👀 context_awareness.py # Context-aware window positioning
├── 🎮 game_hub.py          # Mini-games & currency
├── 💾 pet_components.py    # Core pet logic & stats
├── 🎬 pet_animation.py     # Animation & movement
├── 🛒 inventory_system.py  # Shop & items
├── 💰 currency_system.py   # Economy management
├── 🧹 poop_system.py       # Waste management & cleaning
├── 🏆 treasure_system.py   # Treasure chest system
├── 💬 speech_bubble.py     # Pet communication system
├── 🖥️ system_tray.py      # System tray integration
├── ⚙️ unified_ui.py        # Modern UI components & settings
├── 🎨 ui_components.py     # UI utilities & helpers
├── 🚀 startup_manager.py   # Windows startup integration
├── 📝 requirements.txt    # Python dependencies
├── 📄 LICENSE             # MIT License
└── 📖 README.md           # This file
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

### **🐛 Bug Reports**
- Check existing [issues](https://github.com/Parreirao2/VPet/issues)
- Include steps to reproduce
- Add screenshots if possible

### **✨ Feature Requests**
- Open a new [issue](https://github.com/Parreirao2/VPet/issues)
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
- **Inventory Assets** Assets by Pixelrepo (https://pixelrepo.com)

---

<div align="center">

### ⭐ **Star this repo if you love VPet!** ⭐

**Made with ❤️ by the VPet Community**

</div>
