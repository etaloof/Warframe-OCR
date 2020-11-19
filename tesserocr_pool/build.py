import os


def set_env(name, value):
    print('\tset ', name, '=', value, sep='')
    os.putenv(name, value)


print('Installing tools')
os.system('pip install maturin pytest pytest-benchmark')

print('Installing dependencies')
if 'vcpkg' not in os.listdir():
    os.system('git clone https://github.com/microsoft/vcpkg')
    os.system('.\\vcpkg\\bootstrap-vcpkg.bat')
    os.system('.\\vcpkg\\vcpkg install tesseract:x64-windows-static leptonica:x64-windows-static')

print('Setting up environment')
set_env('VCPKG_ROOT', os.path.abspath('vcpkg'))
set_env('CARGO_TARGET_DIR', 'target')
set_env('RUSTFLAGS', '-Ctarget-feature=+crt-static')

print('Building rust extension')
os.system('maturin develop --release')
#os.system('maturin develop')
