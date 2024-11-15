import bpy
import time
#from . import cs_defUi
 
actionMapProp = "automatism"

strProps = [actionMapProp]
intProps = ["slotMap"]
boolProps = ["canUse"]
actionProps = strProps + intProps + boolProps

mapAct = {"auto": False,
    "filter": "",
    "bone": "",
    "v_min": "",
    "v_max": "",
    "channel": "",
    "space": "",
    "f_start": "",
    "f_end": "",
    "influence": ""}

def setActionsProps(actName, mode = "refresh", channelMap = 0, mapProp = "", mapPropValue = ""):
    if mode == "refresh":
        prp = [p[0] for p in bpy.data.actions[actName].items()]
        for n in actionProps:
            if not n in prp:
                if n in boolProps:
                    bpy.data.actions[actName][n] = False
                elif n in intProps:
                    bpy.data.actions[actName][n] = 0
                else:
                    bpy.data.actions[actName][n] = [mapAct]
    elif mode == "update":
        bpy.data.actions[actName][actionMapProp][channelMap].update({mapProp:mapPropValue})
    elif mode == "addSlot":
        bpy.data.actions[actName][actionMapProp] = bpy.data.actions[actName][actionMapProp] + [mapAct]
    elif mode == "delSlot" and len(bpy.data.actions[actName][actionMapProp]) > 1:
        lst = bpy.data.actions[actName][actionMapProp]
        del lst[channelMap]
        bpy.data.actions[actName][actionMapProp] = lst
        if bpy.data.actions[actName]["slotMap"] >= len(bpy.data.actions[actName][actionMapProp]):
            bpy.data.actions[actName]["slotMap"] = len(bpy.data.actions[actName][actionMapProp])-1
        
def actionBones(actName):
    return list(set([c.data_path.split('"')[1] for c in bpy.data.actions[actName].fcurves if '"' in c.data_path]))

def delActionCons(actName, erase, bool):
    rig = bpy.context.active_object
    pBone = rig.pose.bones
    for b in pBone:
        for c in b.constraints:
            if c.type == 'ACTION':
                if erase:
                    if c.action == None or c.action.name == actName or not c.is_valid:
                        b.constraints.remove(c)
                else:
                    if c.action != None:
                        if c.action.name == actName:
                            c.enabled = bool

def delAllActionsCons(only, erase, bool):
    for a in bpy.data.actions:
        if only:
            if a.get("canUse"):
                delActionCons(a.name, erase, bool)
            else:
                delActionCons(a.name, erase, bool)
        else:
            delActionCons(a.name, erase, bool)

def setAllActionsProps(only):
    for a in bpy.data.actions:
        if only:
            if a.get("canUse"):
                setActionsProps(a.name)
        else:
            setActionsProps(a.name)

def setActionsFakeUser(only, bool):
    for a in bpy.data.actions:
        if only:
            if a.get("canUse"):
                a.use_fake_user = bool
        else:
            a.use_fake_user = bool

def selectActionBones(actName):
    rig = bpy.context.active_object
    bone = rig.data.bones
    names = actionBones(actName)
    for b in bone:
        if b.name in names:
            bone.active = b
            b.select = True
        else:
            b.select = False

def actionCons(actName, bool):
    rig = bpy.context.active_object
    for n in actionBones(actName):
        if n in rig.data.bones:
            b = rig.pose.bones[n]
            for c in b.constraints:
                if c.type == 'ACTION':
                    if c.action != None:
                        if c.action.name == actName:
                            c.enabled = bool

def editAction(actName):
    rig = bpy.context.active_object
    if rig.animation_data.action == None or rig.animation_data.action.name != actName:
        rig.animation_data.action = bpy.data.actions[actName]
        actionCons(actName, False)
        for a in bpy.data.actions:
            if a.name != actName:
                actionCons(a.name, True)
    else:
        rig.animation_data.action = None
        actionCons(actName, True)

def makeAction():
    rig = bpy.context.active_object
    a = bpy.data.actions.new(rig.name)
    bpy.context.scene["rig_action_index"] = bpy.data.actions.find(a.name)

def delActions(mode):
    allActions = (mode == "all")
    singleAction = (mode == "single")
    val = bpy.context.scene["rig_action_index"]
    if singleAction:
        bpy.data.actions.remove(bpy.data.actions[val])
    elif allActions:
        for a in bpy.data.actions:
            bpy.data.actions.remove(a)
    if val == (len(bpy.data.actions)):
        bpy.context.scene["rig_action_index"] = val-1

def makeActionCons(nameCons, boneOwnerName, boneTargetName, actName, f_start, f_end, v_min, v_max, bone_channel, space_trans, infl):
    rig = bpy.context.active_object
    pBone = rig.pose.bones[boneOwnerName]
    c = pBone.constraints.new(type = "ACTION")
    c.name = nameCons
    c.target = rig
    c.subtarget = boneTargetName
    c.influence = infl
    c.transform_channel = bone_channel
    c.target_space = space_trans
    c.min = v_min
    c.max = v_max
    c.action = bpy.data.actions[actName]
    c.frame_start = f_start
    c.frame_end = f_end
    pBone.constraints.move(len(pBone.constraints)-1, 0)


def automatedAction(rfrsh):
    start_time = time.time()
    ##--Addition of actions constraints for automate controls
    for a in [x for x in bpy.data.actions if actionMapProp in x.name]:
        if rfrsh:
            delActionCons(a.name, True, False)
            SnglMtActn(a.name)
        else:
            SnglMtActn(a.name)
#    if rfrsh:
#        cs_defUi.showPopup("%ss applied and updated"%actionMapProp)
    print("Add %ss:"%actionMapProp, str((time.time() - start_time))[:5])

