"""Read GLB geometry and embedded-image metadata without importing a renderer."""
import argparse, json, struct, io
from pathlib import Path
def inspect(path):
 raw=Path(path).read_bytes();magic,version,size=struct.unpack_from('<4sII',raw)
 assert magic==b'glTF' and version==2 and size==len(raw)
 offset=12;document=None;binary=None
 while offset<len(raw):
  length,kind=struct.unpack_from('<II',raw,offset);offset+=8;chunk=raw[offset:offset+length];offset+=length
  if kind==0x4e4f534a:document=json.loads(chunk)
  elif kind==0x004e4942:binary=chunk
 vertices=triangles=0
 for mesh in document.get('meshes',[]):
  for p in mesh['primitives']:
   count=document['accessors'][p['attributes']['POSITION']]['count'];vertices+=count
   if p.get('mode',4)==4:triangles+=(document['accessors'][p['indices']]['count'] if 'indices' in p else count)//3
 images=[]
 try:
  from PIL import Image
  for image in document.get('images',[]):
   result={'name':image.get('name'),'mimeType':image.get('mimeType')}
   if 'bufferView' in image and binary:
    view=document['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
    with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as im:result.update(size=list(im.size),mode=im.mode)
   images.append(result)
 except ImportError:pass
 return {'file':str(path),'bytes':len(raw),'vertices':vertices,'triangles':triangles,'meshes':len(document.get('meshes',[])), 'skins':len(document.get('skins',[])), 'animations':[a.get('name') for a in document.get('animations',[])], 'images':images}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('file');a=p.parse_args();print(json.dumps(inspect(a.file),indent=2))
