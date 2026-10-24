// The model and runtime are same-origin static assets. No speech leaves this worker.
let tts;
async function boot(){
  const base=new URL('./speech/tts/',self.location.href);
  const manifest=await fetch(new URL('chunks.json',base)).then(r=>{if(!r.ok)throw Error('model');return r.json();});
  const data=new Uint8Array(manifest.size);let offset=0;
  for(const part of manifest.parts){
    const response=await fetch(new URL(part.file,base));if(!response.ok)throw Error('download');
    const buffer=await response.arrayBuffer();
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buffer)),b=>b.toString(16).padStart(2,'0')).join('');
    if(hash!==part.sha256)throw Error('integrity');
    data.set(new Uint8Array(buffer),offset);offset+=buffer.byteLength;
    postMessage({type:'progress',message:`准备离线声音 ${Math.round(offset/manifest.size*100)}%…`});
  }
  self.Module={locateFile:path=>new URL(path,base).href,getPreloadedPackage:()=>data.buffer,
    print:()=>{},printErr:()=>{},onAbort:()=>postMessage({type:'error'}),
    onRuntimeInitialized(){try{tts=createOfflineTts(self.Module);postMessage({type:'ready'});}catch{postMessage({type:'error'});}}
  };
  importScripts(new URL('sherpa-onnx-tts.js',base).href);
  importScripts(new URL('sherpa-onnx-wasm-main-tts.js',base).href);
}
self.onmessage=({data:m})=>{
  if(m.type!=='generate'||!tts)return;
  try{
    const audio=tts.generate({text:m.text,sid:0,speed:m.speed || 1});
    if(!audio.samples?.length)throw Error('empty');
    postMessage({type:'audio',id:m.id,samples:audio.samples,sampleRate:tts.sampleRate},[audio.samples.buffer]);
  }catch{postMessage({type:'error',id:m.id});}
};
boot().catch(()=>postMessage({type:'error'}));
