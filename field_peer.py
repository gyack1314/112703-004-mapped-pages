"""现场原始输入和 Linux 接口探测。"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import mmap
import os
import struct
import subprocess
import sys
import zlib


def make_frame(text):
    data = text.encode('utf-8')
    return struct.pack('!I', len(data)) + data + struct.pack('!I', zlib.crc32(data))


def device(args):
    fd, offset, length = map(int, args)
    fd = int(fd)
    with mmap.mmap(fd, 0, access=mmap.ACCESS_READ) as region:
        print(region[offset:offset + length].hex(), flush=True)


def probe(scene, directory):
    page = os.sysconf('SC_PAGE_SIZE')
    offset = page - 6
    record = make_frame(scene['records']['r1'])
    fd = os.memfd_create('observation-pages', os.MFD_CLOEXEC)
    try:
        os.ftruncate(fd, page * 2)
        with mmap.mmap(fd, 0) as region:
            region[offset:offset + 10] = record[:10]
            command = [sys.executable, __file__, 'device', str(fd), str(offset), str(len(record))]
            read = lambda: bytes.fromhex(subprocess.check_output(command, text=True,
                                       pass_fds=(fd,), timeout=3).strip())
            assert read() == record[:10].ljust(len(record), b'\0')
            region[offset:offset + len(record)] = record
            assert read() == record
    finally:
        os.close(fd)
    return {'观测': '独立进程映射读取真实跨页字节', '页大小': page, '记录字节': len(record)}


def load_scene():
    return json.loads(Path(__file__).with_name('field-session.json').read_text(encoding='utf-8'))


def main():
    if sys.argv[1:2] == ['device']:
        device(sys.argv[2:])
        return
    if sys.argv[1:] != ['--probe']:
        raise SystemExit('使用方式：python field_peer.py --probe 或 device [参数]')
    with TemporaryDirectory(prefix='obs-') as scratch:
        print(json.dumps(probe(load_scene(), Path(scratch)), ensure_ascii=False))


if __name__ == '__main__':
    main()
