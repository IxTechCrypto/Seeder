"""
PyInstaller Build Automation for SeederFlasher.exe
Bundles the Cyberpunk UI, esptool, and both T-Display-S3 and T-Display firmware images
into a single, standalone Windows executable.
"""

import os
import sys
import PyInstaller.__main__

def build():
    flasher_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(flasher_dir)
    app_script = os.path.join(flasher_dir, "app.py")
    firmware_dir = os.path.join(flasher_dir, "firmware")
    icon_path = os.path.join(flasher_dir, "icon.ico")
    dist_dir = os.path.join(repo_root, "dist")
    build_dir = os.path.join(repo_root, "build")

    # Validate firmware files exist
    for target in ["tdisplay-s3", "tdisplay"]:
        target_dir = os.path.join(firmware_dir, target)
        for binary in ["bootloader.bin", "partitions.bin", "boot_app0.bin", "firmware.bin"]:
            p = os.path.join(target_dir, binary)
            if not os.path.isfile(p):
                print(f"[!] Error: Missing required binary: {p}")
                sys.exit(1)

    print("[*] All firmware binaries verified.")
    print(f"[*] App script: {app_script}")
    print(f"[*] Firmware bundle directory: {firmware_dir}")
    print(f"[*] Output directory: {dist_dir}")

    pyinstaller_args = [
        app_script,
        "--onefile",
        "--windowed",
        "--name=SeederFlasher",
        f"--add-data={firmware_dir}{os.pathsep}firmware",
        f"--add-data={icon_path}{os.pathsep}.",
        f"--icon={icon_path}",
        "--collect-all=esptool",
        "--collect-all=serial",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        f"--specpath={flasher_dir}",
        "--clean",
        "--noconfirm",
    ]

    print("[*] Running PyInstaller...")
    PyInstaller.__main__.run(pyinstaller_args)

    exe_path = os.path.join(dist_dir, "SeederFlasher.exe")
    if os.path.isfile(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("=" * 60)
        print(f"[+] BUILD SUCCESSFUL!")
        print(f"[+] Executable: {exe_path}")
        print(f"[+] File Size:  {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("[!] Build finished but SeederFlasher.exe was not found in dist/")
        sys.exit(1)

if __name__ == "__main__":
    build()
