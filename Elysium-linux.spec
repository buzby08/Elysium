# -*- mode: python ; coding: utf-8 -*-

# Analysis phase
a = Analysis(
    ['main.py'],  # Entry point of your application
    pathex=[],  # Additional paths to include for module searching, if any
    binaries=[],  # Binary files to include, if any
    datas=[
        ('Images/ElysiumLogo.ico', 'Images'),
        ('Images/ElysiumLogo.png', 'Images'),
        ('Images/light/new_file.png', 'Images/light'),
        ('Images/light/settings.png', 'Images/light'),
        ('Images/dark/new_file.png', 'Images/dark'),
        ('Images/dark/settings.png', 'Images/dark'),
        ('Images/dark/file.png', 'Images/dark'),
        ('Images/dark/folder.png', 'Images/dark'),
        ('Images/light/file.png', 'Images/light'),
        ('Images/light/folder.png', 'Images/light'),
        ('Settings/projects.json', 'Settings'),
        ('Settings/userSettings.json', 'Settings'),
        ('Themes/customWidgetTheme.json', 'Themes'),
        ('Themes/UITheme.json', 'Themes'), 
        ('Themes/UIToWidget.json', 'Themes'), 
        ('Themes/widgetTheme.json', 'Themes'),
        ('files.py', '.'), 
        ('fix.py', '.'), 
        ('gui.py', '.'), 
        ('readme.md', '.'), 
        ('settings.py', '.'), 
        ('theming.py', '.'),
    ],  # Data files to bundle into the executable
    hiddenimports=[
        'customtkinter', 
        'argparse', 
        'PIL',
        'PIL._tkinter_finder',
        'psutil',
        'win32file',
        'ctypes',
        'pwd'
    ],  # Hidden imports if not auto-detected
    hookspath=[],  # Custom hooks (optional)
    hooksconfig={},  # Hook configurations (optional)
    runtime_hooks=[],  # Runtime hooks (optional)
    excludes=[],  # Modules to exclude
    noarchive=False,  # Include archive in the bundle (for performance)
    optimize=0,  # No optimisation (set to 1 or 2 for optimised builds)
)

# Convert pure Python files to Python bytecode archive
pyz = PYZ(a.pure, a.zipped_data)

# Executable creation
exe = EXE(
    pyz,
    a.scripts,  # Scripts from analysis
    [],
    exclude_binaries=True,  # Exclude shared libraries from the executable
    name='Elysium',  # Name of the executable
    debug=True,  # Enable debug logs
    bootloader_ignore_signals=False,  # Bootloader behaviour
    strip=False,  # Do not strip symbols (retain debugging symbols)
    upx=True,  # Use UPX compression for smaller binaries
    console=False,  # GUI app (set to True for console apps)
    disable_windowed_traceback=False,  # Show traceback in GUI if an error occurs
    argv_emulation=False,  # Emulate sys.argv on Mac (not applicable here)
    target_arch=None,  # Use default architecture
    codesign_identity=None,  # Code-signing identity (Mac only)
    entitlements_file=None,  # Entitlements for macOS (not applicable here)
    icon="E:/file explorer/Images/ElysiumLogo.ico",
)

# Collection phase
coll = COLLECT(
    exe,
    a.binaries,  # Include shared libraries
    a.datas,  # Include resource files
    strip=False,  # Do not strip binaries
    upx=True,  # Compress with UPX
    upx_exclude=[],  # Exclude specific files from UPX
    name='Elysium',  # Output folder name
)
