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
            return Image.open(image_path)
        else:
            icon_size = 64
            icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            center = icon_size // 2
            radius = icon_size // 2 - 4
            
            for r in range(radius, 0, -1):
                ratio = r / radius
                r1, g1, b1 = int(COLORS['primary'][1:3], 16), int(COLORS['primary'][3:5], 16), int(COLORS['primary'][5:7], 16)
                r2, g2, b2 = int(COLORS['primary_light'][1:3], 16), int(COLORS['primary_light'][3:5], 16), int(COLORS['primary_light'][5:7], 16)
                
                r_val = int(r1 * ratio + r2 * (1 - ratio))
                g_val = int(g1 * ratio + g2 * (1 - ratio))
                b_val = int(b1 * ratio + b2 * (1 - ratio))
                
                color = f'#{r_val:02x}{g_val:02x}{b_val:02x}'
                draw.ellipse((center - r, center - r, center + r, center + r), fill=color)
            
            draw.ellipse((center - 12, center - 15, center + 12, center + 9), fill='white')
            draw.ellipse((center - 7, center - 8, center - 3, center - 4), fill='black')
            draw.ellipse((center + 3, center - 8, center + 7, center - 4), fill='black')
            draw.arc((center - 5, center - 3, center + 5, center + 5), 0, 180, fill='black', width=2)
            
            return icon

def create_context_menu(pet_manager, show_settings_func, exit_func):
    return SystemTrayMenu.create_menu_items(pet_manager, show_settings_func, exit_func)

def setup_system_tray(pet_manager, show_settings_func, exit_func, icon_path='frames/Adult_Happy.png'):
    icon_image = SystemTrayMenu.create_tray_icon(icon_path)
    
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
