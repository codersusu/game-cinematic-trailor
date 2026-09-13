import bpy
from rigify.feature_sets.CloudRig.utils import post_gen
from math import radians as rad

rig = bpy.context.object
pbs = rig.pose.bones

pbs['DEF-Neck'].bone.bbone_custom_handle_end = pbs['STR-Head'].bone
pbs['IK-UpperArm.L'].lock_ik_z = True

bpy.ops.object.mode_set(mode='EDIT')
ebs = rig.data.edit_bones
ebs['STR-Neck'].parent = ebs['ORG-Chest']
eye_mstr = ebs['MSTR-TGT-Eyes']
eye_mstr.head.x = eye_mstr.tail.x = 0
eye_mstr.tail.z = eye_mstr.head.z
eye_mstr.roll = 0

# Shoulder T-pose A-pose shape key fuckery
ebs['SKH-Shoulder.R'].parent = ebs['ROOT-UpperArm.R']
ebs['SKH-Shoulder.R'].roll = 0.43753692507743835
#ebs['SKH-UpperArm.R'].roll = 0.42060917615890503

# I don't get why this is not propagating from the metarig...
pbs['IK-Forearm.R'].lock_ik_y = pbs['IK-Forearm.R'].lock_ik_z = True
pbs['MSTR-Spine_Chest'].custom_shape_transform = pbs['STR-TAN-Chest']

for suf in post_gen.suffixes:
	ebs[f'IK-Thigh{suf}'].layers = [i==16 for i in range(32)]
	ebs[f'IK-UpperArm{suf}'].layers = [i==16 for i in range(32)]

	if suf==".R":
		# Parent FK bones to Rest Pose helpers
		for fk_arm_name in ['FK-UpperArm', 'FK-Forearm', 'FK-Wrist']:
			ebs[fk_arm_name+suf].parent = ebs["P-"+fk_arm_name+suf]

	pbs[f'FK-Forearm{suf}'].lock_rotation = [False, True, True]

	pbs[f'TGT-Eye{suf}'].custom_shape_scale_xyz = [0.078]*3

	# Delete eyelid helper deform bones
	for i in range(3):
		eyelid_def = ebs[f'DEF-Eyelid_Upper_Helper_{i+1}{suf}']
		ebs.remove(eyelid_def)
		eyelid_def = ebs[f'DEF-Eyelid_Lower_Helper_{i+1}{suf}']
		ebs.remove(eyelid_def)
	
	# This Limit Location constraint needs to come before the Action constraint...
	pbs[f'EyeRing{suf}'].constraints.move(1, 0)


# Reshuffle rest pose constraints
for i in range(2):
	pbs[f'P-IK-MSTR-Wrist.R'].constraints.move(2, 0)

ebs[f'IK-POLE-Thigh.L'].roll = rad(46)
ebs[f'IK-POLE-Thigh.R'].roll = -rad(46)
ebs['FK-Wrist.L'].parent = ebs['P-FK-Wrist.L']
ebs['IK-MSTR-C-Wrist.L'].parent = ebs['IK-INT-Wrist.L']

ik_forearm = pbs['IK-Forearm.L']
ik_forearm.lock_ik_y = ik_forearm.lock_ik_z = True

# Workaround crappy relinking in Rigify/CloudRig that makes it impossible to target ORG bones...
pbs['Robo_Shoulder_Tweak_Z'].constraints[0].targets[1].subtarget = 'ORG-UpperArm.L'

# Fix head squashing when hinge is set between 0-1 (This should probably be in CloudRig?)
pbs['FK-HNG-Head'].constraints[0].use_deform_preserve_volume = True

for pb in pbs:
	for c in pb.constraints:

		if hasattr(c, 'target'):
			# Wakey wakey!
			c.target=c.target

#		if c.name in {"Pose Loc", "Pose Rot"}:
#			# Temporarily disable Default Pose constraints...
#			c.enabled = False

		if c.type == 'ACTION' and c.action.name == 'RIG-Einar_Lips_Wide':
			drv = c.driver_add('influence').driver
			drv.type = 'SCRIPTED'
			var = drv.variables.new()
			var.type = 'TRANSFORMS'
			tgt = var.targets[0]
			tgt.id = rig
			tgt.bone_target = "ACT-Mouth_Corner"+c.subtarget[-2:]
			tgt.transform_type = 'LOC_X'
			tgt.transform_space = 'LOCAL_SPACE'
			drv.expression = "1-(abs(var)/0.01)"

#post_gen.set_custom_property_default(rig, 'Properties', 'ik_left_upperarm', 0.0)
#post_gen.set_custom_property_default(rig, 'Properties', 'ik_right_upperarm', 0.0)

post_gen.set_custom_property_default(rig, 'Properties', 'ik_pole_follow_left_thigh', 1.0)
post_gen.set_custom_property_default(rig, 'Properties', 'ik_pole_follow_right_thigh', 1.0)
post_gen.set_custom_property_default(rig, 'Properties', 'sticky_eyelids_eyes', 0.0)

post_gen.set_custom_property_default(rig, 'Properties', 'parents_MSTR-TGT-Eyes', 4)

post_gen.add_ui_data(rig,
	panel_name="FK/IK Switch",
	row_name="Spine",
	entry_name="Spine IK",
	info={
		'prop_bone': "Properties",
		'prop_id': "ik_spine"
	},
	default = 1.0
)
post_gen.add_ui_data(rig,
	panel_name="Misc",
	row_name="Flap",
	entry_name="Auto Shoulder Guard",
	info={
		'prop_bone': "RoboArm_ShoulderFlap",
		'prop_id': "Auto Shoulder Guard"
	},
	default = 1.0
)

post_gen.add_ui_data(rig,
	panel_name="Misc",
	row_name="Shoulder Robotics",
	entry_name="Realistic Robot Shoulder",
	info={
		'prop_bone': "FK-UpperArm.L",
		'prop_id': "Realistic Shoulder"
	},
	default = 1.0
)

ebs['DEF-Wrist.R'].parent = ebs['STR-Wrist.R']

ebs['ORG-UpperArm.R'].parent = ebs['P-FK-UpperArm.R']

bpy.ops.object.mode_set(mode='OBJECT')

pbs['FK-UpperArm.L'].rotation_mode = 'YXZ'

# Spine deformation as if we were using non-sharp sections...
# (We had to use Sharp Sections due to bendy bone crazy space limitation,
# but at that point things like the satchel strap were already animated, so
# these BB- bones are for backwards comp)
pbs['BB-Chest'].bone.bbone_custom_handle_start = pbs['STR-TAN-Chest'].bone
pbs['BB-Chest'].bone.bbone_custom_handle_end = pbs['STR-TIP-TAN-Chest'].bone
pbs['BB-RibCage'].bone.bbone_custom_handle_start = pbs['STR-TAN-RibCage'].bone
pbs['BB-RibCage'].bone.bbone_custom_handle_end = pbs['STR-TAN-Chest'].bone
