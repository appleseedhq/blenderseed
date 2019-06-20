Features
========

New in 2.0
----------

    * Blender 2.8 support
    * Dynamic OSL script node
    * Texture converter uses internal function (no more need for maketx)
    * Animated textures
    * Native Cryptomatte integration
    * Mesh export is now handled through C++, leading to a 10x reduction in export times
    * Can add and delete objects in viewport render model
    * Stereoscopic rendering support

Supported Features
------------------

    * Pinhole, thin lens (supports physically correct depth of field), orthographic and spherical camera models
    * Camera, transformation and deformation motion blur
    * OSL shading
    * BCD denoiser integration
    * Integrated .tx texture converter
    * Render results directly into Blender or export scene files (including animations) for later rendering
    * AOVs
    * Alpha mapping (object based)
    * Point, directional, area and sun lamps
    * Spot lights (with optional texturing)
    * Physical sun/sky model
    * Gradient, constant color, mirror ball and latitude-longitude map environment models
    * Path tracing and SPPM lighting engines

Planned Features
--------------------

    * OSL volume rendering (once appleseed supports it)
    * Light path visualization
