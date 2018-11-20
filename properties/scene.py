#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2018 The appleseedhq Organization
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

from .. import util

try:
    threads = multiprocessing.cpu_count()
    max_threads = threads
except:
    threads = 1
    max_threads = 32


class AppleseedPostProcessProps(bpy.types.PropertyGroup):
    def update_stamp(self, context):
        self.render_stamp += self.render_stamp_patterns

    def update_name(self, context):
        mapping = {'render_stamp_post_processing_stage': "Render Stamp",
                   'color_map_post_processing_stage': "Color Map",
                   'isolines_post_processing_stage': "Isolines"}
        self.name = mapping[self.model]

    name = bpy.props.StringProperty(name="name",
                                    default="")

    model = bpy.props.EnumProperty(name="model",
                                   items=[
                                       ('render_stamp_post_processing_stage', "Render Stamp", ""),
                                       ('color_map_post_processing_stage', "Color Map", "")],
                                   default='render_stamp_post_processing_stage',
                                   update=update_name)

    # Render stamp
    render_stamp = bpy.props.StringProperty(name="render_stamp",
                                            description="Render stamp text",
                                            default="appleseed {lib-version} | Time: {render-time}")

    render_stamp_patterns = bpy.props.EnumProperty(name="render_stamp_patterns",
                                                   description="Variables to insert into the render stamp",
                                                   items=[
                                                       ('{lib-version}', "Library Version", ""),
                                                       ('{lib-name}', "Library Name", ""),
                                                       ('{lib-variant}', "Library Variant", ""),
                                                       ('{lib-config}', "Library Configuration", ""),
                                                       ('{lib-build-date}', "Library Build Date", ""),
                                                       ('{lib-build-time}', "Library Build Time", ""),
                                                       ('{render-time}', "Render Time", ""),
                                                       ('{peak-memory}', "Peak Memory", "")],
                                                   default="{render-time}",
                                                   update=update_stamp)

    # Color map
    color_map = bpy.props.EnumProperty(name="color_map",
                                       items=[('inferno', "Inferno", ""),
                                              ('jet', "Jet", ""),
                                              ('magma', "Magma", ""),
                                              ('plasma', "Plasma", ""),
                                              ('viridis', "Viridis", ""),
                                              ('custom', "Custom", "")],
                                       default='inferno')

    auto_range = bpy.props.BoolProperty(name="auto_range",
                                        default=True)

    add_legend_bar = bpy.props.BoolProperty(name="add_legend_bar",
                                            default=True)

    legend_bar_ticks = bpy.props.IntProperty(name="legend_bar_ticks",
                                             default=8,
                                             min=2,
                                             soft_max=64)

    range_min = bpy.props.FloatProperty(name="range_min",
                                        default=0.0,
                                        soft_min=0.0,
                                        soft_max=1.0)

    range_max = bpy.props.FloatProperty(name="range_max",
                                        default=1.0,
                                        soft_min=0.0,
                                        soft_max=1.0)

    color_map_file_path = bpy.props.StringProperty(name="color_map_file_path",
                                                   default="",
                                                   subtype='FILE_PATH')

    render_isolines = bpy.props.BoolProperty(name="render_isolines",
                                             default=False)

    line_thickness = bpy.props.FloatProperty(name="line_thickness",
                                             default=1.0,
                                             min=0.5,
                                             soft_max=5.0)


class AppleseedTextureConvertProps(bpy.types.PropertyGroup):
    name = bpy.props.PointerProperty(name="name",
                                     type=bpy.types.Image)

    input_space = bpy.props.EnumProperty(name="input_space",
                                         description="The color space of the file.  PNG, JPG and TIFF files are usually sRGB, EXR is normally linear",
                                         items=[
                                             ('linear', "Linear", ""),
                                             ('sRGB', "sRGB", ""),
                                             ('Rec709', "Rec.709", "")],
                                         default='linear')

    output_depth = bpy.props.EnumProperty(name="output_depth",
                                          description="The bit depth of the output file.  Leave at default for no conversion",
                                          items=[
                                              ('default', "Default", ""),
                                              ('uint8', "Uint8", "Unsigned 8-bit integer"),
                                              ('sint8', "Sint8", "Signed 8-bit integer"),
                                              ('uint16', "Uint16", "Unsigned 16-bit integer"),
                                              ('sint16', "Sint16", "Signed 16-bit integer"),
                                              ('half', "Half", "16-bit float"),
                                              ('float', "Float", "32-bit float")],
                                          default='default')

    command_string = bpy.props.StringProperty(name="command_string",
                                              description="Additional commands",
                                              default="")


class AppleseedRenderSettings(bpy.types.PropertyGroup):
    # Texture conversion

    tex_output_dir = bpy.props.StringProperty(name="tex_output_dir",
                                              description="",
                                              default="",
                                              subtype='DIR_PATH')

    tex_output_use_cust_dir = bpy.props.BoolProperty(name="tex_output_use_cust_dir",
                                                     description="",
                                                     default=False)

    sub_textures = bpy.props.BoolProperty(name="sub_textures",
                                          default=False)

    textures = bpy.props.CollectionProperty(type=AppleseedTextureConvertProps,
                                            name="appleseed Texture",
                                            description="")

    textures_index = bpy.props.IntProperty(name="layer_index",
                                           description="",
                                           default=0)

    # Post processing stages

    post_processing_stages = bpy.props.CollectionProperty(type=AppleseedPostProcessProps,
                                                          name="appleseed post processing",
                                                          description="")

    post_processing_stages_index = bpy.props.IntProperty(name="stage_index",
                                                         description="",
                                                         default=0)

    # Scene render settings.

    scene_export_mode = bpy.props.EnumProperty(name="scene_export_mode",
                                               description="",
                                               items=[
                                                   ('render', "Render", ""),
                                                   ('export_only', "Export Scene Files", "")],
                                               default='render')

    export_selected = bpy.props.BoolProperty(name="export_selected",
                                             default=False)

    threads_auto = bpy.props.BoolProperty(name="threads_auto",
                                          description="Automatically determine the number of rendering threads",
                                          default=True)

    use_embree = bpy.props.BoolProperty(name="use_embree",
                                        description="Use the Intel Embree library for raytracing",
                                        default=False)

    threads = bpy.props.IntProperty(name="threads",
                                    description="Number of threads to use for rendering",
                                    default=threads,
                                    min=1,
                                    max=max_threads)

    log_level = bpy.props.EnumProperty(name="log_level",
                                       items=[('debug', "Debug", ""),
                                              ('info', "Info", ""),
                                              ('error', "Errors", ""),
                                              ('warning', "Warning", ""),
                                              ('fatal', "Fatal", "")],
                                       default='warning')

    tex_cache = bpy.props.IntProperty(name="tex_cache",
                                      description="Size of the texture cache in MB",
                                      default=1024)

    export_hair = bpy.props.BoolProperty(name="export_hair",
                                         description="Export hair particle systems as renderable geometry",
                                         default=False)

    # Sampling.

    decorrelate_pixels = bpy.props.BoolProperty(name="decorrelate_pixels",
                                                description='Avoid correlation patterns at the expense of slightly more sampling noise',
                                                default=True)

    tile_size = bpy.props.IntProperty(name="tile_size",
                                      description="Set the width of the render tile",
                                      default=64,
                                      min=1)

    pixel_filter = bpy.props.EnumProperty(name="Pixel Filter",
                                          description="Pixel filter to use",
                                          items=[('blackman-harris', "Blackman-Harris", "Blackman-Harris"),
                                                 ('box', "Box", "Box"),
                                                 ('catmull', "Catmull-Rom Spline", "Catmull-Rom Spline"),
                                                 ('bspline', "Cubic B-spline", "Cubic B-spline"),
                                                 ('gaussian', "Gaussian", "Gaussian"),
                                                 ('lanczos', "Lanczos", "Lanczos"),
                                                 ('mitchell', "Mitchell-Netravali", "Mitchell-Netravali"),
                                                 ('triangle', "Triangle", "Triangle")],
                                          default='blackman-harris')

    pixel_filter_size = bpy.props.FloatProperty(name="pixel_filter_size",
                                                description="Pixel filter size",
                                                min=0.5,
                                                max=16.0,
                                                default=1.5)

    pixel_sampler = bpy.props.EnumProperty(name="Pixel Sampler",
                                           description="Sampler",
                                           items=[('uniform', "Uniform", "Uniform"),
                                                  ('adaptive', "Adaptive", "Adaptive")],
                                           default='uniform')

    adaptive_batch_size = bpy.props.IntProperty(name="adaptive_batch_size",
                                                description="The number of samples taken in between noise level evaluations",
                                                min=1,
                                                max=1000000,
                                                default=8,
                                                subtype='UNSIGNED')

    adaptive_max_samples = bpy.props.IntProperty(name="adaptive_max_samples",
                                                 description="Maximum number of samples a pixel may take",
                                                 min=1,
                                                 max=1000000,
                                                 default=256,
                                                 subtype='UNSIGNED')

    adaptive_min_samples = bpy.props.IntProperty(name="adaptive_min_samples",
                                                 description="Determines how many uniform samples will be taken before adaptive sampling takes over",
                                                 default=16,
                                                 min=1,
                                                 max=500)

    adaptive_noise_threshold = bpy.props.FloatProperty(name="adaptive_noise_threshold",
                                                       description="The level of noise at which the sampling will end for a pixel.",
                                                       default=1.0,
                                                       min=0.0,
                                                       max=20.0)

    samples = bpy.props.IntProperty(name="samples",
                                    description="Maximum number of anti-aliasing samples",
                                    min=1,
                                    max=8192,
                                    default=16,
                                    subtype='UNSIGNED')

    interactive_max_fps = bpy.props.FloatProperty(name="interactive_max_fps",
                                                  default=10.0)

    interactive_max_samples = bpy.props.IntProperty(name="interactive_max_samples",
                                                    default=-1)

    force_aa = bpy.props.BoolProperty(name="force_aa",
                                      description="When using 1 sample/pixel and Force Anti-Aliasing is disabled, samples are placed at the center of pixels",
                                      default=True)

    renderer_passes = bpy.props.IntProperty(name="renderer_passes",
                                            description="Number of antialiasing passes",
                                            default=1,
                                            min=1,
                                            max=1000000)

    light_sampler = bpy.props.EnumProperty(name="Light Sampler",
                                           description="The method used for sampling lights",
                                           items=[('cdf', 'CDF', 'CDF'),
                                                  ('lighttree', 'Light Tree', 'Light Tree')],
                                           default='cdf')

    tile_ordering = bpy.props.EnumProperty(name="Tile Ordering",
                                           description="Tile ordering",
                                           items=[('linear', "Linear", "Linear"),
                                                  ('spiral', "Spiral", "Spiral"),
                                                  ('hilbert', "Hilbert", "Hilbert"),
                                                  ('random', "Random", "Random")],
                                           default='spiral')

    # Lighting engine.
    lighting_engine = bpy.props.EnumProperty(name="Lighting Engine",
                                             description="Light transport algorithm",
                                             items=[('pt', "Path Tracer", "Unidirectional Path Tracer"),
                                                    ('sppm', "SPPM", "Stochastic Progressive Photon Mapping")],
                                             default='pt')

    record_light_paths = bpy.props.BoolProperty(name="record_light_paths",
                                                default=False)

    # DRT settings.

    enable_ibl = bpy.props.BoolProperty(name="enable_ibl",
                                        description="Enable Image-based lighting",
                                        default=True)

    enable_caustics = bpy.props.BoolProperty(name="enable_caustics",
                                             description="Enable caustics",
                                             default=False)

    enable_clamp_roughness = bpy.props.BoolProperty(name="clamp_roughness",
                                                    default=False)

    enable_dl = bpy.props.BoolProperty(name="enable_dl",
                                       description="Enable direct lighting",
                                       default=True)

    next_event_estimation = bpy.props.BoolProperty(name="next_event_estimation",
                                                   description="Explicitly connect path vertices to light sources to improve efficiency",
                                                   default=True)

    max_bounces_unlimited = bpy.props.BoolProperty(name="max_bounces_unlimited",
                                                   description="No limit to number of ray bounces",
                                                   default=True)

    max_bounces = bpy.props.IntProperty(name="max_bounces",
                                        description="Maximum number of ray bounces",
                                        default=8,
                                        min=0)

    max_diffuse_bounces_unlimited = bpy.props.BoolProperty(name="max_diffuse_bounces_unlimited",
                                                           description="No limit to number of diffuse ray bounces",
                                                           default=True)

    max_diffuse_bounces = bpy.props.IntProperty(name="max_diffuse_bounces",
                                                description="Maximum total number of diffuse bounces",
                                                default=8,
                                                min=0)

    max_glossy_brdf_bounces_unlimited = bpy.props.BoolProperty(name="max_glossy_brdf_bounces_unlimited",
                                                               description="No limit to number of glossy ray bounces",
                                                               default=True)

    max_glossy_brdf_bounces = bpy.props.IntProperty(name="max_glossy_brdf_bounces",
                                                    description="Maximum total number of glossy bounces",
                                                    default=8,
                                                    min=0)

    max_specular_bounces_unlimited = bpy.props.BoolProperty(name="max_specular_bounces_unlimited",
                                                            description="No limit to number of specular ray bounces",
                                                            default=True)

    max_specular_bounces = bpy.props.IntProperty(name="max_specular_bounces",
                                                 description="Maximum total number of specular bounces",
                                                 default=8,
                                                 min=0)

    max_volume_bounces_unlimited = bpy.props.BoolProperty(name="max_volume_bounces_unlimited",
                                                          description="No limit to number of volume ray bounces",
                                                          default=True)

    max_volume_bounces = bpy.props.IntProperty(name="max_volume_bounces",
                                               description="Maximum total number of volume bounces",
                                               default=8,
                                               min=-0)

    max_ray_intensity_unlimited = bpy.props.BoolProperty(name="max_ray_intensity_unlimited",
                                                         description="Unlimited ray intensity",
                                                         default=True)

    max_ray_intensity = bpy.props.FloatProperty(name="max_ray_intensity",
                                                description="Clamp intensity of rays (after the first bounce) to this value to reduce fireflies",
                                                default=1.0,
                                                min=0)

    rr_start = bpy.props.IntProperty(name="rr_start",
                                     description="Consider pruning low contribution paths starting with this bounce",
                                     default=6,
                                     min=1,
                                     max=100)

    optimize_for_lights_outside_volumes = bpy.props.BoolProperty(name="optimize_for_lights_outside_volumes",
                                                                 description="Use when light sources are outside volumes",
                                                                 default=True)

    volume_distance_samples = bpy.props.IntProperty(name="volume_distance_samples",
                                                    description="Number of depth samples to take in a volume",
                                                    default=2,
                                                    min=0,
                                                    max=100)

    dl_light_samples = bpy.props.IntProperty(name="dl_light_samples",
                                             description="Number of samples used to estimate direct lighting",
                                             default=1,
                                             min=0,
                                             max=512)

    dl_low_light_threshold = bpy.props.FloatProperty(name="dl_low_light_threshold",
                                                     description="Light contribution threshold to disable shadow rays",
                                                     default=0.0,
                                                     min=0.0,
                                                     max=10.0)

    ibl_env_samples = bpy.props.IntProperty(name="ibl_env_samples",
                                            description="Number of samples used to estimate environment lighting",
                                            default=1,
                                            min=0,
                                            max=512)

    # SPPM settings.

    sppm_dl_mode = bpy.props.EnumProperty(name="Direct Lighting",
                                          description="SPPM Direct Lighting Component",
                                          items=[('rt', "RT Direct Lighting", 'Use ray tracing to estimate direct lighting'),
                                                 ('sppm', "SPPM Direct Lighting", 'Use photon maps to estimate direct lighting'),
                                                 ('off', "No Direct Lighting", 'Do not estimate direct lighting')],
                                          default='rt')

    # SPPM photon tracing settings.

    sppm_photon_max_length = bpy.props.IntProperty(name="sppm_photon_max_length",
                                                   description="Maximum path length for photons (0 = unlimited)",
                                                   default=0,
                                                   min=0,
                                                   max=100)

    sppm_photon_rr_start = bpy.props.IntProperty(name="sppm_photon_rr_start",
                                                 description="Consider pruning low contribution photons starting with this bounce",
                                                 default=6,
                                                 min=1,
                                                 max=100)

    sppm_env_photons = bpy.props.IntProperty(name="sppm_env_photons",
                                             description="Number of environment photons per render pass",
                                             default=1000000,
                                             min=0)

    sppm_light_photons = bpy.props.IntProperty(name="sppm_light_photons",
                                               description="Number of light photons per render pass",
                                               default=1000000,
                                               min=0)

    # SPPM radiance estimation settings.

    sppm_pt_max_length = bpy.props.IntProperty(name="sppm_pt_max_length",
                                               description="Maximum number of path bounces (0 = unlimited)",
                                               default=0,
                                               min=0,
                                               max=100)

    sppm_pt_rr_start = bpy.props.IntProperty(name="sppm_pt_rr_start",
                                             description="Consider pruning low contribution paths starting with this bounce",
                                             default=6,
                                             min=1,
                                             max=100)

    sppm_initial_radius = bpy.props.FloatProperty(name="sppm_initial_radius",
                                                  description="Initial photon gathering radius in percent of the scene diameter",
                                                  default=0.1,
                                                  min=0.0,
                                                  max=100,
                                                  precision=3)

    sppm_max_per_estimate = bpy.props.IntProperty(name="sppm_max_per_estimate",
                                                  description="Maximum number of photons used to estimate radiance",
                                                  default=100,
                                                  min=1)

    sppm_alpha = bpy.props.FloatProperty(name="sppm_alpha",
                                         description="Evolution rate of photon gathering radius",
                                         default=0.7,
                                         min=0.0,
                                         max=1.0)

    # Denoiser settings

    denoise_mode = bpy.props.EnumProperty(name="Denoise Mode",
                                          description="The mode the denoiser will operate in",
                                          items=[
                                              ('off', "Off", ""),
                                              ('on', "On", ""),
                                              ('write_outputs', "Write Outputs", "")],
                                          default='off')

    denoise_output_dir = bpy.props.StringProperty(name="denoise_output_dir",
                                                  description="Where the denoiser files will be exported",
                                                  default="",
                                                  subtype="DIR_PATH")

    random_pixel_order = bpy.props.BoolProperty(name="random_pixel_order",
                                                default=True)

    skip_denoised = bpy.props.BoolProperty(name="skip_denoised",
                                           default=True)

    prefilter_spikes = bpy.props.BoolProperty(name="prefilter_spikes",
                                              description="This filter attempts to filter pixels that show a strong 'spike' over the average of their neighbors, i.e. fireflies",
                                              default=True)

    spike_threshold = bpy.props.FloatProperty(name="spike_threshold",
                                              description="How much brighter a pixel has to be to be considered a spike",
                                              default=2.0,
                                              min=0.1,
                                              max=4.0)

    patch_distance_threshold = bpy.props.FloatProperty(name="patch_distance_threshold",
                                                       description="This controls the amount of denoising applied to the image",
                                                       default=1.0,
                                                       min=0.5,
                                                       max=3.0)

    denoise_scales = bpy.props.IntProperty(name="denoise_scales",
                                           description="This controls the number of scales that are used to remove low frequency noise",
                                           default=3,
                                           min=1,
                                           max=10)

    mark_invalid_pixels = bpy.props.BoolProperty(name="mark_invalid_pixels",
                                                 default=False)

    # Motion blur settings.

    enable_deformation_blur = bpy.props.BoolProperty(name="enable_deformation_blur",
                                                     description="Global toggle for rendering of deformation motion blur",
                                                     default=False)

    deformation_blur_samples = bpy.props.IntProperty(name="deformation_blur_samples",
                                                     min=2,
                                                     default=2)

    enable_object_blur = bpy.props.BoolProperty(name="enable_object_blur",
                                                description="Global toggle for rendering of object motion blur",
                                                default=False)

    object_blur_samples = bpy.props.IntProperty(name="object_blur_samples",
                                                min=2,
                                                default=2)

    enable_camera_blur = bpy.props.BoolProperty(name="enable_camera_blur",
                                                description="Enable rendering of camera motion blur",
                                                default=False)

    camera_blur_samples = bpy.props.IntProperty(name="camera_blur_samples",
                                                min=2,
                                                default=2)

    shutter_open = bpy.props.FloatProperty(name="shutter_open",
                                           description="Shutter open time (relative to start of current frame)",
                                           default=0.0,
                                           soft_min=0.0,
                                           soft_max=1.0,
                                           step=3,
                                           precision=3)

    shutter_open_end_time = bpy.props.FloatProperty(name="shutter_open_end_time",
                                                    description="Shutter open ending time (relative to start of current frame)",
                                                    default=0.0,
                                                    soft_min=0.0,
                                                    soft_max=1.0,
                                                    step=3,
                                                    precision=3)

    shutter_close = bpy.props.FloatProperty(name="shutter_close",
                                            description="Shutter close time (relative to end of current frame)",
                                            default=1.0,
                                            soft_min=0.0,
                                            soft_max=1.0,
                                            step=3,
                                            precision=3)

    shutter_close_begin_time = bpy.props.FloatProperty(name="shutter_close_begin_time",
                                                       description="Shutter close begin time (relative to start of current frame)",
                                                       default=1.0,
                                                       soft_min=0.0,
                                                       soft_max=1.0,
                                                       step=3,
                                                       precision=3)

    # AOV export

    albedo_aov = bpy.props.BoolProperty(name="albedo_aov",
                                        default=False)

    emission_aov = bpy.props.BoolProperty(name="emission_aov",
                                          default=False)

    diffuse_aov = bpy.props.BoolProperty(name="diffuse_aov",
                                         default=False)

    direct_diffuse_aov = bpy.props.BoolProperty(name="direct_diffuse_aov",
                                                default=False)

    direct_glossy_aov = bpy.props.BoolProperty(name="direct_glossy_aov",
                                               default=False)

    glossy_aov = bpy.props.BoolProperty(name="glossy_aov",
                                        default=False)

    indirect_diffuse_aov = bpy.props.BoolProperty(name="indirect_diffuse_aov",
                                                  default=False)

    indirect_glossy_aov = bpy.props.BoolProperty(name="indirect_glossy_aov",
                                                 default=False)

    normal_aov = bpy.props.BoolProperty(name="normal_aov",
                                        default=False)

    position_aov = bpy.props.BoolProperty(name="position_aov",
                                          default=False)

    depth_aov = bpy.props.BoolProperty(name="depth_aov",
                                       default=False)

    uv_aov = bpy.props.BoolProperty(name="uv_aov",
                                    default=False)

    pixel_time_aov = bpy.props.BoolProperty(name="pixel_time_aov",
                                            default=False)

    invalid_samples_aov = bpy.props.BoolProperty(name="invalid_samples_aov",
                                                 default=False)

    pixel_sample_count_aov = bpy.props.BoolProperty(name="pixel_sample_count_aov",
                                                    default=False)

    pixel_variation_aov = bpy.props.BoolProperty(name="pixel_variation_aov",
                                                 default=False)

    npr_shading_aov = bpy.props.BoolProperty(name="npr_shading_aov",
                                             default=False)

    npr_contour_aov = bpy.props.BoolProperty(name="npr_contour_aov",
                                             default=False)

    # Overrides

    shading_override = bpy.props.BoolProperty(name="shading_override",
                                              default=False)

    override_mode = bpy.props.EnumProperty(name="override_mode",
                                           items=[
                                               ('albedo', "Albedo", ""),
                                               ('facing_ratio', "Facing Ratio", ""),
                                               ('coverage', "Coverage", ""),
                                               ('geometric_normal', "Geometric Normal", ""),
                                               ('ambient_occlusion', "Ambient Occlusion", ""),
                                               ('assembly_instances', "Assembly Instances", ""),
                                               ('barycentric', "Barycentric", ""),
                                               ('bitangent', "Bitangent", ""),
                                               ('color', "Color", ""),
                                               ('depth', "Depth", ""),
                                               ('materials', "Materials", ""),
                                               ('object_instances', "Object Instances", ""),
                                               ('original_shading_normal', "Original Shading Normal", ""),
                                               ('primitives', "Primitives", ""),
                                               ('ray_spread', "Ray Spread", ""),
                                               ('regions', "Regions", ""),
                                               ('screen_space_wireframe', "Screen Space Wireframe", ""),
                                               ('shading_normal', "Shading Normal", ""),
                                               ('sides', "Sides", ""),
                                               ('tangent', "Tangent", ""),
                                               ('uv', "UVs", ""),
                                               ('world_space_position', "World Space Position", ""),
                                               ('world_space_wireframe', "World Space Wireframe", "")],
                                           default='facing_ratio')


def register():
    util.safe_register_class(AppleseedPostProcessProps)
    util.safe_register_class(AppleseedTextureConvertProps)
    util.safe_register_class(AppleseedRenderSettings)
    bpy.types.Scene.appleseed = bpy.props.PointerProperty(type=AppleseedRenderSettings)


def unregister():
    del bpy.types.Scene.appleseed
    util.safe_unregister_class(AppleseedRenderSettings)
    util.safe_unregister_class(AppleseedTextureConvertProps)
    util.safe_unregister_class(AppleseedPostProcessProps)
