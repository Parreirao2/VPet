import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import math
import random
import os
from datetime import datetime
import threading
import webbrowser
from startup_manager import StartupManager
import json
COLORS = {
    'primary': '#4a6baf',
    'primary_light': '#7a9be0',
    'primary_dark': '#2a4b8f',
    'secondary': '#ff9966',
    'background': '#f5f7fa',
    'surface': '#ffffff',
    'text': '#333333',
    'text_light': '#666666',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'disabled': '#cccccc',
    'tooltip_bg': '#f0f0f0',
    'tooltip_text': '#333333',
    'poop_brown': '#8B4513',
    'info': '#2196F3'
}
class BaseUI:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.configure_styles()
    def configure_styles(self):
        pass
class SimpleUI(BaseUI):
    def configure_styles(self):
        self.style.theme_use('clam')
        self.style.configure('TButton',
                            padding=(10, 5),
                            font=('Arial', 10))
        self.style.configure('TFrame',
                            background=COLORS['surface'])
        self.style.configure('TLabel',
                            background=COLORS['surface'],
                            foreground=COLORS['text'],
                            font=('Arial', 10))
        self.style.configure('Title.TLabel',
                            foreground=COLORS['primary'],
                            font=('Arial', 12, 'bold'))
        self.style.configure('Horizontal.TProgressbar',
                            background=COLORS['primary'])
        self.style.configure('Critical.Horizontal.TProgressbar',
                            background=COLORS['error'])
        self.style.configure('TCheckbutton',
                            font=('Arial', 10))
        self.style.configure('TNotebook',
                            background=COLORS['background'])
        self.style.configure('TNotebook.Tab',
                            padding=[10, 5],
                            font=('Arial', 10))
    def show_settings(self, pet_manager):
        settings_window = SimpleSettingsWindow(self.root, pet_manager)
        settings_window.show_settings()
class ModernUI(BaseUI):
    def configure_styles(self):
        self.style.theme_use('clam')
        self.style.configure('Modern.TButton',
                            background=COLORS['primary'],
                            foreground='white',
                            borderwidth=0,
                            focusthickness=0,
                            font=('Arial', 10),
                            padding=(10, 5))
        self.style.map('Modern.TButton',
                      background=[('active', COLORS['primary_light']),
                                 ('disabled', COLORS['disabled'])],
                      foreground=[('disabled', '#999999')])
        self.style.configure('Modern.TFrame',
                            background=COLORS['surface'])
        self.style.configure('Modern.TLabel',
                            background=COLORS['surface'],
                            foreground=COLORS['text'],
                            font=('Arial', 10))
        self.style.configure('Title.TLabel',
                            background=COLORS['surface'],
                            foreground=COLORS['primary'],
                            font=('Arial', 12, 'bold'))
        self.style.configure('Modern.Horizontal.TProgressbar',
                            troughcolor=COLORS['background'],
                            background=COLORS['primary'],
                            thickness=10)
        self.style.configure('Critical.Horizontal.TProgressbar',
                            troughcolor=COLORS['background'],
                            background=COLORS['error'],
                            thickness=10)
        self.style.configure('Modern.TCheckbutton',
                            background=COLORS['surface'],
                            foreground=COLORS['text'],
                            font=('Arial', 10))
        self.style.configure('Modern.TRadiobutton',
                            background=COLORS['surface'],
                            foreground=COLORS['text'],
                            font=('Arial', 10))
        self.style.configure('Modern.Horizontal.TScale',
                            background=COLORS['surface'],
                            troughcolor=COLORS['background'])
        self.style.configure('Modern.TNotebook',
                            background=COLORS['background'],
                            tabmargins=[2, 5, 2, 0])
        self.style.configure('Modern.TNotebook.Tab',
                            background=COLORS['background'],
                            foreground=COLORS['text'],
                            padding=[10, 5],
                            font=('Arial', 10))
        self.style.map('Modern.TNotebook.Tab',
                      background=[('selected', COLORS['surface'])],
                      foreground=[('selected', COLORS['primary'])])
    def show_settings(self, pet_manager):
        settings_window = ModernSettingsWindow(self.root, pet_manager)
        settings_window.show_settings()
class SimpleButton(tk.Button):
    def __init__(self, parent, text="Button", command=None, width=10, height=1,
                 bg=COLORS['primary'], fg="white", **kwargs):
        super().__init__(parent, text=text, command=command,
                        bg=bg, fg=fg,
                        activebackground=COLORS['primary_light'],
                        activeforeground="white",
                        font=("Arial", 10),
                        relief=tk.RAISED,
                        borderwidth=1,
                        padx=10, pady=5,
                        **kwargs)
class RoundedFrame(tk.Frame):
    def __init__(self, parent, bg=COLORS['surface'], corner_radius=10, **kwargs):
        if 'highlightthickness' not in kwargs:
            kwargs['highlightthickness'] = 0
        if 'borderwidth' not in kwargs:
            kwargs['borderwidth'] = 0
        super().__init__(parent, **kwargs)
        self.corner_radius = corner_radius
        self.bg = bg
        self.parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else COLORS['background']
        self.configure(bg=self.parent_bg)
        self.bg_label = None
        self.bg_image = None
        self.after(10, self.create_rounded_bg)
        self.bind('<Configure>', self._on_configure)
    def _on_configure(self, event):
        self.after(10, self.create_rounded_bg)
    def create_rounded_bg(self):
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 or height < 2:
            self.after(50, self.create_rounded_bg)
            return
        if self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None
        image = Image.new('RGB', (width, height), self.parent_bg)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=self.corner_radius,
            fill=self.bg
        )
        self.bg_image = ImageTk.PhotoImage(image)
        self.bg_label = tk.Label(self, image=self.bg_image, bg=self.parent_bg, borderwidth=0, highlightthickness=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
class SimpleSettingsWindow:
    def __init__(self, parent, pet_manager):
        self.parent = parent
        self.pet_manager = pet_manager
        self.window = None
        self.save_listbox = None
        self.startup_manager = StartupManager()
    def show_settings(self):
        if self.window:
            self.window.destroy()
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pet Settings")
        self.window.geometry("700x700")
        self.window.resizable(True, True)
        self.window.configure(bg=COLORS['background'])
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        general_tab = ttk.Frame(notebook)
        save_tab = ttk.Frame(notebook)
        advanced_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        notebook.add(save_tab, text="Save/Load")
        notebook.add(advanced_tab, text="Advanced")
        self._create_general_tab(general_tab)
        self._create_save_tab(save_tab)
        self._create_advanced_tab(advanced_tab)
    def _create_general_tab(self, parent):
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas = tk.Canvas(canvas_frame, yscrollcommand=scrollbar.set, bg=COLORS['background'])
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        content_frame = ttk.Frame(canvas, padding=5)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw')
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        content_frame.bind('<Configure>', configure_scroll_region)
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas_window)
        name_frame = ttk.LabelFrame(content_frame, text="Pet Name", padding=10)
        name_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(name_frame, text=f"Current Name: {self.pet_manager.name}").pack(anchor="w")
        name_entry_frame = ttk.Frame(name_frame)
        name_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_entry_frame, text="New Name:").pack(side=tk.LEFT, padx=(0, 5))
        name_entry = ttk.Entry(name_entry_frame)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        change_btn = SimpleButton(name_frame, text="Change Name",
                                command=lambda: self.change_pet_name(name_entry.get()))
        change_btn.pack(pady=5)
        behavior_frame = ttk.LabelFrame(content_frame, text="Behavior Settings", padding=10)
        behavior_frame.pack(fill=tk.X, padx=10, pady=10)
        always_on_top_var = tk.BooleanVar(value=self.pet_manager.settings.get('always_on_top', True))
        ttk.Checkbutton(behavior_frame, text="Always on top", variable=always_on_top_var,
                       command=lambda: self.pet_manager.update_setting('always_on_top', always_on_top_var.get())).pack(anchor="w")
        start_with_windows_var = tk.BooleanVar(value=self.startup_manager.is_enabled())
        ttk.Checkbutton(behavior_frame, text="Start with Windows", variable=start_with_windows_var,
                       command=lambda: self._toggle_startup(start_with_windows_var.get())).pack(anchor="w")
        size_frame = ttk.LabelFrame(content_frame, text="Pet Size", padding=10)
        size_frame.pack(fill=tk.X, padx=10, pady=10)
        size_var = tk.IntVar(value=self.pet_manager.settings['pet_size'])
        size_label_frame = ttk.Frame(size_frame)
        size_label_frame.pack(fill=tk.X)
        ttk.Label(size_label_frame, text="Size:").pack(side=tk.LEFT)
        size_value_label = ttk.Label(size_label_frame, text=f"{size_var.get()}%")
        size_value_label.pack(side=tk.RIGHT)
        size_slider = ttk.Scale(size_frame, from_=50, to=150, variable=size_var, orient=tk.HORIZONTAL)
        size_slider.pack(fill=tk.X)
        def update_size_label(event=None):
            size_value_label.config(text=f"{size_var.get()}%")
            self.pet_manager.update_setting('pet_size', size_var.get())
        size_slider.bind("<Motion>", update_size_label)
        size_slider.bind("<ButtonRelease-1>", update_size_label)
        speed_frame = ttk.LabelFrame(content_frame, text="Movement Speed", padding=10)
        speed_frame.pack(fill=tk.X, padx=10, pady=10)
        speed_var = tk.IntVar(value=self.pet_manager.settings['movement_speed'])
        speed_label_frame = ttk.Frame(speed_frame)
        speed_label_frame.pack(fill=tk.X)
        ttk.Label(speed_label_frame, text="Speed:").pack(side=tk.LEFT)
        speed_value_label = ttk.Label(speed_label_frame, text=f"{speed_var.get()}/10")
        speed_value_label.pack(side=tk.RIGHT)
        speed_slider = ttk.Scale(speed_frame, from_=1, to=10, variable=speed_var, orient=tk.HORIZONTAL)
        speed_slider.pack(fill=tk.X)
        def update_speed_label(event=None):
            speed_value_label.config(text=f"{speed_var.get()}/10")
            self.pet_manager.update_setting('movement_speed', speed_var.get())
        speed_slider.bind("<Motion>", update_speed_label)
        speed_slider.bind("<ButtonRelease-1>", update_speed_label)
        context_awareness_frame = ttk.LabelFrame(content_frame, text="Context Awareness", padding=10)
        context_awareness_frame.pack(fill=tk.X, padx=10, pady=10)
        dnd_mode_var = tk.BooleanVar(value=self.pet_manager.settings.get('context_awareness_enabled', True))
        dnd_checkbutton = ttk.Checkbutton(context_awareness_frame, text="DND-Mode", variable=dnd_mode_var,
                                           command=lambda: self.pet_manager.update_setting('context_awareness_enabled', dnd_mode_var.get()))
        dnd_checkbutton.pack(anchor="w", pady=(0, 5))
        dnd_explanation = ttk.Label(context_awareness_frame, text="When enabled, the pet will move away from certain windows to avoid disturbing you.",
                                    font=("Arial", 8), foreground=COLORS['text_light'])
        dnd_explanation.pack(anchor="w", padx=(20, 0))
        credits_frame = ttk.LabelFrame(content_frame, text="About", padding=10)
        credits_frame.pack(fill=tk.X, padx=10, pady=10)
        credits_btn = SimpleButton(credits_frame, text="Credits", command=self.show_credits)
        credits_btn.pack(pady=5)
    def show_credits(self):
        """Display credits information in a beautiful popup with clickable links"""
        credits_window = tk.Toplevel(self.window)
        credits_window.title("Credits")
        credits_window.geometry("500x400")
        credits_window.resizable(False, False)
        credits_window.configure(bg=COLORS['background'])
        credits_window.attributes('-topmost', True)
        credits_window.transient(self.window)
        credits_window.grab_set()
        x = self.window.winfo_x() + (self.window.winfo_width() - 500) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 400) // 2
        credits_window.geometry(f"+{x}+{y}")
        main_frame = RoundedFrame(credits_window, bg=COLORS['surface'], corner_radius=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        title_label = tk.Label(main_frame, text="🎮 VPet Credits",
                              font=("Arial", 18, "bold"),
                              bg=COLORS['surface'],
                              fg=COLORS['primary'])
        title_label.pack(pady=(20, 30))
        content_frame = tk.Frame(main_frame, bg=COLORS['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        dev_frame = tk.Frame(content_frame, bg=COLORS['surface'])
        dev_frame.pack(fill=tk.X, pady=(0, 20))
        dev_title = tk.Label(dev_frame, text="🧑‍💻 Game Developer:",
                            font=("Arial", 12, "bold"),
                            bg=COLORS['surface'],
                            fg=COLORS['text'])
        dev_title.pack(anchor="w")
        dev_name = tk.Label(dev_frame, text="Diogo Parreirão",
                           font=("Arial", 11),
                           bg=COLORS['surface'],
                           fg=COLORS['text'])
        dev_name.pack(anchor="w", padx=(20, 0))
        github_link = tk.Label(dev_frame, text="🔗 GitHub Repository",
                              font=("Arial", 10, "underline"),
                              bg=COLORS['surface'],
                              fg=COLORS['primary'],
                              cursor="hand2")
        github_link.pack(anchor="w", padx=(20, 0), pady=(5, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Parreirao2/VPet"))
        assets_frame = tk.Frame(content_frame, bg=COLORS['surface'])
        assets_frame.pack(fill=tk.X, pady=(0, 20))
        assets_title = tk.Label(assets_frame, text="🎨 Assets:",
                               font=("Arial", 12, "bold"),
                               bg=COLORS['surface'],
                               fg=COLORS['text'])
        assets_title.pack(anchor="w")
        assets_name = tk.Label(assets_frame, text="Pixelrepo",
                              font=("Arial", 11),
                              bg=COLORS['surface'],
                              fg=COLORS['text'])
        assets_name.pack(anchor="w", padx=(20, 0))
        pixelrepo_link = tk.Label(assets_frame, text="🔗 Visit Pixelrepo",
                                 font=("Arial", 10, "underline"),
                                 bg=COLORS['surface'],
                                 fg=COLORS['primary'],
                                 cursor="hand2")
        pixelrepo_link.pack(anchor="w", padx=(20, 0), pady=(5, 0))
        pixelrepo_link.bind("<Button-1>", lambda e: webbrowser.open("https://pixelrepo.com"))
        thanks_frame = tk.Frame(content_frame, bg=COLORS['surface'])
        thanks_frame.pack(fill=tk.X, pady=(0, 20))
        thanks_title = tk.Label(thanks_frame, text="💝 Special Thanks:",
                               font=("Arial", 12, "bold"),
                               bg=COLORS['surface'],
                               fg=COLORS['text'])
        thanks_title.pack(anchor="w")
        thanks_name = tk.Label(thanks_frame, text="My Girlfriend Inês H.",
                              font=("Arial", 11),
                              bg=COLORS['surface'],
                              fg=COLORS['text'])
        thanks_name.pack(anchor="w", padx=(20, 0))
        separator = tk.Frame(content_frame, height=2, bg=COLORS['primary'])
        separator.pack(fill=tk.X, pady=20)
        version_label = tk.Label(content_frame, text="VPet - Virtual Pet Desktop Companion",
                                font=("Arial", 9, "italic"),
                                bg=COLORS['surface'],
                                fg=COLORS['text_light'])
        version_label.pack()
        button_frame = tk.Frame(main_frame, bg=COLORS['surface'])
        button_frame.pack(fill=tk.X, pady=(20, 20))
        close_btn = SimpleButton(button_frame, text="Close",
                                command=credits_window.destroy,
                                bg=COLORS['primary'],
                                fg="white",
                                width=12)
        close_btn.pack()
        def on_link_enter(event, label):
            label.config(fg=COLORS['primary_light'])
        def on_link_leave(event, label):
            label.config(fg=COLORS['primary'])
        github_link.bind("<Enter>", lambda e: on_link_enter(e, github_link))
        github_link.bind("<Leave>", lambda e: on_link_leave(e, github_link))
        pixelrepo_link.bind("<Enter>", lambda e: on_link_enter(e, pixelrepo_link))
        pixelrepo_link.bind("<Leave>", lambda e: on_link_leave(e, pixelrepo_link))
        credits_window.protocol("WM_DELETE_WINDOW", credits_window.destroy)
    def _create_save_tab(self, parent):
        save_frame = ttk.LabelFrame(parent, text="Save Pet", padding=10)
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        save_btn = SimpleButton(save_frame, text="Save Current Pet", command=self.save_pet)
        save_btn.pack(pady=5)
        load_frame = ttk.LabelFrame(parent, text="Load Pet", padding=10)
        load_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(load_frame, text="Available Save Files:").pack(anchor="w")
        list_frame = ttk.Frame(load_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        columns = ('filename', 'pet_name', 'stage', 'age', 'currency', 'save_date')
        save_treeview = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        save_treeview.heading('filename', text='File')
        save_treeview.heading('pet_name', text='Pet Name')
        save_treeview.heading('stage', text='Stage')
        save_treeview.heading('age', text='Age (days)')
        save_treeview.heading('currency', text='Coins')
        save_treeview.heading('save_date', text='Last Saved')
        save_treeview.column('filename', width=120)
        save_treeview.column('pet_name', width=100)
        save_treeview.column('stage', width=80)
        save_treeview.column('age', width=80)
        save_treeview.column('currency', width=80)
        save_treeview.column('save_date', width=140)
        save_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=save_treeview.yview)
        self.save_treeview = save_treeview
        self._populate_save_files_treeview()
        button_frame = ttk.Frame(load_frame)
        button_frame.pack(fill=tk.X, pady=5)
        load_btn = SimpleButton(button_frame, text="Load Selected",
                               command=lambda: self.load_selected_pet_from_treeview())
        load_btn.pack(side=tk.LEFT, padx=(0, 5))
        delete_btn = SimpleButton(button_frame, text="Delete Selected",
                                command=lambda: self.delete_selected_pet_from_treeview(),
                                bg=COLORS['error'])
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        refresh_btn = SimpleButton(button_frame, text="Refresh List",
                                 command=self._populate_save_files_treeview)
        refresh_btn.pack(side=tk.LEFT)
        reset_frame = ttk.LabelFrame(parent, text="Reset Pet", padding=10)
        reset_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(reset_frame, text="Warning: This will reset your pet to Baby stage with 0 days age and default stats.",
                 foreground=COLORS['error']).pack(pady=5)
        reset_btn = SimpleButton(reset_frame, text="Reset Pet",
                               command=self.reset_pet,
                               bg=COLORS['error'])
        reset_btn.pack(pady=5)
    def _populate_save_files_treeview(self):
        """Populate the treeview with organized save file information"""
        if not hasattr(self, 'save_treeview'):
            return
        for item in self.save_treeview.get_children():
            self.save_treeview.delete(item)
        save_files = self.pet_manager.get_save_files()
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
        config_files = {
            'settings.json': 'App Settings',
            'ai_chat_settings.json': 'AI Chat Settings (API Keys)',
            'conversation_history.json': 'Chat History',
            'gemini_settings.json': 'Gemini API Settings'
        }
        for save_file in save_files:
            try:
                filepath = os.path.join(save_path, save_file)
                if save_file in config_files:
                    config_label = config_files[save_file]
                    self.save_treeview.insert('', 'end', values=(
                        f"{save_file} ({config_label})",
                        'Configuration File',
                        '-',
                        '-',
                        '-',
                        '-'
                    ), tags=('config',))
                    continue
                with open(filepath, 'r') as f:
                    save_data = json.load(f)
                if 'name' not in save_data or 'stats' not in save_data:
                    self.save_treeview.insert('', 'end', values=(
                        f"{save_file} (Unknown Config)",
                        'Configuration File',
                        '-',
                        '-',
                        '-',
                        '-'
                    ), tags=('config',))
                    continue
                pet_name = save_data.get('name', 'Unknown')
                stage = save_data.get('stage', 'Unknown')
                age = round(save_data.get('stats', {}).get('age', 0), 1)
                currency = save_data.get('currency', 0)
                save_date_str = save_data.get('save_date', '')
                if save_date_str:
                    try:
                        from datetime import datetime
                        save_date = datetime.fromisoformat(save_date_str.replace('Z', '+00:00'))
                        formatted_date = save_date.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = 'Unknown'
                else:
                    formatted_date = 'Unknown'
                if 'backup' in save_file.lower():
                    display_name = f"{save_file} (Backup)"
                    tags = ('backup',)
                elif 'autosave' in save_file.lower():
                    display_name = f"{save_file} (Auto)"
                    tags = ('autosave',)
                else:
                    display_name = save_file
                    tags = ('pet_save',)
                self.save_treeview.insert('', 'end', values=(
                    display_name,
                    pet_name,
                    stage,
                    f"{age}",
                    f"{currency:,}",
                    formatted_date
                ), tags=tags)
            except Exception as e:
                self.save_treeview.insert('', 'end', values=(
                    f"{save_file} (Unreadable)",
                    'Error reading file',
                    '-',
                    '-',
                    '-',
                    '-'
                ), tags=('error',))
                print(f"Error reading save file {save_file}: {e}")
        self.save_treeview.tag_configure('config', background='#f0f0f0', foreground='#666666')
        self.save_treeview.tag_configure('backup', background='#e6f3ff')
        self.save_treeview.tag_configure('autosave', background='#fff2e6')
        self.save_treeview.tag_configure('pet_save', background='white')
        self.save_treeview.tag_configure('error', background='#ffe6e6', foreground='#cc0000')
    def load_selected_pet_from_treeview(self):
        """Load the selected pet from the treeview"""
        selected = self.save_treeview.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a save file to load.")
            return
        item = self.save_treeview.item(selected[0])
        filename = item['values'][0]
        tags = self.save_treeview.item(selected[0], 'tags')
        if 'config' in tags:
            messagebox.showwarning("Invalid Selection",
                                  "Cannot load configuration files as pet saves.\n\nPlease select a pet save file.")
            return
        if 'error' in tags:
            messagebox.showerror("Invalid File",
                               "Cannot load this file due to read errors.\n\nThe file may be corrupted.")
            return
        if ' (' in filename:
            filename = filename.split(' (')[0]
        self.pet_manager.load_pet(filename)
        self.window.destroy()
    def delete_selected_pet_from_treeview(self):
        """Delete the selected pet from the treeview"""
        selected = self.save_treeview.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a save file to delete.")
            return
        item = self.save_treeview.item(selected[0])
        filename = item['values'][0]
        pet_name = item['values'][1]
        tags = self.save_treeview.item(selected[0], 'tags')
        if 'config' in tags:
            if not messagebox.askyesno("Delete Configuration File?",
                                      f"You are about to delete a configuration file:\n\n{filename}\n\n" +
                                      "This may reset your settings or API keys.\n\n" +
                                      "Are you sure you want to continue?",
                                      icon='warning'):
                return
        if ' (' in filename:
            filename = filename.split(' (')[0]
        if 'config' in tags:
            confirm_msg = f"Are you sure you want to delete the configuration file?\n\nFile: {filename}"
        else:
            confirm_msg = f"Are you sure you want to delete the save file for '{pet_name}'?\n\nFile: {filename}"
        if messagebox.askyesno("Confirm Delete", confirm_msg):
            if self.pet_manager.delete_save(filename):
                self.save_treeview.delete(selected[0])
                messagebox.showinfo("Success", "File deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete file.")
    def _create_appearance_tab(self, parent):
        color_frame = ttk.LabelFrame(parent, text="Pet Color", padding=10)
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        current_color = self.pet_manager.settings.get('pet_color', 'black')
        ttk.Label(color_frame, text=f"Current Color: {current_color.title()}").pack(anchor="w")
        color_var = tk.StringVar(value=current_color)
        ttk.Radiobutton(color_frame, text="Black", variable=color_var, value="black",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Blue", variable=color_var, value="blue",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Pink", variable=color_var, value="pink",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Label(color_frame, text="Changes to pet color will take effect immediately.",
                 wraplength=400, font=("Arial", 8)).pack(anchor="w", pady=(5, 0))
        size_frame = ttk.LabelFrame(parent, text="Pet Size", padding=10)
        size_frame.pack(fill=tk.X, padx=10, pady=10)
        size_var = tk.IntVar(value=self.pet_manager.settings['pet_size'])
        size_label_frame = ttk.Frame(size_frame)
        size_label_frame.pack(fill=tk.X)
        ttk.Label(size_label_frame, text="Size:").pack(side=tk.LEFT)
        size_value_label = ttk.Label(size_label_frame, text=f"{size_var.get()}%")
        size_value_label.pack(side=tk.RIGHT)
        size_slider = ttk.Scale(size_frame, from_=50, to=150, variable=size_var, orient=tk.HORIZONTAL)
        size_slider.pack(fill=tk.X)
        def update_size_label(event=None):
            size_value_label.config(text=f"{size_var.get()}%")
            self.pet_manager.update_setting('pet_size', size_var.get())
        size_slider.bind("<Motion>", update_size_label)
        size_slider.bind("<ButtonRelease-1>", update_size_label)
        speed_frame = ttk.LabelFrame(parent, text="Movement Speed", padding=10)
        speed_frame.pack(fill=tk.X, padx=10, pady=10)
        speed_var = tk.IntVar(value=self.pet_manager.settings['movement_speed'])
        speed_label_frame = ttk.Frame(speed_frame)
        speed_label_frame.pack(fill=tk.X)
        ttk.Label(speed_label_frame, text="Speed:").pack(side=tk.LEFT)
        speed_value_label = ttk.Label(speed_label_frame, text=f"{speed_var.get()}/10")
        speed_value_label.pack(side=tk.RIGHT)
        speed_slider = ttk.Scale(speed_frame, from_=1, to=10, variable=speed_var, orient=tk.HORIZONTAL)
        speed_slider.pack(fill=tk.X)
        def update_speed_label(event=None):
            speed_value_label.config(text=f"{speed_var.get()}/10")
            self.pet_manager.update_setting('movement_speed', speed_var.get())
        speed_slider.bind("<Motion>", update_speed_label)
        speed_slider.bind("<ButtonRelease-1>", update_speed_label)
    def _create_advanced_tab(self, parent):
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas = tk.Canvas(canvas_frame, yscrollcommand=scrollbar.set, bg=COLORS['background'])
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        content_frame = ttk.Frame(canvas, padding=5)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw', width=canvas.winfo_width())
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        content_frame.bind('<Configure>', configure_scroll_region)
        def configure_canvas_width(event):
            canvas_width = event.width - scrollbar.winfo_width() - 10
            canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.bind('<Configure>', configure_canvas_width)
        color_frame = ttk.LabelFrame(content_frame, text="Pet Color", padding=10)
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        current_color = self.pet_manager.settings.get('pet_color', 'black')
        ttk.Label(color_frame, text=f"Current Color: {current_color.title()}").pack(anchor="w")
        color_var = tk.StringVar(value=current_color)
        ttk.Radiobutton(color_frame, text="Black", variable=color_var, value="black",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Blue", variable=color_var, value="blue",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Pink", variable=color_var, value="pink",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Label(color_frame, text="Changes to pet color will take effect immediately.",
                 wraplength=400, font=("Arial", 8)).pack(anchor="w", pady=(5, 0))
        age_frame = ttk.LabelFrame(content_frame, text="Pet Age and Stage", padding=10)
        age_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(age_frame, text=f"Current Age: {round(self.pet_manager.pet_state.stats.get_stat('age'), 1)} days").pack(anchor="w")
        ttk.Label(age_frame, text=f"Current Stage: {self.pet_manager.pet_state.stage}").pack(anchor="w")
        age_entry_frame = ttk.Frame(age_frame)
        age_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(age_entry_frame, text=f"Set Age (days) (Current: {round(self.pet_manager.pet_state.stats.get_stat('age'), 1)}):").pack(side=tk.LEFT, padx=(0, 5))
        age_entry = ttk.Entry(age_entry_frame, width=10)
        age_entry.pack(side=tk.LEFT)
        stage_frame = ttk.Frame(age_frame)
        stage_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stage_frame, text="Set Stage:").pack(side=tk.LEFT, padx=(0, 5))
        stage_var = tk.StringVar(value=self.pet_manager.pet_state.stage)
        stage_combo = ttk.Combobox(stage_frame, textvariable=stage_var, values=['Baby', 'Child', 'Teen', 'Adult'], state='readonly')
        stage_combo.pack(side=tk.LEFT)
        apply_btn = SimpleButton(age_frame, text="Apply Changes",
                               command=lambda: self._apply_advanced_changes(age_entry.get(), stage_var.get()))
        apply_btn.pack(pady=5)
        poop_frame = ttk.LabelFrame(content_frame, text="Poop Frequency", padding=10)
        poop_frame.pack(fill=tk.X, padx=10, pady=10)
        poop_var = tk.DoubleVar(value=self.pet_manager.settings.get('poop_frequency', 0.5))
        poop_label_frame = ttk.Frame(poop_frame)
        poop_label_frame.pack(fill=tk.X)
        ttk.Label(poop_label_frame, text="Frequency:").pack(side=tk.LEFT)
        poop_value_label = ttk.Label(poop_label_frame, text=f"{poop_var.get():.1f}")
        poop_value_label.pack(side=tk.RIGHT)
        poop_slider = ttk.Scale(poop_frame, from_=0.1, to=2.0, variable=poop_var, orient=tk.HORIZONTAL)
        poop_slider.pack(fill=tk.X)
        def update_poop_label_visual(event=None):
            poop_value_label.config(text=f"{poop_var.get():.1f}")
        def update_poop_label_complete(event=None):
            value = poop_var.get()
            poop_value_label.config(text=f"{value:.1f}")
            self.pet_manager.update_setting('poop_frequency', value)
            if hasattr(self.pet_manager, 'poop_system') and self.pet_manager.poop_system:
                self.pet_manager.poop_system.poop_chance = value
                print(f"Poop frequency updated to {value:.1f}")
        poop_slider.bind("<Motion>", update_poop_label_visual)
        poop_slider.bind("<ButtonRelease-1>", update_poop_label_complete)
        ttk.Label(poop_frame, text="Lower values mean less frequent poops, higher values mean more frequent poops.",
                 wraplength=400, font=("Arial", 8)).pack(anchor="w", pady=(5, 0))
        depletion_frame = ttk.LabelFrame(content_frame, text="Stat Depletion Rates", padding=10)
        depletion_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(depletion_frame, text="Adjust how quickly each stat decreases over time. Higher values mean faster depletion.",
                 wraplength=400, font=("Arial", 9)).pack(anchor="w", pady=(0, 10))
        for stat in ['hunger', 'happiness', 'energy', 'cleanliness', 'social']:
            stat_frame = ttk.Frame(depletion_frame)
            stat_frame.pack(fill=tk.X, pady=8)
            stat_label_frame = ttk.LabelFrame(stat_frame, text=f"{stat.title()} Rate", padding=5)
            stat_label_frame.pack(fill=tk.X, expand=True)
            slider_frame = ttk.Frame(stat_label_frame)
            slider_frame.pack(fill=tk.X, expand=True, pady=3)
            current_rate = 0.1
            if hasattr(self.pet_manager.pet_state, 'stats') and hasattr(self.pet_manager.pet_state.stats, 'decay_rates'):
                current_rate = self.pet_manager.pet_state.stats.decay_rates.get(stat, 0.1)
            rate_var = tk.DoubleVar(value=current_rate)
            value_label = ttk.Label(slider_frame, text=f"{rate_var.get():.1f}", width=5)
            value_label.pack(side=tk.RIGHT, padx=(5, 0))
            rate_slider = ttk.Scale(slider_frame, from_=0.1, to=2.0, variable=rate_var, orient=tk.HORIZONTAL)
            rate_slider.pack(fill=tk.X, expand=True, pady=3, padx=5)
            slider_labels_frame = ttk.Frame(stat_label_frame)
            slider_labels_frame.pack(fill=tk.X, padx=5)
            ttk.Label(slider_labels_frame, text="Slow", font=("Arial", 8)).pack(side=tk.LEFT)
            ttk.Label(slider_labels_frame, text="Fast", font=("Arial", 8)).pack(side=tk.RIGHT)
            def update_rate_visual(event, v=rate_var, lbl=value_label):
                lbl.config(text=f"{v.get():.1f}")
            def update_rate_complete(event, s=stat, v=rate_var, lbl=value_label):
                value = v.get()
                lbl.config(text=f"{value:.1f}")
                self._update_depletion_rate(s, value)
            rate_slider.bind("<Motion>", update_rate_visual)
            rate_slider.bind("<ButtonRelease-1>", update_rate_complete)
    def _apply_advanced_changes(self, new_age, new_stage):
        try:
            if new_age.strip():
                age = float(new_age)
                if 0 <= age <= 1000:
                    self.pet_manager.pet_state.stats['age'] = age
                    self.pet_manager.check_evolution()
                else:
                    self.show_notification("Invalid Age", "Age must be between 0 and 1000 days", COLORS['warning'])
                    return
            if new_stage != self.pet_manager.pet_state.stage:
                if self.pet_manager.evolve_to(new_stage):
                    self.show_notification("Stage Updated", f"Pet evolved to {new_stage} stage", COLORS['success'])
                else:
                    self.show_notification("Stage Update Failed", "Could not update pet stage", COLORS['error'])
                    return
            self.show_notification("Changes Applied", "Advanced settings updated successfully", COLORS['success'])
        except ValueError:
            self.show_notification("Invalid Input", "Please enter a valid number for age", COLORS['error'])
    def _update_depletion_rate(self, stat, value):
        if hasattr(self.pet_manager.pet_state, 'stats') and hasattr(self.pet_manager.pet_state.stats, 'decay_rates'):
            self.pet_manager.pet_state.stats.decay_rates[stat] = value
            self.pet_manager.update_setting(f'stat_depletion_{stat}', value)
        else:
            self.show_notification("Update Failed", f"Could not update {stat} depletion rate", COLORS['error'])
    def change_pet_name(self, new_name):
        if new_name and new_name.strip():
            self.pet_manager.name = new_name.strip()
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.winfo_children():
                        for frame in tab.winfo_children():
                            if isinstance(frame, ttk.LabelFrame) and frame.cget('text') == 'Pet Name':
                                for child in frame.winfo_children():
                                    if isinstance(child, ttk.Label) and 'Current Name:' in child.cget('text'):
                                        child.config(text=f"Current Name: {self.pet_manager.name}")
                                        break
            self.show_notification("Name Changed", f"Pet name changed to {new_name}", COLORS['success'])
    def _update_pet_color(self, color):
        old_color = self.pet_manager.settings.get('pet_color', 'black')
        self.pet_manager.update_setting('pet_color', color)
        if hasattr(self.pet_manager, 'animation') and hasattr(self.pet_manager.animation, 'handle_color_change'):
            self.pet_manager.animation.handle_color_change(old_color, color)
        else:
            current_direction = None
            if hasattr(self.pet_manager, 'pet_state') and hasattr(self.pet_manager.pet_state, 'direction'):
                current_direction = self.pet_manager.pet_state.direction
            if hasattr(self.pet_manager, 'animation') and hasattr(self.pet_manager.animation, 'load_animations'):
                self.pet_manager.animation.animations = {}
                self.pet_manager.animation.load_animations()
                current_stage = self.pet_manager.pet_state.stage
                if hasattr(self.pet_manager, 'load_stage_animations'):
                    self.pet_manager.load_stage_animations(current_stage)
            if current_direction is not None:
                self.pet_manager.pet_state.direction = current_direction
        self.show_notification("Color Updated", f"Pet color changed to {color.title()}", COLORS['success'])
    def save_pet(self):
        success, message = self.pet_manager.save_pet()
        if success:
            self.show_notification("Save Successful", f"Pet saved to {message}", COLORS['success'])
            if hasattr(self, 'save_treeview'):
                self._populate_save_files_treeview()
        else:
            self.show_notification("Save Failed", f"Failed to save pet: {message}", COLORS['error'])
    def load_pet(self, filename):
        if not filename:
            self.show_notification("No File Selected", "Please select a save file to load.", COLORS['warning'])
            return
        filepath = os.path.join(self.pet_manager.save_path, filename)
        pet, error = self.pet_manager.load_pet(filepath)
        if pet:
            self.show_notification("Load Successful", f"Pet {pet.name} loaded successfully!", COLORS['success'])
            self.window.destroy()
        else:
            self.show_notification("Load Failed", f"Failed to load pet: {error}", COLORS['error'])
    def delete_pet_save(self, listbox):
        filename = listbox.get(tk.ACTIVE)
        if not filename:
            self.show_notification("No File Selected", "Please select a save file to delete.", COLORS['warning'])
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {filename}?", parent=self.window)
        if not confirm:
            return
        success, message = self.pet_manager.delete_save_file(filename)
        if success:
            self.show_notification("Delete Successful", message, COLORS['success'])
            listbox.delete(0, tk.END)
            for save_file in self.pet_manager.get_save_files():
                listbox.insert(tk.END, save_file)
        else:
            self.show_notification("Delete Failed", f"Failed to delete save file: {message}", COLORS['error'])
    def _toggle_startup(self, enabled):
        if enabled:
            success = self.startup_manager.enable()
        else:
            success = self.startup_manager.disable()
        if success:
            self.pet_manager.update_setting('start_with_windows', enabled)
            self.show_notification("Startup Setting",
                                 "Windows startup enabled" if enabled else "Windows startup disabled",
                                 COLORS['success'])
        else:
            self.show_notification("Startup Setting Failed",
                                 "Failed to update Windows startup setting",
                                 COLORS['error'])
    def reset_pet(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset your pet? This will reset to Baby stage with 0 days age and default stats."):
            success, message = self.pet_manager.reset_pet()
            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to reset pet: {message}")
    def periodic_update(self):
        if self.is_visible:
            self.update_stats_display()
            self.update_timer = self.parent.after(1500, self.periodic_update)
    def show_notification(self, title, message, color):
        parent_window = self.window if hasattr(self.window, 'winfo_exists') and self.window.winfo_exists() else self.parent
        notification = tk.Toplevel(parent_window)
        notification.title(title)
        notification.geometry("300x100")
        notification.resizable(False, False)
        notification.configure(bg=color)
        notification.attributes('-topmost', True)
        x = parent_window.winfo_x() + (parent_window.winfo_width() - 300) // 2
        y = parent_window.winfo_y() + (parent_window.winfo_height() - 100) // 2
        notification.geometry(f"+{x}+{y}")
        frame = tk.Frame(notification, bg=color, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        title_label = tk.Label(frame, text=title, font=("Arial", 12, "bold"),
                                bg=color, fg="white")
        title_label.pack(pady=(0, 5))
        message_label = tk.Label(frame, text=message, font=("Arial", 10),
                                 bg=color, fg="white", wraplength=250)
        message_label.pack()
        notification.after(2000, notification.destroy)
        if self.window:
            self.window.bind("<Destroy>", lambda e: notification.destroy() if notification.winfo_exists() else None)
class ModernSettingsWindow(SimpleSettingsWindow):
    def show_settings(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pet Settings")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS['background'])
        main_frame = RoundedFrame(self.window, bg=COLORS['surface'], corner_radius=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        general_tab = ttk.Frame(notebook, style="Modern.TFrame")
        save_tab = ttk.Frame(notebook, style="Modern.TFrame")
        appearance_tab = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(general_tab, text="General")
        notebook.add(save_tab, text="Save/Load")
        notebook.add(appearance_tab, text="Appearance")
        self._create_general_tab(general_tab)
        self._create_save_tab(save_tab)
        self._create_appearance_tab(appearance_tab)
    def _create_general_tab(self, parent):
        name_frame = ttk.LabelFrame(parent, text="Pet Name", padding=10, style='Modern.TLabelframe')
        name_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(name_frame, text=f"Current Name: {self.pet_manager.name}", style='Modern.TLabel').pack(anchor="w")
        name_entry_frame = ttk.Frame(name_frame, style='Modern.TFrame')
        name_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_entry_frame, text="New Name:", style='Modern.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        name_entry = ttk.Entry(name_entry_frame)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        change_btn = ttk.Button(name_frame, text="Change Name", style='Modern.TButton',
                               command=lambda: self.change_pet_name(name_entry.get()))
        change_btn.pack(pady=5)
        behavior_frame = ttk.LabelFrame(parent, text="Behavior Settings", padding=10, style='Modern.TLabelframe')
        behavior_frame.pack(fill=tk.X, padx=10, pady=10)
        always_on_top_var = tk.BooleanVar(value=self.pet_manager.settings.get('always_on_top', True))
        ttk.Checkbutton(behavior_frame, text="Always on top", variable=always_on_top_var, style='Modern.TCheckbutton',
                       command=lambda: self.pet_manager.update_setting('always_on_top', always_on_top_var.get())).pack(anchor="w")
        start_with_windows_var = tk.BooleanVar(value=self.startup_manager.is_enabled())
        ttk.Checkbutton(behavior_frame, text="Start with Windows", variable=start_with_windows_var, style='Modern.TCheckbutton',
                       command=lambda: self._toggle_startup(start_with_windows_var.get())).pack(anchor="w")
        dnd_mode_var = tk.BooleanVar(value=self.pet_manager.settings.get('context_awareness_enabled', True))
        dnd_checkbutton = ttk.Checkbutton(behavior_frame, text="DND-Mode", variable=dnd_mode_var,
                                           command=lambda: self.pet_manager.update_setting('context_awareness_enabled', dnd_mode_var.get()))
        dnd_checkbutton.pack(anchor="w", pady=(5, 0))
        dnd_explanation = ttk.Label(behavior_frame, text="When enabled, the pet will move away from certain windows to avoid disturbing you.",
                                    font=("Arial", 8), foreground=COLORS['text_light'])
        dnd_explanation.pack(anchor="w", padx=(20, 0))
        size_frame = ttk.LabelFrame(parent, text="Pet Size", padding=10, style='Modern.TLabelframe')
        size_frame.pack(fill=tk.X, padx=10, pady=10)
        size_var = tk.IntVar(value=self.pet_manager.settings['pet_size'])
        size_label_frame = ttk.Frame(size_frame, style='Modern.TFrame')
        size_label_frame.pack(fill=tk.X)
        ttk.Label(size_label_frame, text="Size:", style='Modern.TLabel').pack(side=tk.LEFT)
        size_value_label = ttk.Label(size_label_frame, text=f"{size_var.get()}%", style='Modern.TLabel')
        size_value_label.pack(side=tk.RIGHT)
        size_slider = ttk.Scale(size_frame, from_=50, to=150, variable=size_var, orient=tk.HORIZONTAL, style='Modern.Horizontal.TScale')
        size_slider.pack(fill=tk.X)
        def update_size_label(event=None):
            size_value_label.config(text=f"{size_var.get()}%")
            self.pet_manager.update_setting('pet_size', size_var.get())
        size_slider.bind("<Motion>", update_size_label)
        size_slider.bind("<ButtonRelease-1>", update_size_label)
        transparency_frame = ttk.LabelFrame(parent, text="Window Transparency", padding=10, style='Modern.TLabelframe')
        transparency_frame.pack(fill=tk.X, padx=10, pady=10)
        transparency_var = tk.IntVar(value=self.pet_manager.settings.get('transparency', 0))
        transparency_label_frame = ttk.Frame(transparency_frame, style='Modern.TFrame')
        transparency_label_frame.pack(fill=tk.X)
        ttk.Label(transparency_label_frame, text="Transparency:", style='Modern.TLabel').pack(side=tk.LEFT)
        transparency_value_label = ttk.Label(transparency_label_frame, text=f"{transparency_var.get()}%", style='Modern.TLabel')
        transparency_value_label.pack(side=tk.RIGHT)
        transparency_slider = ttk.Scale(transparency_frame, from_=0, to=50, variable=transparency_var, orient=tk.HORIZONTAL, style='Modern.Horizontal.TScale')
        transparency_slider.pack(fill=tk.X)
        def update_transparency_label(event=None):
            transparency_value_label.config(text=f"{transparency_var.get()}%")
            self.pet_manager.update_setting('transparency', transparency_var.get())
            alpha = int(255 * (100 - transparency_var.get()) / 100)
            self.pet_manager.root.attributes('-alpha', alpha/255)
        transparency_slider.bind("<Motion>", update_transparency_label)
        transparency_slider.bind("<ButtonRelease-1>", update_transparency_label)
        speed_frame = ttk.LabelFrame(parent, text="Movement Speed", padding=10, style='Modern.TLabelframe')
        speed_frame.pack(fill=tk.X, padx=10, pady=10)
        speed_var = tk.IntVar(value=self.pet_manager.settings['movement_speed'])
        speed_label_frame = ttk.Frame(speed_frame, style='Modern.TFrame')
        speed_label_frame.pack(fill=tk.X)
        ttk.Label(speed_label_frame, text="Speed:", style='Modern.TLabel').pack(side=tk.LEFT)
        speed_value_label = ttk.Label(speed_label_frame, text=f"{speed_var.get()}/10", style='Modern.TLabel')
        speed_value_label.pack(side=tk.RIGHT)
        speed_slider = ttk.Scale(speed_frame, from_=1, to=10, variable=speed_var, orient=tk.HORIZONTAL, style='Modern.Horizontal.TScale')
        speed_slider.pack(fill=tk.X)
        def update_speed_label(event=None):
            speed_value_label.config(text=f"{speed_var.get()}/10")
            self.pet_manager.update_setting('movement_speed', speed_var.get())
        speed_slider.bind("<Motion>", update_speed_label)
        speed_slider.bind("<ButtonRelease-1>", update_speed_label)
    def show_notification(self, title, message, color):
        notification = tk.Toplevel(self.window)
        notification.overrideredirect(True)
        notification.attributes('-topmost', True)
        x = self.window.winfo_x() + self.window.winfo_width()//2 - 150
        y = self.window.winfo_y() + self.window.winfo_height()//2 - 50
        notification.geometry(f'+{x}+{y}')
        frame = RoundedFrame(notification, bg=color, corner_radius=10)
        frame.pack(padx=2, pady=2)
        title_label = tk.Label(frame, text=title, font=("Arial", 12, "bold"),
                                bg=color, fg="white")
        title_label.pack(padx=20, pady=(10, 5))
        message_label = tk.Label(frame, text=message, font=("Arial", 10),
                                 bg=color, fg="white", wraplength=250)
        message_label.pack(padx=20, pady=(0, 10))
        notification.after(3000, notification.destroy)
class ModernTooltip:
    def __init__(self, widget, text, bg=COLORS['primary_dark'], fg='white', delay=500):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.delay = delay
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    def on_enter(self, event):
        self.schedule_tooltip()
    def on_leave(self, event):
        self.hide_tooltip()
        self.cancel_schedule()
    def on_motion(self, event):
        if self.tooltip_window:
            self.hide_tooltip()
            self.schedule_tooltip()
    def schedule_tooltip(self):
        self.cancel_schedule()
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)
    def cancel_schedule(self):
        if hasattr(self, 'schedule_id'):
            self.widget.after_cancel(self.schedule_id)
            del self.schedule_id
    def show_tooltip(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.lift()
        self.tooltip_window.attributes('-topmost', True)
        bg_color = COLORS['background']
        self.tooltip_window.configure(bg=bg_color)
        frame = RoundedFrame(self.tooltip_window, bg=self.bg, corner_radius=8)
        frame.pack(padx=1, pady=1)
        label = tk.Label(frame, text=self.text, justify=tk.LEFT,
                       background=self.bg, foreground=self.fg,
                       relief=tk.FLAT, borderwidth=0,
                       font=("Arial", 9))
        label.pack(padx=6, pady=3)
    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
class ModernButton(tk.Canvas):
    def __init__(self, parent, text="Button", command=None, width=100, height=30,
                 bg=COLORS['primary'], fg="white", corner_radius=10, **kwargs):
        if hasattr(parent, 'winfo_class') and parent.winfo_class().startswith('T'):
            parent_bg = COLORS['background']
        else:
            parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else COLORS['background']
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg, **kwargs)
        self.text = text
        self.command = command
        self.corner_radius = corner_radius
        self.bg = bg
        self.fg = fg
        self.hover_bg = COLORS['primary_light']
        self.pressed_bg = COLORS['primary_dark']
        self.current_bg = self.bg
        self.draw_button()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    def draw_button(self):
        self.delete("all")
        self.create_rounded_rectangle(
            2, 2, self.winfo_width()-2, self.winfo_height()-2,
            radius=self.corner_radius, fill=self.current_bg
        )
        self.create_text(
            self.winfo_width()/2, self.winfo_height()/2,
            text=self.text, fill=self.fg, font=("Arial", 10, "bold")
        )
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)
    def on_enter(self, event):
        self.current_bg = self.hover_bg
        self.draw_button()
    def on_leave(self, event):
        self.current_bg = self.bg
        self.draw_button()
    def on_press(self, event):
        self.current_bg = self.pressed_bg
        self.draw_button()
    def on_release(self, event):
        self.current_bg = self.hover_bg
        self.draw_button()
        if self.command:
            self.command()
class SpeechBubble:
    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.parent = parent
        self.bubble_window = None
        self.bubble_duration = 5000
        self._bubble_timer = None
        self._update_position_timer = None
        self.responses = {
            'feed': ["Yum yum!", "Delicious!", "More please!", "Tasty!"],
            'play': ["This is fun!", "Wheee!", "Let's play more!", "*excited noises*"],
            'clean': ["So fresh!", "Squeaky clean!", "*happy splashing*", "I feel renewed!"],
            'medicine': ["Feeling better!", "*gulp*", "Tastes weird...", "Thank you!"],
            'pet': ["*purrs*", "I love attention!", "More pets please!", "*happy noises*"],
            'sleep': ["*yawns*", "Zzz...", "Nap time...", "*sleepy noises*"],
            'happy': ["I'm so happy!", "*excited bouncing*", "Best day ever!", "Yay!"],
            'sad': ["*sniffles*", "I'm sad...", "*sighs*", "Need hugs..."],
            'hungry': ["I'm hungry!", "Feed me please!", "*stomach growls*", "Need food..."],
            'sick': ["Not feeling well...", "*coughs*", "I need medicine!", "*sneezes*"],
            'tired': ["*yawns*", "So sleepy...", "Need rest...", "Can barely keep eyes open..."],
            'dirty': ["I need a bath!", "*scratches*", "Feeling icky...", "Too dirty..."],
            'lonely': ["I miss you...", "Play with me?", "*lonely sigh*", "Need company..."],
            'default': ["Hello!", "*happy noises*", "I'm here!", "Notice me!"]
        }
    def show_bubble(self, message_type, custom_message=None):
        self.clear_bubble()
        responses = self.responses.get(message_type, self.responses['default'])
        message = custom_message if custom_message else random.choice(responses)
        self._create_bubble(message)
    def _create_bubble(self, message):
        self.clear_bubble()
        self.bubble_window = tk.Toplevel(self.parent)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.attributes('-topmost', True)
        self.bubble_window.configure(bg=COLORS['surface'])
        bubble_frame = tk.Frame(self.bubble_window, bg=COLORS['surface'],
                               bd=2, relief=tk.RAISED)
        bubble_frame.pack(padx=5, pady=5)
        text_label = tk.Label(bubble_frame, text=message,
                            font=("Arial", 11),
                            bg=COLORS['surface'],
                            fg=COLORS['text'],
                            wraplength=180,
                            justify=tk.CENTER,
                            padx=10, pady=10)
        text_label.pack()
        self._update_bubble_position()
        self._start_position_updates()
        display_time = max(self.bubble_duration, len(message) * 100)
        self._bubble_timer = self.parent.after(display_time, self.clear_bubble)
    def _update_bubble_position(self):
        if not self.bubble_window:
            return
        pet_x = self.parent.winfo_x() + self.canvas.winfo_width() // 2
        pet_y = self.parent.winfo_y() + 100
        bubble_width = self.bubble_window.winfo_reqwidth()
        bubble_height = self.bubble_window.winfo_reqheight()
        bubble_x = max(0, pet_x - bubble_width // 2)
        bubble_y = max(0, pet_y - bubble_height - 20)
        screen_width = self.parent.winfo_screenwidth()
        if bubble_x + bubble_width > screen_width:
            bubble_x = screen_width - bubble_width
        self.bubble_window.geometry(f"+{bubble_x}+{bubble_y}")
    def _start_position_updates(self):
        if self._update_position_timer:
            self.parent.after_cancel(self._update_position_timer)
        self._update_position_timer = self.parent.after(100, self._update_position_loop)
    def _update_position_loop(self):
        if self.bubble_window and self.bubble_window.winfo_exists():
            self._update_bubble_position()
            self._update_position_timer = self.parent.after(100, self._update_position_loop)
    def clear_bubble(self):
        if self._bubble_timer:
            self.parent.after_cancel(self._bubble_timer)
            self._bubble_timer = None
        if self._update_position_timer:
            self.parent.after_cancel(self._update_position_timer)
            self._update_position_timer = None
        if self.bubble_window and self.bubble_window.winfo_exists():
            self.bubble_window.destroy()
            self.bubble_window = None
class SimpleStatusPanel:
    def __init__(self, parent, pet_manager):
        self.parent = parent
        self.pet_manager = pet_manager
        self.panel_window = None
        self.update_timer = None
        self.is_visible = False
        self._stat_widgets = {}
        self.stats_frame = None
        self.name_label = None
        self.age_label = None
        self.currency_label = None
        self.weight_label = None
        self.status_label = None
        self.currency_icon_label = None
        self.currency_icon = None
        self.startup_manager = StartupManager()
    def show_panel(self, x=None, y=None):
        """Show the status panel with adaptive positioning"""
        if self.panel_window:
            self.hide_panel()
        self.panel_window = tk.Toplevel(self.parent)
        self.panel_window.overrideredirect(True)
        self.panel_window.attributes('-topmost', True)
        if x is not None and y is not None:
            self.panel_window.geometry(f"+{x}+{y}")
        self.panel_window.configure(bg=COLORS['background'])
        main_frame = tk.Frame(self.panel_window, bg=COLORS['surface'], bd=2, relief=tk.RAISED)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        title_frame = tk.Frame(main_frame, bg=COLORS['surface'])
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        title_label = tk.Label(title_frame, text="Pet Stats", font=("Arial", 12, "bold"),
                              bg=COLORS['surface'], fg=COLORS['primary'])
        title_label.pack(side=tk.LEFT, padx=5)
        if hasattr(self, 'sleep_timer_label') and self.sleep_timer_label:
            self.sleep_timer_label.lift()
        self.stats_frame = tk.Frame(main_frame, bg=COLORS['surface'], padx=15, pady=15, width=350, height=390)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.stats_frame.pack_propagate(False)
        button_frame = tk.Frame(main_frame, bg=COLORS['surface'])
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        inventory_btn = SimpleButton(button_frame, text="Inventory",
                                  command=self.show_inventory,
                                  bg=COLORS['primary'])
        inventory_btn.pack(side=tk.LEFT, padx=5, pady=5)
        game_hub_btn = SimpleButton(button_frame, text="Game Hub",
                                 command=self.show_game_hub,
                                 bg=COLORS['primary'])
        game_hub_btn.pack(side=tk.LEFT, padx=5, pady=5)
        chat_btn = SimpleButton(button_frame, text="Chat with Pet",
                               command=self.show_chat,
                               bg=COLORS['secondary'])
        chat_btn.pack(side=tk.LEFT, padx=5, pady=5)
        close_btn = SimpleButton(button_frame, text="Close",
                              command=self.hide_panel,
                              bg=COLORS['error'])
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        self._stat_widgets = {}
        self._create_stat_widgets()
        self.update_stats_display()
        self.stats_frame.update()
        self.panel_window.update_idletasks()
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        panel_width = self.panel_window.winfo_width()
        panel_height = self.panel_window.winfo_height()
        if x is not None and y is not None:
            if panel_width == 0 or panel_height == 0:
                self.panel_window.update_idletasks()
                panel_width = self.panel_window.winfo_width()
                panel_height = self.panel_window.winfo_height()
            panel_x = max(0, min(x, screen_width - panel_width))
            panel_y = max(0, min(y, screen_height - panel_height))
            self.panel_window.geometry(f"+{panel_x}+{panel_y}")
            self.panel_window.update_idletasks()
            actual_x = self.panel_window.winfo_x()
            actual_y = self.panel_window.winfo_y()
        else:
            self._position_panel_adaptively()
        self.is_visible = True
        self.update_timer = self.parent.after(100, self.periodic_update)
        self.panel_window.lift()
        self.panel_window.attributes('-topmost', True)
        final_x = self.panel_window.winfo_x()
        final_y = self.panel_window.winfo_y()
    def _position_panel_adaptively(self):
        """Position the panel based on pet's position on screen"""
        if not self.panel_window:
            return
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        pet_x = self.parent.winfo_x() + self.parent.winfo_width() // 2
        pet_y = self.parent.winfo_y() + self.parent.winfo_height() // 2
        self.panel_window.update_idletasks()
        panel_width = self.panel_window.winfo_width()
        panel_height = self.panel_window.winfo_height()
        panel_x = pet_x - panel_width // 2
        panel_y = pet_y + 20
        if pet_y + panel_height + 40 > screen_height:
            panel_y = pet_y - panel_height - 40
        if panel_y < 0:
            panel_x = pet_x + 20
            panel_y = max(0, pet_y - panel_height // 2)
            if panel_x + panel_width > screen_width:
                panel_x = max(0, pet_x - panel_width - 20)
        if panel_x < 0:
            panel_x = 0
        elif panel_x + panel_width > screen_width:
            panel_x = max(0, screen_width - panel_width)
        if panel_y < 0:
            panel_y = 0
        elif panel_y + panel_height > screen_height:
            panel_y = max(0, screen_height - panel_height)
        self.panel_window.geometry(f"+{panel_x}+{panel_y}")
        self.panel_window.lift()
        self.panel_window.attributes('-topmost', True)
    def hide_panel(self):
        """Hide the status panel"""
        if self.panel_window:
            if self.update_timer:
                self.parent.after_cancel(self.update_timer)
                self.update_timer = None
            self.panel_window.destroy()
            self.panel_window = None
            self.is_visible = False
            self.stats_frame = None
            self.name_label = None
            self.age_label = None
            self.currency_label = None
            self.weight_label = None
            self.status_label = None
            self.currency_icon_label = None
            self._stat_widgets = {}
    def update_stats_display(self):
        """Update the stats display with current values"""
        if not self.stats_frame or not self.panel_window:
            return
        try:
            self.panel_window.winfo_exists()
        except tk.TclError:
            self.hide_panel()
            return
        stats = self.pet_manager.get_stats_summary()
        if hasattr(self, 'sleep_timer_label') and self.sleep_timer_label:
            if (hasattr(self.pet_manager, 'pet_state') and
                hasattr(self.pet_manager.pet_state, 'is_sleeping') and
                self.pet_manager.pet_state.is_sleeping and
                hasattr(self.pet_manager.pet_state, 'get_sleep_timer_display')):
                sleep_timer_text = self.pet_manager.pet_state.get_sleep_timer_display()
                self.sleep_timer_label.config(text=sleep_timer_text, bg=COLORS['primary'], fg="white", padx=5, pady=2)
            else:
                self.sleep_timer_label.config(text="", bg=COLORS['surface'])
        if not hasattr(self, '_stat_widgets') or not self._stat_widgets or len(self._stat_widgets) == 0:
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            self._stat_widgets = {}
            self._create_stat_widgets()
            self.stats_frame.update()
        try:
            if hasattr(self, 'name_label') and self.name_label:
                self.name_label.config(text=f"{stats['name']} - {stats['stage']}")
            if hasattr(self, 'age_label') and self.age_label:
                self.age_label.config(text=f"Age: {stats['age']} days")
            if hasattr(self, 'currency_label') and self.currency_label:
                self.currency_label.config(text=f"Coins: {self.pet_manager.pet_state.currency}")
            self._update_stat_bar(stats['hunger'], "hunger")
            self._update_stat_bar(stats['happiness'], "happiness")
            self._update_stat_bar(stats['energy'], "energy")
            self._update_stat_bar(stats['health'], "health")
            self._update_stat_bar(stats['cleanliness'], "cleanliness")
            self._update_stat_bar(stats['social'], "social")
            poop_chance = self._calculate_poop_chance()
            self._update_stat_bar(poop_chance, "poop_chance")
            self.stats_frame.update()
            if stats['status_effects']:
                effects_text = ", ".join(stats['status_effects'])
                if hasattr(self, 'status_label') and self.status_label:
                    self.status_label.config(text=f"Status: {effects_text}", fg=COLORS['error'])
                    if not self.status_label.winfo_ismapped():
                        self.status_label.pack(anchor="w", pady=(5, 0))
                else:
                    self.status_label = tk.Label(self.stats_frame, text=f"Status: {effects_text}",
                                              font=("Arial", 10), bg=COLORS['surface'], fg=COLORS['error'])
                    self.status_label.pack(anchor="w", pady=(5, 0))
            elif hasattr(self, 'status_label') and self.status_label and self.status_label.winfo_ismapped():
                self.status_label.pack_forget()
        except tk.TclError as e:
            self.hide_panel()
        except Exception as e:
            try:
                for widget in self.stats_frame.winfo_children():
                    widget.destroy()
                self._stat_widgets = {}
                self._create_stat_widgets()
                self.stats_frame.update()
            except tk.TclError:
                self.hide_panel()
    def _create_stat_bar(self, value, label):
        """Create a stat bar with proper coloring based on value"""
        stat_frame = tk.Frame(self.stats_frame, bg=COLORS['surface'])
        stat_frame.pack(fill="x", pady=3)
        if value <= 25:
            bar_color = COLORS['error']
            text_color = COLORS['error'] if value == 0 else COLORS['text']
        elif value <= 50:
            bar_color = COLORS['warning']
            text_color = COLORS['text']
        else:
            bar_color = COLORS['success']
            text_color = COLORS['success'] if value >= 90 else COLORS['text']
        label_width = 80
        stat_label = tk.Label(stat_frame, text=f"{label}:", width=10, anchor="w",
                            font=("Arial", 10), bg=COLORS['surface'], fg=COLORS['text'])
        stat_label.pack(side=tk.LEFT, padx=(0, 5))
        bar_container = tk.Frame(stat_frame, height=15, width=150, bg=COLORS['background'])
        bar_container.pack(side=tk.LEFT, padx=5)
        bar_container.pack_propagate(False)
        bar_width = int(150 * value / 100)
        if value > 0:
            bar = tk.Frame(bar_container, height=15, width=bar_width, bg=bar_color)
            bar.place(x=0, y=0)
        value_label = tk.Label(stat_frame, text=f"{int(value)}%", width=5, anchor="e",
                             font=("Arial", 9), bg=COLORS['surface'], fg=text_color)
        value_label.pack(side=tk.LEFT, padx=(5, 0))
    def _create_stat_widgets(self):
        """Create all the stat widgets once"""
        if not self.stats_frame:
            return
        if not hasattr(self, '_stat_widgets') or self._stat_widgets is None:
            self._stat_widgets = {}
        else:
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            self._stat_widgets = {}
        stats = self.pet_manager.get_stats_summary()
        self.name_label = tk.Label(self.stats_frame, text=f"{stats['name']} - {stats['stage']}",
                             font=("Arial", 12, "bold"), bg=COLORS['surface'], fg=COLORS['primary'])
        self.name_label.pack(anchor="w", pady=(0, 10))
        self._stat_widgets['name_stage'] = self.name_label
        self.age_label = tk.Label(self.stats_frame, text=f"Age: {stats['age']} days",
                            font=("Arial", 10), bg=COLORS['surface'], fg=COLORS['text'])
        self.age_label.pack(anchor="w")
        currency_frame = tk.Frame(self.stats_frame, bg=COLORS['surface'])
        currency_frame.pack(anchor="w", pady=(5, 10), fill="x")
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_assets', 'currency.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((16, 16), Image.LANCZOS)
                self.currency_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            pass
        if hasattr(self, 'currency_icon') and self.currency_icon:
            self.currency_icon_label = tk.Label(currency_frame, image=self.currency_icon, bg=COLORS['surface'])
            self.currency_icon_label.image = self.currency_icon
            self.currency_icon_label.pack(side=tk.LEFT, padx=(0, 5))
        self.currency_label = tk.Label(currency_frame, text=f"Coins: {self.pet_manager.pet_state.currency}",
                                font=("Arial", 10, "bold"), bg=COLORS['surface'], fg=COLORS['text'])
        self.currency_label.pack(side=tk.LEFT)
        stats_header = tk.Label(self.stats_frame, text="Pet Statistics",
                              font=("Arial", 11, "bold"), bg=COLORS['surface'], fg=COLORS['primary'])
        stats_header.pack(anchor="w", pady=(10, 5))
        stat_names = ["hunger", "happiness", "energy", "health", "cleanliness", "social"]
        for stat_name in stat_names:
            stat_value = stats[stat_name]
            stat_frame = tk.Frame(self.stats_frame, bg=COLORS['surface'])
            stat_frame.pack(fill="x", pady=3)
            display_name = stat_name.capitalize()
            stat_label = tk.Label(stat_frame, text=f"{display_name}:", width=10, anchor="w",
                                font=("Arial", 10), bg=COLORS['surface'], fg=COLORS['text'])
            stat_label.pack(side=tk.LEFT, padx=(0, 5))
            bar_container = tk.Frame(stat_frame, height=15, width=150, bg=COLORS['background'])
            bar_container.pack(side=tk.LEFT, padx=5)
            bar_container.pack_propagate(False)
            if stat_value <= 25:
                bar_color = COLORS['error']
                text_color = COLORS['error'] if stat_value == 0 else COLORS['text']
            elif stat_value <= 50:
                bar_color = COLORS['warning']
                text_color = COLORS['text']
            else:
                bar_color = COLORS['success']
                text_color = COLORS['success'] if stat_value >= 90 else COLORS['text']
            bar_width = max(1, int(150 * stat_value / 100))
            bar = tk.Frame(bar_container, bg=bar_color)
            bar.place(x=0, y=0, width=bar_width, height=15)
            value_label = tk.Label(stat_frame, text=f"{int(stat_value)}%", width=8, anchor="e",
                                 font=("Arial", 10, "bold"), bg=COLORS['surface'], fg=text_color)
            value_label.pack(side=tk.LEFT, padx=(10, 0))
            value_label.lift()
            self._stat_widgets[f"{stat_name}_bar"] = bar
            self._stat_widgets[f"{stat_name}_label"] = value_label
            self._stat_widgets[f"{stat_name}_container"] = bar_container
        self._create_poop_chance_bar()
        self.stats_frame.update()
    def show_inventory(self):
        """Show the pet's inventory"""
        if self.pet_manager:
            if self.panel_window:
                if self.panel_window.winfo_exists():
                    parent_window = self.panel_window
                else:
                    parent_window = None
            else:
                parent_window = None
            self.pet_manager.show_inventory(parent_window=parent_window)
    def show_game_hub(self):
        """Show the game hub"""
        if self.pet_manager:
            if self.panel_window:
                if self.panel_window.winfo_exists():
                    parent_window = self.panel_window
                else:
                    parent_window = None
            else:
                parent_window = None
            self.pet_manager.show_game_hub(parent_window=parent_window)
    def _update_stat_bar(self, value, stat_name):
        """Update an existing stat bar with new value"""
        if not self.panel_window or not self.stats_frame:
            return
        try:
            self.stats_frame.winfo_exists()
        except Exception:
            return
        if not hasattr(self, '_stat_widgets') or self._stat_widgets is None:
            self._stat_widgets = {}
            try:
                self._create_stat_widgets()
            except Exception:
                return
            return
        bar = self._stat_widgets.get(f"{stat_name}_bar")
        label = self._stat_widgets.get(f"{stat_name}_label")
        container = self._stat_widgets.get(f"{stat_name}_container")
        if not (bar and label and container):
            try:
                self._create_stat_widgets()
                bar = self._stat_widgets.get(f"{stat_name}_bar")
                label = self._stat_widgets.get(f"{stat_name}_label")
                container = self._stat_widgets.get(f"{stat_name}_container")
            except Exception:
                return
            if not (bar and label and container):
                return
        try:
            bar.winfo_exists()
            label.winfo_exists()
            container.winfo_exists()
        except Exception:
            return
        if value <= 25:
            bar_color = COLORS['error']
            text_color = COLORS['error'] if value == 0 else COLORS['text']
        elif value <= 50:
            bar_color = COLORS['warning']
            text_color = COLORS['text']
        else:
            bar_color = COLORS['success']
            text_color = COLORS['success'] if value >= 90 else COLORS['text']
        bar_width = max(1, int(150 * value / 100))
        try:
            bar.place(x=0, y=0, width=bar_width, height=15)
            bar.config(bg=bar_color)
            label.config(text=f"{int(value)}%", fg=text_color)
        except Exception:
            return
    def _create_advanced_tab(self, parent):
        """Create advanced settings tab with scrollbar"""
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas = tk.Canvas(canvas_frame, yscrollcommand=scrollbar.set, bg=COLORS['background'])
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        content_frame = ttk.Frame(canvas, padding=5)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw', width=canvas.winfo_width())
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        content_frame.bind('<Configure>', configure_scroll_region)
        def configure_canvas_width(event):
            canvas_width = event.width - scrollbar.winfo_width() - 10
            canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.bind('<Configure>', configure_canvas_width)
        color_frame = ttk.LabelFrame(content_frame, text="Pet Color", padding=10)
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        current_color = self.pet_manager.settings.get('pet_color', 'black')
        ttk.Label(color_frame, text=f"Current Color: {current_color.title()}").pack(anchor="w")
        color_var = tk.StringVar(value=current_color)
        ttk.Radiobutton(color_frame, text="Black", variable=color_var, value="black",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Blue", variable=color_var, value="blue",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Radiobutton(color_frame, text="Pink", variable=color_var, value="pink",
                       command=lambda: self._update_pet_color(color_var.get())).pack(anchor="w", pady=2)
        ttk.Label(color_frame, text="Changes to pet color will take effect immediately.",
                 wraplength=400, font=("Arial", 8)).pack(anchor="w", pady=(5, 0))
        age_frame = ttk.LabelFrame(content_frame, text="Pet Age and Stage", padding=10)
        age_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(age_frame, text=f"Current Age: {round(self.pet_manager.pet_state.stats.get_stat('age'), 1)} days").pack(anchor="w")
        ttk.Label(age_frame, text=f"Current Stage: {self.pet_manager.pet_state.stage}").pack(anchor="w")
        age_entry_frame = ttk.Frame(age_frame)
        age_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(age_entry_frame, text=f"Set Age (days) (Current: {round(self.pet_manager.pet_state.stats.get_stat('age'), 1)}):").pack(side=tk.LEFT, padx=(0, 5))
        age_entry = ttk.Entry(age_entry_frame, width=10)
        age_entry.pack(side=tk.LEFT)
        stage_frame = ttk.Frame(age_frame)
        stage_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stage_frame, text="Set Stage:").pack(side=tk.LEFT, padx=(0, 5))
        stage_var = tk.StringVar(value=self.pet_manager.pet_state.stage)
        stage_combo = ttk.Combobox(stage_frame, textvariable=stage_var, values=['Baby', 'Child', 'Teen', 'Adult'], state='readonly')
        stage_combo.pack(side=tk.LEFT)
        apply_btn = SimpleButton(age_frame, text="Apply Changes",
                               command=lambda: self._apply_advanced_changes(age_entry.get(), stage_var.get()))
        apply_btn.pack(pady=5)
        poop_frame = ttk.LabelFrame(content_frame, text="Poop Frequency", padding=10)
        poop_frame.pack(fill=tk.X, padx=10, pady=10)
        poop_var = tk.DoubleVar(value=self.pet_manager.settings.get('poop_frequency', 0.5))
        poop_label_frame = ttk.Frame(poop_frame)
        poop_label_frame.pack(fill=tk.X)
        ttk.Label(poop_label_frame, text="Frequency:").pack(side=tk.LEFT)
        poop_value_label = ttk.Label(poop_label_frame, text=f"{poop_var.get():.1f}")
        poop_value_label.pack(side=tk.RIGHT)
        poop_slider = ttk.Scale(poop_frame, from_=0.1, to=2.0, variable=poop_var, orient=tk.HORIZONTAL)
        poop_slider.pack(fill=tk.X)
        def update_poop_label(event=None):
            poop_value_label.config(text=f"{poop_var.get():.1f}")
            self.pet_manager.update_setting('poop_frequency', poop_var.get())
            if hasattr(self.pet_manager, 'poop_system') and self.pet_manager.poop_system:
                self.pet_manager.poop_system.poop_chance = poop_var.get()
        poop_slider.bind("<Motion>", update_poop_label)
        poop_slider.bind("<ButtonRelease-1>", update_poop_label)
        ttk.Label(poop_frame, text="Lower values mean less frequent poops, higher values mean more frequent poops.",
                 wraplength=400, font=("Arial", 8)).pack(anchor="w", pady=(5, 0))
        depletion_frame = ttk.LabelFrame(content_frame, text="Stat Depletion Rates", padding=10)
        depletion_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(depletion_frame, text="Adjust how quickly each stat decreases over time. Higher values mean faster depletion.",
                 wraplength=400, font=("Arial", 9)).pack(anchor="w", pady=(0, 10))
        for stat in ['hunger', 'happiness', 'energy', 'cleanliness', 'social']:
            stat_frame = ttk.Frame(depletion_frame)
            stat_frame.pack(fill=tk.X, pady=8)
            stat_label_frame = ttk.LabelFrame(stat_frame, text=f"{stat.title()} Rate", padding=5)
            stat_label_frame.pack(fill=tk.X, expand=True)
            slider_frame = ttk.Frame(stat_label_frame)
            slider_frame.pack(fill=tk.X, expand=True, pady=3)
            current_rate = 0.1
            if hasattr(self.pet_manager.pet_state, 'stats') and hasattr(self.pet_manager.pet_state.stats, 'decay_rates'):
                current_rate = self.pet_manager.pet_state.stats.decay_rates.get(stat, 0.1)
            rate_var = tk.DoubleVar(value=current_rate)
            value_label = ttk.Label(slider_frame, text=f"{rate_var.get():.1f}", width=5)
            value_label.pack(side=tk.RIGHT, padx=(5, 0))
            rate_slider = ttk.Scale(slider_frame, from_=0.1, to=2.0, variable=rate_var, orient=tk.HORIZONTAL)
            rate_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=3, padx=5)
            slider_labels_frame = ttk.Frame(stat_label_frame)
            slider_labels_frame.pack(fill=tk.X, padx=5)
            ttk.Label(slider_labels_frame, text="Slow", font=("Arial", 8)).pack(side=tk.LEFT)
            ttk.Label(slider_labels_frame, text="Fast", font=("Arial", 8)).pack(side=tk.RIGHT)
            def update_rate(event, s=stat, v=rate_var, lbl=value_label):
                lbl.config(text=f"{v.get():.1f}")
                self._update_depletion_rate(s, v.get())
            rate_slider.bind("<Motion>", lambda e, s=stat, v=rate_var, lbl=value_label: lbl.config(text=f"{v.get():.1f}"))
            rate_slider.bind("<ButtonRelease-1>", update_rate)
    def _update_depletion_rate(self, stat, new_rate):
        """Update stat depletion rate"""
        self.pet_manager.pet_state.stats.decay_rates[stat] = new_rate
        self.show_notification("Rate Updated", f"{stat.title()} depletion rate updated to {new_rate:.1f}", COLORS['success'])
    def _toggle_startup(self, enabled):
        """Toggle Windows startup setting"""
        if enabled:
            success = self.startup_manager.enable()
        else:
            success = self.startup_manager.disable()
        if success:
            self.pet_manager.update_setting('start_with_windows', enabled)
            self.show_notification("Startup Setting",
                                 "Windows startup enabled" if enabled else "Windows startup disabled",
                                 COLORS['success'])
        else:
            self.show_notification("Startup Setting Failed",
                                 "Failed to update Windows startup setting",
                                 COLORS['error'])
    def reset_pet(self):
        """Reset pet to initial state"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset your pet? This will reset to Baby stage with 0 days age and default stats."):
            success, message = self.pet_manager.reset_pet()
            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to reset pet: {message}")
    def periodic_update(self):
        """Periodically update the stats display"""
        if self.is_visible:
            self.update_stats_display()
            self.update_timer = self.parent.after(1500, self.periodic_update)
    def show_inventory(self):
        """Show the pet's inventory"""
        if self.pet_manager:
            self.pet_manager.show_inventory()
    def show_game_hub(self):
        """Show the game hub"""
        if self.pet_manager:
            self.pet_manager.show_game_hub()
    def show_chat(self):
        """Show the AI chat interface"""
        if self.pet_manager:
            if not hasattr(self.pet_manager, 'ai_chat_system'):
                from ai_chat_system import AIChatSystem
                self.pet_manager.ai_chat_system = AIChatSystem(self.pet_manager)
            parent_window = self.panel_window if self.panel_window and self.panel_window.winfo_exists() else None
            self.pet_manager.ai_chat_system.create_chat_window(parent_window=parent_window)
    def _calculate_poop_chance(self):
        """Calculate the current poop chance percentage"""
        try:
            if hasattr(self.pet_manager, 'pet_state') and hasattr(self.pet_manager.pet_state, 'poop_system'):
                poop_system = self.pet_manager.pet_state.poop_system
                cleanliness = self.pet_manager.pet_state.stats.get_stat('cleanliness') if hasattr(self.pet_manager.pet_state, 'stats') else 100
                if hasattr(poop_system, 'current_poop_chance'):
                    base_chance = poop_system.current_poop_chance
                else:
                    pressure_ratio = getattr(poop_system, 'poop_pressure', 0) / getattr(poop_system, 'max_poop_pressure', 100)
                    base_chance = getattr(poop_system, 'base_poop_chance', 0.05) + (pressure_ratio * (getattr(poop_system, 'max_poop_chance', 0.4) - getattr(poop_system, 'base_poop_chance', 0.05)))
                cleanliness_factor = 1 + ((100 - cleanliness) / 200)
                adjusted_chance = base_chance * cleanliness_factor
                return min(adjusted_chance * 100, 95)
            else:
                return 0
        except Exception as e:
            print(f"Error calculating poop chance: {e}")
            return 0
    def _create_poop_chance_bar(self):
        """Create the poop chance bar widget"""
        if not self.stats_frame:
            return
        poop_chance_value = self._calculate_poop_chance()
        poop_stat_frame = tk.Frame(self.stats_frame, bg=COLORS['surface'])
        poop_stat_frame.pack(fill="x", pady=3)
        poop_stat_label = tk.Label(poop_stat_frame, text="Poop Chance:", width=10, anchor="w",
                            font=("Arial", 10), bg=COLORS['surface'], fg=COLORS['text'])
        poop_stat_label.pack(side=tk.LEFT, padx=(0, 5))
        poop_bar_container = tk.Frame(poop_stat_frame, height=15, width=150, bg=COLORS['background'])
        poop_bar_container.pack(side=tk.LEFT, padx=5)
        poop_bar_container.pack_propagate(False)
        poop_bar_width = max(1, int(150 * poop_chance_value / 100))
        poop_bar = tk.Frame(poop_bar_container, bg=COLORS['poop_brown'])
        poop_bar.place(x=0, y=0, width=poop_bar_width, height=15)
        poop_value_label = tk.Label(poop_stat_frame, text=f"{int(poop_chance_value)}%", width=8, anchor="e",
                             font=("Arial", 10, "bold"), bg=COLORS['surface'], fg=COLORS['text'])
        poop_value_label.pack(side=tk.LEFT, padx=(10, 0))
        poop_value_label.lift()
        self._stat_widgets["poop_chance_bar"] = poop_bar
        self._stat_widgets["poop_chance_label"] = poop_value_label
        self._stat_widgets["poop_chance_container"] = poop_bar_container
    def show_notification(self, title, message, color):
        """Show a notification with simple styling"""
        notification = tk.Toplevel(self.panel_window if self.panel_window else self.parent)
        notification.title(title)
        notification.geometry("300x100")
        notification.resizable(False, False)
        notification.configure(bg=color)
        notification.attributes('-topmost', True)
        parent_window = self.panel_window if self.panel_window else self.parent
        x = parent_window.winfo_x() + (parent_window.winfo_width() - 300) // 2
        y = parent_window.winfo_y() + (parent_window.winfo_height() - 100) // 2
        notification.geometry(f"+{x}+{y}")