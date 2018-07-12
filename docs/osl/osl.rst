.. _label_osl:

Open Shading Language
=====================

What is it?
-----------
	Open Shading Language (OSL) is a small, customized computer language intended specifically for writing shaders in a physically plausible rendering engine.  While it was originally designed at Sony Pictures Imageworks for their Arnold renderer it has since been integrated into appleseed and several other renderer engines (such as Renderman and Cycles).

How does it work with appleseed?
--------------------------------
	Since the beginning appleseed has had its own native shading system (henceforth the ‘built in system’, or ‘BIS’).  While this system worked well enough, it was limited to defining material surfaces and optionally assigning UV mapped textures to them.  That was it.  It couldn’t do any kind of procedural patterns, coordinate manipulation, fancy BSDF mixing, or any of the other utility functions that were needed for a production renderer.  Instead of expanding the BIS system with these features, the decision was made to integrate OSL instead, as it is fully capable of all these features and is developed and hosted by a major visual effects company.  As of the current release (1.0), the BIS system is no longer exposed in blenderseed.

How do I use it in blenderseed?
-------------------------------
	OSL is available in conjunction with the node editor in Blender.  When a material is created, by default it will add an OSL node tree and link to it.  If you have an open node editor you can use the 'view nodetree' button under the material preview to switch the node view to the current material.  You can add nodes to the editor using Shift+A.  You can add nodes from the different categories to build up your material, but always make sure the final node is an as_closure2surface node, as that is required to export the material properly.

Where does the OSL shading system get the nodes from?
-----------------------------------------------------
	The OSL shaders are found in one of two directories in the appleseed download, “shaders/appleseed” and “shaders/blenderseed”.  When blenderseed starts up it scans those two directories and builds the nodes dynamically based on the parameters contained inside the .oso files.  When the scene is rendered the output file will point to those shaders and describe the connections between them.  The shaders themselves are not copied or moved.

Textures with OSL
-----------------
	OSL can directly load most image formats (JPEG, PNG, TIFF).  However, this is not the best practice for using it.  Full sized textures take up a lot of memory in the render, and in many cases objects will not be sufficiently large enough in the output frame to justify the memory space used for high resolution, detailed images.  The solution is to create a .tx file using maketx, a utility that ships with appleseed.  Maketx will take an input image and produce a tiled, mipmapped version that is far more efficient when used with OSL.  This is due to a few different features: for one the tiling allows appleseed to only load the sections of the image that are visible.  Second the mipmapping allows appleseed to load in the appropriate resolution of the texture depending on how large the object is in the output frame. These two features not only reduce the memory requirement for textures, they also speed up the render.

How do I convert textures?
--------------------------
	Textures can be converted to .tx files using the :ref:`texture converter<label_tex_conv>` panel in the material tab.

Can I write my own shaders?
---------------------------
	Absolutely.  OSL shaders can be written in any text editor and compiled into .oso files using the oslc utility that’s included with appleseed.  The .oso file can then be placed into the shaders/blenderseed folder and it will be scanned and added into the available nodes during the next startup.
	If you choose to write your own OSL shader, there are several formatting rules and :ref:`metadata<label_osl_metadata>` tags that should be used in order to properly build the node’s UI and category.
