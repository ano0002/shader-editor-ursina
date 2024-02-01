import customtkinter
from ursina import *  
import pygments.lexers
from chlorophyll import CodeView
import tkinter as tk
from ursina.shader import default_fragment_shader, default_vertex_shader
import os
import builtins

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue") 

app = Ursina(window_type="tkinter",size=(1280,720))

tkWindow = app.getTkWindow()
tkWindow.state('zoomed')
tkWindow.configure(background='#212121')

tabview = customtkinter.CTkTabview(master=tkWindow,border_width=0,corner_radius=0)

tabview.add("Vertex")  # add tab at the end
tabview.add("Fragment")  # add tab at the end
tabview.add("Geometry")  # add tab at the end

tabview.set("Vertex")

vertexCode = CodeView(tabview.tab("Vertex"), lexer=pygments.lexers.GLShaderLexer, color_scheme="mariana",autohide_scrollbar=True)
fragmentCode = CodeView(tabview.tab("Fragment"), lexer=pygments.lexers.GLShaderLexer, color_scheme="mariana",autohide_scrollbar=True)
geometryCode = CodeView(tabview.tab("Geometry"), lexer=pygments.lexers.GLShaderLexer, color_scheme="mariana",autohide_scrollbar=True)

vertexCode.pack(fill=tk.BOTH, expand=True)
fragmentCode.pack(fill=tk.BOTH, expand=True)
geometryCode.pack(fill=tk.BOTH, expand=True)

def resetVertex():
    vertexCode.delete(1.0, tk.END)
    vertexCode.insert(tk.END, default_vertex_shader)

def resetFragment():
    fragmentCode.delete(1.0, tk.END)
    fragmentCode.insert(tk.END, default_fragment_shader)
    
def resetGeometry():
    geometryCode.delete(1.0, tk.END)


custom_shader = Shader()

def compile():
    global custom_shader
    vertex = vertexCode.get(1.0, tk.END).strip()
    geometry = geometryCode.get(1.0, tk.END).strip()
    fragment = fragmentCode.get(1.0, tk.END).strip()
    custom_shader = Shader(vertex=vertex, geometry=geometry, fragment=fragment)
    
def run():
    global camera
    camera.shader = custom_shader
    
def compile_run():
    compile()
    run()
    compile_and_run.configure(text="■")
    compile_and_run.configure(command=stop)
    compile_and_run.configure(text_color="red")

def stop():
    camera.shader = Shader(name="default")
    compile_and_run.configure(text="►")
    compile_and_run.configure(command=compile_run)
    compile_and_run.configure(text_color="green")

compile_and_run = customtkinter.CTkButton(tkWindow,text="►",command=compile_run,text_color="green",fg_color="#22272b",border_width=2,border_color="#22272b",hover_color="#343d46",corner_radius=0,border_spacing=0,width=40,font=("Arial", 20),height=40)

console = tk.Text(tkWindow,fg="#c5c8c6",bg="#1d1f21",borderwidth=0,highlightthickness=0,insertbackground="#c5c8c6",font=("Arial", 12))

def console_print(*args, **kwargs):
    console.insert(tk.END, "\n")
    console.insert(tk.END, *args, **kwargs)
    console.see(tk.END)

builtins.print = console_print

def configure(event):
    height = round(tkWindow.winfo_height()/3*2+.5)
    width = round(tkWindow.winfo_width()/3+.5)
    window.size = (width*2, height)
    tabview.rowconfigure(0, weight=1)
    tabview.columnconfigure(0, weight=1)
    tabview.configure(width=width, height=height)
    tabview.place(x=width*2, y=0, anchor="nw")
    compile_and_run.place(x=tkWindow.winfo_width()-compile_and_run.winfo_reqwidth(),y=0,anchor="nw")
    console.place(x=0,y=height,anchor="nw",width=width*3)

tkWindow.bind("<Configure>", configure)

def new_project():
    stop()
    resetVertex()
    resetFragment()
    resetGeometry()

def open_vertex():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            vertexCode.delete(1.0, tk.END)
            vertexCode.insert(tk.END, f.read())

def open_fragment():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            fragmentCode.delete(1.0, tk.END)
            fragmentCode.insert(tk.END, f.read())

def open_geometry():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            geometryCode.delete(1.0, tk.END)
            geometryCode.insert(tk.END, f.read())

def open_project():
    directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
    if directory:
        files = os.listdir(directory)
        for file in files:
            if file.endswith(".vert"):
                with open(directory+"/"+file, 'r') as f:
                    vertexCode.delete(1.0, tk.END)
                    vertexCode.insert(tk.END, f.read())
            elif file.endswith(".frag"):
                with open(directory+"/"+file, 'r') as f:
                    fragmentCode.delete(1.0, tk.END)
                    fragmentCode.insert(tk.END, f.read())
            elif file.endswith(".geom"):
                with open(directory+"/"+file, 'r') as f:
                    geometryCode.delete(1.0, tk.END)
                    geometryCode.insert(tk.END, f.read())
            
def save_project():
    directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
    if directory:
        with open(directory+"/vertex.vert", 'w') as f:
            f.write(vertexCode.get(1.0, tk.END).strip())
        with open(directory+"/fragment.frag", 'w') as f:
            f.write(fragmentCode.get(1.0, tk.END).strip())
        with open(directory+"/geometry.geom", 'w') as f:
            f.write(geometryCode.get(1.0, tk.END).strip())

def save_vertex():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".vert",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(vertexCode.get(1.0, tk.END).strip())
        file.close()

def save_fragment():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".frag",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(fragmentCode.get(1.0, tk.END).strip())
        file.close()

def save_geometry():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".geom",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(geometryCode.get(1.0, tk.END).strip())
        file.close()


menubar = tk.Menu(tkWindow,relief=tk.FLAT,borderwidth=0)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=new_project)

openmenu = tk.Menu(filemenu, tearoff=0)
openmenu.add_command(label="Shader Project", command=open_project)
openmenu.add_command(label="Vertex Shader", command=open_vertex)
openmenu.add_command(label="Fragment Shader", command=open_fragment)
openmenu.add_command(label="Geometry Shader", command=open_geometry)
filemenu.add_cascade(label="Open", menu=openmenu)

savemenu = tk.Menu(filemenu, tearoff=0)
savemenu.add_command(label="Shader Project", command=save_project)
savemenu.add_command(label="Vertex Shader", command=save_vertex)
savemenu.add_command(label="Fragment Shader", command=save_fragment)
savemenu.add_command(label="Geometry Shader", command=save_geometry)
filemenu.add_cascade(label="Save", menu=savemenu)

filemenu.add_separator()
resetmenu = tk.Menu(filemenu, tearoff=0)
resetmenu.add_command(label="Vertex Shader", command=resetVertex)
resetmenu.add_command(label="Fragment Shader", command=resetFragment)
resetmenu.add_command(label="Geometry Shader", command=resetGeometry)
resetmenu.add_command(label="All", command=new_project)
filemenu.add_cascade(label="Reset",menu=resetmenu)

filemenu.add_separator()
filemenu.add_command(label="Exit", command=tkWindow.quit)
menubar.add_cascade(label="File", menu=filemenu)


tkWindow.config(menu=menubar)


Entity(model='cube', color=color.orange, scale=(2,2,2))

EditorCamera()

new_project()

app.run()