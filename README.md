# Ursina Engine Shader Editor

## What is this?

This is a shader editor for the [Ursina Engine](https://www.ursinaengine.org/). It is still in development and is not ready for use yet but feel free to try it and to modify it as you want.

## How do I use it?

### Installation

1. Clone this repository 
2. Run `pip install -r requirements.txt` in the root directory of the repository
3. You're done! Now just run `python main.py` to start the editor.

### Usage

Simply start the editor with `python main.py` and start coding away.
To run the shader you have to click the play button in the top-right of the editor.
To see the uniforms you added in your glsl code, go in the `Uniforms` tab in the editor and click on `Extract`.

> :warning: **To save use the menu in the top-left (ctrl-s hasn't been implemented yet)**: Be very careful here!


### Samples

To test if everything is working for you just open the app and click `File>Open>Shader Project`. Then just open the [`Invert_color`](\Samples\Invert_color) folder from the [`Samples`](\Samples) directory. You should see two uniforms appear in the uniform tab of the editor. To start the shader just click the play button in the top-right of the editor and then play around with the settings to see how it works.

Any feedback is appreciated.


