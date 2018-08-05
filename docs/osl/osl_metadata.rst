.. _label_osl_metadata:

OSL Metadata
============

When blenderseed scans an OSL shader it looks for several specific metadata tags that can be attached to a shader or parameter.  This metadata is used to populate the node interface in Blender with buttons, sockets, labels, and the range a value can be.  While this metadata is not essential to the shader execution itself, it is essential for making the node usable.

- Shader Metadata:  This metadata is used to describe the shader as a whole.
	- string node_name
		This is the name of the node.  If it is not used the name of the OSL file will be used.
	- string classification
		This tells blenderseed what the shader is.  Options are:
			- surface
			- shader
			- utility
			- texture/2d
			- texture/3d
- Parameter Metadata:  This is metadata that is used on each parameter.
	- string label
		This defines the name of the parameter that will appear in the UI.
	- int as_blender_input_socket
		This tells the UI whether it should hide the socket connection for this parameter.  You would use this for any parameter that you do not want to be controllable through a texture. '0' hides the socket.
	- string help
		This is a tooltip that will appear whenever a parameter is hovered over.
	- string option
		This is used to define the menu options of a drop down list.  Entries should be formatted with a '|' separating each option.
	- string widget
		This is used for defining two things: if a string parameter needs a file selector option, or if the direct control of a parameter should be hidden (so only the socket is visible).  Options are:
		
			- filename (tells blenderseed to add a file selection button to a string property)
			- null (tells blenderseed to hide the direct control for a parameter)
			- checkBox (tells blenderseed that the value should be expressed as a checkbox.  Requires an integer value and int as_blender_input_socket to be set to 0)

|

- Max/Min limits: Integer and float properties can be set with one of four different options that control the range of adjustment a parameter can have.  Options are:
	- max
	- min 
	- softmax 
	- softmin

- Examples:
	- string help = "This is a help string"
	- int softmin = 5
	- string node_name = "asClosure2Surface"