Motion Blur
===========

.. image:: /_static/screenshots/render_panels/motion_blur.JPG

|

- Shutter Open
	- This is when the shutter opens in relation to the current frame.  '0' opens on the beginning of the frame.
- Shutter Close
	- This is when the shutter closes in relation to the current frame.  '1' shuts at the end of the frame. [#f1]_
- Camera Blur
	- Enables blur caused by motion of the camera.
- Object Blur
	- Enables blur caused by the motion (translation, rotation, or scaling) of an object.
- Deformation Blur
	- Enables blur caused by an object changing shape (deforming)

.. rubric:: Footnotes:

.. [#f1] For realistic blur the shutter should close before the end of the frame.  '0.5' is equivalent to a 180 degree shutter, which is a common shutter type used in motion picture cameras.