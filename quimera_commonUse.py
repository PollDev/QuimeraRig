import bpy
from . import quimera_rigModules, quimera_rigActions_modules

class OBJECT_OT_ExecFunctions(bpy.types.Operator):
    
    """Operator for exec functions"""
    
    bl_idname = "quimera.function" 
    bl_label = "Quimera exec functions"
    bl_options = {'UNDO', 'INTERNAL'}
    function: bpy.props.StringProperty()
    tool_tip: bpy.props.StringProperty()
    
    @classmethod
    def description(cls, context, properties):
        return properties.tool_tip
    
    def execute(self, context):
        exec(self.function)   
        return {"FINISHED"}

def rgs():
    bpy.utils.register_class(OBJECT_OT_ExecFunctions)

def unrgs():
    bpy.utils.unregister_class(OBJECT_OT_ExecFunctions)

if __name__ == "__main__":
    rgs()


