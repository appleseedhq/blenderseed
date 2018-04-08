Lighting
========

- Engine:
	- This sets the lighting engine used during the render.
- Light Sampler:
	- This sets how lights in the scene are sampled.

Path Tracing Engine
-------------------

.. image:: /_static/screenshots/render_panels/lighting.JPG

|

- Next Event Estimation:
	- Whether or not light sources are directly sampled in addition to being hit by indirect rays.
- Direct Lighting:
	- Whether or not discreet light sources (point, spotlight and Sun) are directly sampled at each surface hit point.
- Low Light Threshold:
	- This prevents shadow rays from being traced to lights that do not contribute significant illumination to the surface hit point.  Higher numbers can lead to a decrease in lighting quality but an increase in convergence speed.
- Image Based Lighting:
	- Whether or not an environment map can contribute lighting to the scene.
- Caustics:
	- Whether or not caustic effects are rendered.
- Bounces:
	- Global: Sets a maximum number of bounces for a light ray.
	- Diffuse: Sets a maximum number of diffuse bounces a ray can make.
	- Glossy: Sets the number of glossy bounces a ray can make.
	- Specular: Sets the number of specular bounces a ray can make.
	- Volume: Sets the number of bounces a ray can make inside a volume.
	- Max Ray Intensity: Sets the maximum brightness an indirect ray can contribute to the scene.  Lowering this can remove fireflies at the expense of accurate lighting.
- Russian Roulette Start Bounce:
	- Sets the bounce after which Russian Roulette will be used to terminate rays that are not expected to contribute much to the final image.  Lowering this can increase noise but speed up rendering.
- Volume Distance Samples: 
	- ToDo
- Optimize for Lights Outside Volumes
	- This can help reduce noise when light sources are not inside a volume.
- Mesh Light Multiplier:
	- This is a global multiplier for the intensity of any mesh lights in the scene.
- Export Mesh Lights:
	- Whether or not to export mesh lights.

SPPM Engine
-----------

.. image:: /_static/screenshots/render_panels/lighting_2.JPG

|