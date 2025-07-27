import win32gui
import win32process
import psutil
import time
import random
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse

class ContextAwareness:
    def __init__(self, pet_manager):
        self.pet_manager = pet_manager
        self.last_app_check = datetime.now()
        self.current_app = None
        self.current_window_title = ""
        self.comment_cooldown = 60
        self.last_comment_time = datetime.now() - timedelta(seconds=self.comment_cooldown + 1)
        self.monitoring_enabled = True
        
        self.detected_apps = set()
        self.session_apps = {}
        
        self.app_database = {
            'chrome.exe': 'Google Chrome',
            'firefox.exe': 'Firefox',
            'msedge.exe': 'Microsoft Edge',
            'opera.exe': 'Opera',
            'brave.exe': 'Brave Browser',
            'safari.exe': 'Safari',
            'iexplore.exe': 'Internet Explorer',
            
            'winword.exe': 'Microsoft Word',
            'excel.exe': 'Microsoft Excel',
            'powerpnt.exe': 'PowerPoint',
            'outlook.exe': 'Outlook',
            'onenote.exe': 'OneNote',
            'teams.exe': 'Microsoft Teams',
            
            'googledrivesync.exe': 'Google Drive',
            
            'code.exe': 'Visual Studio Code',
            'devenv.exe': 'Visual Studio',
            'notepad++.exe': 'Notepad++',
            'sublime_text.exe': 'Sublime Text',
            'atom.exe': 'Atom',
            'pycharm64.exe': 'PyCharm',
            'pycharm.exe': 'PyCharm',
            'idea64.exe': 'IntelliJ IDEA',
            'idea.exe': 'IntelliJ IDEA',
            'eclipse.exe': 'Eclipse',
            'notepad.exe': 'Notepad',
            'vim.exe': 'Vim',
            'emacs.exe': 'Emacs',
            'webstorm64.exe': 'WebStorm',
            'webstorm.exe': 'WebStorm',
            
            'vlc.exe': 'VLC Media Player',
            'wmplayer.exe': 'Windows Media Player',
            'spotify.exe': 'Spotify',
            'itunes.exe': 'iTunes',
            'netflix.exe': 'Netflix',
            'youtube.exe': 'YouTube',
            'twitch.exe': 'Twitch',
            'obs64.exe': 'OBS Studio',
            'obs32.exe': 'OBS Studio',
            
            'steam.exe': 'Steam',
            'epicgameslauncher.exe': 'Epic Games',
            'origin.exe': 'Origin',
            'uplay.exe': 'Ubisoft Connect',
            'battlenet.exe': 'Battle.net',
            'minecraft.exe': 'Minecraft',
            'roblox.exe': 'Roblox',
            'discord.exe': 'Discord',
            'gog.exe': 'GOG Galaxy',
            'rockstarlauncher.exe': 'Rockstar Games Launcher',
            
            'skype.exe': 'Skype',
            'zoom.exe': 'Zoom',
            'slack.exe': 'Slack',
            'telegram.exe': 'Telegram',
            'whatsapp.exe': 'WhatsApp',
            'signal.exe': 'Signal',
            
            'photoshop.exe': 'Adobe Photoshop',
            'illustrator.exe': 'Adobe Illustrator',
            'indesign.exe': 'Adobe InDesign',
            'premiere.exe': 'Adobe Premiere Pro',
            'afterfx.exe': 'Adobe After Effects',
            'blender.exe': 'Blender',
            'gimp.exe': 'GIMP',
            'figma.exe': 'Figma',
            'canva.exe': 'Canva',
            'sketch.exe': 'Sketch',
            'davinci resolve.exe': 'DaVinci Resolve',
            'unity.exe': 'Unity',
            'unrealengine.exe': 'Unreal Engine',
            
            'explorer.exe': 'File Explorer',
            'winrar.exe': 'WinRAR',
            '7zfm.exe': '7-Zip',
            'totalcmd.exe': 'Total Commander',
            
            'taskmgr.exe': 'Task Manager',
            'regedit.exe': 'Registry Editor',
            'cmd.exe': 'Command Prompt',
            'powershell.exe': 'PowerShell',
            'calculator.exe': 'Calculator',
            'mspaint.exe': 'Paint',
            'snagit32.exe': 'Snagit',
            'greenshot.exe': 'Greenshot',
            
            'mbam.exe': 'Malwarebytes',
            'avastui.exe': 'Avast Antivirus',
            'avgui.exe': 'AVG Antivirus',
            'msmpeng.exe': 'Windows Defender',
            
            'notion.exe': 'Notion',
            'evernote.exe': 'Evernote',
            'todoist.exe': 'Todoist',
            'trello.exe': 'Trello',
            'asana.exe': 'Asana',
            'monday.exe': 'Monday.com',
            
            'quickbooks.exe': 'QuickBooks',
            'mint.exe': 'Mint',
            'excel.exe': 'Excel',
            
            'anki.exe': 'Anki',
            'duolingo.exe': 'Duolingo',
            'khan.exe': 'Khan Academy',
            
            'kindle.exe': 'Kindle',
            'calibre.exe': 'Calibre',
            'adobe reader.exe': 'Adobe Reader',
            'foxit reader.exe': 'Foxit Reader'
        }
        
        self.first_detection_responses = {
            'browsers': [
                "Ooh! Web time! 🌐 *scurries away*",
                "Internet! I'll hide! 💻 *wiggles*",
                "Browsing? Moving! 🏃‍♂️ *zoom*",
                "Web stuff! Bye bye! 👋 *hops away*",
                "Online time! I go hide! 🫣"
            ],
            'youtube': [
                "Video time! 📺 *bounces to corner*",
                "YouTube! Shh! 🤫 *tippy toes*",
                "Movies! I'll be quiet! 🍿 *whispers*",
                "Watch time! Hiding! 👀 *peeks*",
                "Videos! Corner time! 📱 *scampers*"
            ],
            'netflix': [
                "Movie! 🎬 *curls up small*",
                "Show time! Sleepy corner! 😴 *yawns*",
                "Netflix! Cozy spot! 🛋️ *snuggles*",
                "Binge time! I nap! 💤 *zzz*",
                "Entertainment! Quiet mode! 🤐"
            ],
            'office': [
                "Work work! 📝 *salutes and hops*",
                "Important stuff! Moving! 💼 *scurries*",
                "Office time! I hide! 🏢 *tippy toes*",
                "Documents! Shh! 📄 *whispers*",
                "Busy human! Bye! 👋 *zooms away*"
            ],
            'coding': [
                "Code magic! ✨ *sparkles away*",
                "Beep boop! Moving! 💻 *robot dance*",
                "Programming! I go! 🚀 *whoosh*",
                "Code time! Corner! 👨‍💻 *hops*",
                "Computer stuff! Hiding! 🖥️ *peeks*"
            ],
            'gaming': [
                "Game time! 🎮 *cheers from far*",
                "Play play! Go win! 🏆 *bounces*",
                "Gaming! I watch! 👀 *excited*",
                "Adventure! Good luck! ⚔️ *waves*",
                "Games! Yay! Moving! 🕹️ *cheers*"
            ],
            'music': [
                "Music! 🎵 *dances away*",
                "Tunes! Wiggle wiggle! 🎶 *bounces*",
                "Songs! I dance too! 💃 *spins*",
                "Beats! Moving to rhythm! 🥁 *tap tap*",
                "Music time! Groove! 🎤 *wiggles*"
            ],
            'communication': [
                "Chat chat! 💬 *whispers and hides*",
                "Friends! Say hi! 👋 *waves*",
                "Talk time! Quiet! 🤫 *tippy toes*",
                "Social! I'll be good! 😇 *angel face*",
                "Conversation! Shh! 🗣️ *covers mouth*"
            ],
            'creative': [
                "Art! Pretty! 🎨 *sparkly eyes*",
                "Create! Inspire! ✨ *twirls*",
                "Design! Wow! 🖌️ *amazed*",
                "Making! Beautiful! 🌟 *claps*",
                "Art time! I watch! 👀 *peeks*"
            ],
            'learning': [
                "Study! Smart! 📚 *puts on tiny glasses*",
                "Learning! Brain grow! 🧠 *points to head*",
                "School! Knowledge! 🎓 *salutes*",
                "Books! Wisdom! 💡 *lightbulb*",
                "Study time! Quiet! 🤓 *whispers*"
            ],
            'default': [
                "Busy human! 😊 *tippy toes*",
                "Work time! I move! 💪 *flexes*",
                "Focus! Shh! 🤫 *whispers*",
                "Important! I hide! 🫣 *covers eyes*",
                "Concentrate! Go go! 🏃‍♂️ *zooms*"
            ]
        }
        
        self.app_responses = {
            'browsers': [
                "Still browsing! 🌐 *peeks*",
                "Web web web! 💻 *giggles*",
                "Internet fun! 🔍 *bounces*",
                "Click click! 🖱️ *watches*",
                "Browsing! Yay! 📱 *wiggles*"
            ],
            'youtube': [
                "More videos! 📺 *excited*",
                "Still watching! 👀 *munches*",
                "Video time! 🍿 *happy*",
                "YouTube! Fun! 🎬 *claps*",
                "Watch watch! 📱 *bounces*"
            ],
            'netflix': [
                "Movie still! 🎬 *cozy*",
                "Show time! 📺 *snuggles*",
                "Netflix! Sleepy! 😴 *yawns*",
                "Binge! Comfy! 🛋️ *curls up*",
                "Entertainment! 🍿 *happy*"
            ],
            'office': [
                "Work work! 📝 *cheers*",
                "Still busy! 💼 *tippy toes*",
                "Office! Important! 🏢 *salutes*",
                "Documents! 📄 *whispers*",
                "Productive! 💪 *flexes*"
            ],
            'coding': [
                "Code code! 💻 *sparkles*",
                "Still programming! 🚀 *beeps*",
                "Beep boop! ⚡ *robot*",
                "Computer magic! ✨ *amazed*",
                "Coding! Smart! 🤓 *impressed*"
            ],
            'gaming': [
                "Game game! 🎮 *cheers*",
                "Still playing! 🕹️ *excited*",
                "Win win! 🏆 *bounces*",
                "Gaming! Fun! ⚔️ *waves*",
                "Play time! 🎯 *happy*"
            ],
            'music': [
                "Music! 🎵 *dances*",
                "Still jamming! 🎶 *wiggles*",
                "Beats! 🥁 *tap tap*",
                "Songs! Yay! 🎤 *spins*",
                "Tunes! 🎼 *bounces*"
            ],
            'communication': [
                "Chat chat! 💬 *whispers*",
                "Still talking! 🗣️ *quiet*",
                "Friends! 👥 *waves*",
                "Social! 💕 *happy*",
                "Conversation! 📞 *shh*"
            ],
            'creative': [
                "Art art! 🎨 *sparkly*",
                "Still creating! ✨ *amazed*",
                "Pretty! 🖌️ *claps*",
                "Design! Wow! 🌟 *twirls*",
                "Creative! 🎭 *inspired*"
            ],
            'learning': [
                "Study! 📚 *smart*",
                "Still learning! 🎓 *proud*",
                "Books! 📖 *reads*",
                "Knowledge! 🧠 *grows*",
                "School! 💡 *bright*"
            ],
            'default': [
                "Busy busy! 😊 *tippy toes*",
                "Work! 💪 *cheers*",
                "Focus! 🤫 *quiet*",
                "Important! 🎯 *serious*",
                "Concentrate! 🧘 *zen*"
            ]
        }
        
    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            return {
                'hwnd': hwnd,
                'title': window_title,
                'process_name': process_name,
                'process_path': process.exe() if hasattr(process, 'exe') else '',
                'pid': pid
            }
        except Exception as e:
            return None
    
    def get_window_rectangle(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return {
                'left': rect[0],
                'top': rect[1], 
                'right': rect[2],
                'bottom': rect[3],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
        except:
            return None
    
    def detect_content_context(self, window_title, process_name):
        title_lower = window_title.lower()
        
        if 'youtube' in title_lower or 'youtube.com' in title_lower:
            return 'youtube'
        
        if 'netflix' in title_lower:
            return 'netflix'
        
        if any(site in title_lower for site in ['facebook', 'twitter', 'instagram', 'linkedin', 'reddit']):
            return 'social_media'
        
        if any(email in title_lower for email in ['gmail', 'outlook', 'mail', 'email']):
            return 'email'
        
        if any(shop in title_lower for shop in ['amazon', 'ebay', 'shop', 'store', 'cart']):
            return 'shopping'
        
        if any(news in title_lower for news in ['news', 'bbc', 'cnn', 'reuters', 'times']):
            return 'news'
        
        return None
    
    def categorize_app(self, process_name, window_title):
        process_lower = process_name.lower()
        
        if any(browser in process_lower for browser in ['chrome', 'firefox', 'edge', 'opera', 'brave', 'safari']):
            content_context = self.detect_content_context(window_title, process_name)
            if content_context:
                return content_context
            return 'browsers'
        
        if any(office in process_lower for office in ['winword', 'excel', 'powerpnt', 'outlook', 'onenote']):
            return 'office'
        
        if any(dev in process_lower for dev in ['code', 'devenv', 'notepad++', 'sublime', 'atom', 'pycharm', 'idea', 'eclipse', 'vim', 'emacs', 'webstorm']):
            return 'coding'
        
        if any(game in process_lower for game in ['steam', 'epic', 'origin', 'uplay', 'battlenet', 'minecraft', 'roblox', 'gog', 'rockstar']):
            return 'gaming'
        
        if any(music in process_lower for music in ['spotify', 'itunes', 'vlc', 'wmplayer']):
            return 'music'
        
        if any(comm in process_lower for comm in ['discord', 'skype', 'zoom', 'slack', 'telegram', 'whatsapp', 'teams']):
            return 'communication'
        
        if any(creative in process_lower for creative in ['photoshop', 'illustrator', 'premiere', 'afterfx', 'blender', 'gimp', 'figma', 'sketch', 'davinci', 'unity', 'unreal']):
            return 'creative'
        
        if any(learn in process_lower for learn in ['anki', 'duolingo', 'khan', 'kindle', 'calibre']):
            return 'learning'
        
        content_context = self.detect_content_context(window_title, process_name)
        if content_context:
            return content_context
        
        return 'default'
    
    def calculate_safe_position(self, window_rect, screen_width, screen_height, min_y=0):
        if not window_rect:
            return None

        pet_size = 256
        margin = 60

        current_x = self.pet_manager.root.winfo_x()
        current_y = self.pet_manager.root.winfo_y()

        potential_positions = []

        if window_rect['right'] + margin + pet_size <= screen_width:
            y_pos = max(min_y, min(window_rect['top'], screen_height - pet_size - margin))
            potential_positions.append((window_rect['right'] + margin, y_pos))

        if window_rect['left'] - margin - pet_size >= 0:
            y_pos = max(min_y, min(window_rect['top'], screen_height - pet_size - margin))
            potential_positions.append((window_rect['left'] - margin - pet_size, y_pos))

        if window_rect['bottom'] + margin + pet_size <= screen_height:
            x_pos = max(margin, min(window_rect['left'], screen_width - pet_size - margin))
            potential_positions.append((x_pos, window_rect['bottom'] + margin))

        if window_rect['top'] - margin - pet_size >= min_y:
            x_pos = max(margin, min(window_rect['left'], screen_width - pet_size - margin))
            potential_positions.append((x_pos, window_rect['top'] - margin - pet_size))

        corner_positions = [
            (screen_width - pet_size - margin, screen_height - pet_size - margin),
            (margin, screen_height - pet_size - margin),
            (screen_width - pet_size - margin, max(min_y, margin)),
            (margin, max(min_y, margin)),
        ]
        potential_positions.extend(corner_positions)

        safe_positions = []
        for x, y in potential_positions:
            pet_rect = {'left': x, 'top': y, 'right': x + pet_size, 'bottom': y + pet_size}
            if not self.rectangles_overlap(pet_rect, window_rect):
                safe_positions.append((x, y))

        if not safe_positions:
            return corner_positions[0]

        safe_positions.sort(key=lambda pos: ((pos[0] - current_x)**2 + (pos[1] - current_y)**2)**0.5)
        return safe_positions[0]
    
    def rectangles_overlap(self, rect1, rect2):
        return not (rect1['right'] < rect2['left'] or 
                   rect1['left'] > rect2['right'] or
                   rect1['bottom'] < rect2['top'] or
                   rect1['top'] > rect2['bottom'])
    
    def should_comment(self):
        return (datetime.now() - self.last_comment_time).total_seconds() > self.comment_cooldown
    
    def make_contextual_comment(self, category, app_name):
        if not self.should_comment():
            return

        movement_comments = [
            "Oops, am I in your way? Let me move! 🏃‍♂️",
            "I'll get out of your way so you can focus! 🤓",
            "Making space for you! *scurries away*",
            "You look busy! I'll hide for a bit. 🫣",
            "Let me give you some room. *hops to the side*",
        ]

        if random.random() < 0.3:
            comment = random.choice(movement_comments)
            self._ensure_speech_bubble_visibility()

            def show_bubble_and_move():
                if hasattr(self.pet_manager, 'speech_bubble'):
                    self.pet_manager.speech_bubble.show_bubble('custom', comment, use_typewriter=False)
                    # Move immediately after showing the bubble
                    self.move_pet_to_safe_position(self.get_active_window_info(), delay_ms=100)
            
            self.pet_manager.root.after(200, show_bubble_and_move)
            self.last_comment_time = datetime.now()
    
    def move_pet_to_safe_position(self, window_info, delay_ms=1000):
        if not window_info:
            return

        window_rect = self.get_window_rectangle(window_info['hwnd'])
        if not window_rect:
            return

        screen_width = self.pet_manager.root.winfo_screenwidth()
        screen_height = self.pet_manager.root.winfo_screenheight()
        min_y = 150

        safe_pos = self.calculate_safe_position(window_rect, screen_width, screen_height, min_y)
        if safe_pos:
            if delay_ms <= 0:
                # Move immediately
                self._smooth_move_to_position(safe_pos)
            else:
                self.pet_manager.root.after(delay_ms, lambda: self._smooth_move_to_position(safe_pos))
    
    def _smooth_move_to_position(self, target_pos):
        if not hasattr(self.pet_manager, 'root') or not self.pet_manager.root.winfo_exists():
            return

        target_x, target_y = target_pos

        if hasattr(self.pet_manager, 'animation') and self.pet_manager.animation:

            self.pet_manager.animation.pause_movement()
            self.pet_manager.pet_state.is_interacting = True

            current_x = self.pet_manager.root.winfo_x()
            self.pet_manager.pet_state.direction = 'right' if target_x > current_x else 'left'
            self.pet_manager.pet_state.current_animation = 'Walking'

            def controlled_move_step():
                if not self.pet_manager.root.winfo_exists():
                    self.pet_manager.pet_state.current_animation = 'Standing'
                    self.pet_manager.pet_state.is_interacting = False
                    self.pet_manager.animation.schedule_resume_movement(1000)
                    return

                curr_x = self.pet_manager.root.winfo_x()
                curr_y = self.pet_manager.root.winfo_y()
                dx = target_x - curr_x
                dy = target_y - curr_y
                distance = (dx**2 + dy**2)**0.5

                if abs(dx) > 2:
                    self.pet_manager.pet_state.direction = 'right' if dx > 0 else 'left'

                if distance < 10:
                    self.pet_manager.pet_state.current_animation = 'Standing'
                    self.pet_manager.pet_state.is_interacting = False
                    self.pet_manager.animation.schedule_resume_movement(1000)
                    return

                # Use normal movement speed (same as regular idling movement)
                speed_setting = self.pet_manager.settings.get('movement_speed', 5)
                pixels_per_step = max(1, speed_setting)  # Same as normal movement
                
                step_x = pixels_per_step * (dx / distance) if distance > 0 else 0
                step_y = pixels_per_step * (dy / distance) if distance > 0 else 0

                new_x = curr_x + step_x
                new_y = curr_y + step_y
                self.pet_manager.root.geometry(f'+{int(new_x)}+{int(new_y)}')

                # Use same timing as normal movement (50ms)
                self.pet_manager.root.after(50, controlled_move_step)

            controlled_move_step()
    
    def update_context_awareness(self):
        if not self.monitoring_enabled or self.pet_manager.pet_state.is_interacting:
            return
        
        # Add sleep state check to prevent movement while sleeping
        if hasattr(self.pet_manager.pet_state, 'is_sleeping') and self.pet_manager.pet_state.is_sleeping:
            return
        
        if (datetime.now() - self.last_app_check).total_seconds() < 3:
            return
        self.last_app_check = datetime.now()
        
        window_info = self.get_active_window_info()
        if not window_info:
            return
        
        process_name = window_info['process_name']
        window_title = window_info['title']
        
        if 'virtual' in window_title.lower() and 'pet' in window_title.lower():
            return
        
        category = self.categorize_app(process_name, window_title)
        app_name = self.app_database.get(process_name, process_name.replace('.exe', '').title())
        
        current_context = f"{process_name}:{category}"
        if current_context != self.current_app:
            self.current_app = current_context
            
            if self._should_avoid_window(category, app_name):
                if random.random() < 0.3:
                    self.make_contextual_comment(category, app_name)
            else:
                self.make_contextual_comment(category, app_name)
    
    def toggle_monitoring(self, enabled):
        self.monitoring_enabled = enabled
        if enabled:
            self.last_app_check = datetime.now() - timedelta(seconds=10)
    
    def set_comment_cooldown(self, seconds):
        self.comment_cooldown = seconds
    
    def reset_comment_timer(self):
        self.last_comment_time = datetime.now() - timedelta(seconds=self.comment_cooldown + 1)
        self.current_app = None
    
    def reset_app_memory(self):
        self.detected_apps.clear()
        self.session_apps.clear()
        self.current_app = None
    
    def _should_avoid_window(self, category, app_name):
        work_categories = {
            'coding',
            'office',
            'creative',
            'learning',
            'browsers',
            'youtube',
            'netflix',
            'gaming',
            'communication'
        }
        
        utility_categories = {
            'default'
        }
        
        non_intrusive_apps = {
            'File Explorer',
            'Windows Explorer',
            'Task Manager',
            'Control Panel',
            'Settings',
            'Calculator',
            'Notepad',
            'Paint',
            'Windows Security',
            'Device Manager'
        }
        
        if app_name in non_intrusive_apps:
            return False
            
        if category in utility_categories:
            return False
            
        return category in work_categories
    
    def _ensure_speech_bubble_visibility(self):
        pass
    
    def get_current_context(self):
        window_info = self.get_active_window_info()
        if window_info:
            category = self.categorize_app(window_info['process_name'], window_info['title'])
            return {
                'process': window_info['process_name'],
                'title': window_info['title'],
                'category': category,
                'app_name': self.app_database.get(window_info['process_name'], 'Unknown')
            }
        return None