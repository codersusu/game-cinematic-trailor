"""Read-only V5→V6 audit, including evidence for reusing frames1–359.
Run with Blender --background --disable-autoexec --python-exit-code1.
Loads both scenes, evaluates animation on CPU, writes renders/v6/scene-audit.json.
Neither saved scene is edited. A failed check raises after writing the report.
"""
from pathlib import Path
from array import array
from mathutils import Vector,Quaternion
import math
import hashlib, json, re, sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_scene_v5 import coordinates, simple, digest
RIG='Bip01'
NEW_CAMERA='V6 | The first reach'
ADDED_OBJECTS={NEW_CAMERA:'CAMERA',NEW_CAMERA+' focus':'EMPTY'}
ALLOW_FIXED={'Bip01 Spine1','Bip01 Spine2','Bip01 R Clavicle','Bip01 R UpperArm','Bip01 R Forearm','Bip01 R Hand'}
BONE_PATH=re.compile(r'^pose\.bones\["(.*)"\]\.([a-z_]+)$')
WORLD_MATRIX_TOLERANCE=2e-6
CURVE_TOLERANCE=1e-7

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

def allowed_bone(name):return name in ALLOW_FIXED or name.startswith('Bip01 R Finger')
def allowed_curve(path):
 m=BONE_PATH.match(path)
 return bool(m and allowed_bone(m[1]) and m[2]=='rotation_quaternion')

def primitives(owner,skip=()):
 if owner is None:return None
 result={}
 for prop in owner.bl_rna.properties:
  key=prop.identifier
  if key=='rna_type' or key in skip or prop.is_readonly:continue
  try:
   value=getattr(owner,key)
   if prop.type in {'BOOLEAN','ENUM','FLOAT','INT','STRING'}:
    result[key]=sorted(value) if isinstance(value,set) else simple(value)
   elif prop.type=='POINTER' and isinstance(value,bpy.types.ID):result[key]=simple(value)
  except (AttributeError,TypeError,ValueError):pass
 return result

def curve_record(fc):
 return {'path':fc.data_path,'index':fc.array_index,'extrapolation':fc.extrapolation,'mute':fc.mute,
  'keys':[{'co':list(k.co),'left':list(k.handle_left) if k.interpolation=='BEZIER' else None,'right':list(k.handle_right) if k.interpolation=='BEZIER' else None,'interpolation':k.interpolation,'left_type':k.handle_left_type,'right_type':k.handle_right_type,'easing':k.easing,'amplitude':k.amplitude,'back':k.back,'period':k.period} for k in fc.keyframe_points],
  'modifiers':[primitives(m) for m in fc.modifiers]}

def animation(owner,filter_reach=False):
 ad=getattr(owner,'animation_data',None)
 if not ad:return None
 curves=sorted((curve_record(fc) for fc in ad.action.fcurves if not(filter_reach and allowed_curve(fc.data_path))),key=lambda x:(x['path'],x['index'])) if ad.action else []
 return {'curves':curves,'action_settings':primitives(ad.action,{'name','use_fake_user'}) if ad.action else None,
  'ad_settings':primitives(ad,{'action'}),'drivers':[{'curve':curve_record(fc),'type':fc.driver.type,'expression':fc.driver.expression,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':simple(t.id),'data_path':t.data_path,'bone_target':t.bone_target,'transform_type':t.transform_type,'transform_space':t.transform_space} for t in v.targets]} for v in fc.driver.variables]} for fc in ad.drivers],
  'nla':[{'name':tr.name,'mute':tr.mute,'strips':[{'settings':primitives(st),'action':st.action.name if st.action else None} for st in tr.strips]} for tr in ad.nla_tracks]}

def nodes(tree):
 if not tree:return None
 result=[]
 for n in tree.nodes:
  item={'name':n.name,'type':n.bl_idname,'properties':primitives(n,{'location','width','height','label','select','show_options','show_preview','show_texture','color','use_custom_color','parent'}),
   'inputs':[(x.identifier,simple(x.default_value)) for x in n.inputs if hasattr(x,'default_value')],
   'outputs':[(x.identifier,simple(x.default_value)) for x in n.outputs if hasattr(x,'default_value')]}
  if hasattr(n,'color_ramp'):item['color_ramp']={'settings':primitives(n.color_ramp),'elements':[(e.position,list(e.color)) for e in n.color_ramp.elements]}
  for key in ('texture_mapping','color_mapping'):
   if hasattr(n,key):item[key]=primitives(getattr(n,key))
  result.append(item)
 return {'nodes':result,'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links),'animation':animation(tree)}

def mesh_record(me):
 attrs={}
 for at in me.attributes:
  prop,width,code={'FLOAT':('value',1,'f'),'INT':('value',1,'i'),'BOOLEAN':('value',1,'b'),'FLOAT_VECTOR':('vector',3,'f'),'FLOAT2':('vector',2,'f'),'FLOAT_COLOR':('color',4,'f'),'BYTE_COLOR':('color',4,'f')}.get(at.data_type,(None,None,None))
  if prop:
   try:attrs[at.name]={'domain':at.domain,'type':at.data_type,'sha256':coordinates(at.data,prop,width,code)}
   except (AttributeError,TypeError):attrs[at.name]={'domain':at.domain,'type':at.data_type,'count':len(at.data)}
 return {'name':me.name,'vertices':len(me.vertices),'polygons':len(me.polygons),'co':coordinates(me.vertices,'co',3),'loops':coordinates(me.loops,'vertex_index',1,'i'),'edges':coordinates(me.edges,'vertices',2,'i'),'material_indices':coordinates(me.polygons,'material_index',1,'i'),'smooth':coordinates(me.polygons,'use_smooth',1,'b'),'uv':{u.name:coordinates(u.data,'uv',2) for u in me.uv_layers},'attributes':attrs,'materials':[m.name if m else None for m in me.materials],
  'shape_keys':{'keys':[{'name':k.name,'co':coordinates(k.data,'co',3),'value':k.value,'slider_min':k.slider_min,'slider_max':k.slider_max,'relative_key':k.relative_key.name} for k in me.shape_keys.key_blocks],'animation':animation(me.shape_keys)} if me.shape_keys else None}

def object_record(o):
 r={'type':o.type,'data':o.data.name if o.data else None,'properties':primitives(o,{'active_material','active_material_index'}),'matrix_basis':[list(v) for v in o.matrix_basis],'matrix_parent_inverse':[list(v) for v in o.matrix_parent_inverse],'animation':animation(o,o.name==RIG),'constraints':[primitives(c) for c in o.constraints],'modifiers':[{'type':m.type,'properties':primitives(m)} for m in o.modifiers],'collections':sorted(c.name for c in o.users_collection),'custom_properties':{k:simple(o[k]) for k in o.keys() if k!='_RNA_UI' and not(o.name==RIG and k=='v6_reach_layer')}}
 if o.type=='ARMATURE':
  r['bones']={b.name:{'matrix':[list(v) for v in b.matrix_local],'properties':primitives(b),'parent':b.parent.name if b.parent else None} for b in o.data.bones}
  r['pose_constraints']={b.name:[primitives(c) for c in b.constraints] for b in o.pose.bones}
 elif o.type=='MESH':r['weights_sha256']=digest([[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]);r['vertex_groups']=[g.name for g in o.vertex_groups]
 elif o.type in {'CAMERA','LIGHT'}:r['data_properties']=primitives(o.data);r['data_animation']=animation(o.data);r['nodes']=nodes(getattr(o.data,'node_tree',None));r['dof']=primitives(o.data.dof) if o.type=='CAMERA' else None
 elif o.type=='CURVE':r['curve']={'properties':primitives(o.data),'splines':[{'properties':primitives(sp),'points':[list(p.co) for p in sp.points],'bezier':[{'co':list(p.co),'left':list(p.handle_left),'right':list(p.handle_right)} for p in sp.bezier_points]} for sp in o.data.splines]}
 return r

def render_settings(s):
 return {'render':primitives(s.render,{'filepath'}),'image':primitives(s.render.image_settings),'ffmpeg':primitives(s.render.ffmpeg),'cycles':primitives(s.cycles),'view':primitives(s.view_settings),'display':primitives(s.display_settings),'units':primitives(s.unit_settings),'frame_range':[s.frame_start,s.frame_end,s.frame_step],'time_remapping':[s.render.frame_map_old,s.render.frame_map_new],'world':{'name':s.world.name,'properties':primitives(s.world),'nodes':nodes(s.world.node_tree),'animation':animation(s.world),'cycles':primitives(s.world.cycles)},'compositor':nodes(s.node_tree),'view_layers':{v.name:{'properties':primitives(v),'cycles':primitives(v.cycles)} for v in s.view_layers}}

def image_records():
 records={};errors=[]
 for im in bpy.data.images:
  if im.source not in ('FILE','TILED'):continue
  packed=bool(im.packed_file or len(im.packed_files));p=Path(bpy.path.abspath(im.filepath)) if im.filepath else None
  relative=None
  if p:
   try:relative=p.resolve().relative_to(ROOT).as_posix()
   except ValueError:errors.append('Image path outside project: '+im.name)
  if not packed and (not p or not p.is_file()):errors.append('Missing image: '+im.name)
  if im.filepath and not im.filepath.startswith('//'):errors.append('Image path is not Blender-relative: '+im.name)
  packed_hashes=[hashlib.sha256(bytes(pf.packed_file.data)).hexdigest() for pf in im.packed_files] if len(im.packed_files) else ([hashlib.sha256(bytes(im.packed_file.data)).hexdigest()] if im.packed_file else [])
  records[im.name]={'path':relative,'packed':packed,'packed_sha256':packed_hashes,'file_sha256':sha(p) if p and p.is_file() else None,'dimensions':list(im.size),'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode}
 for lib in bpy.data.libraries:
  p=Path(bpy.path.abspath(lib.filepath))
  if not lib.filepath.startswith('//') or not p.is_file():errors.append('Invalid linked library: '+lib.name)
  try:p.resolve().relative_to(ROOT)
  except ValueError:errors.append('External linked library: '+lib.name)
 return records,errors

def static_snapshot():
 s=bpy.context.scene;s.frame_set(1)
 images,image_errors=image_records()
 return {'objects':{o.name:object_record(o) for o in bpy.data.objects},'meshes':{m.name:mesh_record(m) for m in bpy.data.meshes},'materials':{m.name:{'properties':primitives(m),'nodes':nodes(m.node_tree),'animation':animation(m)} for m in bpy.data.materials},'node_groups':{n.name:nodes(n) for n in bpy.data.node_groups},'settings':render_settings(s),'images':images,'dependency_errors':image_errors,'markers':[{'frame':m.frame,'name':m.name,'camera':m.camera.name if m.camera else None} for m in sorted(s.timeline_markers,key=lambda m:(m.frame,m.name))],'embedded_texts':[t.name for t in bpy.data.texts]}

def sample_time(scene,time):scene.frame_set(int(time),subframe=time%1)
def matrix_values(m):return [float(x) for row in m for x in row]

def evaluated_snapshot():
 s=bpy.context.scene;rig=bpy.data.objects[RIG];early=list(range(1,360))+[359.5];early_set=set(early);all_times=list(range(1,577))+[359.5]
 feet=[b.name for b in rig.pose.bones if b.name=='Bip01 Pelvis' or any(x in b.name for x in (' Thigh',' Calf',' Foot',' Toe'))]
 body={};legs={};cameras={};root={};early_curves={};reach={};curves=list(rig.animation_data.action.fcurves)
 for time in all_times:
  sample_time(s,time);key=str(time);rw=rig.matrix_world.copy()
  legs[key]={n:matrix_values(rw@rig.pose.bones[n].matrix) for n in feet}
  root[key]=matrix_values(bpy.data.objects['Heroine v4 • native root motion'].matrix_world)
  if time>=360:
   reach[key]={n:{'position':list((rw@rig.pose.bones[n].matrix).translation),'quaternion':list((rw@rig.pose.bones[n].matrix).to_quaternion())} for n in rig.pose.bones.keys() if allowed_bone(n)}
  if time in early_set:
   body[key]={b.name:matrix_values(rw@b.matrix) for b in rig.pose.bones}
   early_curves[key]={fc.data_path+':'+str(fc.array_index):fc.evaluate(time) for fc in curves}
   cam=s.camera;d=cam.data;focus=d.dof.focus_object
   cameras[key]={'name':cam.name,'matrix':matrix_values(cam.matrix_world),'data':primitives(d),'dof':primitives(d.dof),'focus_matrix':matrix_values(focus.matrix_world) if focus else None}
 return {'all_bones_early':body,'legs_all_frames':legs,'root_all_frames':root,'cameras_early':cameras,'rig_curves_early':early_curves,'reach_samples':reach,'feet_bones':feet,'early_sample_count':len(early),'full_sample_count':len(all_times)}

def numeric_comparison(old,new,tolerance):
 maximum=0.;path=None;count=0;missing=[]
 def walk(a,b,p):
  nonlocal maximum,path,count
  if isinstance(a,dict) and isinstance(b,dict):
   if a.keys()!=b.keys():missing.append(p+' keys differ')
   for k in a.keys()&b.keys():walk(a[k],b[k],p+'/'+str(k))
  elif isinstance(a,list) and isinstance(b,list):
   if len(a)!=len(b):missing.append(p+' lengths differ')
   for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+'/'+str(i))
  elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
   count+=1;delta=abs(a-b)
   if delta>maximum:maximum=delta;path=p
  elif a!=b:missing.append(p+' differs')
 walk(old,new,'')
 return {'passed':not missing and maximum<=tolerance,'maximum_absolute_difference':maximum,'maximum_difference_path':path,'tolerance':tolerance,'numeric_values_compared':count,'structural_differences':missing[:30],'baseline_sha256':digest(old),'candidate_sha256':digest(new)}

def mapping_comparison(old,new):
 changed=sorted(k for k in old.keys()&new.keys() if old[k]!=new[k]);missing=sorted(old.keys()-new.keys());added=sorted(new.keys()-old.keys())
 return {'passed':not(changed or missing or added),'baseline_count':len(old),'candidate_count':len(new),'changed':changed,'missing':missing,'added':added,'changed_fields':{k:[x for x in old[k].keys()|new[k].keys() if old[k].get(x)!=new[k].get(x)] for k in changed if isinstance(old[k],dict) and isinstance(new[k],dict)},'baseline_sha256':digest(old),'candidate_sha256':digest(new)}

def main():
 out=ROOT/'renders/v6';out.mkdir(parents=True,exist_ok=True);source=ROOT/'observatory-v5.blend';candidate=ROOT/'observatory-v6.blend';report={'source_scene':source.name,'candidate_scene':candidate.name,'status':'failed','errors':[]};errors=report['errors']
 try:
  report.update(source_sha256=sha(source),candidate_sha256=sha(candidate))
  bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);baseline=static_snapshot();base_eval=evaluated_snapshot()
  bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);revised=static_snapshot();new_eval=evaluated_snapshot()
  added={n:r['type'] for n,r in revised['objects'].items() if n not in baseline['objects']};report['new_objects']={'expected':ADDED_OBJECTS,'actual':added,'passed':added==ADDED_OBJECTS}
  if added!=ADDED_OBJECTS:errors.append('Only the expected reach camera and focus empty may be added')
  preserved_objects={n:r for n,r in revised['objects'].items() if n not in ADDED_OBJECTS}
  checks={'objects_except_allowed_reach_curves':mapping_comparison(baseline['objects'],preserved_objects)}
  for key in ('meshes','materials','node_groups','images'):checks[key]=mapping_comparison(baseline[key],revised[key])
  checks['render_world_compositor_settings']={'passed':baseline['settings']==revised['settings'],'baseline_sha256':digest(baseline['settings']),'candidate_sha256':digest(revised['settings']),'changed_sections':[k for k in baseline['settings'] if baseline['settings'][k]!=revised['settings'][k]]}
  for key in ('all_bones_early','legs_all_frames','root_all_frames','cameras_early','rig_curves_early'):
   checks[key]=numeric_comparison(base_eval[key],new_eval[key],CURVE_TOLERANCE if key=='rig_curves_early' else WORLD_MATRIX_TOLERANCE)
  expected_markers=baseline['markers']+[{'frame':385,'name':NEW_CAMERA,'camera':NEW_CAMERA}];expected_markers.sort(key=lambda m:(m['frame'],m['name']))
  checks['camera_cut_schedule']={'passed':revised['markers']==expected_markers,'baseline':baseline['markers'],'candidate':revised['markers']}
  for name,check in checks.items():
   if not check['passed']:errors.append('Failed preservation check: '+name)
  errors.extend(revised['dependency_errors'])
  if revised['embedded_texts']:errors.append('Candidate has embedded Python/text datablocks')
  if sha(source)!=report['source_sha256'] or sha(candidate)!=report['candidate_sha256']:errors.append('A saved scene changed during the read-only audit')
  reach_diagnostics={'maximum_adjacent_quaternion_degrees':0.,'maximum_adjacent_quaternion_bone':None,'maximum_adjacent_quaternion_frame':None,'maximum_adjacent_wrist_displacement_m':0.,'maximum_wrist_change_vs_baseline_m':0.}
  for f in range(360,577):
   current=new_eval['reach_samples'][str(f)];old=base_eval['reach_samples'][str(f)]
   distance=(Vector(current['Bip01 R Hand']['position'])-Vector(old['Bip01 R Hand']['position'])).length
   reach_diagnostics['maximum_wrist_change_vs_baseline_m']=max(distance,reach_diagnostics['maximum_wrist_change_vs_baseline_m'])
   if f==360:continue
   previous=new_eval['reach_samples'][str(f-1)]
   wrist_step=(Vector(current['Bip01 R Hand']['position'])-Vector(previous['Bip01 R Hand']['position'])).length
   reach_diagnostics['maximum_adjacent_wrist_displacement_m']=max(wrist_step,reach_diagnostics['maximum_adjacent_wrist_displacement_m'])
   for bone in current:
    delta=Quaternion(current[bone]['quaternion']).rotation_difference(Quaternion(previous[bone]['quaternion'])).angle
    degrees=math.degrees(min(delta,2*math.pi-delta))
    if degrees>reach_diagnostics['maximum_adjacent_quaternion_degrees']:reach_diagnostics.update(maximum_adjacent_quaternion_degrees=degrees,maximum_adjacent_quaternion_bone=bone,maximum_adjacent_quaternion_frame=f)
  reach_diagnostics['notes']='Continuity guardrails only; these numbers do not establish natural acting. Quaternion deltas are measured in world space.'
  reach_diagnostics['passed']=reach_diagnostics['maximum_adjacent_quaternion_degrees']<30 and reach_diagnostics['maximum_adjacent_wrist_displacement_m']<.2 and reach_diagnostics['maximum_wrist_change_vs_baseline_m']>.1
  if not reach_diagnostics['passed']:errors.append('Reach movement missing or continuity guardrail failed')
  report['reach_motion_diagnostics']=reach_diagnostics
  changed_bones=sorted({BONE_PATH.match(fc.data_path)[1] for fc in bpy.data.objects[RIG].animation_data.action.fcurves if allowed_curve(fc.data_path)})
  report.update(checks=checks,allowed_bones=changed_bones,allowed_channels=['rotation_quaternion'],early_reuse={'frames':[1,359],'additional_motion_blur_sample':359.5,'all_rig_bones':len(bpy.data.objects[RIG].pose.bones),'early_samples':base_eval['early_sample_count'],'full_root_and_leg_samples':base_eval['full_sample_count'],'safe':all(checks[k]['passed'] for k in checks) and not errors},images=revised['images'],dependency_errors=revised['dependency_errors'],embedded_texts=revised['embedded_texts'])
  report['non_rendering_reach_metadata']=bpy.data.objects[RIG].get('v6_reach_layer')
  report['status']='passed' if not errors else 'failed'
 except Exception as exc:
  errors.append(type(exc).__name__+': '+str(exc))
 finally:
  (out/'scene-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('V6_SCENE_AUDIT',report['status'],errors)
 if errors:raise RuntimeError('; '.join(errors))

if __name__=='__main__':main()
