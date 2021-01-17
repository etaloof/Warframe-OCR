import os
import platform
import sys


def set_env(name, value):
    print('\tset ', name, '=', value, sep='')
    os.putenv(name, value)


print('Installing tools')
os.system('pip install maturin pytest pytest-benchmark pytest-benchmark[histogram]')

print('Installing dependencies')
platform_name = platform.system()
if platform_name == 'Windows':
    if 'vcpkg' not in os.listdir():
        os.system('git clone https://github.com/microsoft/vcpkg')
        os.system('.\\vcpkg\\bootstrap-vcpkg.bat')
        os.system('.\\vcpkg\\vcpkg install tesseract:x64-windows-static leptonica:x64-windows-static')
elif platform_name == 'Linux':
    os.system('sudo -A apt install libleptonica-dev libtesseract-dev clang')
    os.system('sudo -A pacman --noconfirm tesseract tesseract-data-eng leptonica clang')
else:
    print('Unsupported platform', platform_name, file=sys.stderr)
    exit(1)

print('Setting up environment')
set_env('VCPKG_ROOT', os.path.abspath('vcpkg'))
set_env('CARGO_TARGET_DIR', 'target')
if platform_name == 'Linux':
    # compile with '+crt-static' once https://github.com/rust-lang/rust/issues/78210 is fixed (broken as of rustc 1.49)
    set_env('RUSTFLAGS', '-Ctarget-feature=-crt-static')
else:
    set_env('RUSTFLAGS', '-Ctarget-feature=+crt-static')

print('Building rust extension')
os.system('pip uninstall -y tesserocr_pool')
os.system('rm -rdf tesserocr_pool')
os.system('maturin develop --release')
#os.system('maturin develop')
