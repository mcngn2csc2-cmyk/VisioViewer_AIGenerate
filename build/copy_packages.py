"""
copy_packages.py - Post-build script to copy libvisio_ng and olefile into the PyInstaller bundle.
Called by build_exe.bat after pyinstaller finishes.
"""
import os
import shutil
import sys


def main():
    internal_dir = os.path.join("build", "dist", "VisioViewer", "_internal")

    if not os.path.isdir(internal_dir):
        print(f"[ERROR] _internal directory not found: {internal_dir}")
        sys.exit(1)

    packages = ["libvisio_ng", "olefile"]

    for pkg_name in packages:
        try:
            mod = __import__(pkg_name)
            src = os.path.dirname(os.path.abspath(mod.__file__))
            dst = os.path.join(internal_dir, pkg_name)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Copied {pkg_name}: {src} -> {dst}")
        except ImportError:
            print(f"  [WARN] {pkg_name} not found, skipping.")
        except Exception as e:
            print(f"  [ERROR] Failed to copy {pkg_name}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
