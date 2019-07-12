Object Options
==========

.. image:: /_static/screenshots/object_panels/obj_options.PNG

|

- Double Sided Shading:
    This tells the renderer to apply the object material to both sides of the polygon.  This is required for glass materials to render properly.
- SPPM Photon Target:
    This flag indicates that the object should be a 'target' for the photons emitted from lamps in SPPM render mode.  Targeting a glass object with strong caustic effects this way can reduce rendering noise.
- Nested Glass Priority:
    This allows you to set the priority for this object where it intersects with another object. A higher number equals a higher priority (i.e. 2 takes precedence over 1). This allows you to correctly render intersecting media like fluid in a glass.
- SSS Set:
    A user can assign this object to an existing SSS set by selecting it here.
- Ray Visibility Flags:
    These flags determine if an object is visible to specific ray types during rendering.
- Object Alpha:
    This allows a user to determine the transparency of an object.  The parameter can also be driven by a texture map, allowing for cutout effects like leaves.
- Motion Blur:
    This flag determines if a deforming object will be rendered with deformation motion blur.
- Object Export:
    This option allows an object to be used as a proxy for a pre-existing appleseed archive assembly.  The assembly will replace the object in the scene at render time.
