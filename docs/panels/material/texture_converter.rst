.. _label_tex_conv:

Texture Converter
=================

The texture converter is a utility for converting traditional image formats (JPEG, PNG, TIFF, etc...) into tiled, mipmapped .tx files for use with appleseed's OSL shading system.

.. image:: /_static/screenshots/material_panels/tex_convert.PNG

|

- Texture List:
	This shows the list of textures in the scene.
- Use Converted Textures:
	This tells blenderseed to substitute texture paths with the .tx version during export and rendering.
- Add Textures:
	This manually adds a texture entry to the list.
- Remove Textures:
	This manually removes the selected texture slot from the list.
- Refresh Textures:
	This scans the texture files that are used in the scene and adds them to the list.  Entries will not be duplicated if they already exists.
- Convert Textures:
	This launches maketx and converts all the textures in the list to .tx versions (if they havent already been converted)
- Texture:
	This is the filepath of the selected entry in the texture list.  Clicking on the filepath button will open a file selection window.
- Input Color Space:
	This parameter tells maketx what color space the original file is in.  If it is anything other than 'linear' the colorspace will be converted during the maketx process.  RGB textures such as color or specular color are usually sRGB.  Bump maps, normal maps, and other greyscale value maps (roughness, metallness) are usually linear, but this may vary depending on the texture source.
- Output Bit Depth:
	This allows you to manually specify the bit depth of the .tx file.  Leaving it at 'default' will set the bit depth to the same size as the input.
- Additional Commands:
	This allows you to specify any additional command variables that should be used during the maketx process.