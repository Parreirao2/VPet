"""System Tray Module

This module provides a comprehensive system tray integration for the Tamagotchi application with:
- Status submenu with pet statistics (hunger, happiness, energy, etc.)
- All interaction options (feed, play, clean, pet, medicine)
- Modern styling with rounded corners and gradients
- Proper menu structure with separators

This module consolidates functionality from the previous modern_system_tray and unified_system_tray modules.
"""

import pystray
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes
from ctypes import wintypes

# Import win32 from pystray._util for notification constants
from pystray._util import win32

# Import color scheme from unified_ui
from unified_ui import COLORS

class SystemTrayMenu:
    """Provides comprehensive styling for system tray menu"""
    
    @staticmethod
    def create_custom_menu_item(title, action):
        """Create a custom menu item with modern styling"""
        # Create a custom menu item with modern appearance
        # Note: pystray has limited customization options for menu items
        # We're using the best approach available within its constraints
        return pystray.MenuItem(title, action)
    
    @staticmethod
    def create_menu_items(pet_manager, show_settings_func, exit_func):
        """Create styled menu items for the system tray with modern appearance"""
        # Force refresh of stats before creating menu to ensure latest values
        pet_manager.pet_state.stats.update()
        
        # Create menu items with custom icons
        return (
            # Status submenu with pet statistics
            pystray.MenuItem('Status', pystray.Menu(
                SystemTrayMenu.create_custom_menu_item(f'Hunger: {pet_manager.pet_state.stats.get_stat("hunger"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Happiness: {pet_manager.pet_state.stats.get_stat("happiness"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Energy: {pet_manager.pet_state.stats.get_stat("energy"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Health: {pet_manager.pet_state.stats.get_stat("health"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Cleanliness: {pet_manager.pet_state.stats.get_stat("cleanliness"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Social: {pet_manager.pet_state.stats.get_stat("social"):.0f}%', None),
                SystemTrayMenu.create_custom_menu_item(f'Age: {pet_manager.pet_state.stats.get_stat("age"):.1f} days', None),

                SystemTrayMenu.create_custom_menu_item(f'Stage: {pet_manager.pet_state.stage}', None)
            )),
            pystray.Menu.SEPARATOR,
            # Only keep Inventory and add Game Hub
            SystemTrayMenu.create_custom_menu_item('Inventory', lambda: pet_manager.show_inventory()),
            SystemTrayMenu.create_custom_menu_item('Game Hub', lambda: pet_manager.show_game_hub()),
            pystray.Menu.SEPARATOR,
            SystemTrayMenu.create_custom_menu_item('Settings', show_settings_func),
            SystemTrayMenu.create_custom_menu_item('Exit', exit_func)
        )
    
    @staticmethod
    def create_tray_icon(image_path=None):
        """Create a modern system tray icon"""
        if image_path and os.path.exists(image_path):
            # Use provided image if available
            return Image.open(image_path)
        else:
            # Create a default icon with modern styling
            icon_size = 64
            icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Draw a circular background with gradient effect
            center = icon_size // 2
            radius = icon_size // 2 - 4
            
            # Create gradient effect (simple implementation)
            for r in range(radius, 0, -1):
                # Calculate color based on radius (gradient from primary to primary_light)
                ratio = r / radius
                # Parse hex colors and create gradient
                r1, g1, b1 = int(COLORS['primary'][1:3], 16), int(COLORS['primary'][3:5], 16), int(COLORS['primary'][5:7], 16)
                r2, g2, b2 = int(COLORS['primary_light'][1:3], 16), int(COLORS['primary_light'][3:5], 16), int(COLORS['primary_light'][5:7], 16)
                
                r_val = int(r1 * ratio + r2 * (1 - ratio))
                g_val = int(g1 * ratio + g2 * (1 - ratio))
                b_val = int(b1 * ratio + b2 * (1 - ratio))
                
                color = f'#{r_val:02x}{g_val:02x}{b_val:02x}'
                draw.ellipse((center - r, center - r, center + r, center + r), fill=color)
            
            # Draw a simple pet silhouette
            # Head
            draw.ellipse((center - 12, center - 15, center + 12, center + 9), fill='white')
            # Eyes
            draw.ellipse((center - 7, center - 8, center - 3, center - 4), fill='black')
            draw.ellipse((center + 3, center - 8, center + 7, center - 4), fill='black')
            # Smile
            draw.arc((center - 5, center - 3, center + 5, center + 5), 0, 180, fill='black', width=2)
            
            return icon

# Utility functions for system tray integration
# These provide backward compatibility with both previous modules

def create_context_menu(pet_manager, show_settings_func, exit_func):
    """Create a context menu for the system tray"""
    return SystemTrayMenu.create_menu_items(pet_manager, show_settings_func, exit_func)

def setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path='frames/Adult_Happy.png'):
    """Setup system tray with comprehensive styling"""
    # Create icon
    icon_image = SystemTrayMenu.create_tray_icon(icon_path)
    
    # Create a function that generates an updated menu each time it's accessed
    def get_updated_menu():
        # This function will be called each time the menu is opened
        # ensuring we always get the latest stats
        try:
            # Force refresh of stats before creating menu
            pet_manager.pet_state.stats.update()  # Force stats update before creating menu
            # Return a freshly created menu with updated stats
            return SystemTrayMenu.create_menu_items(pet_manager, show_settings_func, exit_func)
        except Exception as e:
            # Return a simple menu as fallback
            return (pystray.MenuItem('Error loading menu', None),)
    
    # Create menu object first to ensure it's properly initialized
    menu = pystray.Menu(get_updated_menu)
    
    # Create and return system tray icon with the menu
    icon = pystray.Icon("tamagotchi_pet", icon_image, "Virtual Pet", menu)
    
    # Override the default notify function to handle right-click properly
    original_notify = icon._notify
    
    def custom_notify(hwnd, msg, wparam, lparam):
        # Handle right-click events specially
        if msg == win32.WM_RBUTTONDOWN or msg == win32.WM_RBUTTONUP:
            # Get cursor position
            point = win32.POINT()
            win32.GetCursorPos(ctypes.byref(point))
            
            # Set foreground window (required for menu to show)
            win32.SetForegroundWindow(hwnd)
            
            # Force menu initialization
            if not hasattr(icon, '_menu_handle') or icon._menu_handle is None:
                # Force menu initialization
                icon.menu = pystray.Menu(get_updated_menu)
                # Force menu property access to trigger initialization
                dummy = icon.menu
            
            # Show the menu
            hmenu, callbacks = icon._menu_handle
            
            # Use TrackPopupMenu for better compatibility
            index = win32.TrackPopupMenu(
                hmenu,
                win32.TPM_RETURNCMD | win32.TPM_RIGHTBUTTON,
                point.x,
                point.y,
                0,  # Reserved parameter, must be zero
                hwnd,
                None)  # No rectangle to exclude
            
            # Handle menu selection
            if index > 0 and index <= len(callbacks):
                try:
                    callback = callbacks[index - 1]
                    callback()
                except Exception as e:
                    pass
            
            # Send WM_NULL message to the window to prevent hang
            win32.PostMessage(hwnd, win32.WM_NULL, 0, 0)
            return True  # Indicate we handled this message
        
        # For other messages, use the original notify function
        return original_notify(hwnd, msg, wparam, lparam)
    
    # Replace the notify function
    icon._notify = custom_notify
    
    # Set the menu update function as an attribute of the icon for reference
    icon.update_menu = get_updated_menu
    
    # Add a method to update the icon's menu in real-time
    def update_icon_menu():
        try:
            # Check if the icon has a menu handle
            if hasattr(icon, '_menu_handle') and icon._menu_handle is not None:
                # Get the current menu handle
                hmenu, callbacks = icon._menu_handle
                
                # Create a new menu with updated stats
                new_menu = pystray.Menu(get_updated_menu)
                
                # Force the icon to update its menu
                icon.menu = new_menu
                
                # Force menu property access to trigger initialization
                dummy = icon.menu
                
                return True
            return False
        except Exception as e:
            return False
    
    # Add the update method to the icon
    icon.update_icon_menu = update_icon_menu
    
    return icon

# Provide backward compatibility functions for existing code

# For code using modern_system_tray
def create_modern_context_menu(pet_manager, show_settings_func, exit_func):
    """Backward compatibility function for modern_system_tray"""
    return create_context_menu(pet_manager, show_settings_func, exit_func)

def setup_modern_system_tray(pet_manager, show_settings_func, exit_func, icon_path=None):
    """Backward compatibility function for modern_system_tray"""
    return setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path)

# For code using unified_system_tray
def create_unified_context_menu(pet_manager, show_settings_func, exit_func):
    """Backward compatibility function for unified_system_tray"""
    return create_context_menu(pet_manager, show_settings_func, exit_func)

def setup_unified_system_tray(pet_manager, show_settings_func, exit_func, icon_path=None):
    """Backward compatibility function for unified_system_tray"""
    return setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path)
