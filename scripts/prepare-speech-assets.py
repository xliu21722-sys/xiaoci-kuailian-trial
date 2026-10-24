"""Download pinned official, freely distributable speech assets for a build.

No API keys, recordings or scripts are read. Archives are hash-checked before
extraction. The explicit directories in Vosk's tar are required by its WASM FS.
"""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import shutil
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent / 'speech-assets'
SOURCES = [
 ('vosk-cn.zip', 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
  '3af8b0e7e0f835ae9d414ce5df580237a3cfb08d586c9fbbb0f7ff29ad5b14ba'),
 ('tts-zh.tar.bz2', 'https://github.com/k2-fsa/sherpa-onnx/releases/download/v2.0.0/sherpa-onnx-wasm-simd-2.0.0-matcha-icefall-zh-baker.tar.bz2',
  'aaddc15072e1c60b47a0481b5425e50ddaba2427e9acc21deafa5efce0a18e96'),
]
downloads = ROOT / 'downloads'
downloads.mkdir(parents=True, exist_ok=True)
for name, url, expected in SOURCES:
    target = downloads / name
    if not target.exists():
        temporary = target.with_suffix('.part')
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as out:
            shutil.copyfileobj(response, out)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
            raise SystemExit('Downloaded asset checksum mismatch: ' + name)
        temporary.replace(target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise SystemExit('Existing asset checksum mismatch: ' + name)
    print('Verified:', name)

(ROOT / 'asr').mkdir(exist_ok=True)
with zipfile.ZipFile(downloads / SOURCES[0][0]) as source:
    if source.testzip():
        raise SystemExit('Invalid model ZIP')
    entries = []
    for member in source.infolist():
        parts = PurePosixPath(member.filename).parts
        if not parts or '..' in parts or member.filename.startswith('/'):
            raise SystemExit('Unsafe ZIP entry')
        entries.append((member, PurePosixPath('model', *parts[1:]).as_posix()))
    with (ROOT / 'asr/model.tar.gz').open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as archive:
        for member, name in entries:
            info = tarfile.TarInfo(name)
            info.mode = 0o755 if member.is_dir() else 0o644
            if member.is_dir():
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            else:
                data = source.read(member)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))

destination = ROOT / 'tts'
destination.mkdir(exist_ok=True)
with tarfile.open(downloads / SOURCES[1][0]) as archive:
    # Reject links, devices and traversal rather than relying on Python defaults.
    for member in archive:
        path = destination / member.name
        if not path.resolve().is_relative_to(destination.resolve()):
            raise SystemExit('Unsafe TAR path')
        if member.isdir():
            path.mkdir(parents=True, exist_ok=True)
        elif member.isfile():
            path.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, path.open('wb') as out:
                shutil.copyfileobj(source, out)
        else:
            raise SystemExit('Unexpected TAR entry type')
print('Ready: speech-assets (no user audio included).')
