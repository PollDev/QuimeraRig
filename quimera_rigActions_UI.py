import bpy

classes = []

tab = "Quimera Rigging Tools"
panName = "Rig Actions"
rigActName = panName[:-1]

actionMapProp = "automatism"
actionProps = [actionMapProp, "slotMap", "canUse"]

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
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if bpy.context.active_object.animation_data == None:
                eyes = "HIDE_ON"
            else:
                eyes = "HIDE_OFF" if bpy.context.active_object.animation_data.action == item else "HIDE_ON"
            rowM = layout.row(align = 1)

            if "canUse" in item:
                rowM.prop(item, '["canUse"]', text="")
            else:              
                rowM.label(text="", icon="BLANK1")
                
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
            row.operator(execFunc,text="Apply %s"%panName).function= modul+".automatedAction(True)"
            row = rew.column(align=1)
            row.operator(execFunc,text="", icon = "ADD").function= modul+".makeAction()"
            row.operator(execFunc,text="", icon = "REMOVE").function= modul+".delActions('single')"
            row.separator()
            row.menu(MENU_MT_RigActions.bl_idname,text="", icon="DOWNARROW_HLT")
        else:
            logicDrawInfo(layout.column())

classes.append(PANEL_PT_RigActions)

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

                    BxT = col.box().column(align = 1)
                    row = BxT.row(align = 1)
                    row.enabled = not all([p in a for p in actionProps])
                    row.operator(execFunc,text="Set Props").function= modul+".setActionsProps('"+a.name+"')"

                    BxB = col.box().column(align = 1)
                    ruw = BxT.row(align = 1)
                    
                    rwList = a.get(actionMapProp)
                    if rwList:
                        for d in rwList:
                            for p in d:
                                if a["slotMap"] == rwList.index(d):
                                    row = BxB.row(align = 1)

    #                                csBool = not((p == "influence" or p == "filter") and d["auto"])
    #                                row.enabled = csBool
                                    row.label(text=p)
    #                                row = BxB.row(align = 1)
    #                                row.enabled = csBool
    #                                row.prop(a, '["'+p+'"]', text="")

                    for s in range(len(a[actionMapProp])):
                        operation = "bpy.data.actions['%s']"%a.name+"['slotMap'] = %s"%str(s)
                        ruw.operator(execFunc,text=a[actionMapProp][s]["bone"], depress = (a['slotMap'] == s)).function= operation
                    ruw.operator(execFunc,text="", icon="ADD").function= modul+".setActionsProps('"+a.name+"', mode='addSlot')"
                    ruw.operator(execFunc,text="", icon="REMOVE").function= modul+".setActionsProps('"+a.name+"', mode='delSlot', channelMap = %s)"%str(a['slotMap'])
        else:
            logicDrawInfo(layout.column())

classes.append(PANEL_PT_RigActionsProps)

class MENU_MT_RigActions(bpy.types.Menu):

    bl_label = "Metarigs"
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