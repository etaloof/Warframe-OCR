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

    if 'clang' not in os.listdir():
        os.system('mkdir clang')
        os.system('cd clang && curl -o llvm.exe https://prereleases.llvm.org/win-snapshots/LLVM-12.0.0-6923b0a7-win64.exe')
        os.system('cd clang && curl -Lo 7za.zip https://www.7-zip.org/a/7za920.zip')
        os.system('cd clang && curl -Lo 7z-installer.exe https://www.7-zip.org/a/7z1900-x64.exe')

        import zipfile
        with zipfile.ZipFile('clang/7za.zip') as f:
            f.extract('7za.exe', 'clang')

        os.system('cd clang && 7za e 7z-installer.exe 7z.exe')
        os.system('cd clang && 7z e llvm.exe bin/libclang.dll')
    set_env('LIBCLANG_PATH', os.path.abspath('clang'))
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
