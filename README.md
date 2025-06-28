# Virtual Pet (VPet) Desktop Application

A modern desktop Tamagotchi-style virtual pet that lives on your computer screen. Take care of your pet as it grows from a baby to an adult through various life stages!

![Virtual Pet Screenshot](frames/Baby_Happy.png)

## Features

### Pet Life Cycle
- **Growth Stages**: Your pet evolves through 4 distinct life stages - Baby, Child, Teen, and Adult
- **Aging System**: Pet ages over time and evolves when reaching certain age thresholds
- **Customizable**: Choose from different pet colors (black, blue, pink)

### Comprehensive Stats System
- **Hunger**: Feed your pet to keep it satisfied
- **Happiness**: Play with your pet to keep it happy
- **Energy**: Let your pet rest to maintain energy
- **Health**: Keep other stats high to maintain good health
- **Cleanliness**: Clean up after your pet to maintain hygiene
- **Social**: Interact with your pet to fulfill social needs

### Interactive Gameplay
- **Feeding System**: Various food items with different stat effects
- **Poop System**: Clean up after your pet to maintain cleanliness
- **Double-Click Interaction**: Double-click your pet for happiness boosts
- **Drag & Drop**: Move your pet around your screen
- **Animation System**: Different animations for various pet states and activities

### Desktop Integration
- **Always On Top**: Pet stays visible on your desktop
- **System Tray**: Access controls and stats from the system tray
- **Transparent Background**: Pet integrates seamlessly with your desktop
- **Auto-Save**: Pet data is automatically saved every 5 minutes

## Getting Started

### Installation

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

### Basic Controls

- **Left-click**: Select your pet
- **Double-click**: Give your pet a happiness boost (has cooldown)
- **Right-click**: Open the context menu with options
- **Drag**: Move your pet around the screen

## Caring For Your Pet

### Feeding

Access the inventory through the right-click menu to feed your pet. Different foods have various effects on your pet's stats:

- Basic foods (bread, milk) provide moderate hunger satisfaction
- Treats (chocolate, cake) boost happiness but may reduce health
- Balanced meals (steak, salmon) provide better overall stat benefits

### Cleaning

Your pet will occasionally produce waste that needs to be cleaned:

1. Select the toilet paper from your inventory
2. Click on the poop to clean it up
3. Leaving waste uncleaned will reduce your pet's cleanliness stat

### Health Management

- Your pet becomes sick if any stat falls below 25%
- A sick pet will display a sickness icon and health will gradually decrease
- Restore all stats above 25% to cure your pet

### Evolution

Your pet will evolve as it ages:

- Baby → Child: 30 days
- Child → Teen: 60 days
- Teen → Adult: 90 days

## Customization

Access settings through the system tray icon to customize:

- Pet size
- Transparency
- Movement speed
- Activity level
- Pet color (black, blue, pink)
- Poop frequency

## Saving and Loading

- Your pet's state is automatically saved every 5 minutes
- Save files are stored in the `saves` directory
- You can manually save through the system tray menu

## Technical Details

This application is built with:

- Python 3.8+
- Tkinter for the GUI
- PIL (Pillow) for image processing
- Pystray for system tray integration

## Project Structure

- `main.py`: Main application entry point
- `pet_components.py`: Core pet stats and growth systems
- `pet_animation.py`: Pet animation and movement logic
- `poop_system.py`: Waste generation and cleaning mechanics
- `inventory_system.py`: Item management and usage
- `frames/`: Animation frame images for different pet stages
- `img_assets/`: Food and item images

## License

[Your License Information Here]

## Acknowledgements

- Pixel art assets for the pet and items
- Contributors and testers