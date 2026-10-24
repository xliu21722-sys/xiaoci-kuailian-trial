/* Two inputs: microphone and the app's AI playback. Only mic PCM goes to ASR. */
class CaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super(); this.active=true; this.phase=0; this.sumMic=0; this.sumPartner=0; this.count=0;
    this.mic=[]; this.mixed=[]; this.level=0;
    this.port.onmessage=event=>{
      if(event.data?.type==='stop') { this.flush(); this.active=false;this.port.postMessage({type:'stopped'}); }
    };
  }
  flush() {
    if (!this.mic.length) return;
    const mic=new Int16Array(this.mic), mixed=new Int16Array(this.mixed);
    this.port.postMessage({type:'pcm',mic:mic.buffer,mixed:mixed.buffer,level:this.level},[mic.buffer,mixed.buffer]);
    this.mic=[]; this.mixed=[];this.level=0;
  }
  process(inputs,outputs) {
    for(const channel of (outputs[0] || [])) channel.fill(0);
    if(!this.active) return false;
    const a=inputs[0]?.[0],b=inputs[1]?.[0];
    const length=a?.length || b?.length || outputs[0]?.[0]?.length || 128;
    for(let i=0;i<length;i++) {
      const m=a?.[i] || 0,p=b?.[i] || 0;
      this.sumMic+=m;this.sumPartner+=p;this.count++;this.phase+=16000;
      this.level=Math.max(this.level,Math.abs(m));
      if(this.phase>=sampleRate) {
        const mic=this.sumMic/this.count, partner=this.sumPartner/this.count;
        this.mic.push(Math.round(Math.max(-1,Math.min(1,mic))*32767));
        this.mixed.push(Math.round(Math.max(-1,Math.min(1,0.72*(mic+partner)))*32767));
        this.phase-=sampleRate;this.sumMic=0;this.sumPartner=0;this.count=0;
        if(this.mic.length>=1600) this.flush();
      }
    }
    return true;
  }
}
registerProcessor('duici-capture',CaptureProcessor);
