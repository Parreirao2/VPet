#!/usr/bin/env python3
"""
Build script to create VPet executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path



def create_icon():
    """Create the executable icon from Adult_Walk1.png or a default if not found"""
    icon_path = "icon.ico"
    source_image_path = os.path.join("frames", "Adult_Walk1.png")

    if os.path.exists(source_image_path):
        print(f"📝 Creating icon from {source_image_path}...")
        try:
            from PIL import Image
            img = Image.open(source_image_path)
            # Resize to a common icon size, e.g., 256x256, and save as .ico
            img.thumbnail((256, 256), Image.LANCZOS)
            img.save(icon_path, format='ICO')
            print(f"✅ Created icon: {icon_path}")
            return True
        except Exception as e:
            print(f"⚠️ Could not create icon from {source_image_path}: {e}")
            # Fallback to default icon creation if specific image fails
            return _create_default_icon(icon_path)
    else:
        print(f"⚠️ {source_image_path} not found. Creating default icon...")
        return _create_default_icon(icon_path)

def _create_default_icon(icon_path):
    """Helper to create a simple default icon"""
    try:
        from PIL import Image, ImageDraw
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=(100, 150, 200), outline=(50, 100, 150), width=2)
        draw.ellipse([18, 20, 26, 28], fill=(0, 0, 0))
        draw.ellipse([38, 20, 46, 28], fill=(0, 0, 0))
        draw.ellipse([30, 32, 34, 36], fill=(255, 100, 100))
        draw.arc([24, 38, 40, 46], start=0, end=180, fill=(0, 0, 0), width=2)
        img.save(icon_path, format='ICO')
        print(f"✅ Created default icon: {icon_path}")
        return True
    except Exception as e:
        print(f"❌ Could not create default icon: {e}")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building VPet executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=VirtualPet',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    # Add icon if it exists
    if os.path.exists('icon.ico'):
        cmd.append('--icon=icon.ico')
    
    # Add data files
    data_dirs = ['frames', 'img_assets']
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            cmd.extend(['--add-data', f'{data_dir};{data_dir}'])
    
    # Add hidden imports
    hidden_imports = [
        'PIL._tkinter_finder',
        'google.generativeai',
        'pystray._win32',
        'tkinter',
        'tkinter.ttk'
    ]
    
    for import_name in hidden_imports:
        cmd.extend(['--hidden-import', import_name])
    
    # Main script
    cmd.append('main.py')
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"Error: {e.stderr}")
        return False

def create_distribution():
    """Create a distribution folder with all necessary files"""
    print("📦 Creating distribution package...")
    
    dist_dir = Path("VPet_Distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Copy executable
    exe_path = Path("dist/VirtualPet.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "VirtualPet.exe")
        print(f"✅ Copied executable to {dist_dir}")
    else:
        print("❌ Executable not found!")
        return False
    
    # Copy essential folders
    essential_dirs = ['frames', 'img_assets']
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, dist_dir / dir_name)
            print(f"✅ Copied {dir_name} folder")
    
    # Create saves directory
    saves_dir = dist_dir / "saves"
    saves_dir.mkdir()
    print("✅ Created saves directory")
    
    # Create README for distribution
    readme_content = """# VPet - Virtual Pet Desktop Companion

## How to Run
Simply double-click on `VirtualPet.exe` to start your virtual pet!

## Features
- Virtual pet that lives on your desktop
- Feed, play, and care for your pet
- Mini-games to earn coins
- AI chat system (requires Google Gemini API key)
- Evolution system through different life stages
- Customizable appearance and behavior

## First Time Setup
1. Run VirtualPet.exe
2. Your pet will appear on your desktop
3. Right-click on your pet to access the menu
4. Go to Settings to customize your pet

## AI Chat (Optional)
To enable AI chat with your pet:
1. Get a free Google Gemini API key from: https://makersuite.google.com/app/apikey
2. Right-click your pet → Chat with Pet
3. Enter your API key when prompted

## System Tray
Look for the pet icon in your system tray (bottom-right corner) to access:
- Settings
- Stats
- Save/Load options
- Exit

## Troubleshooting
- If the pet doesn't appear, check your system tray
- Make sure all files are in the same folder as VirtualPet.exe
- Windows may show a security warning - click "More info" then "Run anyway"

Enjoy your virtual pet companion! 🐾
"""
    
    with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Distribution package created in: {dist_dir}")
    print(f"📁 Package size: {sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    
    return True

def main():
    """Main build process"""
    print("🐾 VPet Executable Builder 🐾")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found! Please run this script from the VPet directory.")
        return False
    
    
    
    # Step 2: Create icon
    create_icon()
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Step 4: Create distribution package
    if not create_distribution():
        return False
    
    print("\n🎉 Build completed successfully!")
    print("📦 Your VPet executable is ready in the 'VPet_Distribution' folder")
    print("📋 You can now share this folder with others!")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)