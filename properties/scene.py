
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2017 The appleseedhq Organization
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import multiprocessing

import bpy

try:
    threads = multiprocessing.cpu_count()
    max_threads = threads
except:
    threads = 1
    max_threads = 32


def scene_enumerator(self, context):
    matches = []
    for scene in bpy.data.scenes:
        matches.append((scene.name, scene.name, ""))
    return matches


def camera_enumerator(self, context):
    return object_enumerator('CAMERA')


class AppleseedRenderSettings(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed = bpy.props.PointerProperty(
            name="appleseed Render Settings",
            description="appleseed render settings",
            type=cls)

        # Scene render settings.

        cls.selected_scene = bpy.props.EnumProperty(name="Scene",
                                                    description="Select the scene to export",
                                                    items=scene_enumerator)

        cls.selected_camera = bpy.props.EnumProperty(name="Camera",
                                                     description="Select the camera to export",
                                                     items=camera_enumerator)

        cls.output_mode = bpy.props.EnumProperty(name="Output Mode",
                                                 description="Set the mode of export",
                                                 items=[('render', 'Render', ''),
                                                        ('export_only', 'Export Files Only', '')],
                                                 default='render')

        cls.project_path = bpy.props.StringProperty(
            description="Root folder for the appleseed project. Rendered images are saved in a render/ subdirectory.",
            subtype='DIR_PATH')

        cls.threads_auto = bpy.props.BoolProperty(name="Auto Threads",
                                                description="Automatically determine the number of rendering threads",
                                                default=True)

        cls.threads = bpy.props.IntProperty(name="Rendering Threads",
                                            description="Number of threads to use for rendering",
                                            default=threads,
                                            min=1,
                                            max=max_threads)

        cls.generate_mesh_files = bpy.props.BoolProperty(name="Export Geometry",
                                                         description="Write geometry to disk as .obj files",
                                                         default=True)

        cls.export_mode = bpy.props.EnumProperty(name="",
                                                 description="Geometry export mode",
                                                 items=[
                                                     ('all', "All", "Export all geometry, overwriting existing .obj files"),
                                                     ('partial', "Partial", "Only export geometry that has not been written to disk"),
                                                     ('selected', "Selected", "Only export selected geometry")],
                                                 default='all')

        cls.export_hair = bpy.props.BoolProperty(name="Export Hair",
                                                 description="Export hair particle systems as renderable geometry",
                                                 default=False)

        # Sampling.

        cls.decorrelate_pixels = bpy.props.BoolProperty(name="Decorrelate Pixels",
                                                        description='Avoid correlation patterns at the expense of slightly more sampling noise',
                                                        default=True)

        cls.pixel_filter = bpy.props.EnumProperty(name="Pixel Filter",
                                                  description="Pixel filter to use",
                                                  items=[("box", "Box", "Box"),
                                                         ("triangle", "Triangle", "Triangle"),
                                                         ("gaussian", "Gaussian", "Gaussian"),
                                                         ("mitchell", "Mitchell-Netravali", "Mitchell-Netravali"),
                                                         ("bspline", "Cubic B-spline", "Cubic B-spline"),
                                                         ("catmull", "Catmull-Rom Spline", "Catmull-Rom Spline"),
                                                         ("lanczos", "Lanczos", "Lanczos"),
                                                         ("blackman-harris", "Blackman-Harris", "Blackman-Harris")],
                                                  default="blackman-harris")

        cls.pixel_filter_size = bpy.props.FloatProperty(name="Pixel Filter Size",
                                                        description="Pixel filter size",
                                                        min=0.0,
                                                        max=16.0,
                                                        default=1.5)

        cls.pixel_sampler = bpy.props.EnumProperty(name="Pixel Sampler",
                                                   description="Sampler",
                                                   items=[("uniform", "Uniform", "Uniform"),
                                                          ("adaptive", "Adaptive", "Adaptive")],
                                                   default="uniform")

        cls.sampler_min_samples = bpy.props.IntProperty(name="Min Samples",
                                                        description="Minimum number of anti-aliasing samples",
                                                        min=1,
                                                        max=1000000,
                                                        default=16,
                                                        subtype='UNSIGNED')

        cls.sampler_max_samples = bpy.props.IntProperty(name="Max Samples",
                                                        description="Maximum number of anti-aliasing samples",
                                                        min=1,
                                                        max=1000000,
                                                        default=256,
                                                        subtype='UNSIGNED')

        cls.force_aa = bpy.props.BoolProperty(name="Force Anti-Aliasing",
                                              description="When using 1 sample/pixel and Force Anti-Aliasing is disabled, samples are placed at the center of pixels",
                                              default=True)

        cls.renderer_passes = bpy.props.IntProperty(name="Passes",
                                                    description="Number of antialiasing passes",
                                                    default=1,
                                                    min=1,
                                                    max=1000000)

        cls.light_sampler = bpy.props.EnumProperty(name="Light Sampler",
                                                   description="The method used for sampling lights",
                                                   items=[('cdf', 'CDF', 'CDF'),
                                                          ('lighttree', 'Light Tree', 'Light Tree')],
                                                   default='cdf')

        cls.tile_ordering = bpy.props.EnumProperty(name="Tile Ordering",
                                                   description="Tile ordering",
                                                   items=[
                                                       ('linear', "Linear", "Linear"),
                                                       ('spiral', "Spiral", "Spiral"),
                                                       ('hilbert', "Hilbert", "Hilbert"),
                                                       ('random', "Random", "Random")],
                                                   default='spiral')

        cls.sampler_max_contrast = bpy.props.FloatProperty(name="Max Contrast",
                                                           description="Maximum contrast",
                                                           min=0,
                                                           max=1000,
                                                           default=1)

        cls.sampler_max_variation = bpy.props.FloatProperty(name="Max Variation",
                                                            description="Maximum variation",
                                                            min=0,
                                                            max=1000,
                                                            default=1)

        # Lighting engine.
        cls.lighting_engine = bpy.props.EnumProperty(name="Engine",
                                                     description="Light transport algorithm",
                                                     items=[('pt', "Path Tracing", "Unidirectional path tracing"),
                                                            ('sppm', "SPPM", "Stochastic Progressive Photon Mapping")],
                                                     default='pt')

        # DRT settings.

        cls.ibl_enable = bpy.props.BoolProperty(name="Image-Based Lighting",
                                                description="Enable Image-based lighting",
                                                default=True)

        cls.caustics_enable = bpy.props.BoolProperty(name="Caustics",
                                                     description="Enable caustics",
                                                     default=False)

        cls.direct_lighting = bpy.props.BoolProperty(name="Direct Lighting",
                                                     description="Enable direct lighting",
                                                     default=True)

        cls.next_event_est = bpy.props.BoolProperty(name="Next Event Estimation",
                                                    description="Explicitly connect path vertices to light sources to improve efficiency",
                                                    default=True)

        cls.max_bounces_unlimited = bpy.props.BoolProperty(name="",
                                                        description="No limit to number of ray bounces",
                                                        default=True)

        cls.max_bounces = bpy.props.IntProperty(name="",
                                                description="Maximum number of ray bounces (-1 = unlimited)",
                                                default=8,
                                                min=0)

        cls.use_separate_bounces = bpy.props.BoolProperty(name="Use Individual Bounce Limits",
                                                          description="Use individual limits for different ray types",
                                                          default=False)

        cls.max_diffuse_bounces_unlimited = bpy.props.BoolProperty(name="",
                                                        description="No limit to number of diffuse ray bounces",
                                                        default=True)

        cls.max_diffuse_bounces = bpy.props.IntProperty(name="",
                                                        description="Maximum total number of diffuse bounces: -1 = Unlimited",
                                                        default=8,
                                                        min=0)

        cls.max_glossy_bounces_unlimited = bpy.props.BoolProperty(name="",
                                                        description="No limit to number of glossy ray bounces",
                                                        default=True)

        cls.max_glossy_bounces = bpy.props.IntProperty(name="",
                                                       description="Maximum total number of glossy bounces: -1 = Unlimited",
                                                       default=8,
                                                       min=0)

        cls.max_specular_bounces_unlimited = bpy.props.BoolProperty(name="",
                                                        description="No limit to number of specular ray bounces",
                                                        default=True)

        cls.max_specular_bounces = bpy.props.IntProperty(name="",
                                                         description="Maximum total number of specular bounces: -1 = Unlimited",
                                                         default=8,
                                                         min=0)

        cls.max_volume_bounces_unlimited = bpy.props.BoolProperty(name="",
                                                        description="No limit to number of volume ray bounces",
                                                        default=True)

        cls.max_volume_bounces = bpy.props.IntProperty(name="",
                                                       description="Maximum total number of volume bounces: -1 = Unlimited",
                                                       default=8,
                                                       min=-0)

        cls.max_ray_intensity = bpy.props.FloatProperty(name="Max Ray Intensity",
                                                        description="Clamp intensity of rays (after the first bounce) to this value to reduce fireflies (0 = unlimited)",
                                                        default=0,
                                                        min=0)

        cls.rr_start = bpy.props.IntProperty(name="Russian Roulette Start Bounce",
                                             description="Consider pruning low contribution paths starting with this bounce",
                                             default=6,
                                             min=1,
                                             max=100)

        cls.optimize_for_lights_outside_volumes = bpy.props.BoolProperty(name="Optimize for Lights Outside Volumes",
                                                                         description="Use when light sources are outside volumes",
                                                                         default=True)

        cls.volume_distance_samples = bpy.props.IntProperty(name="Volume Distance Samples",
                                                            description="Number of depth samples to take in a volume",
                                                            default=2,
                                                            min=0,
                                                            max=100)

        cls.dl_light_samples = bpy.props.IntProperty(name="Direct Lighting Samples",
                                                     description="Number of samples used to estimate direct lighting",
                                                     default=1,
                                                     min=0,
                                                     max=512)

        cls.dl_low_light_threshold = bpy.props.FloatProperty(name="Low Light Threshold",
                                                             description="Light contribution threshold to disable shadow rays",
                                                             default=0.0,
                                                             min=0.0,
                                                             max=10.0)

        cls.ibl_env_samples = bpy.props.IntProperty(name="IBL Samples",
                                                    description="Number of samples used to estimate environment lighting",
                                                    default=1,
                                                    min=0,
                                                    max=512)

        # SPPM settings.

        cls.sppm_dl_mode = bpy.props.EnumProperty(name="Direct Lighting",
                                                  description="SPPM Direct Lighting Component",
                                                  items=[('sppm', "Use photon maps to estimate direct lighting", ''),
                                                         ('rt', "Use ray tracing to estimate direct lighting", ''),
                                                         ('off', "Do not estimate direct lighting", '')],
                                                  default='rt')

        # SPPM photon tracing settings.

        cls.sppm_photon_max_length = bpy.props.IntProperty(name="Max Bounces",
                                                           description="Maximum path length for photons (0 = unlimited)",
                                                           default=0,
                                                           min=0,
                                                           max=100)

        cls.sppm_photon_rr_start = bpy.props.IntProperty(name="Photon Tracing Russian Roulette Start Bounce",
                                                         description="Consider pruning low contribution photons starting with this bounce",
                                                         default=6,
                                                         min=1,
                                                         max=100)

        cls.sppm_env_photons = bpy.props.IntProperty(name="Environment Photons",
                                                     description="Number of environment photons per render pass",
                                                     default=1000000,
                                                     min=0)

        cls.sppm_light_photons = bpy.props.IntProperty(name="Light Photons",
                                                       description="Number of light photons per render pass",
                                                       default=1000000,
                                                       min=0)

        # SPPM radiance estimation settings.

        cls.sppm_pt_max_length = bpy.props.IntProperty(name="Max Bounces",
                                                       description="Maximum number of path bounces (0 = unlimited)",
                                                       default=0,
                                                       min=0,
                                                       max=100)

        cls.sppm_pt_rr_start = bpy.props.IntProperty(name="Path Tracing Russian Roulette Start Bounce",
                                                     description="Consider pruning low contribution paths starting with this bounce",
                                                     default=6,
                                                     min=1,
                                                     max=100)

        cls.sppm_initial_radius = bpy.props.FloatProperty(name="Initial Radius",
                                                          description="Initial photon gathering radius in percent of the scene diameter",
                                                          default=0.1,
                                                          min=0.0,
                                                          max=100,
                                                          precision=3)

        cls.sppm_max_per_estimate = bpy.props.IntProperty(name="Max Photons",
                                                          description="Maximum number of photons used to estimate radiance",
                                                          default=100,
                                                          min=1)

        cls.sppm_alpha = bpy.props.FloatProperty(name="Alpha",
                                                 description="Evolution rate of photon gathering radius",
                                                 default=0.7,
                                                 min=0.0,
                                                 max=1.0)

        # Miscellaneous settings.

        cls.export_emitting_obj_as_lights = bpy.props.BoolProperty(name="Export Emitting Objects As Mesh Lights",
                                                                   description="Export object with light-emitting materials as mesh (area) lights",
                                                                   default=True)

        cls.enable_diagnostics = bpy.props.BoolProperty(name="Enable diagnostics",
                                                        description='',
                                                        default=False)

        cls.quality = bpy.props.FloatProperty(name="Quality",
                                              description='',
                                              default=3.0,
                                              min=0.0,
                                              max=20.0,
                                              precision=3)

        cls.light_mats_radiance_multiplier = bpy.props.FloatProperty(name="Global Meshlight Energy Multiplier",
                                                                     description="Multiply the exitance of light-emitting materials by this factor",
                                                                     min=0.0,
                                                                     max=100.0,
                                                                     default=1.0)

        cls.recompute_vertex_normals = bpy.props.BoolProperty(name="Recompute Vertex Normals",
                                                              description="If checked, vertex normals will be recomputed during tessellation",
                                                              default=True)

        cls.specular_multiplier = bpy.props.FloatProperty(name="Specular Components Multiplier",
                                                          description="Multiply the intensity of specular components by this factor",
                                                          min=0.0,
                                                          max=1000.0,
                                                          default=1.0,
                                                          subtype='FACTOR')

        cls.point_lights_radiance_multiplier = bpy.props.FloatProperty(name="Point Lights Energy Multiplier",
                                                                       description="Multiply the exitance of point lights by this factor",
                                                                       min=0.0,
                                                                       max=1000.0,
                                                                       default=1.0,
                                                                       subtype='FACTOR')

        cls.spot_lights_radiance_multiplier = bpy.props.FloatProperty(name="Spot Lights Energy Multiplier",
                                                                      description="Multiply the exitance of spot lights by this factor",
                                                                      min=0.0,
                                                                      max=1000.0,
                                                                      default=1.0,
                                                                      subtype='FACTOR')

        # Motion blur settings.

        cls.mblur_enable = bpy.props.BoolProperty(name="",
                                                  description="Enable rendering of motion blur",
                                                  default=False)

        cls.mblur_samples = bpy.props.IntProperty(name="Motion Blur Samples",
                                                  description="Number of samples to use for motion blur",
                                                  default=2)

        cls.def_mblur = bpy.props.BoolProperty(name="Deformation",
                                               description="Global toggle for rendering of deformation motion blur. Warning - objects with deformation motion blur enabled will add to export time!",
                                               default=False)

        cls.ob_mblur = bpy.props.BoolProperty(name="Object",
                                              description="Global toggle for rendering of object motion blur",
                                              default=False)

        cls.cam_mblur = bpy.props.BoolProperty(name="Camera",
                                               description="Enable rendering of camera motion blur",
                                               default=False)

        cls.shutter_open = bpy.props.FloatProperty(name="Shutter Open",
                                                   description="Shutter open time (relative to start of current frame)",
                                                   default=0.0,
                                                   min=0.0,
                                                   max=0.999,
                                                   step=3,
                                                   precision=3)

        cls.shutter_close = bpy.props.FloatProperty(name="Shutter Close",
                                                    description="Shutter close time (relative to end of current frame)",
                                                    default=1.0,
                                                    min=0.001,
                                                    max=1.0,
                                                    step=3,
                                                    precision=3)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.appleseed


def register():
    pass


def unregister():
    pass
