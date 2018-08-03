Sampling
========

.. image:: /_static/screenshots/render_panels/sampling.JPG   

|

- Samples
    The number of samples per pixel, per pass.
- Passes
    The number of times the renderer will cycles around the pixels of the image. [#f2]_ [#f3]_
- FPS
    The frame rate at which the interactive render will run.
- Max Samples
    The maximum number of samples per pixel that will be taken in interactive mode before rendering ends.
- Tile Pattern
    This determines the order in which the tiles are processed during rendering.
- Tile Size
    Determines the width and height of the 'chunks' (or tiles) the image is split into for rendering.
- Filer
    This defines the filter method appleseed uses to combine pixels with their neighbors.
- Filter Size
    The size of the kernel used during filtering.

- Force Antialiasing
	Force Antialiasing is only relevant when the number of samples is set to 1: when Force Antialiasing is enabled samples are placed randomly inside pixels; when it is disabled, samples are placed at the center of the pixels.
- Decorrelate Pixels
	Avoids correlation patterns at the expense of slightly more sampling noise.

.. rubric:: Footnotes

.. [#f2] Setting the passes higher than 1 and lowering the number of samples enables a featured called 'progressive rendering'.  The image will appear in its entirety after one pass and noise will be subsequently reduced with each addtional pass.
.. [#f3] Progressive rendering is slower than single pass rendering, however it does have its advantages.  If you are not certain how many samples will be needed to create a clean image, you can set the samples to a low number and the passes number to a higher one.  When the image has reached an acceptable level of quality the render can be aborted.