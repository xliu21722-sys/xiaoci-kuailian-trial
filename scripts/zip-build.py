from pathlib import Path
import hashlib, subprocess, sys, zipfile
platform,arch=sys.argv[1:3]
root=Path('runtime/build-trial')/('小词快练-'+platform+'-'+arch)
out=Path('release');out.mkdir(exist_ok=True)
name='Xiaoci-'+('Mac' if platform=='darwin' else 'Windows')+'-'+arch+'-0.4.0.zip'
target=out/name
if platform=='darwin':
 subprocess.run(['/usr/bin/ditto','-c','-k','--sequesterRsrc','--keepParent',str(root),str(target)],check=True)
else:
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(root.parent))
with zipfile.ZipFile(target) as z:
 if z.testzip():raise SystemExit('Invalid release ZIP')
checksum=hashlib.sha256(target.read_bytes()).hexdigest()
(out/(name+'.sha256')).write_text(checksum+'  '+name+'\n')
print(name,target.stat().st_size,checksum)
