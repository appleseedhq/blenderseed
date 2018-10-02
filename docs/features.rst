Features
========

New in 1.0
----------

    * Completely redesigned export and render stage.  It now uses the appleseed.python bindings (no more random export files in odd places)
    * Interactive rendering
    * Adaptive image sampling
    * Full OSL materials
    * Area lamps
    * Support for linked objects and groups
    * Archive assemblies
    * Post processing stages
    * The appleseed renderer is now bundled directly with blenderseed (no more configuration woes)
    * Adjustable number of motion segments for camera, object, and deformation blur

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

    * Dynamic OSL script node
    * OSL volume rendering (once appleseed supports it)
