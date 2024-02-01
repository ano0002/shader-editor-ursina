from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
import tkinter as tk

# Start ShowBase, but don't open a Panda window yet
base = ShowBase(windowType='none')

# Start Tkinter integration, get the root window handle
base.startTk()

frame = base.tkRoot
frame.update()
id = frame.winfo_id()
width = frame.winfo_width()
height = frame.winfo_height()

props = WindowProperties()
props.setParentWindow(id)
props.setOrigin(0, 0)
props.setSize(width, height)

base.makeDefaultPipe()
base.openDefaultWindow(props=props)

scene = base.loader.loadModel("environment")
scene.reparentTo(base.render)

tkWindow = base.tkRoot

tk.Text(tkWindow).pack()

base.run()