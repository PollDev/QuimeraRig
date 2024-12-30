import bpy
from . import myTimer
actionMapProp = "automatism"

strProps = [actionMapProp]
intProps = ["slotMap"]
boolProps = ["canUse"]
actionProps = strProps + intProps + boolProps

mapAct = {"filter": {"value":"", "auto":False},
    "bone": "",
    "v_min": 0.0,
    "v_max": 1.0,
    "channel": "LOCATION_X",
    "space": "LOCAL",
    "spaceBone": "",
    "mixMode": "BEFORE_SPLIT",
    "f_start": {"value":0, "auto":False},
    "f_end": {"value":10, "auto":False},
    "influence": {"value":1.0, "auto":False}}

def setActionsProps(actName, mode = "refresh", channelMap = 0, mapProp = "", mapPropChannel = "value", mapPropValue = ""):
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
        p = bpy.data.actions[actName][actionMapProp][channelMap].get(mapProp)
        if hasattr(p, '__iter__') and type(p)!=str:
            bpy.data.actions[actName][actionMapProp][channelMap][mapProp].update({mapPropChannel:mapPropValue})
        else:
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

def editAction(actName):
    rig = bpy.context.active_object
    if rig.animation_data == None:
        rig.animation_data_create()
    if rig.animation_data.action == None or rig.animation_data.action.name != actName:
        rig.animation_data.action = bpy.data.actions[actName]
        delActionCons(actName, False, False)
        for a in bpy.data.actions:
            if a.name != actName:
                delActionCons(a.name, False, True)
    else:
        rig.animation_data.action = None
        delActionCons(actName, False, True)

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

def makeActionCons(nameCons, boneOwnerName, boneTargetName, actName, f_start, f_end, v_min, v_max, bone_channel, space_trans, influence, mix_mode, space_bone):
    rig = bpy.context.active_object
    pBone = rig.pose.bones[boneOwnerName]
    c = pBone.constraints.new(type = "ACTION")
    c.name = nameCons
    c.target = rig
    c.subtarget = boneTargetName
    c.influence = influence
    c.transform_channel = bone_channel
    c.target_space = space_trans
    c.space_object = rig
    c.space_subtarget = space_bone
    c.min = v_min
    c.max = v_max
    c.action = bpy.data.actions[actName]
    c.frame_start = f_start
    c.frame_end = f_end
    c.mix_mode = mix_mode
    pBone.constraints.move(len(pBone.constraints)-1, 0)

@myTimer
def setRigActionCons(actName):
    def getSides(word):
        sideL = ("_L", ".L")
        sideR = ("_R", ".R")
        useL = any(((e in word) for e in sideL))
        useR = any(((e in word) for e in sideR))
        usedSide = ("sideL" if useL else "sideR") if any((useL, useR)) else "noSide"
        return usedSide 
        
    a = bpy.data.actions.get(actName)
    map = a.get(actionMapProp) if a else None
    if map:
        for d in map:
            for n in actionBones(actName):
                filterMatch = getSides(d["bone"]) == "noSide" or any((getSides(d["bone"]) == getSides(n), getSides(n) == "noSide"))
                filter = filterMatch if d["filter"]["auto"] else (d["filter"]["value"] in n)

                if filter:
                    autoValue = 1.0 if getSides(d["bone"]) == "noSide" else (0.5 if getSides(n) == "noSide" else 1.0)
                    influence = autoValue if d["influence"]["auto"] else d["influence"]["value"]
                    
                    makeActionCons(actName+"_manager_"+d["bone"],
                    n, 
                    d["bone"], 
                    actName, 
                    round(a.frame_range[0]) if d["f_start"]["auto"] else d["f_start"]["value"], 
                    round(a.frame_range[1]) if d["f_end"]["auto"] else d["f_end"]["value"], 
                    d["v_min"], 
                    d["v_max"], 
                    d["channel"], 
                    d["space"], 
                    influence,
                    d["mixMode"],
                    d["spaceBone"])
                    
def inAllActions(mode, all=False, erase=False, bool=False):
    for a in bpy.data.actions:
        if a.get("canUse") or all:
            if mode == "constraint":
                delActionCons(a.name, erase, bool)
            elif mode == "fakeUser":
                a.use_fake_user = bool
            elif mode == "setActionsProps":
                setActionsProps(a.name)
            elif mode == "setRigActionCons":
                delActionCons(a.name, True, bool)
                setRigActionCons(a.name)
                
             
                
                
                