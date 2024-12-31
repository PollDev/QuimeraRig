import os
import bpy
from . import tabName, popUp
classes = []

tab = tabName
panName = "Quimera tools"

addonName = os.path.dirname(os.path.realpath(__file__)).split("\\")[-1]
execFunc = "quimera.function"

class MENU_MT_CustomRigTemplates(bpy.types.Menu):
    
    bl_idname = "MENU_MT_CustomRigTemplates"
    bl_label = "Customs templates"

    def draw(self, context):
        layout = self.layout
        if bpy.context.preferences.addons[addonName].preferences['loadRigsTemplates']:
            path = bpy.context.preferences.addons[addonName].preferences['rigsTemplates']
            for s in os.listdir(path):
                ext = ".blend"
                if ext == s[-len(ext):]:
                    button = layout.operator(execFunc,text = s[:-len(ext)])
                    button.function = "importRig('%s')"%s
        else:
            layout.label(text = "No enabled load rig templates")

classes.append(MENU_MT_CustomRigTemplates)

def importRig(fileName):
    try:
        path = bpy.context.preferences.addons[addonName].preferences['rigsTemplates']+"\\"+fileName
        collName = bpy.context.preferences.addons[addonName].preferences['rigColl']
        bpy.ops.wm.append(filepath=path, directory= path+"\\Collection", filename=collName)
    except:
        popUp(message = "Collection rig to import no avaible")

def quimeraTemplates(self, context):
    self.layout.menu(MENU_MT_CustomRigTemplates.bl_idname,text="Customs templates", icon="MOD_ARMATURE")

class PANEL_PT_QuimeraMain(bpy.types.Panel):

    """Collection of commands for boost the rig creation experience"""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = tab
    bl_label = ""
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text=panName, icon="CONSTRAINT_BONE")

    def draw(self, context):
        layout = self.layout
        actObj = bpy.context.active_object
        
        if actObj == None:
            layout.label(text="Active object no avaible", icon="ERROR")
        elif actObj.type != "ARMATURE":
            layout.label(text="Active object no is a armature", icon="INFO")
        else:
            col = layout.box().column()
            row = col.row()
            row.alert = (actObj.destiny_rig == actObj)
            row.prop(actObj, "destiny_rig", text = "Target rig")
            col.prop(actObj.data, "script_postGeneration", text = "script post-generation")

            col = layout.column()
            col.enabled = not any([actObj.destiny_rig == i for i in [actObj, None]])
            button = col.operator(execFunc,text = "Build rig", icon = "ARMATURE_DATA")
            button.function = "qR.apply_rigMdls()"
                
classes.append(PANEL_PT_QuimeraMain)

def rgs():
    bpy.types.VIEW3D_MT_armature_add.append(quimeraTemplates)
    for c in classes:
        bpy.utils.register_class(c)

def unrgs():
    bpy.types.VIEW3D_MT_armature_add.remove(quimeraTemplates)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    rgs()

