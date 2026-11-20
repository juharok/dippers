# names.json의 fog.open 원만 걷히고, 나머지 땅을 안개로 덮는 그림(fog.png, 1024px)을 만든다.
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage
ext,names,out=sys.argv[1],sys.argv[2],sys.argv[3]
G=1024;S=8188
land=np.load(ext)['land']; land=ndimage.zoom(land.astype(np.float32),G/land.shape[0],order=1)>0.5
d=json.load(open(names))
yy,xx=np.mgrid[:G,:G].astype(np.float32)
openm=np.zeros((G,G),np.float32)
for o in d['fog']['open']:
    cx,cy,r=o['x']*G/S,o['y']*G/S,o['r']*G/S
    dd=np.sqrt((xx-cx)**2+(yy-cy)**2)
    openm=np.maximum(openm,np.clip((r-dd)/(r*0.35),0,1))
cover=ndimage.gaussian_filter(ndimage.binary_dilation(land,iterations=10).astype(np.float32),6)
rng=np.random.default_rng(3)
def fbm(o):
    a=np.zeros((G,G),np.float32)
    for sc,amp in o: a+=ndimage.zoom(rng.standard_normal((G//sc+3,G//sc+3)).astype(np.float32),sc,order=3)[:G,:G]*amp
    return a
cl=fbm([(128,1),(48,.6),(16,.3),(6,.15)]);cl=(cl-cl.min())/(cl.max()-cl.min())
alpha=np.clip(cover*(1-openm)*(0.72+0.28*cl),0,0.93)
col=np.zeros((G,G,4),np.uint8)
tone=(236+12*(cl-0.5)).clip(0,255)
col[...,0]=tone;col[...,1]=(tone-6).clip(0,255);col[...,2]=(tone-22).clip(0,255);col[...,3]=(alpha*255).astype(np.uint8)
Image.fromarray(col,'RGBA').save(out,optimize=True)
print('fog',out)
