"""
copy_packages.py - Post-build script to copy Python packages into the PyInstaller bundle.
Handles both package directories (__init__.py) and single-file modules (.py).
"""
import os
import shutil
import sys


def copy_package(pkg_name: str, internal_dir: str) -> None:
    mod = __import__(pkg_name)
    src_file = os.path.abspath(mod.__file__)
    print(f"  {pkg_name} found at: {src_file}")

    if os.path.basename(src_file) == "__init__.py":
        # Package directory (e.g. libvisio_ng/__init__.py)
        src_dir = os.path.dirname(src_file)
        dst_dir = os.path.join(internal_dir, pkg_name)
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        print(f"  Copied directory: {src_dir} -> {dst_dir}")
    else:
        # Single-file module (e.g. olefile.py)
        dst_file = os.path.join(internal_dir, os.path.basename(src_file))
        shutil.copy2(src_file, dst_file)
        print(f"  Copied file: {src_file} -> {dst_file}")


def main():
    internal_dir = os.path.join("build", "dist", "VisioViewer", "_internal")

    if not os.path.isdir(internal_dir):
        print(f"[ERROR] _internal directory not found: {internal_dir}")
        sys.exit(1)

    for pkg_name in ["libvisio_ng", "olefile"]:
        try:
            copy_package(pkg_name, internal_dir)
        except ImportError:
            print(f"  [WARN] {pkg_name} not found, skipping.")
        except Exception as e:
            print(f"  [ERROR] Failed to copy {pkg_name}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
