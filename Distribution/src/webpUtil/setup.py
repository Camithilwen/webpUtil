import sys
from cx_Freeze import setup, Executable

# Path to the main application script
main_script = "E:/Shepherd/Fall-2024/webpUtil/Distribution/src/webpUtil/webpUtil.py"

# Dependencies for the build
build_exe_options = {
    "includes": ["PyQt5", "webp", "webptools"],  # Required modules
    "include_files": [
        "E:/Shepherd/Fall-2024/webpUtil/Distribution/src/webpUtil/WEBPconvert.py",  # Supporting script
        "E:/Shepherd/Fall-2024/webpUtil/Distribution/src/webpUtil/DR1 icon.ico",  # Icon
        "E:/Shepherd/Fall-2024/webpUtil/Distribution/src/webpUtil/lib/output/release-static/x86/bin/dwebp.exe"
    ],
    "packages": [],  # Add additional packages if needed
    "excludes": ["tkinter", "unittest"],  # Exclude unused modules
    "optimize": 1,  # Optimization level: 0 (none), 1 (basic), 2 (full)
}

# Set base to "Win32GUI" for GUI-based applications on Windows
# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

# Define the executable configuration
executables = [
    Executable(
        main_script,
        #base=base,
        target_name="webpUtil.exe",
        icon="E:/Shepherd/Fall-2024/webpUtil/Distribution/src/webpUtil/DR1 icon.ico",  # Icon for the executable
    )
]

# Setup function to configure the build
setup(
    name="webpUtil",
    version="0.1",
    description="webpUtil: A utility to convert WEBP images using PyQt5",
    options={"build_exe": build_exe_options},
    executables=executables,
)
