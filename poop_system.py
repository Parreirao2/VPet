import tkinter as tk
from PIL import Image, ImageTk
import os
import random
from datetime import datetime, timedelta
class PoopSystem:
    def __init__(self, root, canvas, pet_state):
        self.root = root
        self.canvas = canvas
        self.pet_state = pet_state
        self.poops = []
        self.poop_images = []
        self.toilet_paper_image = None
        self.load_images()
        self.base_poop_chance = 0.05
        self.current_poop_chance = self.base_poop_chance
        self.max_poop_chance = 0.4
        self.poop_pressure = 0.0
        self.max_poop_pressure = 100.0
        self.pressure_increase_rate = self.pet_state.pet_manager.settings.get('poop_frequency', 0.5)
        self.last_pressure_update = datetime.now()
        self.food_consumed = 0
        self.food_pressure_multiplier = 8.0
        self.last_poop_time = datetime.now()
        self.min_poop_interval = 300
        self.post_poop_pressure_reduction = 60.0
        self.cleaning_mode = False
        self.original_cursor = None
        self.poop_check_timer = None
        self.poop_animation_timer = None
        self.start_poop_animation()
        self.start_poop_check_timer()
    def add_food_consumed(self, amount=1):
        self.food_consumed += amount
        pressure_increase = amount * self.food_pressure_multiplier
        self.poop_pressure = min(self.max_poop_pressure, self.poop_pressure + pressure_increase)
        self.update_poop_chance()
        self.start_poop_check_timer()
    def load_images(self):
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets')
            poop1 = Image.open(os.path.join(img_path, 'poop1.png')).convert("RGBA")
            poop2 = Image.open(os.path.join(img_path, 'poop2.png')).convert("RGBA")
            size = (32, 32)
            poop1 = poop1.resize(size, Image.LANCZOS)
            poop2 = poop2.resize(size, Image.LANCZOS)
            for img in [poop1, poop2]:
                background = Image.new("RGBA", img.size, (0, 0, 0, 0))
                background.paste(img, (0, 0), img)
                img = background
            self.poop_images = [
                ImageTk.PhotoImage(poop1),
                ImageTk.PhotoImage(poop2)
            ]
            toilet_paper = Image.open(os.path.join(img_path, 'toilet_paper.png')).convert("RGBA")
            toilet_paper = toilet_paper.resize((32, 32), Image.LANCZOS)
            background = Image.new("RGBA", toilet_paper.size, (0, 0, 0, 0))
            background.paste(toilet_paper, (0, 0), toilet_paper)
            toilet_paper = background
            self.toilet_paper_image = ImageTk.PhotoImage(toilet_paper)
        except Exception as e:
            print(f'Error loading poop images: {e}')
    def update_poop_pressure(self):
        now = datetime.now()
        elapsed_minutes = (now - self.last_pressure_update).total_seconds() / 60.0
        self.last_pressure_update = now
        pressure_increase = elapsed_minutes * self.pressure_increase_rate
        self.poop_pressure = min(self.max_poop_pressure, self.poop_pressure + pressure_increase)
        self.update_poop_chance()
    def update_poop_chance(self):
        pressure_ratio = self.poop_pressure / self.max_poop_pressure
        self.current_poop_chance = self.base_poop_chance + (pressure_ratio * (self.max_poop_chance - self.base_poop_chance))
    def check_poop_generation(self, x, y):
        if self.pet_state.is_interacting or self.cleaning_mode:
            return
        now = datetime.now()
        if (now - self.last_poop_time).total_seconds() < self.min_poop_interval:
            return
        self.update_poop_pressure()
        cleanliness = self.pet_state.stats.get_stat('cleanliness') if hasattr(self.pet_state, 'stats') else 100
        cleanliness_factor = 1 + ((100 - cleanliness) / 200)
        final_chance = self.current_poop_chance * cleanliness_factor
        random_value = random.random()
        if random_value <= final_chance:
            screen_x = self.root.winfo_x() + 128
            screen_y = self.root.winfo_y() + 128
            self.generate_poop(screen_x, screen_y)
            self.last_poop_time = now
            self.poop_pressure = max(0, self.poop_pressure - self.post_poop_pressure_reduction)
            self.food_consumed = max(0, self.food_consumed - 1)
            self.update_poop_chance()
    def generate_poop(self, screen_x, screen_y):
        poop_img = self.poop_images[0]
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        abs_x = screen_x + offset_x
        abs_y = screen_y + offset_y
        poop_window = tk.Toplevel(self.root)
        poop_window.overrideredirect(True)
        poop_window.attributes('-topmost', True)
        transparent_color = '#010101'
        poop_window.config(bg=transparent_color)
        poop_window.attributes('-transparentcolor', transparent_color)
        poop_canvas = tk.Canvas(poop_window, width=32, height=32,
                               highlightthickness=0, bg=transparent_color)
        poop_canvas.pack()
        poop_id = poop_canvas.create_image(16, 16, image=poop_img)
        poop_window.geometry(f'32x32+{abs_x}+{abs_y}')
        self.poops.append({
            'id': poop_id,
            'window': poop_window,
            'canvas': poop_canvas,
            'image': poop_img,
            'time': datetime.now(),
            'abs_x': abs_x,
            'abs_y': abs_y,
            'frame': 0
        })
        if hasattr(self.pet_state, 'stats'):
            self.pet_state.stats.modify_stat('cleanliness', -9)
            self.pet_state.poop_system_dirty = True
    def start_cleaning_mode(self):
        if not self.cleaning_mode:
            self.cleaning_mode = True
            self.original_cursor = self.canvas.cget('cursor')
            if hasattr(self.pet_state, 'pet_manager') and hasattr(self.pet_state.pet_manager, 'inventory_system'):
                pass
            else:
                try:
                    self.canvas.config(cursor='hand2')
                    self.canvas.bind('<Motion>', self.move_toilet_paper)
                    self.toilet_paper_id = self.canvas.create_image(0, 0, image=self.toilet_paper_image)
                    self.canvas.bind('<Button-1>', self.clean_poop)
                except Exception as e:
                    print(f"Error setting custom cursor: {e}")
                    self.canvas.config(cursor='hand2')
                    self.canvas.bind('<Button-1>', self.clean_poop)
    def move_toilet_paper(self, event):
        if hasattr(self, 'toilet_paper_id'):
            abs_x = self.root.winfo_pointerx()
            abs_y = self.root.winfo_pointery()
            self.canvas.coords(self.toilet_paper_id, abs_x, abs_y)
            self.check_poop_cleaning(abs_x, abs_y)
    def check_poop_cleaning(self, x, y):
        for poop in self.poops[:]:
            poop_x = poop['window'].winfo_x() + 16
            poop_y = poop['window'].winfo_y() + 16
            if abs(x - poop_x) < 32 and abs(y - poop_y) < 32:
                poop['window'].destroy()
                self.poops.remove(poop)
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', 15)
                    print(f"Poop cleaned! Cleanliness increased to {self.pet_state.stats.get_stat('cleanliness')}")
    def stop_cleaning_mode(self):
        if self.cleaning_mode:
            self.cleaning_mode = False
            self.canvas.config(cursor=self.original_cursor)
            if hasattr(self, 'toilet_paper_id'):
                self.canvas.delete(self.toilet_paper_id)
                delattr(self, 'toilet_paper_id')
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Button-1>')
    def clean_poop(self, event):
        if not self.cleaning_mode:
            return
        abs_x = self.root.winfo_x() + event.x
        abs_y = self.root.winfo_y() + event.y
        cleaned = False
        for i, poop in enumerate(self.poops[:]):
            poop_x = poop['window'].winfo_x() + 16
            poop_y = poop['window'].winfo_y() + 16
            distance = ((poop_x - abs_x) ** 2 + (poop_y - abs_y) ** 2) ** 0.5
            if distance < 20:
                poop['window'].destroy()
                self.poops.pop(i)
                cleaned = True
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', 2)
                    print(f"Poop cleaned! Cleanliness increased to {self.pet_state.stats.get_stat('cleanliness')}")
                break
        if not self.poops:
            self.stop_cleaning_mode()
            return cleaned
    def start_poop_check_timer(self):
        self.check_old_poops()
        self.poop_check_timer = self.root.after(15000, self.start_poop_check_timer)
    def check_old_poops(self):
        now = datetime.now()
        has_old_poops = False
        for poop in self.poops:
            if (now - poop['time']).total_seconds() > 300:
                has_old_poops = True
                if hasattr(self.pet_state, 'stats'):
                    self.pet_state.stats.modify_stat('cleanliness', -3)
                    print(f"Old poop found! Cleanliness reduced to {self.pet_state.stats.get_stat('cleanliness')}")
        if has_old_poops:
            if hasattr(self.pet_state, 'stats'):
                self.pet_state.stats.modify_stat('happiness', -0.5)
                self.pet_state.stats.modify_stat('health', -0.2)
                print(f"Old poops affecting pet! Happiness: {self.pet_state.stats.get_stat('happiness')}, Health: {self.pet_state.stats.get_stat('health')}")
            if len(self.poops) > 3 and self.pet_state.current_animation != 'sad':
                self.pet_state.current_animation = 'sad'
    def start_poop_animation(self):
        self.animate_poops()
        self.poop_animation_timer = self.root.after(500, self.start_poop_animation)
    def animate_poops(self):
        if not self.poops:
            return
        for poop in self.poops:
            poop['frame'] = 1 - poop['frame']
            poop_img = self.poop_images[poop['frame']]
            poop['image'] = poop_img
            poop['canvas'].itemconfig(poop['id'], image=poop_img)
            transparent_color = '#010101'
            poop['window'].config(bg=transparent_color)
            poop['window'].attributes('-transparentcolor', transparent_color)
            poop['canvas'].config(bg=transparent_color)
            poop['window'].update()
    def cleanup(self):
        if self.poop_check_timer:
            self.root.after_cancel(self.poop_check_timer)
            self.poop_check_timer = None
        if hasattr(self, 'poop_animation_timer') and self.poop_animation_timer:
            self.root.after_cancel(self.poop_animation_timer)
            self.poop_animation_timer = None
        for poop in self.poops:
            if 'window' in poop and poop['window'].winfo_exists():
                poop['window'].destroy()
        self.poops = []
    def clean_all_poops(self):
        for poop in self.poops:
            poop['window'].destroy()
        self.poops = []
    def remove_poop(self, index):
        if 0 <= index < len(self.poops):
            self.poops[index]['window'].destroy()
            removed_poop = self.poops.pop(index)
            return True
        return False
    def get_poop_status(self):
        return {
            'poop_pressure': round(self.poop_pressure, 1),
            'current_poop_chance': round(self.current_poop_chance, 3),
            'food_consumed': self.food_consumed,
            'active_poops': len(self.poops),
            'time_since_last_poop': round((datetime.now() - self.last_poop_time).total_seconds(), 1)
        }