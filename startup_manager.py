"""Startup Manager Module

This module handles Windows startup functionality and provides utilities for:
- Managing Windows startup registry entries
- Verifying startup status
- Enabling/disabling startup
"""

import os
import winreg
import sys
import logging
from datetime import datetime

class StartupManager:
    """Manages Windows startup functionality"""
    
    def __init__(self, app_name="TamagotchiPet"):
        self.app_name = app_name
        self.key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for startup operations"""
        logger = logging.getLogger('StartupManager')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup file handler
        log_file = os.path.join(logs_dir, 'startup.log')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
        return logger
    
    def is_enabled(self):
        """Check if application is set to run at startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            
            # Verify if the path is correct
            current_exe = sys.executable
            return value == f'"{current_exe}" "{os.path.abspath(sys.argv[0])}"'
            
        except WindowsError:
            return False
    
    def enable(self):
        """Enable application to run at startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_WRITE)
            executable = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            
            # Set registry value
            winreg.SetValueEx(
                key,
                self.app_name,
                0,
                winreg.REG_SZ,
                f'"{executable}" "{script_path}"'
            )
            
            winreg.CloseKey(key)
            self.logger.info(f'Startup enabled for {self.app_name}')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to enable startup: {str(e)}')
            return False
    
    def disable(self):
        """Disable application from running at startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            
            self.logger.info(f'Startup disabled for {self.app_name}')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to disable startup: {str(e)}')
            return False
    
    def verify_startup_status(self):
        """Verify startup status and fix if necessary"""
        is_enabled = self.is_enabled()
        should_be_enabled = self._get_setting_from_config()
        
        if is_enabled != should_be_enabled:
            self.logger.warning(f'Startup status mismatch. Is: {is_enabled}, Should be: {should_be_enabled}')
            if should_be_enabled:
                return self.enable()
            else:
                return self.disable()
        
        return True
    
    def _get_setting_from_config(self):
        """Get startup setting from settings file"""
        try:
            settings_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'saves',
                'settings.json'
            )
            
            if not os.path.exists(settings_path):
                return False
            
            import json
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                return settings.get('start_with_windows', False)
                
        except Exception as e:
            self.logger.error(f'Failed to read settings: {str(e)}')
            return False