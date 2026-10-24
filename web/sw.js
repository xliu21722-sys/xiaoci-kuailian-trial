const CACHE='xiaoci-0.4.0-5-149f732ef4f5fcf8';
const shell=['./','./index.html','./app.js?v=149f732ef4f5fcf8','./styles.css?v=149f732ef4f5fcf8','./assets/logo.png','./capture-worklet.js','./tts-worker.js','./vosk-worker.js','./help.html'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(c=>c.addAll(shell)));});
// Activate at the next normal visit. Never reload or replace a worker mid-rehearsal.
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('xiaoci-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);
  // Never cache API calls, keys, microphone data, user files or recordings.
  if(event.request.method!=='GET'||url.origin!==self.location.origin)return;
  event.respondWith((async()=>{
    const cached=await caches.match(event.request);
    // HTML needs current navigation and notices. Keep audio/model assets cached,
    // keep open rehearsals untouched, and fall back to HTML cache when offline.
    if(event.request.mode==='navigate') {
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
      try {
        const response=await fetch(event.request,{cache:'no-cache',signal:controller.signal});
        if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(event.request,copy)).catch(()=>{}));return response;}
        return cached || response;
      } catch(error) {if(cached)return cached;throw error;}
      finally {clearTimeout(timer);}
    }
    if(cached)return cached;
    const response=await fetch(event.request);
    if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(event.request,copy)).catch(()=>{}));}
    return response;
  })());
});
