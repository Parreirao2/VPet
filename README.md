# 🐾 Virtual Pet (VPet) Desktop Application 🐾

A modern desktop Tamagotchi-style virtual pet that lives on your computer screen. Take care of your pet as it grows from a baby to an adult through various life stages! Feed it, play with it, chat with it using AI, and watch it thrive in this delightful virtual companion experience.

## 🎭 Pet Evolution Stages

(Baby)
<img src="frames/Baby_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Child)
<img src="frames/Child_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Teen)
<img src="frames/Teen_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Adult)
<img src="frames/Adult_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Special)
???HIDDEN???

## 🖥️ Demo

![Virtual Pet Demo](img_assets/VPet_Demo.apng)



## ✨ Features

### 🌱 Pet Life Cycle & Evolution
- **Growth Stages**: Your pet evolves through 5 distinct life stages - Baby, Child, Teen, Adult, and Special
- **Natural Evolution**: Pet ages over time and evolves automatically when reaching age thresholds:
  - Baby → Child: 30 days
  - Child → Teen: 60 days  
  - Teen → Adult: 90 days
- **Instant Evolution Items**: Use special Evo1 items to evolve your pet to the next stage immediately
- **Special Evolution**: Use Evo2 items to unlock the secret "Special" stage with unique animations
- **Stage-Based Personalities**: Each life stage has distinct personality traits and behaviors
- **Customizable Appearance**: Choose from different pet colors (black, blue, pink)

### 📊 Comprehensive Stats System
- **Hunger** (0-100%): Feed your pet to keep it satisfied - affects health when too low
- **Happiness** (0-100%): Play with your pet to keep it joyful - influences mood and behavior
- **Energy** (0-100%): Let your pet rest to maintain energy - depletes with activities
- **Health** (0-100%): Maintain through balanced care - decreases when other stats are critical
- **Cleanliness** (0-100%): Clean up after your pet to maintain hygiene - affected by waste
- **Social** (0-100%): Interact with your pet to fulfill social needs - improved through attention
- **Dynamic Decay**: Stats decrease over time at different rates based on pet's life stage
- **Status Effects**: Visual indicators when stats are low (hungry, tired, sick, sad, dirty, lonely)

### 🎮 Interactive Gameplay
- **Advanced Feeding System**: 80+ different food items with unique stat effects
- **Natural Behaviors**: Pet exhibits realistic animal behaviors including random napping and natural waste patterns
- **Double-Click Interaction**: Double-click your pet for happiness boosts (with cooldown)
- **Drag & Drop**: Move your pet around your screen freely
- **Rich Animation System**: Multiple animations for different pet states, moods, and activities
- **Smart Speech Bubbles**: Adaptive communication system with intelligent positioning and directional tails
- **Sickness System**: Pet becomes sick when stats are too low, requiring proper care

### 🧠 Enhanced Natural Behaviors
- **Random Sleep System**: Pet takes realistic naps like a real animal (25% base chance when idle, increasing to 60% if pet hasn't slept recently)
- **Natural Pooping System**: Realistic waste management that increases over time and after eating, with proper cooldown periods after pooping
- **Smooth Animations**: Natural movement speed with proper direction-aware sprite flipping for realistic motion

### 🤖 AI Chat System
- **Intelligent Conversations**: Chat with your pet using Google Gemini AI models
- **Multiple AI Models**: Choose from 7 different Gemini models (free and paid options):
  - **FREE**: Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 1.5 Flash
  - **PAID**: Gemini 2.0 Pro, Gemini 2.0 Flash, Gemini 2.0 Flash-Lite, Gemini 1.5 Pro
- **Personality-Aware**: AI responses adapt to your pet's current stage, stats, and mood
- **Typewriter Effect**: Responses appear with realistic typing animation
- **Friendly Error Handling**: User-friendly error messages for API issues
- **Secure Storage**: API keys stored locally and securely

### 🧠 Context Awareness
- **Application Monitoring**: The pet actively monitors the applications you are using and can comment on them, bringing a new level of interaction.
- **Intelligent Movement**: VPet is aware of your workspace and will intelligently move away from active application windows to avoid obstructing your view.
- **Smart Responses**: The AI can provide context-aware responses based on the detected application, with a memory system to provide relevant follow-up comments.
- **Frequency Control**: To avoid being intrusive, the pet uses smart frequency control to limit how often it comments on your applications.

### 💰 Currency & Game Hub
- **Coin Economy**: Earn coins through gameplay and pet care activities
- **Three Exciting Mini-Games**:
  
  **🎲 Number Guesser**:
  - Guess numbers within increasing ranges
  - Progressive difficulty with each level
  - Rewards: 1-7+ coins based on level batches
  - Limited guesses with strategic gameplay
  
  **⚡ Reaction Test**:
  - Test your reflexes against decreasing time limits
  - Goal times get faster as you level up (3.0s down to 0.3s)
  - Rewards: 1-7+ coins for successful reactions
  - Performance-based feedback system
  
  **🎯 Ball Clicker**:
  - Click black balls while avoiding red ones
  - Dynamic ball spawning with increasing difficulty
  - Timed rounds with click requirements
  - Rewards: 1-7+ coins for completing levels

- **Progressive Rewards**: Higher levels in each game provide better coin rewards
- **Energy Cost**: Playing games consumes your pet's energy, adding strategic depth

### 🛒 Comprehensive Inventory & Shop
- **80+ Food Items**: Extensive variety with different effects and prices (15-70 coins)
- **Care Items**: 
  - Toilet Paper (Free) - Cleans poop, +15% cleanliness
  - Shower (Free) - +15% cleanliness boost
- **Evolution Items**:
  - Evo1 (10,000 coins) - Evolve to next stage
  - Evo2 (1,000,000 coins) - Evolve to special stage
- **Smart Shopping**: Items sorted by price for easy browsing
- **Detailed Tooltips**: Hover over items to see effects and prices
- **Quantity Management**: Track owned items with quantity displays

### 💻 Desktop Integration
- **Always On Top**: Pet stays visible on your desktop (toggleable)
- **System Tray**: Complete control panel accessible from system tray
- **Transparent Background**: Pet integrates seamlessly with your desktop
- **Auto-Save**: Pet data automatically saved every 5 minutes
- **Startup Integration**: Option to start with Windows
- **Multi-Monitor Support**: Pet can move across multiple screens

## 🚀 Getting Started

### 📥 Installation

1. Ensure you have Python 3.8+ installed on your system
2. Clone this repository or download the source code
3. Install required dependencies:
   ```
   pip install pillow tkinter pystray google-generativeai
   ```
4. Run the application:
   ```
   python main.py
   ```

### 🎮 Basic Controls

- **Left-click**: Select your pet
- **Double-click**: Give your pet a happiness boost (has cooldown)
- **Right-click**: Open the context menu to see your pet's stats at a glance
- **Drag**: Move your pet around the screen

## 💕 Caring For Your Pet

### 🍔 Feeding Your Pet

Access the inventory through the right-click menu to feed your pet from 80+ different food items including:

- **🥖 Bakery Items**: Bread, buns, baguettes, bagels (15-35 coins)
- **🍰 Desserts & Sweets**: Chocolate, cakes, cookies, pies (20-60 coins)  
- **🍖 Main Dishes**: Steak, salmon, burgers, pizza (30-70 coins)
- **🍜 International Cuisine**: Ramen, spaghetti, curry, sushi (35-50 coins)
- **🥞 Breakfast Items**: Pancakes, waffles, eggs, bacon (20-40 coins)
- **🍿 Snacks & Sides**: Fries, popcorn, chips, ice cream (20-45 coins)
- **🥗 Healthy Options**: Salads, fruits, vegetables (15-40 coins)
- **🥤 Beverages**: Water, juices, sodas, coffee (10-30 coins)

Each food item has unique effects on your pet's stats - some boost happiness and energy while others may affect health or cleanliness. Choose wisely based on your pet's current needs!
- **Egg Salad Bowl** (40 coins): Hunger +3, Happiness +1, Energy +2, Health +2, Cleanliness -1
- **Egg Tart** (25 coins): Hunger +2, Happiness +3, Energy +1, Cleanliness -1

## 🎮 Game Hub & Mini-Games

### 🎲 Number Guesser
- **Objective**: Guess the correct number within an increasing range
- **Mechanics**: Start with 1-10, range expands as you level up
- **Lives**: 3+ guesses per level (increases every 5 levels)
- **Rewards**: 1-7+ coins based on level batches
- **Strategy**: Higher levels = bigger ranges but better rewards

### ⚡ Reaction Test  
- **Objective**: Click the button as fast as possible when it turns red
- **Mechanics**: Wait times are random (1-3 seconds)
- **Goal Times**: Start at 3.0s, decrease to 0.3s minimum as you level up
- **Rewards**: 1-7+ coins for meeting time goals
- **Penalty**: Level decreases if you're too slow

### 🎯 Ball Clicker
- **Objective**: Click required number of black balls while avoiding red ones
- **Mechanics**: Balls spawn randomly, red balls reduce score
- **Requirements**: 5+ black balls per level (increases with level)
- **Time Limit**: 8-15 seconds depending on level
- **Rewards**: 1-7+ coins for completing levels

### 🧹 Cleaning & Hygiene

Your pet creates waste that affects cleanliness:

1. **Automatic Waste Generation**: Pet creates poop based on poop frequency setting
2. **Cleaning Tools**: Use toilet paper (free) or shower (free) from inventory
3. **Cleanliness Impact**: Uncleaned waste reduces cleanliness over time
4. **Health Connection**: Low cleanliness contributes to sickness

### 🏥 Health & Sickness System

- **Sickness Triggers**: Any stat below 25% can cause sickness
- **Health Decay**: Sick pets lose health over time (faster with multiple low stats)
- **Visual Indicators**: Sickness overlay appears on sick pets
- **Recovery**: Restore all stats above 25% to cure sickness
- **Prevention**: Maintain balanced stats through regular care

### 🔄 Evolution System

#### Natural Evolution (Age-Based)
- **Baby → Child**: 30 days old
- **Child → Teen**: 60 days old  
- **Teen → Adult**: 90 days old

#### Instant Evolution Items
- **Evo1 Item** (10,000 coins): Evolve to next natural stage immediately
- **Evo2 Item** (1,000,000 coins): Evolve to secret "Special" stage

### 🤖 AI Chat Features

- **Setup**: Requires Google Gemini API key (free tier available)
- **Model Selection**: Choose from 7 different AI models
- **Personality**: AI adapts responses to pet's current stage and stats
- **Context Awareness**: AI knows about all game features and can provide guidance
- **Error Handling**: Friendly messages for API issues or credit problems

> **Note**: Your API key is stored locally in the `saves` directory. Do not share this folder with anyone to protect your key.

## 🎨 Customization

Access settings through the system tray icon to customize:

- Pet name
- Pet size
- Transparency
- Movement speed
- Activity level
- Pet color (black, blue, pink)
- Poop frequency

## 💾 Saving and Loading

- Your pet's state is automatically saved every 5 minutes
- Save files are stored in the `saves` directory
- You can manually save through the system tray menu

## 🔧 Technical Details

This application is built with:

- Python 3.8+
- Tkinter for the GUI
- PIL (Pillow) for image processing
- Pystray for system tray integration

## 📁 Project Structure

- `main.py`: Main application entry point
- `pet_components.py`: Core pet stats and growth systems
- `pet_animation.py`: Pet animation and movement logic
- `poop_system.py`: Waste generation and cleaning mechanics
- `inventory_system.py`: Item management and usage
- `currency_system.py`: Virtual currency management for in-game economy
- `game_hub.py`: Mini-games implementation including Number Guesser and Reaction Test
- `speech_bubble.py`: Pet communication system
- `system_tray.py`: System tray integration and menu controls
- `context_awareness.py`: Monitors active applications and triggers pet responses, enabling the pet to react to your computer usage.
- `frames/`: Animation frame images for different pet stages and colors
- `img_assets/`: Food, item, and currency images

## 🤫 Cheat Codes

- **Unlock 10,000,000 coins**: Change your pet's name to `UUDDLRLRBA` in the settings to activate the cheat.