import bpy
from bpy.props import FloatProperty, IntProperty, EnumProperty, PointerProperty

#------------------------------------
# Particle system properties
#------------------------------------
class AppleseedPsysProps( bpy.types.PropertyGroup):
    shape = EnumProperty( name = "Strand Shape",
                                        description = "Strand shape to use for rendering",
                                        items = [
                                        ( 'thick', 'Thick', 'Use thick strands for rendering'),
                                        ( 'ribbon', 'Ribbon', 'Use ribbon strands for rendering - ignore thickness of strand')],
                                        default = 'thick') 
                                        
    root_size = FloatProperty( name = "Root", 
                                        description = "Thickness of strand root",
                                        default = 1.0,
                                        min = 0.0,
                                        max = 100)

    tip_size = FloatProperty( name = "Tip", 
                                        description = "Thickness of strand tip",
                                        default = 0.0,
                                        min = 0.0, 
                                        max = 100)

    resolution = IntProperty( name = "Resolution",
                                        description = "Cylindrical resolution of strand. Default of 0 should be sufficient in the majority of cases. Higher values require longer export times",
                                        default = 0, 
                                        min = 0,
                                        max = 2)
                                        
    scaling = FloatProperty( name = "Scaling",
                                        description = "Multiplier of width properties",
                                        default = 0.01,
                                        min = 0.0,
                                        max = 1000)

def register():
    bpy.utils.register_class( AppleseedPsysProps)
    bpy.types.ParticleSettings.appleseed = PointerProperty( type = AppleseedPsysProps)
    
def unregister():
    bpy.utils.unregister_class( AppleseedPsysProps)
