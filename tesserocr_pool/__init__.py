import pathlib
from importlib.machinery import ExtensionFileLoader
from importlib.util import spec_from_loader, module_from_spec


def import_extension_module(module_name: str, path_to_extension_module: str):
    # you don't want to know how long it took me to get this right
    loader = ExtensionFileLoader(module_name, path_to_extension_module)
    spec = spec_from_loader(module_name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


path_base = pathlib.Path(__file__).parent.joinpath('target/release/')

name = 'tesserocr_pool'
path = path_base.joinpath(name).with_suffix('.dll')


tesserocr_pool = import_extension_module(name, str(path))
__all__ = set(tesserocr_pool.__all__)
reexported = {k: v for k, v in tesserocr_pool.__dict__.items() if k in __all__}
globals().update(reexported)
