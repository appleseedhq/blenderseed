.. title:: Path Tracing Tips

Path Tracing Tips 
=================
i.e. how do all these crazy parameters fit together?

|

What is Path Tracing, and why should I care?
    Path tracing is one of the dominant (if not *the* dominant) rendering technique in use today, and the images it produces can be almost indistinguishable from reality.  It does this by using raytracing to accurately trace the path a beam of light takes as it bounces, reflects and refracts its way to the camera lens.  While computationally expensive, path tracing has the advantage of naturally capturing the way light moves through a scene.  Effects like global illumination (illumination created by light reflecting off objects) occur naturally with path tracing.  With older methods such as REYES, these effects were laborious to create.

Path Tracing explained in thirty seconds...
    Path tracing works by taking a pixel from the output image frame and sending a virtual ray from the camera, through that pixel, and out into the scene.  The ray will bounce off objects until it runs out of energy, hits a light source, or reaches a preset number of reflections (bounces).  When that happens, the ray is traced back to the camera through all the objects it has hit and the final ‘color’ of that pixel sample is determined.

What are you skipping?
    Quite a bit.  What was described above is the path that an individual ray takes, a single sample per pixel would account for only a minute fraction of the possible paths light could take through the scene to that pixel.  This lack of accuracy is visible as noise in the image.  Path tracers get around this limitation by shooting dozens or even hundreds of rays through each pixel.  As each ray follows a slightly different path, the color of the pixel will 'converge', that is, gradually get closer to the correct value.  As this happens the noise in the image also decreases.  While a path tracer can never perfectly converge a pixel or image (the samples needed is almost infinitely high), eventually it gets close enough that the remaining noise is not objectionable to the human eye.

What else?
    Plain path tracing can produce beautiful images, eventually.  One challenge that is frequently encountered is that light sources are not found often enough when rays bounce around randomly (especially small sources).  To solve this issue, when a surface is hit by a ray, a secondary path (or paths) will be traced from that point directly to a light source.  This is referred to as ‘next event estimation'.  One of the major features that distinguish one path tracer from another is how they perform this direct light sampling in scenes with dozens (or hundreds) of lights.

Okay, but path tracing is soooooooo slow
    Path tracing by its very nature is (and always will be) slower than legacy methods.  While improvements to speed are continually being made, a path tracer simply has to crunch more numbers than older methods.

What are the settings and how do they connect?  Get to the point...
    For appleseed, the settings that control the quality of the render (and the time spent to do it) are found in the render settings panel.  

First off, some terminology:
    - Direct lighting: 
        This is any lighting that results when rays from a light source strike a surface without being blocked.
    - Indirect lighting: 
        This is lighting that results when a ray bounces around through the scene at least once (i.e it doesn’t come directly from a light source).
    - Caustics: 
        These are distinctive patterns that occur when light rays are focused together because of reflection or refraction.  Light patterns on the bottom of a pool are a good example.  Basic path tracing is notoriously bad at resolving caustics, as they are the result of very specific reflection and refraction light bounces.  When the ray is traced ‘backwards’ (i.e. from the camera to a light) the odds of these specific paths being found is relatively small.  Appleseed has an SPPM (Stochastic Progressive Photon Mapping) integrator that is much more effective for rendering caustics.
    - Convergence: 
        This is a term used to indicate how close an image is to being ‘correct’, or finished.  When the render first starts each pixel is quite far off from where it should be, and as it accumulates more samples it gets closer, or ‘converges’, to the correct color.
    - Firefly: 
        A specific kind of lighting artifact that affects path tracers.  It is a pixel that is unusually bright compared to the neighboring pixels, appearing much like a firefly in the dark.  They typically happen when a ray bounces off a surface and randomly hits a very bright, small light source.  The small size of the light means it isn’t hit very often, but when it is, it contributes a large amount of energy to a pixel.

Some of the notable controls are:
    - Samples: 
        This is the main quality control.  The higher this is, the more rays are sent through each pixel, the cleaner the image will be, and the longer it will take to render.
    - Passes: 
        A pass is one round through all the pixels in the output image.  Appleseed can perform what is called ‘progressive rendering’, which is when the image is converged through multiple passes over the image.  The benefit of this is that you can see a rough version of the entire image that cleans up with each pass until the maximum number of passes has been reached.  The downside is that it slows down the rendering process somewhat, so there are tradeoffs to using it.  If you decide to render in multiple passes, the ‘Samples’ control will determine how many pixel samples are taken per pass.

Path Tracer settings:
    - Directly Sample Lights: 
        This is the control that determines if light sources are directly sampled at surface hit points.  There’s really no reason why you’d turn this off except if you have no discreet light sources in your scene.  
        
        There are two additional controls that affect direct light sampling:  
        
        - 'Samples' sets how many rays are traced to light sources for each surface hit point, so you may want to raise this if you have a scene with a lot of direct lighting.  
        
        - 'Low Light Threshold' is a setting that you can use to speed up render convergence at the expense of lighting quality.  It does this by not directly sampling a light if that light is determined to have less illumination on that point than the threshold setting.  It’s a tradeoff, less light rays mean faster convergence, but too high of a threshold can cause the lighting of the entire scene to darken.

    - Image-Based Lighting:
        This lets you control whether HDRI backgrounds can contribute light to the scene.  The Samples parameter next to it has the same purpose as the direct lighting samples.
    - Caustics: 
        This is a scene wide control that enables or disable refractive caustics.  Caustic patterns are very difficult to render properly with a path tracer (due to the unlikelihood of the light source being hit properly) so it’s usually best to disable them entirely.
    - Bounces:  
        These controls allow you to limit the number of times a ray can bounce.  While you can allow the ray to bounce up to 99 times (basically unlimited) virtually all useful lighting information is gained after six bounces or so.  All that extra ray tracing time basically gets you nothing.  The bounce limits are also settable by the type of bounce.  For instance, you can tell a ray to terminate after it hits a diffuse surface twice, regardless of what the global setting is at.  Keep in mind that some situations may require high bounce counts in one category or another.  For example, glass will require high specular bounce levels to look correct.
    - Max Ray intensity:  
        This is a bit of a cheat in that it alters the intensity of light bounces, but it benefits the final render by reducing fireflies.  It does this by putting a limit on how bright an indirect light ray can be.  Lowering this too far can cause indirect lighting to appear dull or washed out.  Once again, it’s a compromise between faster convergence and lighting accuracy.
    - Russian Roulette Start Bounce: 
        This is another optimization that attempts to reduce the number of light rays traced in the scene.  After a ray has reached the same bounce count as the setting, it stands a chance of being randomly terminated.  While this does a good job of reducing the number of rays that need to be traced all the way to the bounce limit, setting it too low can hurt the convergence of the image by stopping paths too soon.

What settings should I use?
    It depends on the image you’re trying to render, honestly.  If you are rendering an outdoor image lit by an HDRI sky and you have a few shiny objects that are directly lit, you could feasibly get a converged image with less than 100 samples and only a few bounces.  If, on the other hand, you’re rendering an indoor scene with highly diffuse objects that are largely lit by indirect lighting, it will take considerably more samples (maybe even over 1,000) and a higher bounce limit.  Trial and error are the keys.  Use render regions if possible to isolate difficult areas of illumination.

What is the adaptive sampler?  Is it better?
    The adaptive sampler adds an extra step to the rendering process.  After a set number of samples, it will evaluate the remaining noise in the tile it is working on.  If that noise is below a certain threshold, it will stop rendering that tile.  The advantages of this process are that more difficult parts of the image will receive more samples for the same amount of render time, leading to an overall cleaner image.  While the differences between adaptive and uniform rendering can often be subtle, the noise distribution and potential time savings of the adaptive sampler are often preferred.

Adaptive sampling controls:
    - Noise threshold: 
        This determines the acceptable level of noise for a tile to be considered done.  Lowering the number lowers this level, hence the tile will render for longer.
    - Max samples: 
        This is the upper limit for how many samples can be taken per pixel.  If a pixel hits this level and still hasn’t reached the noise threshold, it will stop sampling anyway.
    - Uniform samples: 
        This is how many samples each pixel will receive before adaptive sampling begins.  This step is necessary to resolve fine details in the image.  If it is set too low there may be noise or other artifacts in the image that never clear up even with high max sample levels.
    - Step size:  
        This is how many samples are added to a pixel in between noise evaluations.  This noise evaluation does take some processing time, so it may be tempting to raise this number.  However, if it is set too high you may be wasting samples.  For instance if you set it to 64 samples and a tile only needs 75 samples to converge, it will still have to take the remaining 53 samples to reach 128, which is the next time the noise evaluation would run.

What about denoising?
    One of the biggest disadvantages of path tracing is the image noise of an incomplete render.  This is compounded by the fact that as the image continues to render, additional samples make less and less of an impact.  This means it can often take a huge amount of time to remove the last bits of noise.  To eliminate this time sink, most path tracers have some form of denoising that can be used on the image instead.  Appleseed uses the `BCD denoiser <https://github.com/superboubek/bcd>`_.  While denoising can speed up the render process, incorrect settings or too low convergence will cause blurry textures and other image artifacts.

Anything else?
    High resolution HDRI’s are difficult to sample and may lead to slow convergence.  You are better off using a low-resolution image for the lighting itself and then compositing in a high resolution background afterwards.
