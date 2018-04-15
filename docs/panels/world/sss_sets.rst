.. _label_sss_sets:

SSS Sets
========

.. image:: /_static/screenshots/world_panel/sss_sets.JPG

|

SSS sets are a way for appleseed to treat separate meshes as a single object when doing SSS calculations.  This can prevent artifacts where meshes intersect.

.. image:: /_static/screenshots/world_panel/sss_sets_example.png

Objects on the right are in a common SSS set.  Objects on the left are not.

|

- Add Set
	- This adds an SSS set to the current scene.
- Remove Set
	- This removes the currently selected set from the scene.
- SSS Set Name
	- This allows you to set the name of the SSS set.