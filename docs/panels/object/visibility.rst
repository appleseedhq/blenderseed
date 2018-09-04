Visibility
==========

.. image:: /_static/screenshots/object_panels/visibility.PNG

|

- Visibility Flags:
    These flags determine if an object is visible to specific ray types during rendering.
- Ray Bias:
    This is used to offset the starting point of a ray from the surface of an object.
- Object Alpha:
    This allows a user to determine the transparency of an object.  The parameter can also be driven by a texture map, allowing for cutout effects like leaves.
- Double Sided Shading:
    This tells the renderer to apply the object material to both sides of the polygon.  This is required for glass materials to render properly.
- Nested Glass Priority:
    This allows you to set the priority for this object where it intersects with another object. A higher number equals a higher priority (i.e. 2 takes precedence over 1). This allows you to correctly render intersecting media like fluid in a glass.
- SSS Set:
    A user can assign this object to an existing SSS set by selecting it here.