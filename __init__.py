bl_info = {
    'name': "Quimera Tools",
    'author': 'Pablo Ebed Lopez de la Hoz',
    'version': (0,0,0),
    'blender': (4, 1, 0),
    'location': 'View3d, Quimera Tools',
    'description': 'Toolset for create and modify rigs',
    'wiki_url': '',
    'tracker_url': 'https://github.com/PollDev/QuimeraRig/issues',
    'category': 'Rigging'}

import bpy, time

tabName = "Quimera Tools"

transChannels = ("LOCATION_X",
                "LOCATION_Y",
                "LOCATION_Z",
                "ROTATION_X",
                "ROTATION_Y",
                "ROTATION_Z",
                "SCALE_X",
                "SCALE_Y",
                "SCALE_Z")

class QuimeraPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    rigsTemplates: bpy.props.StringProperty(name="", subtype='FILE_PATH')
    rigColl: bpy.props.StringProperty(name="")
    loadRigsTemplates: bpy.props.BoolProperty(name="", default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row(align = 1)
        row.prop(self, "loadRigsTemplates", text = "Load rig templates")
        row = col.row(align = 1)
        row.enabled = self.loadRigsTemplates
        row.prop(self, "rigColl", text = "Collection name")
        row = col.row(align = 1)
        row.enabled = self.loadRigsTemplates
        row.prop(self, "rigsTemplates", text = "Templates folder")

def myTimer(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__}{args} starts")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = round(time.time() - start_time, 4)
        print(f'{func.__name__}{args} finished in {end_time} seconds')
        return result
    return wrapper

def popUp(message = "", title = "Report", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def register():
    bpy.utils.register_class(QuimeraPreferences)
    
    from .quimera_commonUse import rgs
    rgs()

    from .quimera_UI import rgs
    rgs()

    from .quimera_rigActions_UI import rgs
    rgs()
    
    bpy.types.Object.destiny_rig = bpy.props.PointerProperty(name="destiny_rig",type=bpy.types.Object)
    bpy.types.Armature.script_postGeneration = bpy.props.PointerProperty(name="script_postGeneration",type=bpy.types.Text)
    bpy.types.Scene.rig_action_index = bpy.props.IntProperty()
    
def unregister():
    del bpy.types.Object.destiny_rig
    del bpy.types.Armature.script_postGeneration
    del bpy.types.Scene.rig_action_index
    
    from .quimera_commonUse import unrgs
    unrgs()

    from .quimera_UI import unrgs
    unrgs()
    
    from .quimera_rigActions_UI import unrgs
    unrgs()

    bpy.utils.unregister_class(QuimeraPreferences)

if __name__ == "__main__":
    register()