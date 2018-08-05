Motion Blur
===========

.. image:: /_static/screenshots/render_panels/motion_blur.JPG

|

- Shutter Open Begin
    This is when the shutter begins to open in relation to the current frame.  '0' opens on the beginning of the frame.
- Shutter Open End
    This is when the shutter is fully open
- Shutter Close Begin
    This is when the shutter begins to close in relation to the current frame. [#f1]_
- Shutter Close End
    This is when the shutter is fully closed.
- Camera Blur
    Enables blur caused by motion of the camera.
- Object Blur
    Enables blur caused by the motion (translation, rotation, or scaling) of an object.
- Deformation Blur
    Enables blur caused by an object changing shape (deforming)

.. rubric:: Footnotes:

.. [#f1] For realistic blur the shutter should close before the end of the frame.  '0.5' is equivalent to a 180 degree shutter, which is a common shutter type used in motion picture cameras.