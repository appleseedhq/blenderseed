Sampling
========

.. image:: /_static/screenshots/render_panels/sampling.JPG   

|

- Sampler
    - Uniform: Every pixel is sampled the same number of times.
    - Adaptive: Sampling is based on whether or not a tile has reached a certain noise threshold.

- Passes
    The number of times the sampler will loop over all the pixels in the image. [#f1]_ [#f2]_

- Uniform Sampler
    - Samples: The number of samples taken per pixel per pass.

- Adaptive Sampler
    - Batch Size: The number of pixel samples taken in between noise evaluations.
    - Max Samples: The total number of samples that can be taken per pixel per pass.
    - Noise Threshold: The level of noise that is acceptable in the final image.  A pixel will render until it hits this limit or the max samples.
    - Uniform Samples: The number of uniform samples that are taken before adaptive sampling kicks in.  This is necessary to ake sure fine details are captured in the image before noise evaluations start.

- Interactive Render
    - FPS: The maximum framerate of the interactive render session.
    - Max Samples: The number of samples taken before rendering halts in interactive mode.

- Tile Pattern
    - Pattern: The order in which tiles are selected during rendering.  Pick anything other that random.
    - Tile Size: This is the size of the tiles that the image is broken into for rendering.

- Pixel Filter:
    - Filter: This is the type of filter used for image reconstruction.
    - Filter Size: The size of the filter kernel.

.. rubric:: Footnotes

.. [#f1] Setting the passes higher than 1 and lowering the number of samples enables a featured called 'progressive rendering'.  The image will appear in its entirety after one pass and noise will be subsequently reduced with each additional pass.
.. [#f2] Progressive rendering is slower than single pass rendering, however it does have its advantages.  If you are not certain how many samples will be needed to create a clean image, you can set the samples to a low number and the passes number to a higher one.  When the image has reached an acceptable level of quality the render can be aborted.