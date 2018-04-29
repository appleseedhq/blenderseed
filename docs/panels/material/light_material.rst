Light Material
==============

.. image:: /_static/screenshots/material_panels/light_emission.PNG

|

- Radiance:
	This is the color of the light light_emission
- Profile:
	This selects one of two different emission profiles:
		Diffuse EDF: This is a standard profile that emits light in a Lambertian fasion (i.e. directionless)
		Cone EDF: This profile allows you to change the angle of distribution, allowing you to create a pseudo spotlight light distribution from a mesh lamp
- Cone EDF Angle (*only applicable to Cone EDF profile*):
	This defines the angle of the light emission for the Cone EDF profile
- Radiance Multiplier:
	This is a multiplier to the Radiance value.  You can use this to increase the intensity of the light
- Exposure:
	This is another way of increasing the intensity of the lamp, only this one works with exposure.  Increasing the number by one doubles the strength of the emission
- Cast Indirect Light:
	Defines whether the light will contribute to indirect lighting in addition to direct light.  Turning this off may increase convergence speed but lower the realism of the lighting
- Importance Multiplier:
	This raises or lowers the likelihood of this light being chosen for a direct sample from a surface hit point.  Changing this may help when the light is not being sampled often enough, however it is usually best left alone
- Light Near Start:
	Changing this can help avoid fireflies when a bright light is near another surface