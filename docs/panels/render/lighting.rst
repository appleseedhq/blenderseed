Lighting
========

- Lighting:
    This sets the lighting engine used during the render.

Path Tracing Engine
-------------------

.. image:: /_static/screenshots/render_panels/lighting.JPG

- Record Light Paths:
    This instructs appleseed to store information on the path that a light ray travels.  It can then be retrieved and visualized in appleseed.studio.  See `here <https://vimeo.com/263532331>`_ for a demonstration of this feature.
- Directly Sample Lights:
    Whether or not discreet light sources (point, spotlight and Sun) are directly sampled at each surface hit point.
- Samples:
    How many light paths are sent to the light at every surface hit.  Raising this can lower the variance on large area lamps.
- Low Light Threshold:
    This prevents shadow rays from being traced to lights that do not contribute significant illumination to the surface hit point.  Higher numbers can lead to a decrease in lighting quality but an increase in convergence speed.
- Light Importance Sampling:
    This control activates importance sampling on rays traced directly to lights.  In some cases it may help to reduce noise.
- Environment Emits Light:
    Whether or not an environment map can contribute lighting to the scene.
- Samples:
    How many samples are taken of the environment light at every surface hit.
- Caustics:
    Whether or not caustic effects are rendered.
- Clamp Roughness:
    Raises the roughness of materials on hits by indirect rays.  This can lower variance for caustics and strong specular reflections.
- Bounces:
    - Global: Sets a maximum number of bounces for a light ray.
    - Diffuse: Sets a maximum number of diffuse bounces a ray can make.
    - Glossy: Sets the number of glossy bounces a ray can make.
    - Specular: Sets the number of specular bounces a ray can make.
    - Volume: Sets the maximum number of volume scattering events.
    - Max Ray Intensity: Sets the maximum brightness an indirect ray can contribute to the scene.  Lowering this can remove fireflies at the expense of accurate lighting.
- Russian Roulette Start Bounce:
    Sets the bounce after which Russian Roulette will be used to terminate rays that are not expected to contribute much to the final image.  Lowering this can increase noise but speed up rendering.
- Optimize for Lights Outside Volumes:
    Use this if lights sources are outside of a volume.

SPPM Engine
-----------

.. image:: /_static/screenshots/render_panels/lighting_2.JPG

|