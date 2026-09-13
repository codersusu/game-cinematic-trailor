import bpy
from rigify.feature_sets.CloudRig.utils import post_gen

rig = bpy.context.object

rig.data.bones['PVT-Root'].layers = [i==0 for i in range(32)]

rig.data['ui_data'] = {
	'Satchel' : {
		'' : {
			'Darts' : {
				'Darts' : {'prop_bone':'Properties_Character_Satchel', 'prop_id':'Darts'}
			},
			'Slide': {
				'Slide' : {'prop_bone':'Properties_Character_Satchel', 'prop_id':'Slide'}
			},
			'StrapFollosRoot': {
				'Strap Follows Root' : {'prop_bone':'Properties_Character_Satchel', 'prop_id':'Strap Follows Root'}
			},
			'Wrench': {
				'Wrench' : {'prop_bone':'Properties_Character_Satchel', 'prop_id':'Wrench'},
			}
		}
	}
}