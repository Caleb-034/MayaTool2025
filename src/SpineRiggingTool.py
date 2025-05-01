import maya.cmds as cmds

def create_spine_joints(name_prefix="spine", joint_count=5, start_pos=(0, 0, 0), spacing=2):
    joints = []
    for i in range(joint_count):
        pos = (start_pos[0], start_pos[1] + (i * spacing), start_pos[2])
        jnt = cmds.joint(name=f"{name_prefix}_jnt_{i+1}", position=pos)
        joints.append(jnt)
        if i > 0:
            cmds.joint(joints[i-1], e=True, zso=True, oj='xyz', sao='yup')
    cmds.select(clear=True)
    return joints

def create_spine_ik(joints, name_prefix="spine"):
    ik_handle, effector, curve = cmds.ikHandle(
        name=f"{name_prefix}_ikHandle",
        startJoint=joints[0],
        endEffector=joints[-1],
        solver="ikSplineSolver",
        createCurve=True,
        simplifyCurve=False
    )
    curve = cmds.rename(curve, f"{name_prefix}_ik_curve")
    return ik_handle, curve

def create_controls_for_curve(curve, name_prefix="spine_ctrl"):
    cvs = cmds.ls(f"{curve}.cv[*]", flatten=True)
    controls = []
    for i, cv in enumerate(cvs):
        pos = cmds.pointPosition(cv)
        ctrl_name = f"{name_prefix}_{i+1}"
        ctrl = cmds.circle(name=ctrl_name, normal=(1, 0, 0), radius=1)[0]
        grp = cmds.group(ctrl, name=f"{ctrl}_grp")
        cmds.xform(grp, ws=True, t=pos)

        cluster = cmds.cluster(cv, name=f"{ctrl_name}_cluster")[1]
        cmds.connectAttr(f"{ctrl}.translate", f"{cluster}.translate")
        controls.append(ctrl)
    return controls

def organize_rig(joints, ik_handle, controls):
    rig_grp = cmds.group(empty=True, name="spine_rig_grp")
    joints_grp = cmds.group(joints[0], name="spine_joints_grp")
    ik_grp = cmds.group(ik_handle, name="spine_ik_grp")
    ctrl_grp = cmds.group(empty=True, name="spine_controls_grp")

    for ctrl in controls:
        grp = cmds.listRelatives(ctrl, parent=True)[0]
        cmds.parent(grp, ctrl_grp)

    cmds.parent(joints_grp, ik_grp, ctrl_grp, rig_grp)

def build_spine_rig():
    if cmds.objExists("spine_rig_grp"):
        cmds.warning("Spine rig already exists. Delete it or rename it befoer you make a new one!")
        return

    joints = create_spine_joints()
    ik_handle, curve = create_spine_ik(joints)
    controls = create_controls_for_curve(curve)
    organize_rig(joints, ik_handle, controls)
    print("Spine rig created!")

# Run the rig creation
build_spine_rig()
