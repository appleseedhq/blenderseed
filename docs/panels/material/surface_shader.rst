Surface Shader
==============

.. image:: /_static/screenshots/material_panels/surface_shader.PNG

|

- OSL Node Tree:
	- This is where the name of an OSL node tree will appear if one is linked to the material.  See the :ref:`OSL <label_osl>` page for more information.
- Add appleseed Material Node:
	- This adds an OSL node tree and links it to the material.
- BSDF Model:
	- This is where you select which surface BSDF is used for this object.

|

*The selected BSDF will determine what parameters appear following the BSDF model.*

|

- BSSRDF Model:
	- This selects the BSSRDF (Subsurface Scattering) model.
- Volumetric Model:
	- This determines the volumetric shader that is applied to the object.
- Alpha:
	- This defines the overall opacity of the material.  This works in conjunction with the :ref:`Object Alpha <label_obj_alpha>` settings.
- Bump Map:
	- This activates bump mapping for the material.
- Normal Map:
	- This tells blenderseed that the input map is actually a normal map.
- Bump Amplitude:
	- This is a multiplier for the bump values contained in the map.
- Bump Offset:
	- This changes the gray level that is considered 'neutral' or no bump.