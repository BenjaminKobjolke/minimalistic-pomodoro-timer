import tkinter as tk
from tkinter import ttk
import configparser
from typing import Optional
import os
import time
from PIL import Image, ImageFont, ImageDraw, ImageTk
from logger import Logger

class PomodoroTimer:
    """Main timer class implementing the Pomodoro timer functionality."""
    
    def __init__(self) -> None:
        self.logger = Logger()
        self.logger.info("Initializing Pomodoro Timer")
        
        self.window = tk.Tk()
        # Setup window
        self.window.title("Pomodoro")  # Add title for Alt+Tab
        
        # Remove all decorations
        self.window.overrideredirect(True)
        self.window.attributes('-alpha', 0.9, '-topmost', True)
        
        # We're using alpha transparency instead of transparentcolor
        # This makes the entire window clickable while still appearing transparent
        self.window.attributes('-alpha', 0.95)  # Slightly higher alpha for better visibility
        
        # Keep in taskbar
        self.window.wm_attributes('-toolwindow', False)
        self.window.update_idletasks()  # Ensure window is created
        
        # Set window style to show in Alt+Tab
        if os.name == 'nt':  # Windows only
            import ctypes
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        
        # Timer state
        self.duration = 25 * 60  # 25 minutes in seconds
        self.target_end_time = None
        self.running = False
        self.move_speed = 50  # Fast move speed
        self.font_size = 96  # Default font size
        self.default_duration_seconds = 25 * 60 # Default timer duration
        
        # Load settings
        self.config = configparser.ConfigParser()
        self.load_settings() # This will potentially update self.default_duration_seconds

        self.duration = self.default_duration_seconds # Initialize timer duration
        
        # Load font
        self.font = None
        if self.config.has_section('Display') and self.config.has_option('Display', 'font_path'):
            try:
                font_path = self.config.get('Display', 'font_path')
                self.font = ImageFont.truetype(font_path, self.font_size)
                self.logger.info(f"Custom font loaded successfully: {font_path}")
            except Exception as e:
                self.logger.warning(f"Could not load custom font: {e}")
        
        if self.font is None:
            try:
                self.font = ImageFont.truetype("arial.ttf", self.font_size)
                self.logger.info("Using Arial font")
            except Exception as e:
                self.logger.error(f"Could not load Arial font: {e}")
                raise SystemExit("Could not load any font. Please check your font configuration.")
        
        # Setup UI
        self.setup_ui()
        self.setup_bindings()
        
        # Create initial display immediately
        self.window.update()  # Force window creation
        self.update_display()
    
    def load_settings(self) -> None:
        """Load window position from settings file."""
        try:
            self.config.read('settings.ini')
            x = self.config.getint('Window', 'x')
            y = self.config.getint('Window', 'y')
            self.window.geometry(f'+{x}+{y}')
            
            if self.config.has_section('Display'):
                self.font_size = self.config.getint('Display', 'font_size')

            if self.config.has_section('Timer') and self.config.has_option('Timer', 'custom_duration_minutes'):
                custom_duration_minutes = self.config.getint('Timer', 'custom_duration_minutes')
                if custom_duration_minutes > 0:
                    self.default_duration_seconds = custom_duration_minutes * 60
                    self.logger.info(f"Loaded custom duration: {custom_duration_minutes} minutes.")
                else:
                    self.logger.warning("Invalid custom_duration_minutes in settings.ini, using default.")
            else:
                self.logger.info("No custom duration found in settings.ini, using default.")
                # self.default_duration_seconds is already 25*60 by default from __init__

        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.window.geometry('+100+100')
            # self.default_duration_seconds remains the default 25*60 if settings load fails or section/option is missing
    
    def save_settings(self) -> None:
        """Save current window position and custom duration to settings file."""
        try:
            x = self.window.winfo_x()
            y = self.window.winfo_y()
            self.config['Window'] = {'x': str(x), 'y': str(y)}

            if not self.config.has_section('Timer'):
                self.config.add_section('Timer')
            self.config.set('Timer', 'custom_duration_minutes', str(self.default_duration_seconds // 60))

            with open('settings.ini', 'w') as f:
                self.config.write(f)
            self.logger.info(f"Settings saved, custom duration: {self.default_duration_seconds // 60} minutes.")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
    
    def setup_ui(self) -> None:
        """Setup the timer display and UI elements."""
        # Calculate window dimensions
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), "00:00", font=self.font)
        self.width = bbox[2] - bbox[0] + 40  # Add padding
        self.height = bbox[3] - bbox[1] + 20  # Add padding
        
        # Create a canvas with a very dark background that will be nearly invisible
        # but still allow clicks anywhere in the window
        self.canvas = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            bg='#000000',  # Pure black background
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Create border that's only visible when window is focused
        self.window.bind('<FocusIn>', self.on_focus_in)
        self.window.bind('<FocusOut>', self.on_focus_out)
    
    def setup_bindings(self) -> None:
        """Setup keyboard bindings."""
        self.window.bind('s', self.toggle_timer)
        self.window.bind('r', self.reset_timer)
        self.window.bind('e', self.prompt_duration)  # Bind 'e' to prompt_duration
        self.window.bind('<Left>', lambda e: self.move_window('left'))
        self.window.bind('<Right>', lambda e: self.move_window('right'))
        self.window.bind('<Up>', lambda e: self.move_window('up'))
        self.window.bind('<Down>', lambda e: self.move_window('down'))
        self.window.bind('<Shift-Left>', lambda e: self.move_window('left', slow=True))
        self.window.bind('<Shift-Right>', lambda e: self.move_window('right', slow=True))
        self.window.bind('<Shift-Up>', lambda e: self.move_window('up', slow=True))
        self.window.bind('<Shift-Down>', lambda e: self.move_window('down', slow=True))
        self.window.bind('<Destroy>', lambda e: self.save_settings())

    def prompt_duration(self, event: Optional[tk.Event] = None) -> None:
        """Prompt user for a new timer duration."""
        # Ensure simpledialog is imported
        from tkinter import simpledialog

        new_duration_minutes = simpledialog.askinteger(
            "Set Timer Duration",
            "Enter duration in minutes:",
            parent=self.window,
            minvalue=1  # Ensure positive duration
        )

        if new_duration_minutes is not None:
            self.duration = new_duration_minutes * 60  # Convert to seconds
            self.default_duration_seconds = self.duration # Update the default duration
            self.save_settings() # Save the new default duration immediately
            self.reset_timer() # Reset to apply new duration (will use default_duration_seconds)
            self.logger.info(f"Timer duration set to {new_duration_minutes} minutes and saved as default.")
        else:
            self.logger.info("User cancelled duration input or entered invalid input.")

    def get_time_left(self) -> int:
        """Calculate the time left based on the system clock."""
        if not self.running or self.target_end_time is None:
            return self.duration
        
        remaining = self.target_end_time - time.time()
        return max(0, int(remaining))
    
    def create_time_image(self) -> ImageTk.PhotoImage:
        """Create the timer display image."""
        # Create a transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        time_left = self.get_time_left()
        minutes = time_left // 60
        seconds = time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Calculate text dimensions to center it vertically
        bbox = draw.textbbox((0, 0), time_str, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1] - 15
        
        # Calculate position to center text vertically
        # Add a small offset to adjust for font rendering peculiarities
        x_pos = 20  # Keep horizontal position the same
        y_pos = (self.height - text_height) // 2 - 2  # Center vertically with slight adjustment
        
        # Draw text in green
        draw.text((x_pos, y_pos), time_str, fill='#00ff00', font=self.font)
        
        return ImageTk.PhotoImage(img)
    
    def update_display(self) -> None:
        """Update the timer display."""
        self.canvas.delete('all')
        
        # Draw white border when focused
        if self.window.focus_get() is not None:
            # Use coordinates that ensure the border is visible on all sides
            # Subtract 1 from width and height to ensure the border is fully within the canvas
            self.canvas.create_rectangle(
                1, 1, self.width - 1, self.height - 1,
                outline='white',
                width=1
            )
        
        # Update time display
        time_image = self.create_time_image()
        self.canvas.create_image(0, 0, anchor='nw', image=time_image)
        self.canvas._time_image = time_image  # Prevent garbage collection
        
        if self.running:
            if self.get_time_left() == 0:
                self.running = False
                self.target_end_time = None
            else:
                self.window.after(100, self.update_display)  # Update more frequently for smoother display
    
    def toggle_timer(self, event: Optional[tk.Event] = None) -> None:
        """Toggle timer between running and paused states."""
        self.running = not self.running
        if self.running:
            # Set target end time based on current time plus remaining duration
            self.target_end_time = time.time() + self.get_time_left()
            self.update_display()
        else:
            # Store remaining time when paused
            self.duration = self.get_time_left()
            self.target_end_time = None
    
    def reset_timer(self, event: Optional[tk.Event] = None) -> None:
        """Reset timer to the stored default duration."""
        self.duration = self.default_duration_seconds
        self.target_end_time = None
        self.running = False
        self.logger.info(f"Timer reset to stored duration: {self.duration // 60} minutes.")
        self.update_display()
    
    def move_window(self, direction: str, slow: bool = False) -> None:
        """Move window in specified direction."""
        speed = 5 if slow else self.move_speed
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        
        if direction == 'left':
            x -= speed
        elif direction == 'right':
            x += speed
        elif direction == 'up':
            y -= speed
        elif direction == 'down':
            y += speed
        
        self.window.geometry(f'+{x}+{y}')
    
    def on_focus_in(self, event: Optional[tk.Event] = None) -> None:
        """Handle window focus in event."""
        self.update_display()
    
    def on_focus_out(self, event: Optional[tk.Event] = None) -> None:
        """Handle window focus out event."""
        self.update_display()
    
    def run(self) -> None:
        """Start the timer application."""
        self.window.mainloop()
