Sampling
========

.. image:: /_static/screenshots/render_panels/sampling.JPG   

|

Common Settings
---------------

- Tile Size
	Determines the width and height of the 'chunks' (or tiles) the image is split into for rendering.
- Filer
	This defines the filter method appleseed uses to combine pixels with their neighbors.
- Filter Size
	The size of the kernel used during filtering.
- Pixel Sampler
	Uniform: Renders the same number of samples for each pixel.
	Adaptive: Samples the pixel until a specific noise level (or quality) is reached, at which point that pixel will no longer be sampled.  In some cases this can lead to faster rendering. [#f1]_

Uniform Sampling Settings
-------------------------

- Passes
	The number of times the renderer will cycles around the pixels of the image. [#f2]_ [#f3]_
- Samples
	The number of samples per pixel, per pass.
- Force Antialiasing
	Force Antialiasing is only relevant when the number of samples is set to 1: when Force Antialiasing is enabled samples are placed randomly inside pixels; when it is disabled, samples are placed at the center of the pixels.
- Decorrelate Pixels
	Avoids correlation patterns at the expense of slightly more sampling noise.

|

.. image:: /_static/screenshots/render_panels/sampling_2.JPG

|

Adaptive Sampling Settings
--------------------------

- Passes
	This is the maximum number of passes that may be done in a rendering process before the process ends.
- Min Samples/Max Samples
	This is the range of samples that can be taken during a pass.  Each pass will sample a pixel until it reaches the minimum, and then the adaptive sampler will continue to render samples until either the selected quality level is reached or the maximum samples are reached.  If the maximum sample level is reached an the pixel has still not reached the set quality level it will continue to be sampled during the next render pass.

.. rubric:: Footnotes

.. [#f1] The adaptive sampler can be difficult to adjust and may lead to flickering in animations.
.. [#f2] Setting the passes higher than 1 and lowering the number of samples enables a featured called 'progressive rendering'.  The image will appear in its entirety after one pass and noise will be subsequently reduced with each addtional pass.
.. [#f3] Progressive rendering is slower than single pass rendering, however it does have its advantages.  If you are not certain how many samples will be needed to create a clean image, you can set the samples to a low number and the passes number to a higher one.  When the image has reached an acceptable level of quality the render can be aborted.