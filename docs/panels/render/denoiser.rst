Denoiser
========

.. image:: /_static/screenshots/render_panels/denoiser.JPG

|

- Denoise Mode:
    - On:
        Denoising will run after a render completes
    - Write Outputs:
        The render will write out several multilayer EXR files that can then be denoised at a later time using the denoise utility.  The render itself will not be denoised
    - Prefilter Spikes:
        This filter attempts to remove fireflies (overly bright pixels) from the image before denoising
    - Spike Threshold:
        How high a pixel has to be compared to its neighbors to be considered a spike
    - Patch Distance:
        This controls the overall level of denoising that will be applied.  Raising this too high can lead to a blurry image
    - Denoise Scales:
        This sets how many scale levels are used to remove low frequency noise from the image