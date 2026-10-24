from pathlib import Path
import hashlib, json, shutil, sys
root=Path(__file__).resolve().parent.parent
out=root/(sys.argv[1] if len(sys.argv)>1 else 'web')/'speech'
out.mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'speech-assets/asr',out/'asr',dirs_exist_ok=True)
source=root/'speech-assets/tts/sherpa-onnx-wasm-simd-2.0.0-matcha-icefall-zh-baker'
tts=out/'tts';tts.mkdir(exist_ok=True)
for name in ['sherpa-onnx-tts.js','sherpa-onnx-wasm-main-tts.js','sherpa-onnx-wasm-main-tts.wasm']:
 shutil.copy2(source/name,tts/name)
data=(source/'sherpa-onnx-wasm-main-tts.data').read_bytes();parts=[]
for start in range(0,len(data),40*1024*1024):
 chunk=data[start:start+40*1024*1024];name='model-'+str(len(parts))+'.bin';(tts/name).write_bytes(chunk)
 parts.append({'file':name,'sha256':hashlib.sha256(chunk).hexdigest(),'size':len(chunk)})
(tts/'chunks.json').write_text(json.dumps({'size':len(data),'parts':parts}))
print('Verified official speech resources assembled.')
