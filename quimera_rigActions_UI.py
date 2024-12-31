import bpy
from . import tabName, transChannels
from .quimera_rigActions_modules import actionProps, actionMapProp

classes = []

tab = tabName
panName = "Rig Actions"
rigActName = panName[:-1]

drawModes = {"POSE"}
obTypes = {"ARMATURE"}

modul = "quimera_rigActions_modules"
execFunc = "quimera.function"

def logicDraw() -> bool:
    if bpy.context.mode in drawModes and not bpy.context.active_object == None:
        if bpy.context.active_object.type in obTypes:
            return True

def logicDrawInfo(col):
    col.label(text="Only avaible for object types: "+str(obTypes)[1:][:-1])
    col.label(text="In modes: "+str(drawModes)[1:][:-1])

class ACTION_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        rig = bpy.context.active_object
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # if rig.animation_data == None:
            #     eyes = "HIDE_ON"
            # else:
            eyes = "HIDE_ON" if rig.animation_data == None or rig.animation_data.action != item else "HIDE_OFF"
            rowM = layout.row(align = 1)

            if "canUse" in item: rowM.prop(item, '["canUse"]', text="")
            else: rowM.label(text="", icon="BLANK1")
                
            row = rowM.row(align = 1)
            row.active = True if item.get("canUse") else False
            
            row.scale_x = 1.2
            row.operator(execFunc,text="", icon="RESTRICT_SELECT_OFF").function= modul+".selectActionBones('"+item.name+"')"
            row.operator(execFunc,text="", icon = eyes).function= modul+".editAction('"+item.name+"')"
            row.prop(item, "name", text="", emboss=False)
            row.prop(item, 'use_fake_user', text="")

classes.append(ACTION_UL_list)

class PANEL_PT_RigActions(bpy.types.Panel):

    """ """

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = tab
    bl_label = panName

    def draw(self, context):
        layout = self.layout
        if logicDraw() == True:
            col = layout.column(align = 1)
            rew = col.row(align = 1)
            row = rew.column(align=1)
            row.scale_y = 1.3
            row.template_list("ACTION_UL_list", "", bpy.data, "actions", bpy.context.scene, "rig_action_index")
            row.operator(execFunc,text="Apply %s"%panName).function= modul+".inAllActions('setRigActionCons', all=False, erase=False, bool=False)"
            row = rew.column(align=1)
            row.operator(execFunc,text="", icon = "ADD").function= modul+".makeAction()"
            row.operator(execFunc,text="", icon = "REMOVE").function= modul+".delActions('single')"
            row.separator()
            row.menu(MENU_MT_RigActions.bl_idname,text="", icon="DOWNARROW_HLT")
        else:
            logicDrawInfo(layout.column())

classes.append(PANEL_PT_RigActions)

class MENU_MT_RigActions(bpy.types.Menu):

    bl_label = "Rig actions"
    bl_idname = "MENU_MT_RigActions"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(execFunc,text="Remove all actions", icon = "PANEL_CLOSE").function= modul+"inAllActions('constraint', all=False, erase=False, bool=False)"
        col.operator(execFunc,text="Remove all no %ss"%rigActName, icon = "PANEL_CLOSE").function= modul+".rmvActns('dntMt')"
        col.separator()
        col.operator(execFunc,text="Remove all actions constraints", icon = "PANEL_CLOSE").function= modul+".mngActCnstrnts(False, False, True, False)"
        col.operator(execFunc,text="Remove only %ss constraints"%rigActName, icon = "PANEL_CLOSE").function= modul+".mngActCnstrnts(True, False, True, False)"
        col.operator(execFunc,text="Remove only no %ss constraints"%rigActName, icon = "PANEL_CLOSE").function= modul+".mngActCnstrnts(True, True, True, False)"
        col.separator()
        col.operator(execFunc,text="Enable all actions constraints", icon = "HIDE_OFF").function= modul+".mngActCnstrnts(False, False, False, True)"
        col.operator(execFunc,text="Disable all actions constraints", icon = "HIDE_ON").function= modul+".mngActCnstrnts(False, False, False, False)"
        col.operator(execFunc,text="Enable only %ss constraints"%rigActName, icon = "HIDE_OFF").function= modul+".mngActCnstrnts(True, False, False, True)"
        col.operator(execFunc,text="Disable only %ss constraints"%rigActName, icon = "HIDE_ON").function= modul+".mngActCnstrnts(True, False, False, False)"
        col.operator(execFunc,text="Enable only no %ss constraints"%rigActName, icon = "HIDE_OFF").function= modul+".mngActCnstrnts(True, True, False, True)"
        col.operator(execFunc,text="Disable only no %ss constraints"%rigActName, icon = "HIDE_ON").function= modul+".mngActCnstrnts(True, True, False, False)"
        col.separator()
        col.operator(execFunc,text="Enable all actions fake users", icon = "FAKE_USER_ON").function= modul+".mngFkUsrs(False, True)"
        col.operator(execFunc,text="Disable all actions fake users", icon = "FAKE_USER_OFF").function= modul+".mngFkUsrs(False, False)"
        col.operator(execFunc,text="Enable only %ss fake users"%rigActName, icon = "FAKE_USER_ON").function= modul+".mngFkUsrs(True, True)"
        col.operator(execFunc,text="Disable only %ss fake users"%rigActName, icon = "FAKE_USER_OFF").function= modul+".mngFkUsrs(True, False)"
        col.separator()
        col.operator(execFunc,text="Set props on all actions").function= modul+".mngActEditPrp(False)"
        col.operator(execFunc,text="Set props only on %ss"%rigActName).function= modul+".mngActEditPrp(True)"

classes.append(MENU_MT_RigActions)

class MENU_MT_ActionChannel(bpy.types.Menu):

    bl_label = "Action channel"
    bl_idname = "MENU_MT_ActionChannel"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for i in transChannels:
            drawEditOp(col, "channel", i)
            
classes.append(MENU_MT_ActionChannel)

class MENU_MT_ActionMixMode(bpy.types.Menu):

    bl_label = "Mix mode"
    bl_idname = "MENU_MT_ActionMixMode"

    def draw(self, context):
        layout = self.layout
        lst = ('BEFORE_FULL',
            'BEFORE',
            'BEFORE_SPLIT',
            'AFTER_FULL',
            'AFTER',
            'AFTER_SPLIT')
        col = layout.column()
        for i in lst:
            drawEditOp(col, "mixMode", i)
            
classes.append(MENU_MT_ActionMixMode)

class MENU_MT_ActionSpace(bpy.types.Menu):

    bl_label = "Action space"
    bl_idname = "MENU_MT_ActionSpace"

    def draw(self, context):
        layout = self.layout
        lst = ("WORLD", 
               "CUSTOM", 
               "POSE", 
               "LOCAL_WITH_PARENT", 
               "LOCAL", 
               "LOCAL_OWNER_ORIENT")
        col = layout.column()
        for i in lst:
            drawEditOp(col, "space", i)

classes.append(MENU_MT_ActionSpace)

class PANEL_PT_RigActionsProps(bpy.types.Panel):

    """ """

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = tab
    bl_label = "%s properties"%panName
    bl_parent_id = "PANEL_PT_RigActions"

    def draw(self, context):
        layout = self.layout
        if logicDraw() == True:
            col = layout.column(align = 0)
            for a in bpy.data.actions:
                if bpy.context.scene.rig_action_index == bpy.data.actions.find(a.name):

                    boxTop = col.box().column(align = 1)
                    
                    row = boxTop.row(align = 1)
                    row.enabled = not all([p in a for p in actionProps])
                    row.operator(execFunc,text="Set Props").function= modul+".setActionsProps('"+a.name+"')"
                    ruw = boxTop.row(align = 1)

                    boxBottom = col.box().column(align = 1)
                    
                    rwList = a.get(actionMapProp)
                    if rwList:
                        for d in rwList:
                            for p in d:
                                if a["slotMap"] == rwList.index(d):
                                    noDct = d[p] if any((type(d[p])==v for v in (str, int, float))) else d[p]["value"]
                                    txt = noDct if type(noDct) == str else str(round(noDct, 3))
                                    if p == "bone" or p == "spaceBone":
                                        if p == "bone" or d["space"] == 'CUSTOM':
                                            row = boxBottom.box().row(align = 1)
                                            row.alert = not (txt in bpy.context.active_object.data.bones)
                                            row.scale_x = 0.3
                                            row.label(text=p+":", icon = "BONE_DATA")
                                            row.alert = False
                                            row.scale_x = 1
                                            row.operator("quimera.run_menu" , text=txt).prop = p
                                            v = bpy.context.active_bone.name
                                            w = modul+'.setActionsProps("%s", mode = "update", channelMap = %s, mapProp = "%s", mapPropValue = "%s")'
                                            f = w%(a.name, a["slotMap"], p, v)
                                            row.operator(execFunc, text='', icon='EYEDROPPER').function= f
                                    elif any((p == t for t in ("space", "channel", "mixMode"))):
                                        row = boxBottom.box().row(align = 0)
                                        row.scale_x = 0.3
                                        row.label(text=p+":")
                                        row.scale_x = 1
                                        row.menu("MENU_MT_Action"+p[:1].upper()+p[1:], text=txt)
                                    else:
                                        row = boxBottom.box().row(align = 1)
                                        row.scale_x = 0.3
                                        row.label(text=p+":")
                                        row.scale_x = 1
                                        if not(p == "v_min" or p == "v_max"):
                                            if not d[p]["auto"]:
                                                row.operator("quimera.run_menu" , text=txt).prop = p
                                                row.scale_x = 0.3
                                            w = modul+'.setActionsProps("%s", mode = "update", channelMap = %s, mapProp = "%s", mapPropChannel = "auto", mapPropValue = %s)'
                                            f = w%(a.name, a["slotMap"], p, not d[p]["auto"])
                                            row.operator(execFunc, text="Automatic", icon= "CHECKBOX_HLT" if d[p]["auto"] else "CHECKBOX_DEHLT").function= f
                                        else:
                                            row.operator("quimera.run_menu" , text=txt).prop = p
                                            row.operator(execFunc, text='', icon='EYEDROPPER').function= modul+f'.autoMapTransformChannel("{a.name}", {a["slotMap"]}, "{p}", "{d["channel"]}")'
                                    row.separator()

                        for s in range(len(a[actionMapProp])):
                            operation = "bpy.data.actions['%s']"%a.name+"['slotMap'] = %s"%str(s)
                            ruw.operator(execFunc,text=a[actionMapProp][s]["bone"], depress = (a['slotMap'] == s)).function= operation
                        ruw.operator(execFunc,text="", icon="ADD").function= modul+".setActionsProps('"+a.name+"', mode='addSlot')"
                        ruw.operator(execFunc,text="", icon="REMOVE").function= modul+".setActionsProps('"+a.name+"', mode='delSlot', channelMap = %s)"%str(a['slotMap'])
        else:
            logicDrawInfo(layout.column())

classes.append(PANEL_PT_RigActionsProps)

def drawEditOp(col, propName, propValue):
    i = bpy.context.scene.get("rig_action_index")
    if i != None:
        a = bpy.data.actions[i]
        p = a.get(actionMapProp) if a else None
        if p:
            n = propName
            v = propValue
            w = modul+'.setActionsProps("%s", mode = "update", channelMap = %s, mapProp = "%s", mapPropValue = "%s")'
            f = w%(a.name, a["slotMap"], n, v)
            col.operator(execFunc,text=v,depress=p[a["slotMap"]][n]==v).function= f
        else:
            col.label(text=str(propValue))
    else:
        col.label(text=str(propValue))
    
class BONES_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            rowM = layout.row(align = 1)
            f = f'bpy.context.scene["tmpSwap"] = "{item.name}"'
            rowM.operator(execFunc,text=item.name,depress=item.name==bpy.context.scene["tmpSwap"]).function= f

classes.append(BONES_UL_list)

class OBJECT_OT_RunMenu(bpy.types.Operator):
    
    """Operator for exec functions"""
    
    bl_idname = "quimera.run_menu" 
    bl_label = "run menu"
    bl_options = {'UNDO', 'INTERNAL'}
    prop: bpy.props.StringProperty()
    
    def execute(self, context):
        i = bpy.context.scene.get("rig_action_index")
        if i != None:
            t = bpy.context.scene["tmpSwap"]
            a = bpy.data.actions[i]
            p = self.prop
            v = '"'+t+'"' if type(t)==str else t
            w = modul+'.setActionsProps("%s", mode = "update", channelMap = %s, mapProp = "%s", mapPropValue = %s)'
            f = w%(a.name, a["slotMap"], p, v)
            bpy.ops.quimera.function(function=f)
        return {"FINISHED"}

    def invoke(self, context, event):
        i = bpy.context.scene.get("rig_action_index")
        if i != None:
            a = bpy.data.actions[i]
            p = self.prop
            v = a[actionMapProp][a["slotMap"]][p]
            v = v if any((type(v)==ty for ty in (str, int, float))) else v['value']
            bpy.context.scene["tmpSwap"] = v 
            ui = bpy.context.scene.id_properties_ui("tmpSwap")
            if p == "influence":
                ui.update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
            elif p != "filter" and not 'bone' in self.prop.lower():
                limit = 1000000 if type(v) == int else 1000000.0
                ui.update(min=-limit, max=limit, soft_min=-limit, soft_max=limit)
        return context.window_manager.invoke_props_dialog(self, width = 200, title ="Edit "+p)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if 'bone' in self.prop.lower():
            col.template_list("BONES_UL_list", "", bpy.context.active_object.data, "bones", bpy.context.scene, "rig_action_index")
        else:
            col.prop(bpy.context.scene, '["tmpSwap"]', text="")
    
classes.append(OBJECT_OT_RunMenu)

def rgs():
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except:
            continue
    bpy.types.Scene.rig_action_index = bpy.props.IntProperty()

def unrgs():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    try:
        del bpy.types.Scene.rig_action_index
    except:
        pass

if __name__ == "__main__":
    rgs()