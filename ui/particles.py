import bpy

#---------------------------------------
# Particle settings UI
#---------------------------------------


class AppleseedPsysPanel(bpy.types.Panel):
    bl_label = "Hair Rendering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "particle"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        psys = context.particle_system
        return renderer == 'APPLESEED_RENDER' and context.object is not None and psys and psys.settings.type == 'HAIR'

    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout
        asr_psys = context.particle_system.settings.appleseed

        layout.prop(asr_psys, "shape")
        layout.prop(asr_psys, "resolution")
        layout.label("Thickness:")
        row = layout.row()
        row.prop(asr_psys, "root_size")
        row.prop(asr_psys, "tip_size")
        layout.prop(asr_psys, "scaling")


def register():
    bpy.utils.register_class(AppleseedPsysPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedPsysPanel)
