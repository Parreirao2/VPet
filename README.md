# 🐾 Virtual Pet (VPet) Desktop Application 🐾

A modern desktop Tamagotchi-style virtual pet that lives on your computer screen. Take care of your pet as it grows from a baby to an adult through various life stages! Feed it, play with it, and watch it thrive in this delightful virtual companion experience.


(Baby)
<img src="frames/Baby_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Child)
<img src="frames/Child_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Teen)
<img src="frames/Teen_Happy.png" alt="Virtual Pet Screenshot" width="45"/>

(Adult)
<img src="frames/Adult_Happy.png" alt="Virtual Pet Screenshot" width="45"/>



## ✨ Features

### 🌱 Pet Life Cycle
- **Growth Stages**: Your pet evolves through 4 distinct life stages - Baby, Child, Teen, and Adult
- **Aging System**: Pet ages over time and evolves when reaching certain age thresholds
- **Customizable**: Choose from different pet colors (black, blue, pink)

### 📊 Comprehensive Stats System
- **Hunger**: Feed your pet to keep it satisfied
- **Happiness**: Play with your pet to keep it happy
- **Energy**: Let your pet rest to maintain energy
- **Health**: Keep other stats high to maintain good health
- **Cleanliness**: Clean up after your pet to maintain hygiene
- **Social**: Interact with your pet to fulfill social needs

### 🎮 Interactive Gameplay
- **Feeding System**: Various food items with different stat effects
- **Poop System**: Clean up after your pet to maintain cleanliness
- **Double-Click Interaction**: Double-click your pet for happiness boosts
- **Drag & Drop**: Move your pet around your screen
- **Animation System**: Different animations for various pet states and activities
- **Speech Bubbles**: Your pet communicates with you through cute speech bubbles

### 💰 Currency & Game Hub
- **Currency System**: Earn coins by taking care of your pet and playing mini-games
- **Mini-Games**: 
  - *Number Guesser*: Test your luck by guessing numbers with increasing difficulty levels
  - *Reaction Test*: Test your reflexes and earn rewards based on your reaction time
- **Progressive Difficulty**: Games become more challenging as you level up, with bigger rewards
- **Shop**: Spend your hard-earned coins on special items and treats for your pet
- **Economy System**: Balance your spending between necessities and luxury items

### 💻 Desktop Integration
- **Always On Top**: Pet stays visible on your desktop
- **System Tray**: Access controls and stats from the system tray
- **Transparent Background**: Pet integrates seamlessly with your desktop
- **Auto-Save**: Pet data is automatically saved every 5 minutes

## 🚀 Getting Started

### 📥 Installation

1. Ensure you have Python 3.8+ installed on your system
2. Clone this repository or download the source code
3. Install required dependencies:
   ```
   pip install pillow tkinter pystray
   ```
4. Run the application:
   ```
   python main.py
   ```

### 🎮 Basic Controls

- **Left-click**: Select your pet
- **Double-click**: Give your pet a happiness boost (has cooldown)
- **Right-click**: Open the context menu with options
- **Drag**: Move your pet around the screen

## 💕 Caring For Your Pet

### 🍔 Feeding

Access the inventory through the right-click menu to feed your pet. Different foods have various effects on your pet's stats:

- Basic foods (bread, milk) provide moderate hunger satisfaction
- Treats (chocolate, cake) boost happiness but may reduce health
- Balanced meals (steak, salmon) provide better overall stat benefits
- Special foods can be purchased with coins earned from mini-games

## 🎮 Game Hub & Economy

The Game Hub provides entertainment for both you and your pet while earning valuable currency!

### 🎲 Mini-Games

- **Number Guesser**: 
  - Guess the correct number within a range
  - Difficulty increases with each level
  - Higher levels mean bigger number ranges and more rewards
  - Earn coins based on your performance

- **Reaction Test**:
  - Test your reflexes by clicking when the screen changes
  - Faster reactions earn more coins
  - Progressive difficulty system challenges your skills
  - Compete against your previous best times

### 💰 Currency System

- Earn coins by:
  - Playing mini-games successfully
  - Taking good care of your pet
  - Completing special achievements
- Spend coins on:
  - Premium food items with better stat effects
  - Special toys and accessories
  - Unique pet customizations
  - Stat boosters and special items

### 🧹 Cleaning

Your pet will occasionally produce waste that needs to be cleaned:

1. Select the toilet paper from your inventory
2. Click on the poop to clean it up
3. Leaving waste uncleaned will reduce your pet's cleanliness stat

### 🏥 Health Management

- Your pet becomes sick if any stat falls below 25%
- A sick pet will display a sickness icon and health will gradually decrease
- Restore all stats above 25% to cure your pet

### 🔄 Evolution

Your pet will evolve as it ages:

- Baby → Child: 30 days
- Child → Teen: 60 days
- Teen → Adult: 90 days

## 🎨 Customization

Access settings through the system tray icon to customize:

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
- `frames/`: Animation frame images for different pet stages and colors
- `img_assets/`: Food, item, and currency images

## 📄 License

[Your License Information Here]

## 👏 Acknowledgements

- Pixel art assets for the pet and items
- Contributors and testers