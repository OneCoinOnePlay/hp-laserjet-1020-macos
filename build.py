#!/usr/bin/env python3
"""Build and validate the HP 1020 arm64 driver and macOS installer.

GPL-2.0-or-later. Requires macOS, Python 3 and Xcode Command Line Tools.
"""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.1'


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def write_test_pdf(path):
    text = b'BT /F1 24 Tf 72 740 Td (HP LaserJet 1020 - driver validation) Tj ET\n'
    objects = [
        b'<</Type /Catalog /Pages 2 0 R>>',
        b'<</Type /Pages /Kids [3 0 R] /Count 1>>',
        b'<</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources <</Font <</F1 4 0 R>>>> /Contents 5 0 R>>',
        b'<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>',
        b'<</Length ' + str(len(text)).encode() + b'>>\nstream\n' + text + b'endstream',
    ]
    data = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(data)
    data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<</Size {len(offsets)} /Root 1 0 R>>\nstartxref\n{xref}\n%%EOF\n'.encode())
    path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, help='Use a specific macOS SDK directory')
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        parser.error('Build on an Apple silicon Mac.')
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    src = ROOT / 'src'
    compiler = ['clang', '-arch', 'arm64', '-mmacosx-version-min=13.0', '-Wall', '-O2', f'-I{src}']
    sources = [src / 'rastertozjs.c', src / 'jbig.c', src / 'jbig_ar.c', '-lcups', '-lcupsimage']
    sdk = args.sdk or Path(subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip())
    compile_args = compiler + ['-isysroot', str(sdk)]
    run(compile_args + ['-o', build / 'rastertozjs'] + sources)
    run(compile_args + ['-o', build / 'arm2hpdl', src / 'arm2hpdl.c'])
    firmware = build / 'sihp1020.dl'
    with firmware.open('wb') as output:
        run([build / 'arm2hpdl', src / 'sihp1020.img'], stdout=output)
    run(compile_args + [f'-DHP1020_FIRMWARE_PATH="{firmware}"', '-o', build / 'rastertozjs-validation'] + sources)
    pdf = build / 'test-page.pdf'
    raster = build / 'test.raster'
    output_file = build / 'test.zjs'
    write_test_pdf(pdf)
    env = os.environ.copy()
    env['PPD'] = str(ROOT / 'ppd/HP-LaserJet-1020-Apple-Silicon.ppd')
    with raster.open('wb') as output:
        run(['/usr/libexec/cups/filter/cgpdftoraster', '1', 'validation', 'HP 1020 validation', '1', 'PageSize=A4 Resolution=600dpi', pdf], env=env, stdout=output)
    with output_file.open('wb') as output:
        run([build / 'rastertozjs-validation', '1', 'validation', 'HP 1020 validation', '1', 'PageSize=A4', raster], stdout=output)
    data = output_file.read_bytes()
    firmware_data = firmware.read_bytes()
    if not data.startswith(firmware_data) or len(data) < len(firmware_data) + 2000:
        raise RuntimeError('Driver did not emit firmware and page data.')
    position = data.index(b'JZJZ', len(firmware_data)) + 4
    chunks = []
    while data[position:position + 1] != b'\x1b':
        size, kind, items, reserved, signature = struct.unpack_from('>IIIHH', data, position)
        if signature != 0x5a5a or size < 16 or position + size > len(data):
            raise RuntimeError('Invalid ZjStream chunk.')
        chunks.append(kind)
        position += size
    if chunks[0] != 0 or chunks[-1] != 1 or chunks.count(2) != 1 or chunks.count(3) != 1:
        raise RuntimeError('Expected one complete ZjStream page.')
    print(f'Validation passed: firmware and one 600 dpi page, {len(chunks)} ZjStream chunks.')
    run(['codesign', '--force', '--sign', '-', build / 'rastertozjs'])
    package_root = build / 'pkgroot'
    driver = package_root / 'Library/Printers/HP1020'
    ppds = package_root / 'Library/Printers/PPDs/Contents/Resources'
    driver.mkdir(parents=True, exist_ok=True)
    ppds.mkdir(parents=True, exist_ok=True)
    for origin in [build / 'rastertozjs', firmware, ROOT / 'LICENSE', src / 'COPYING', ROOT / 'THIRD_PARTY.md']:
        shutil.copyfile(origin, driver / origin.name)
    shutil.copyfile(ROOT / 'scripts/setup-printer.sh', driver / 'setup-printer.sh')
    shutil.copyfile(ROOT / 'ppd/HP-LaserJet-1020-Apple-Silicon.ppd', ppds / 'HP-LaserJet-1020-Apple-Silicon.ppd')
    for file in package_root.rglob('*'):
        file.chmod(0o755 if file.is_dir() or file.name in ('rastertozjs', 'setup-printer.sh') else 0o644)
    package_scripts = build / 'package-scripts'
    package_scripts.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'scripts/postinstall', package_scripts / 'postinstall')
    (package_scripts / 'postinstall').chmod(0o755)
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    package = dist / 'HP-LaserJet-1020-Apple-Silicon.pkg'
    run(['pkgbuild', '--root', package_root, '--scripts', package_scripts, '--identifier', 'local.hp1020.arm64.driver', '--version', VERSION, '--install-location', '/', '--ownership', 'recommended', package])
    checksum = hashlib.sha256(package.read_bytes()).hexdigest()
    (dist / (package.name + '.sha256')).write_text(f'{checksum}  {package.name}\n')
    print(f'Created {package}')


if __name__ == '__main__':
    main()
