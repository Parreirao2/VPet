import pystray
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes
from ctypes import wintypes

from pystray._util import win32

from unified_ui import COLORS

class SystemTrayMenu:
    
    @staticmethod
    def create_custom_menu_item(title, action):
        return pystray.MenuItem(title, action)
    
    @staticmethod
    def create_menu_items(pet_manager, show_settings_func, exit_func):
        pet_manager.pet_state.stats.update()
        
        return (
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
            SystemTrayMenu.create_custom_menu_item('Inventory', lambda: pet_manager.show_inventory()),
            SystemTrayMenu.create_custom_menu_item('Game Hub', lambda: pet_manager.show_game_hub()),
            pystray.Menu.SEPARATOR,
            SystemTrayMenu.create_custom_menu_item('Settings', show_settings_func),
            SystemTrayMenu.create_custom_menu_item('Exit', exit_func)
        )
    
    @staticmethod
    def create_tray_icon(image_path=None):
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                # Ensure image is in RGBA mode for transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                return img
            except Exception as e:
                print(f"Error loading image for tray icon: {e}")
                # Fallback to generic icon if image loading fails
                pass
        
        # Generic fallback icon (simple circle)
        icon_size = 64
        icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0)) # Transparent background
        draw = ImageDraw.Draw(icon)
        
        center = icon_size // 2
        radius = icon_size // 2 - 4
        
        # Draw a simple red circle as a fallback
        draw.ellipse((center - radius, center - radius, center + radius, center + radius), fill=(255, 0, 0, 255)) # Red circle
        
        return icon

def create_context_menu(pet_manager, show_settings_func, exit_func):
    return SystemTrayMenu.create_menu_items(pet_manager, show_settings_func, exit_func)

def setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path='frames/Adult_Happy.png'):
    # Ensure the icon path is absolute
    absolute_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), icon_path)
    icon_image = SystemTrayMenu.create_tray_icon(absolute_icon_path)
    
    def get_updated_menu():
        try:
            pet_manager.pet_state.stats.update()
            return SystemTrayMenu.create_menu_items(pet_manager, show_settings_func, exit_func)
        except Exception as e:
            return (pystray.MenuItem('Error loading menu', None),)
    
    menu = pystray.Menu(get_updated_menu)
    
    icon = pystray.Icon("tamagotchi_pet", icon_image, "Virtual Pet", menu)
    
    original_notify = icon._notify
    
    def custom_notify(hwnd, msg, wparam, lparam):
        if msg == win32.WM_RBUTTONDOWN or msg == win32.WM_RBUTTONUP:
            point = win32.POINT()
            win32.GetCursorPos(ctypes.byref(point))
            
            win32.SetForegroundWindow(hwnd)
            
            if not hasattr(icon, '_menu_handle') or icon._menu_handle is None:
                icon.menu = pystray.Menu(get_updated_menu)
                dummy = icon.menu
            
            hmenu, callbacks = icon._menu_handle
            
            index = win32.TrackPopupMenu(
                hmenu,
                win32.TPM_RETURNCMD | win32.TPM_RIGHTBUTTON,
                point.x,
                point.y,
                0,
                hwnd,
                None)
            
            if index > 0 and index <= len(callbacks):
                try:
                    callback = callbacks[index - 1]
                    callback()
                except Exception as e:
                    pass
            
            win32.PostMessage(hwnd, win32.WM_NULL, 0, 0)
            return True
        
        return original_notify(hwnd, msg, wparam, lparam)
    
    icon._notify = custom_notify
    
    icon.update_menu = get_updated_menu
    
    def update_icon_menu():
        try:
            if hasattr(icon, '_menu_handle') and icon._menu_handle is not None:
                hmenu, callbacks = icon._menu_handle
                
                new_menu = pystray.Menu(get_updated_menu)
                
                icon.menu = new_menu
                
                dummy = icon.menu
                
                return True
            return False
        except Exception as e:
            return False
    
    icon.update_icon_menu = update_icon_menu
    
    return icon


def create_modern_context_menu(pet_manager, show_settings_func, exit_func):
    return create_context_menu(pet_manager, show_settings_func, exit_func)

def setup_modern_system_tray(pet_manager, show_settings_func, exit_func, icon_path=None):
    return setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path)

def create_unified_context_menu(pet_manager, show_settings_func, exit_func):
    return create_context_menu(pet_manager, show_settings_func, exit_func)

def setup_unified_system_tray(pet_manager, show_settings_func, exit_func, icon_path=None):
    return setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path)
