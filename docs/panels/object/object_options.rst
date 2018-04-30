Object Options
==============

.. image:: /_static/screenshots/object_panels/object_options.PNG

|

- SSS Set:
	This assigns the object to an SSS set.  The sets themselves are set in the :ref:`SSS Sets <label_sss_sets>` panel.
- Nested Dielectric Medium Priority:
	This allows you to set the priority for this object where it intersects with another object.  A higher number equals a higher priority (i.e. 2 takes precedence over 1).  This allows you to correctly render intersecting media like fluid in a glass.
- Ray Bias Method:
	This allows you to set how a ray is biased (offset from the actual shading point).
- Ray Bias Distance:
	This sets how far away from the shading point the ray will be biased.
	
.. _label_obj_alpha:

- Object Alpha:
	This sets the opacity of the object.  A texture may be used to create patterns.  The effects of this option are combined with any material-based alpha mapping.
