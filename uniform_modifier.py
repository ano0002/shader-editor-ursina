import tkinter as tk
import customtkinter
from ursina import Texture,Vec2,Vec3,Vec4

class Uniform(customtkinter.CTkFrame):
    def __init__(self, master,name,type, camera, default_value=None, params=None):
        super().__init__(master)
        self.master = master
        self.name = name
        self.type = type
        self._default_value = default_value
        self._params = params
        self._cam = camera
        self.create_widgets()
        if hasattr(self,"uniform_entry") and self.get() != None:
            self.update_shader()
        

    def create_widgets(self):
        self.create_label()
        self.create_entry()

    def create_label(self):
        self.uniform_label = customtkinter.CTkLabel(self, text=self.name + " (" + self.type + ")")
        self.uniform_label.pack(side="left",padx=20)

    def create_entry(self):
        pass

    def get(self):
        pass

    def update_shader(self,event=None):
        print(f"Updating {self.name} to {self.get()}")
        self._cam.set_shader_input(self.name, self.get())

class UniformInt(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkSlider(self, from_=0, to=100, command=self.update_shader)
        if self._params:
            self.uniform_entry.configure(from_=self._params[0], to=self._params[1])
        if self._default_value:
            self._default_value = int(self._default_value)
            self.uniform_entry.set(self._default_value)
        self.uniform_entry.pack(side="right")

    def get(self):
        return int(self.uniform_entry.get())

class UniformFloat(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkEntry(self)
        if self._default_value:
            self._default_value = float(self._default_value)
            self.uniform_entry.set(self._default_value)
        self.uniform_entry.pack(side="right")
        
    def get(self):
        return float(self.uniform_entry.get())

class UniformBool(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkSwitch(self, text="On/Off", command=self.update_shader)
        if self._default_value:
            if self._default_value in ("True","true","1","on","On","ON"):
                self.uniform_entry.set(True)
            else:
                self.uniform_entry.set(False)
            self.uniform_entry.set(self._default_value)
        self.uniform_entry.pack(side="right")

    def get(self):
        return self.uniform_entry.get()

class UniformImage(Uniform):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._image = None

    def create_entry(self):
        self.uniform_entry = customtkinter.CTkButton(self, text="Choose Image", command=self.image_picker)
        self.uniform_entry.pack(side="right")
    
    def image_picker(self):
        new_image = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("images files","*.jpg *.png *.jpeg"),("all files","*.*")))
        if new_image:
            self._image = Texture(new_image)
            self.update_shader()
    
    def get(self):
        return self._image
    
class UniformColor(Uniform):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._color = None
        
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkButton(self, text="Choose Color", command=self.color_picker)
        self.uniform_entry.pack(side="right")
    
    def color_picker(self):
        new_color = tk.colorchooser.askcolor()
        if new_color:
            self._color = new_color
            self.update_shader()
    def get(self):
        return self._color