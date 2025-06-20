import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import copy

# Main Application Class

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        # Variables to store images and states
        self.image = None
        self.tk_image = None
        self.cropped_img = None
        self.undo_stack = []
        self.redo_stack = []

        # Coordinates for cropping
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Create canvas for original and cropped image
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="gray")
        self.canvas.pack(side="left")

        self.cropped_canvas = tk.Canvas(self.root, width=300, height=200, bg="white")
        self.cropped_canvas.pack(side="left")

        # Right panel with buttons and controls
        self.controls = tk.Frame(self.root)
        self.controls.pack(side="right", fill="y")

        self.load_btn = tk.Button(self.controls, text="Load Image", command=self.load_image)
        self.load_btn.pack(pady=5)

        self.save_btn = tk.Button(self.controls, text="Save Cropped Image", command=self.save_cropped_image)
        self.save_btn.pack(pady=5)

        self.resize_slider = tk.Scale(self.controls, from_=10, to=200, orient='horizontal', label='Resize %', command=self.resize_image)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=5)
        # Undo and Redo buttons
        self.undo_btn = tk.Button(self.controls, text="Undo", command=self.undo)
        self.undo_btn.pack(pady=5)

        self.redo_btn = tk.Button(self.controls, text="Redo", command=self.redo)
        self.redo_btn.pack(pady=5)

        # Grayscale filter button
        self.filter_btn = tk.Button(self.controls, text="Apply Grayscale Filter", command=self.apply_grayscale)
        self.filter_btn.pack(pady=5)

        # Color filter buttons grouped in a frame
        self.color_frame = tk.LabelFrame(self.controls, text="Color Filters")
        self.color_frame.pack(pady=10)

        # Buttons for color tints
        tk.Button(self.color_frame, text="Red Tint", command=lambda: self.apply_color_tint('red')).pack(fill='x')
        tk.Button(self.color_frame, text="Green Tint", command=lambda: self.apply_color_tint('green')).pack(fill='x')
        tk.Button(self.color_frame, text="Blue Tint", command=lambda: self.apply_color_tint('blue')).pack(fill='x')
        tk.Button(self.color_frame, text="Yellow Tint", command=lambda: self.apply_color_tint('yellow')).pack(fill='x')
 
        # Bind mouse events for cropping functionality
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
# part1 Image Loading
    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            img_cv = cv2.imread(path)
            self.image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.cropped_img = None
            self.display_image(self.image)
            self.cropped_canvas.delete("all")
#part2 saving of the modified image
    def save_cropped_image(self):
        if self.cropped_img is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.cropped_img, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Saved", "Cropped image saved successfully")
        else:
            messagebox.showwarning("No Cropped Image", "Please crop an image before saving.")

    def display_image(self, img):
        img_pil = Image.fromarray(img)
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
#part3 Image Cropping
    def display_cropped_image(self, img):
        img_pil = Image.fromarray(img)
        tk_cropped = ImageTk.PhotoImage(img_pil)
        self.cropped_canvas.delete("all")
        self.cropped_canvas.create_image(0, 0, anchor='nw', image=tk_cropped)
        self.cropped_canvas.image = tk_cropped

    def on_mouse_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_release(self, event):
        if self.image is None:
            return
        x1, y1, x2, y2 = map(int, (self.start_x, self.start_y, event.x, event.y))
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        self.undo_stack.append(copy.deepcopy(self.image))
        cropped = self.image[y1:y2, x1:x2]
        self.cropped_img = cropped
        self.display_cropped_image(cropped)
#part4 Image Resizing
    def resize_image(self, value):
        if self.cropped_img is None:
            return
        scale = int(value) / 100
        new_size = (int(self.cropped_img.shape[1] * scale), int(self.cropped_img.shape[0] * scale))
        resized = cv2.resize(self.cropped_img, new_size)
        self.display_cropped_image(resized)
 # Implement undo/redo functionality :Undo last image change
    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.image))
            self.image = self.undo_stack.pop()
            self.cropped_img = None
            self.display_image(self.image)
            self.cropped_canvas.delete("all")

    # Redo previously undone change
    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.image))
            self.image = self.redo_stack.pop()
            self.cropped_img = None
            self.display_image(self.image)
            self.cropped_canvas.delete("all")

    # Apply grayscale effect to the image
    def apply_grayscale(self):
        if self.image is not None:
            self.undo_stack.append(copy.deepcopy(self.image))
            gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.display_image(self.image)

    # Apply a specific color tint by zeroing out other channels
    def apply_color_tint(self, color):
        if self.image is None:
            return
        self.undo_stack.append(copy.deepcopy(self.image))
        tinted = self.image.copy()
        if color == 'red':
            tinted[:, :, 1] = 0  # Remove green
            tinted[:, :, 2] = 0  # Remove blue
        elif color == 'green':
            tinted[:, :, 0] = 0  # Remove red
            tinted[:, :, 2] = 0  # Remove blue
        elif color == 'blue':
            tinted[:, :, 0] = 0  # Remove red
            tinted[:, :, 1] = 0  # Remove green
        elif color == 'yellow':
            tinted[:, :, 2] = 0  # Remove blue (Red + Green = Yellow)
        self.image = tinted
        self.display_image(self.image)
if __name__ == '__main__':
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
