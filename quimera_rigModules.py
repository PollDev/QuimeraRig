import bpy

### --- GOLDEN VARIABLES --- ### 

genModuleName = "constructor_rig_module"

graftPropName = "bone_graft"
graftBonesNamesMemory = {}

### --- FUNCTIONS --- ### 

### - BONES - ###

def putBonesInCollections(bone, boneCollName, add = True, createColl = True):
    cl = bone.id_data.collections_all
    
    def addBoneToColl(bn):
        if len(bn.collections) != 0 and not add:
            for c in [c for c in bn.collections]:
                c.unassign(bn)
        if type(boneCollName) == str:
            if not boneCollName in cl and createColl:
                bn.id_data.collections.new(boneCollName)
            cl[boneCollName].assign(bn)
        else:
            for n in boneCollName:
                if not n in cl and createColl:
                    bn.id_data.collections.new(n)
                cl[n].assign(bn)
                
    if type(bone) == list:
        for bn in bone:
            addBoneToColl(bn)
    else:
        addBoneToColl(bone)

def copyBoneCollections(boneSource, boneDestiny):
    if len(boneSource.collections) != 0:
        putBonesInCollections(boneDestiny, [c.name for c in boneSource.collections], add = False)

def eBoneTransCoord(eBoneDestiny, eBoneSource):
    eBoneDestiny.tail = eBoneSource.tail
    eBoneDestiny.head = eBoneSource.head
    eBoneDestiny.roll = eBoneSource.roll
    eBoneDestiny.bbone_segments = eBoneSource.bbone_segments
    eBoneDestiny.bbone_x = eBoneSource.bbone_x
    eBoneDestiny.bbone_z = eBoneSource.bbone_z

def eBoneSync(rigObj, eBoneSyncName, boneSource, boneCollName = None, parentLogic = ["GET_PARENT", "USE_CONNECT"], create = True):
    eBone = rigObj.data.edit_bones
    if create:
        sync = eBone.new(eBoneSyncName)
    else:
        sync = eBone[eBoneSyncName]
    src = boneSource
    sync.head = (0, 1, 1)
    sync.tail = (0, 1, 2)
    eBoneTransCoord(sync, src)
    try:
        if "GET_PARENT" in parentLogic:
            sync.parent = eBone[src.parent.name]
        if "USE_CONNECT" in parentLogic:
            sync.use_connect = src.use_connect
    except:
        pass
    sync.use_local_location = src.use_local_location
    sync.use_inherit_rotation = src.use_inherit_rotation
    sync.inherit_scale = src.inherit_scale
    sync.use_deform = src.use_deform
    if boneCollName == None:
        copyBoneCollections(src, sync)
    else:
        if type(boneCollName) == str or type(boneCollName) == int:
            rigObj.data.collections_all[boneCollName].assign(sync)
        else:
            for c in boneCollName:
                rigObj.data.collections_all[c].assign(sync)
    return sync

### - OBJECTS - ###                

def selectObject(objName):
    ob = bpy.data.objects
    ob[objName].select_set(True) 
    bpy.context.view_layer.objects.active = ob[objName]

def showSelectionObj(showObjName, notShowObjsNamesList):
    ob = bpy.data.objects
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    ob[showObjName].hide_viewport = False
    for n in notShowObjsNamesList:
        if n in ob:
            ob[n].hide_viewport = True
    selectObject(showObjName)

### - RIG MODULES - ###

def rigMdl_syncEraser(rigSource, rigTarget, bonesNamesList):
    if bpy.context.mode == 'EDIT_ARMATURE':
        sourceRigEBone = rigSource.data.edit_bones
        targetRigEBone = rigTarget.data.edit_bones
        
        for n in bonesNamesList:
            if not (n in sourceRigEBone) and targetRigEBone[n][graftPropName]:
                targetRigEBone.remove(targetRigEBone[n])
    else:
        rigGraftBonesNamesPre = [b.name for b in rigTarget.data.bones if graftPropName in b]
        return rigGraftBonesNamesPre

def rigMdl_rawInsert(rigSource, rigTarget):
    
    mmry = []
    consBones = []
    
    def copyPoseBoneConstraints(destinyPoseBone, sourcePoseBone):
        if not bpy.context.mode == 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        for c in destinyPoseBone.constraints:
            destinyPoseBone.constraints.remove(c)
        for cSrc in sourcePoseBone.constraints:
            cDst = destinyPoseBone.constraints.new(cSrc.type)
            cDst.name = cSrc.name
            for prop in dir(cSrc):
                try:
                    if prop == "target":
                        cDst.target = rigTarget
                    else:
                        setattr(cDst, prop, getattr(cSrc, prop))
                except:
                    continue
                
    if bpy.context.mode == 'EDIT_ARMATURE':
        targetRigEBone = rigTarget.data.edit_bones
        for b in rigSource.data.edit_bones:
#            if rigSource.pose.bones[b.name].get(genModuleName) == "rawInsert":
            if b.name in targetRigEBone:
                currentBone = eBoneSync(rigTarget, b.name, b, create = False)
            else:
                currentBone = eBoneSync(rigTarget, b.name, b)
            
            currentBone[graftPropName] = True
            mmry.append(currentBone.name)
            consBones.append(b.name)
        graftBonesNamesMemory.update({"rawInsert": {"bones": mmry, "consBones": consBones}})
        
    elif bpy.context.mode == 'POSE':
        for n1, n2 in zip(graftBonesNamesMemory["rawInsert"]["bones"], graftBonesNamesMemory["rawInsert"]["consBones"]):
            copyPoseBoneConstraints(rigTarget.pose.bones[n1], rigSource.pose.bones[n2])
            
### --- LOGIC --- ### 

def apply_rigMdls():
    sourceRig = bpy.context.active_object
    destinyRig = sourceRig.destiny_rig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    selectObject(sourceRig.name)
    selectObject(destinyRig.name)

    rigGraftBonesNamesPre = rigMdl_syncEraser(sourceRig, destinyRig, [])

    bpy.ops.object.mode_set(mode='EDIT')

    rigMdl_rawInsert(sourceRig, destinyRig)
    rigMdl_syncEraser(sourceRig, destinyRig, rigGraftBonesNamesPre)

    bpy.ops.object.mode_set(mode='POSE')

    rigMdl_rawInsert(sourceRig, destinyRig)

    graftBonesNamesMemory.clear()
    #showSelectionObj(destinyRig.name, [sourceRig.name])


