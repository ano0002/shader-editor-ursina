import customtkinter
from ursina import *  
from cupcake import Editor, Languages
import tkinter as tk
from ursina.shader import default_fragment_shader, default_vertex_shader
from autocompletion_words import methods, classes, keywords
import os
import builtins
from uniform_modifier import *
from panda3d.core import MultiplexStream, Notify, Filename

uniform_names = [
    "p3d_ModelViewProjectionMatrix",
    "p3d_ModelViewMatrix",
    "p3d_ProjectionMatrix",
    "p3d_ModelMatrix",
    "p3d_ViewMatrix",
    "p3d_ViewProjectionMatrix",
    "p3d_NormalMatrix",
    "p3d_ProjectionMatrixInverse",
    "p3d_ProjectionMatrixTranspose",
    "p3d_ModelViewMatrixInverseTranspose",
    "p3d_Texture0",
    "p3d_Texture1",
    "p3d_Texture2",
    "p3d_Texture3",
    "p3d_TextureModulate",
    "p3d_TextureAdd",
    "p3d_TextureNormal",
    "p3d_TextureHeight",
    "p3d_TextureGloss",
    "p3d_TextureMatrix",
    "p3d_ColorScale",
    "p3d_Material",
    "p3d_LightModel",
    "p3d_ClipPlane",
    "osg_FrameTime",
    "osg_DeltaFrameTime",
    "osg_FrameNumber",
    "p3d_TransformTable",
    "p3d_LightSource",
    "p3d_Fog",
    "tex",
    "dtex"
]

uniform_associations = {
    "float":UniformFloat,
    "int":UniformInt,
    "bool":UniformBool,
    "sampler2D":UniformImage
}

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue") 

app = Ursina(window_type="tkinter",size=(1280,720))

tkWindow = app.getTkWindow()
tkWindow.state('zoomed')
tkWindow.configure(background='#212121')

tabview = customtkinter.CTkTabview(master=tkWindow,border_width=0,corner_radius=0,anchor="nw",command= lambda : setActiveTab(tabview.get()))



tabview.add("Vertex") 
tabview.add("Fragment") 
tabview.add("Geometry") 
tabview.add("Uniforms") 

tabview.set("Vertex")

vertexCode = Editor(tabview.tab("Vertex"), language=Languages.GLSL)
autocomplete = vertexCode.content.text.auto_completion
fragmentCode = Editor(tabview.tab("Fragment"), language=Languages.GLSL, autocomplete = autocomplete)
geometryCode = Editor(tabview.tab("Geometry"), language=Languages.GLSL, autocomplete = autocomplete)

for word in methods:
    if word not in autocomplete.get_items_text():
        autocomplete.add_item(word, "method")

for word in classes:
    if word not in autocomplete.get_items_text():
        autocomplete.add_item(word, "class")

for word in keywords:
    if word not in autocomplete.get_items_text():
        autocomplete.add_item(word, "keyword")

vertexCode.pack(fill=tk.BOTH, expand=True)
fragmentCode.pack(fill=tk.BOTH, expand=True)
geometryCode.pack(fill=tk.BOTH, expand=True)

vertexCode.focus_force()


uniform_list = tk.Frame(tabview.tab("Uniforms"),bg="#212121")
uniform_list.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=20, pady=20)

def extract_uniforms(code):
    uniforms = []
    for line in code.split("\n"):
        if "uniform" in line:
            line,params = line[7:].split(";")
            if len(params) > 5:
                try :
                    params = params[2:].strip("(").strip(")").split(",")
                    params = list(map(float,params))
                    params = [int(x) if x.is_integer() else x for x in params]
                    params = tuple(params)
                except:
                    params = None
            else:
                params = None
            elements = line.replace("="," ").split(" ")
            elements = [x for x in elements if x != ""]
            uniforms.append([elements,params])
    return uniforms

def get_uniforms():
    for child in uniform_list.winfo_children():
        child.destroy()
    uniforms = extract_uniforms(vertexCode.content.get(1.0, tk.END).strip())
    uniforms.extend(extract_uniforms(fragmentCode.content.get(1.0, tk.END).strip()))
    uniforms.extend(extract_uniforms(geometryCode.content.get(1.0, tk.END).strip()))
    for (uniform,params) in uniforms:
        if uniform[1] not in uniform_names:
            kwargs = {"master":uniform_list,"name":uniform[1],"type":uniform[0],"camera":camera}
            if len(uniform) > 2 :
                kwargs["default_value"] = uniform[2]
            if params != None:
                kwargs["params"] = params
            if uniform[0] in uniform_associations:
                uniform_setter = uniform_associations[uniform[0]](**kwargs)
            else:
                uniform_setter = Uniform(**kwargs)
            uniform_setter.pack(fill=tk.X, expand=True, side=tk.TOP)

extractor_button = customtkinter.CTkButton(tabview.tab("Uniforms"),text="Extract",command=get_uniforms,text_color="green",fg_color="#22272b",border_width=2,border_color="#22272b",hover_color="#343d46",corner_radius=0,border_spacing=0,width=40,font=("Arial", 20),height=40)
extractor_button.pack(fill=tk.X, expand=True, side=tk.BOTTOM)

        
def setActiveTab(tab):
    vertexCode.content.text.active = False
    fragmentCode.content.text.active = False
    geometryCode.content.text.active = False
    if tab == "Vertex":
        vertexCode.content.text.active = True
        autocomplete.updateMaster(vertexCode.content.text)
        vertexCode.focus_force()
    elif tab == "Fragment":
        fragmentCode.content.text.active = True
        autocomplete.updateMaster(fragmentCode.content.text)
        fragmentCode.focus_force()
    elif tab == "Geometry":
        geometryCode.content.text.active = True
        autocomplete.updateMaster(geometryCode.content.text)
        geometryCode.focus_force()
    elif tab == "Uniforms":
        get_uniforms()


def resetVertex():
    vertexCode.content.delete(1.0, tk.END)
    vertexCode.content.insert(tk.END, default_vertex_shader.strip())

def resetFragment():
    fragmentCode.content.delete(1.0, tk.END)
    fragmentCode.content.insert(tk.END, default_fragment_shader.strip())
    
def resetGeometry():
    geometryCode.content.delete(1.0, tk.END)

def clearConsole():
    global console_content
    console_content = ""
    console.configure(state=tk.NORMAL)
    console.delete(1.0, tk.END)
    console.configure(state=tk.DISABLED)
    with open("./data/panda3d.log", "w") as f:
        f.write("")

custom_shader = Shader()

def compile():
    global custom_shader
    vertex = vertexCode.content.get(1.0, tk.END).strip()
    geometry = geometryCode.content.get(1.0, tk.END).strip()
    fragment = fragmentCode.content.get(1.0, tk.END).strip()
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

console = tk.Text(tkWindow,fg="#c5c8c6",bg="#1d1f21",borderwidth=0,highlightthickness=0,insertbackground="#c5c8c6",font=("Arial", 12),state=tk.DISABLED)

def console_print(*args, **kwargs):
    console.configure(state=tk.NORMAL)
    console.insert(tk.END, "\n")
    console.insert(tk.END, *args, **kwargs)
    console.see(tk.END)
    console.configure(state=tk.DISABLED)

def update_console():
    global console_content
    with open("./data/panda3d.log", "r") as f:
        new_content = f.read()
    if new_content != console_content:
        console_print(new_content[len(console_content):])
        console_content = new_content
    tkWindow.after(100, update_console)

builtins.print = console_print

def configure(event):
    if event.widget != tkWindow:
        return
    height = round(tkWindow.winfo_height()/3*2+.5)
    width = round(tkWindow.winfo_width()/3+.5)
    window.size = (width*2, height)
    tabview.rowconfigure(0, weight=1)
    tabview.columnconfigure(0, weight=1)
    tabview.configure(width=width, height=height)
    tabview.place(x=width*2, y=0, anchor="nw")
    compile_and_run.place(x=tkWindow.winfo_width()-compile_and_run.winfo_reqwidth(),y=0,anchor="nw")
    console.place(x=10,y=height+10,anchor="nw",width=width*3-20,height=height/2-20)

tkWindow.bind("<Configure>", configure)

def new_project():
    stop()
    resetVertex()
    resetFragment()
    resetGeometry()
    get_uniforms()

def open_vertex():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            vertexCode.content.delete(1.0, tk.END)
            vertexCode.content.insert(tk.END, f.read())
        tabview.set("Vertex")
        vertexCode.focus_force()
    get_uniforms()

def open_fragment():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            fragmentCode.content.delete(1.0, tk.END)
            fragmentCode.content.insert(tk.END, f.read())
        tabview.set("Fragment")
        fragmentCode.focus_force()
    get_uniforms()
        
def open_geometry():
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        with open(file, 'r') as f:
            geometryCode.content.delete(1.0, tk.END)
            geometryCode.content.insert(tk.END, f.read())
        tabview.set("Geometry")
        geometryCode.focus_force()
    get_uniforms()
        
def open_project():
    directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
    if directory:
        files = os.listdir(directory)
        for file in files:
            if file.endswith(".vert"):
                with open(directory+"/"+file, 'r') as f:
                    vertexCode.content.delete(1.0, tk.END)
                    vertexCode.content.insert(tk.END, f.read())
            elif file.endswith(".frag"):
                with open(directory+"/"+file, 'r') as f:
                    fragmentCode.content.delete(1.0, tk.END)
                    fragmentCode.content.insert(tk.END, f.read())
            elif file.endswith(".geom"):
                with open(directory+"/"+file, 'r') as f:
                    geometryCode.content.delete(1.0, tk.END)
                    geometryCode.content.insert(tk.END, f.read())
    get_uniforms()
            
def save_project():
    directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
    if directory:
        with open(directory+"/vertex.vert", 'w') as f:
            f.write(vertexCode.content.get(1.0, tk.END).strip())
        with open(directory+"/fragment.frag", 'w') as f:
            f.write(fragmentCode.content.get(1.0, tk.END).strip())
        with open(directory+"/geometry.geom", 'w') as f:
            f.write(geometryCode.content.get(1.0, tk.END).strip())

def save_vertex():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".vert",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(vertexCode.content.get(1.0, tk.END).strip())
        file.close()

def save_fragment():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".frag",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(fragmentCode.content.get(1.0, tk.END).strip())
        file.close()

def save_geometry():
    file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".geom",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        file.write(geometryCode.content.get(1.0, tk.END).strip())
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


#Redirect Panda3D output to console
nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename('./data/panda3d.log'))
nout.addStandardOutput()
nout.addSystemDebug()

clearConsole()
update_console()
setActiveTab("Vertex")

app.run()