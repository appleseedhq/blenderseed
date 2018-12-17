General
=======

.. image:: /_static/screenshots/render_panels/system.JPG

|

- Auto Threads
    Select this option to have appleseed automatically determine the number of rendering threads to use.  Unselect it to choose manually.
- Noise Seed:
    This is used to initialize the number generator used for sampling.  Changing it will cause different noise patterns in the rendered image.
- Vary Noise per Frame:
    This offsets the noise seed by the current frame number.  In animations this causes the noise pattern to vary between frames, mimicking the appearance of film grain.
- Render Logging
    Selects the level of feedback from appleseed during rendering.
- Texture Cache
    Sets the size of the cache used for storing textures.  Raising this will increase memory usage but may help speed up rendering.
- Experimental Features
    These features are active in appleseed, but maybe not quite ready for production.  Use at your own risk.

    - Use Embree
        Use Intel's Embree raytracing library.
