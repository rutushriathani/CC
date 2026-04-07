import os
import tarfile
import hashlib
import glob
import json

def get_state_dir():
    return os.path.expanduser('~/.docksmith')

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def parse_docksmithfile(path):
    steps = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            instr, *rest = line.split(' ', 1)
            arg = rest[0] if rest else ''
            steps.append({'instr': instr, 'arg': arg, 'raw': line, 'line': i})
    return steps

def compute_file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def compute_layer_digest(tar_path):
    h = hashlib.sha256()
    with open(tar_path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return 'sha256:' + h.hexdigest()

def zero_tarinfo(tarinfo):
    tarinfo.mtime = 0
    tarinfo.uid = 0
    tarinfo.gid = 0
    tarinfo.uname = ''
    tarinfo.gname = ''
    return tarinfo

def sorted_tar_add(context_dir, src_glob):
    # Returns sorted list of absolute paths matching glob
    matches = glob.glob(os.path.join(context_dir, src_glob), recursive=True)
    return sorted(matches)
