General
=======

.. image:: /_static/screenshots/render_panels/system.JPG

|

- Auto Threads
    Select this option to have appleseed automatically determine the number of rendering threads to use.  Unselect it to choose manually.
- Render Logging
    Selects the level of feedback from appleseed during rendering.
- Override Shading
    Select this to replace all the shading in a scene with the selected option.  Useful for troubleshooting scene issues.
- Texture Cache
    Sets the size of the cache used for storing textures.  Raising this will increase memory usage but may help speed up rendering.
- Experimental Features
    These features are active in appleseed, but maybe not quite ready for production.  Use at your own risk.

    - Use Embree
        Use Intel's Embree raytracing library.
