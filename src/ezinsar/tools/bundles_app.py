#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Application bundles
    
    (From `ezinsar` package)

Changelog:
    * 1.0.0: Initial release

"""
import os
import shutil
from ezinsar import __versionPackage__ as version1
__condaenv__ = os.environ['CONDA_DEFAULT_ENV']

home_dir = os.path.expanduser("~")
try:
    pythonpath = os.environ['PYTHONPATH']
except:
    os.environ['PYTHONPATH'] = ''
    pythonpath = os.environ['PYTHONPATH']

def bundle_macOS(desktop=True,config=True,tsdisplayer=True,docs=True):
    """Bundle for macOS
    """
    if os.path.isdir(home_dir+'/miniforge3'):
        condadir = 'miniforge3'
    else:
        condadir = 'miniconda3'

    ## Create the required directory
    if os.path.isdir("%s/Applications/EZ-InSAR" % (home_dir)):
        shutil.rmtree("%s/Applications/EZ-InSAR" % (home_dir))

    if os.path.isdir("EZ-InSAR-CLI.app"):
        shutil.rmtree('EZ-InSAR-CLI.app')
    os.makedirs("EZ-InSAR-CLI.app/Contents/MacOS")

    if desktop:
        if os.path.isdir("EZ-InSAR-Desktop.app"):
            shutil.rmtree('EZ-InSAR-Desktop.app')
        os.makedirs('EZ-InSAR-Desktop.app')
        os.makedirs("EZ-InSAR-Desktop.app/Contents/MacOS")

    if config:
        if os.path.isdir("EZ-InSAR-Config.app"):
            shutil.rmtree('EZ-InSAR-Config.app')
        os.makedirs('EZ-InSAR-Config.app')
        os.makedirs("EZ-InSAR-Config.app/Contents/MacOS")

    if tsdisplayer:
        if os.path.isdir("EZ-InSAR-TSDisplayer.app"):
            shutil.rmtree('EZ-InSAR-TSDisplayer.app')
        os.makedirs('EZ-InSAR-TSDisplayer.app')
        os.makedirs("EZ-InSAR-TSDisplayer.app/Contents/MacOS")

    if docs:
        if os.path.isdir("EZ-InSAR-Docs.app"):
            shutil.rmtree('EZ-InSAR-Docs.app')
        os.makedirs('EZ-InSAR-Docs.app')
        os.makedirs("EZ-InSAR-Docs.app/Contents/MacOS")

    ## Create the launchers
    with open('EZ-InSAR-CLI.app/Contents/MacOS/EZ-InSAR-CLI','w') as fout:
        fout.write('#!/bin/bash\n')
        fout.write('CONDA_PATH="$HOME/%s"\n' % (condadir))
        fout.write('ENV_NAME="%s"\n' % (__condaenv__))
        fout.write('osascript <<EOF\n')
        fout.write('tell application "Terminal"\n')
        fout.write('\tactivate\n')
        fout.write('\tdo script "source $CONDA_PATH/etc/profile.d/conda.sh && conda activate $ENV_NAME && ezinsar -h"\n')
        fout.write('end tell\n')
        fout.write('EOF\n')
                
    os.system("chmod +x EZ-InSAR-CLI.app/Contents/MacOS/EZ-InSAR-CLI")

    if desktop:
        with open('EZ-InSAR-Desktop.app/Contents/MacOS/EZ-InSAR-desktop','w') as fout:
            fout.write('#!/bin/bash\n')
            fout.write('CONDA_PATH="$HOME/%s"\n' % (condadir))
            fout.write('ENV_NAME="%s"\n' % (__condaenv__))
            fout.write('osascript <<EOF\n')
            fout.write('tell application "Terminal"\n')
            fout.write('\tactivate\n')
            fout.write('\tdo script "source $CONDA_PATH/etc/profile.d/conda.sh && conda activate $ENV_NAME && ezinsar; exit"\n')
            fout.write('end tell\n')
            fout.write('EOF\n')
                    
        os.system("chmod +x EZ-InSAR-Desktop.app/Contents/MacOS/EZ-InSAR-desktop")

    if config:
        with open('EZ-InSAR-Config.app/Contents/MacOS/EZ-InSAR-config','w') as fout:
            fout.write('#!/bin/bash\n')
            fout.write('CONDA_PATH="$HOME/%s"\n' % (condadir))
            fout.write('ENV_NAME="%s"\n' % (__condaenv__))
            fout.write('osascript <<EOF\n')
            fout.write('tell application "Terminal"\n')
            fout.write('\tactivate\n')
            fout.write('\tdo script "source $CONDA_PATH/etc/profile.d/conda.sh && conda activate $ENV_NAME && ezinsar desktop config; exit"\n')
            fout.write('end tell\n')
            fout.write('EOF\n')
                    
        os.system("chmod +x EZ-InSAR-Config.app/Contents/MacOS/EZ-InSAR-config")

    if tsdisplayer:
        with open('EZ-InSAR-TSDisplayer.app/Contents/MacOS/EZ-InSAR-tsdisplayer','w') as fout:
            fout.write('#!/bin/bash\n')
            fout.write('CONDA_PATH="$HOME/%s"\n' % (condadir))
            fout.write('ENV_NAME="%s"\n' % (__condaenv__))
            fout.write('osascript <<EOF\n')
            fout.write('tell application "Terminal"\n')
            fout.write('\tactivate\n')
            fout.write('\tdo script "source $CONDA_PATH/etc/profile.d/conda.sh && conda activate $ENV_NAME && ezinsar tsdisplayer; exit"\n')
            fout.write('end tell\n')
            fout.write('EOF\n')
                    
        os.system("chmod +x EZ-InSAR-TSDisplayer.app/Contents/MacOS/EZ-InSAR-tsdisplayer")

    if docs:
        with open('EZ-InSAR-Docs.app/Contents/MacOS/EZ-InSAR-docs','w') as fout:
            fout.write('#!/bin/bash\n')
            fout.write('CONDA_PATH="$HOME/%s"\n' % (condadir))
            fout.write('ENV_NAME="%s"\n' % (__condaenv__))
            fout.write('osascript <<EOF\n')
            fout.write('tell application "Terminal"\n')
            fout.write('\tactivate\n')
            fout.write('\tdo script "source $CONDA_PATH/etc/profile.d/conda.sh && conda activate $ENV_NAME && ezinsar desktop docs; exit"\n')
            fout.write('end tell\n')
            fout.write('EOF\n')
                    
        os.system("chmod +x EZ-InSAR-Docs.app/Contents/MacOS/EZ-InSAR-docs")


    ## Create the Info.plist
    with open("EZ-InSAR-CLI.app/Contents/Info.plist","w") as fout:
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \n')
        fout.write('"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
        fout.write('<plist version="1.0">\n')
        fout.write('<dict>\n')
        fout.write('\t<key>CFBundleName</key>\n')
        fout.write('\t<string>EZ-InSAR-3_Command_Line_Interface</string>\n')
        fout.write('\t<key>CFBundleIdentifier</key>\n')
        fout.write('\t<string>EZInSAR.3.CommandLineInterface</string>\n')
        fout.write('\t<key>CFBundleVersion</key>\n')
        fout.write('\t<string>%s</string>\n' % (version1))
        fout.write('\t<key>CFBundleExecutable</key>\n')
        fout.write('\t<string>EZ-InSAR-CLI</string>\n')
        fout.write('\t<key>CFBundleIconFile</key>\n')
        fout.write('\t<string>EZInSARCLI</string>\n')
        fout.write('</dict>\n')
        fout.write('</plist>\n')

    if desktop:
        from ezinsardesktopmodule import __versionPackage__ as version2

        with open("EZ-InSAR-Desktop.app/Contents/Info.plist","w") as fout:
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \n')
            fout.write('"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            fout.write('<plist version="1.0">\n')
            fout.write('<dict>\n')
            fout.write('\t<key>CFBundleName</key>\n')
            fout.write('\t<string>EZ-InSAR-3_Desktop_Application</string>\n')
            fout.write('\t<key>CFBundleIdentifier</key>\n')
            fout.write('\t<string>EZInSAR.3.Destktop</string>\n')
            fout.write('\t<key>CFBundleVersion</key>\n')
            fout.write('\t<string>%s</string>\n' % (version2))
            fout.write('\t<key>CFBundleExecutable</key>\n')
            fout.write('\t<string>EZ-InSAR-desktop</string>\n')
            fout.write('\t<key>CFBundleIconFile</key>\n')
            fout.write('\t<string>EZInSARdesktop</string>\n')
            fout.write('</dict>\n')
            fout.write('</plist>\n')

    if config:
        from ezinsardesktopmodule import __versionPackage__ as version2

        with open("EZ-InSAR-Config.app/Contents/Info.plist","w") as fout:
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \n')
            fout.write('"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            fout.write('<plist version="1.0">\n')
            fout.write('<dict>\n')
            fout.write('\t<key>CFBundleName</key>\n')
            fout.write('\t<string>EZ-InSAR-3_Config_Application</string>\n')
            fout.write('\t<key>CFBundleIdentifier</key>\n')
            fout.write('\t<string>EZInSAR.3.Config</string>\n')
            fout.write('\t<key>CFBundleVersion</key>\n')
            fout.write('\t<string>%s</string>\n' % (version2))
            fout.write('\t<key>CFBundleExecutable</key>\n')
            fout.write('\t<string>EZ-InSAR-config</string>\n')
            fout.write('\t<key>CFBundleIconFile</key>\n')
            fout.write('\t<string>EZInSARconfig</string>\n')
            fout.write('</dict>\n')
            fout.write('</plist>\n')

    if tsdisplayer:
        from ezinsartsdisplayermodule import __versionPackage__ as version3

        with open("EZ-InSAR-TSDisplayer.app/Contents/Info.plist","w") as fout:
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \n')
            fout.write('"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            fout.write('<plist version="1.0">\n')
            fout.write('<dict>\n')
            fout.write('\t<key>CFBundleName</key>\n')
            fout.write('\t<string>EZ-InSAR-3_TSDisplayer_Application</string>\n')
            fout.write('\t<key>CFBundleIdentifier</key>\n')
            fout.write('\t<string>EZInSAR.3.TSDisplayer</string>\n')
            fout.write('\t<key>CFBundleVersion</key>\n')
            fout.write('\t<string>%s</string>\n' % (version3))
            fout.write('\t<key>CFBundleExecutable</key>\n')
            fout.write('\t<string>EZ-InSAR-tsdisplayer</string>\n')
            fout.write('\t<key>CFBundleIconFile</key>\n')
            fout.write('\t<string>EZInSARtsdisplayer</string>\n')
            fout.write('</dict>\n')
            fout.write('</plist>\n')

    if docs:
        from ezinsar import __versionPackage__ as version4

        with open("EZ-InSAR-Docs.app/Contents/Info.plist","w") as fout:
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \n')
            fout.write('"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            fout.write('<plist version="1.0">\n')
            fout.write('<dict>\n')
            fout.write('\t<key>CFBundleName</key>\n')
            fout.write('\t<string>EZ-InSAR-3_Docs_Application</string>\n')
            fout.write('\t<key>CFBundleIdentifier</key>\n')
            fout.write('\t<string>EZInSAR.3.Docs</string>\n')
            fout.write('\t<key>CFBundleVersion</key>\n')
            fout.write('\t<string>%s</string>\n' % (version4))
            fout.write('\t<key>CFBundleExecutable</key>\n')
            fout.write('\t<string>EZ-InSAR-docs</string>\n')
            fout.write('\t<key>CFBundleIconFile</key>\n')
            fout.write('\t<string>EZInSARdocs</string>\n')
            fout.write('</dict>\n')
            fout.write('</plist>\n')

    ## Create the icons
    pathim = __file__.replace('src/ezinsar/tools/bundles_app.py','private/EZ_InSAR_logo_whiteback.png')
    os.makedirs("EZ-InSAR-CLI.app/Contents/Resources")

    if os.path.isdir("EZInSARCLI.iconset"):
        shutil.rmtree('EZInSARCLI.iconset')
    if os.path.isdir("EZInSARCLI.icns"):
        shutil.rmtree('EZInSARCLI.icns')
    os.makedirs("EZInSARCLI.iconset")

    os.system('sips -z 16 16 %s --out EZInSARCLI.iconset/icon_16x16.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 32 32 %s --out EZInSARCLI.iconset/icon_16x16@2x.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 32 32    %s --out EZInSARCLI.iconset/icon_32x32.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 64 64    %s --out EZInSARCLI.iconset/icon_32x32@2x.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 128 128   %s --out EZInSARCLI.iconset/icon_128x128.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 256 256   %s --out EZInSARCLI.iconset/icon_128x128@2x.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 256 256   %s --out EZInSARCLI.iconset/icon_256x256.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 512 512   %s --out EZInSARCLI.iconset/icon_256x256@2x.png > /dev/null 2>&1' % (pathim))
    os.system('sips -z 512 512   %s --out EZInSARCLI.iconset/icon_512x512.png > /dev/null 2>&1' % (pathim))
    os.system('iconutil -c icns EZInSARCLI.iconset -o EZInSARCLI.icns')

    os.rename('EZInSARCLI.icns','EZ-InSAR-CLI.app/Contents/Resources/EZInSARCLI.icns')

    if os.path.isdir("EZInSARCLI.iconset"):
        shutil.rmtree('EZInSARCLI.iconset')

    if desktop:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_whiteback.png')

        os.makedirs("EZ-InSAR-Desktop.app/Contents/Resources")

        if os.path.isdir("EZInSARdesktop.iconset"):
            shutil.rmtree('EZInSARdesktop.iconset')
        if os.path.isdir("EZInSARdesktop.icns"):
            shutil.rmtree('EZInSARdesktop.icns')
        os.makedirs("EZInSARdesktop.iconset")

        os.system('sips -z 16 16 %s --out EZInSARdesktop.iconset/icon_16x16.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32 %s --out EZInSARdesktop.iconset/icon_16x16@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32    %s --out EZInSARdesktop.iconset/icon_32x32.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 64 64    %s --out EZInSARdesktop.iconset/icon_32x32@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 128 128   %s --out EZInSARdesktop.iconset/icon_128x128.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARdesktop.iconset/icon_128x128@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARdesktop.iconset/icon_256x256.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARdesktop.iconset/icon_256x256@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARdesktop.iconset/icon_512x512.png > /dev/null 2>&1' % (pathim))
        os.system('iconutil -c icns EZInSARdesktop.iconset -o EZInSARdesktop.icns')

        os.rename('EZInSARdesktop.icns','EZ-InSAR-Desktop.app/Contents/Resources/EZInSARdesktop.icns')

        if os.path.isdir("EZInSARdesktop.iconset"):
            shutil.rmtree('EZInSARdesktop.iconset')

    if config:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_config_whiteback.png')

        os.makedirs("EZ-InSAR-Config.app/Contents/Resources")

        if os.path.isdir("EZInSARconfig.iconset"):
            shutil.rmtree('EZInSARconfig.iconset')
        if os.path.isdir("EZInSARconfig.icns"):
            shutil.rmtree('EZInSARconfig.icns')
        os.makedirs("EZInSARconfig.iconset")

        os.system('sips -z 16 16 %s --out EZInSARconfig.iconset/icon_16x16.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32 %s --out EZInSARconfig.iconset/icon_16x16@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32    %s --out EZInSARconfig.iconset/icon_32x32.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 64 64    %s --out EZInSARconfig.iconset/icon_32x32@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 128 128   %s --out EZInSARconfig.iconset/icon_128x128.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARconfig.iconset/icon_128x128@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARconfig.iconset/icon_256x256.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARconfig.iconset/icon_256x256@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARconfig.iconset/icon_512x512.png > /dev/null 2>&1' % (pathim))
        os.system('iconutil -c icns EZInSARconfig.iconset -o EZInSARconfig.icns')

        os.rename('EZInSARconfig.icns','EZ-InSAR-Config.app/Contents/Resources/EZInSARconfig.icns')

        if os.path.isdir("EZInSARconfig.iconset"):
            shutil.rmtree('EZInSARconfig.iconset')

    if tsdisplayer:
        import ezinsartsdisplayermodule
        pathim = ezinsartsdisplayermodule.__file__.replace('src/ezinsartsdisplayermodule/__init__.py','private/EZ_InSAR_logo_tsdisplayer_whiteback.png')

        os.makedirs("EZ-InSAR-TSDisplayer.app/Contents/Resources")

        if os.path.isdir("EZInSARtsdisplayer.iconset"):
            shutil.rmtree('EZInSARtsdisplayer.iconset')
        if os.path.isdir("EZInSARtsdisplayer.icns"):
            shutil.rmtree('EZInSARtsdisplayer.icns')
        os.makedirs("EZInSARtsdisplayer.iconset")

        os.system('sips -z 16 16 %s --out EZInSARtsdisplayer.iconset/icon_16x16.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32 %s --out EZInSARtsdisplayer.iconset/icon_16x16@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32    %s --out EZInSARtsdisplayer.iconset/icon_32x32.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 64 64    %s --out EZInSARtsdisplayer.iconset/icon_32x32@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 128 128   %s --out EZInSARtsdisplayer.iconset/icon_128x128.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARtsdisplayer.iconset/icon_128x128@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARtsdisplayer.iconset/icon_256x256.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARtsdisplayer.iconset/icon_256x256@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARtsdisplayer.iconset/icon_512x512.png > /dev/null 2>&1' % (pathim))
        os.system('iconutil -c icns EZInSARtsdisplayer.iconset -o EZInSARtsdisplayer.icns')

        os.rename('EZInSARtsdisplayer.icns','EZ-InSAR-TSDisplayer.app/Contents/Resources/EZInSARtsdisplayer.icns')

        if os.path.isdir("EZInSARtsdisplayer.iconset"):
            shutil.rmtree('EZInSARtsdisplayer.iconset')

    if docs:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_docs_whiteback.png')

        os.makedirs("EZ-InSAR-Docs.app/Contents/Resources")

        if os.path.isdir("EZInSARdocs.iconset"):
            shutil.rmtree('EZInSARdocs.iconset')
        if os.path.isdir("EZInSARdocs.icns"):
            shutil.rmtree('EZInSARdocs.icns')
        os.makedirs("EZInSARdocs.iconset")

        os.system('sips -z 16 16 %s --out EZInSARdocs.iconset/icon_16x16.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32 %s --out EZInSARdocs.iconset/icon_16x16@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 32 32    %s --out EZInSARdocs.iconset/icon_32x32.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 64 64    %s --out EZInSARdocs.iconset/icon_32x32@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 128 128   %s --out EZInSARdocs.iconset/icon_128x128.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARdocs.iconset/icon_128x128@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 256 256   %s --out EZInSARdocs.iconset/icon_256x256.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARdocs.iconset/icon_256x256@2x.png > /dev/null 2>&1' % (pathim))
        os.system('sips -z 512 512   %s --out EZInSARdocs.iconset/icon_512x512.png > /dev/null 2>&1' % (pathim))
        os.system('iconutil -c icns EZInSARdocs.iconset -o EZInSARdocs.icns')

        os.rename('EZInSARdocs.icns','EZ-InSAR-Docs.app/Contents/Resources/EZInSARdocs.icns')

        if os.path.isdir("EZInSARdocs.iconset"):
            shutil.rmtree('EZInSARdocs.iconset')

    ## Move the app(s)
    os.makedirs("%s/Applications/EZ-InSAR" % (home_dir))
    os.rename("EZ-InSAR-CLI.app","%s/Applications/EZ-InSAR/EZ-InSAR-CLI.app" % (home_dir))
    if desktop:
        os.rename("EZ-InSAR-Desktop.app","%s/Applications/EZ-InSAR/EZ-InSAR-Desktop.app" % (home_dir))
    if config:
        os.rename("EZ-InSAR-Config.app","%s/Applications/EZ-InSAR/EZ-InSAR-Config.app" % (home_dir))
    if tsdisplayer:
        os.rename("EZ-InSAR-TSDisplayer.app","%s/Applications/EZ-InSAR/EZ-InSAR-TSDisplayer.app" % (home_dir))
    if docs:
        os.rename("EZ-InSAR-Docs.app","%s/Applications/EZ-InSAR/EZ-InSAR-Docs.app" % (home_dir))
    
    
def bundle_Linux(desktop=True,config=True,tsdisplayer=True,docs=True):
    """Bundle for Linux systems
    """
    if os.path.isdir(home_dir+'/miniforge3'):
        condadir = 'miniforge3'
    else:
        condadir = 'miniconda3'
    
    ## Create the required directories
    if os.path.isfile("%s/.local/share/applications/EZ-InSAR-CLI.desktop" % (home_dir)):
        os.remove("%s/.local/share/applications/EZ-InSAR-CLI.desktop" % (home_dir))
    
    if desktop:
        if os.path.isfile("%s/.local/share/applications/EZ-InSAR-Desktop.desktop" % (home_dir)):
            os.remove("%s/.local/share/applications/EZ-InSAR-Desktop.desktop" % (home_dir))

    if config:
        if os.path.isfile("%s/.local/share/applications/EZ-InSAR-Config.desktop" % (home_dir)):
            os.remove("%s/.local/share/applications/EZ-InSAR-Config.desktop" % (home_dir))

    if tsdisplayer:
        if os.path.isfile("%s/.local/share/applications/EZ-InSAR-TSDisplayer.desktop" % (home_dir)):
            os.remove("%s/.local/share/applications/EZ-InSAR-TSDisplayer.desktop" % (home_dir))

    if docs:
        if os.path.isfile("%s/.local/share/applications/EZ-InSAR-Docs.desktop" % (home_dir)):
            os.remove("%s/.local/share/applications/EZ-InSAR-Docs.desktop" % (home_dir))

    pathim = __file__.replace('src/ezinsar/tools/bundles_app.py','private/EZ_InSAR_logo_whiteback.png')
    with open("%s/.local/share/applications/EZ-InSAR-CLI.desktop" % (home_dir),"w") as fout:
        fout.write('[Desktop Entry]\n')
        fout.write('Type=Application\n')
        fout.write('Name=EZ-InSAR-CLI\n')
        fout.write('Comment=Run EZ-InSAR with Command Line Interface mode\n')
        fout.write('Exec=gnome-terminal -- bash -l -c "source ~/.bashrc && export CONDA_AUTO_ACTIVATE_BASE=false && source %s/etc/profile.d/conda.sh && conda activate %s && export PYTHONPATH="%s"; ezinsar -h; exec bash"\n' % (home_dir+'/'+condadir,__condaenv__,pythonpath))        
        fout.write('Icon=%s\n' % (pathim))
        fout.write('Terminal=false\n')
        fout.write('Categories=Utility;\n')

    if desktop:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_whiteback.png')

        with open("%s/.local/share/applications/EZ-InSAR-Desktop.desktop" % (home_dir),"w") as fout:
            fout.write('[Desktop Entry]\n')
            fout.write('Type=Application\n')
            fout.write('Name=EZ-InSAR-Desktop\n')
            fout.write('Comment=Run EZ-InSAR with the GUI\n')
            fout.write('Exec=gnome-terminal -- bash -l -c "source ~/.bashrc && export CONDA_AUTO_ACTIVATE_BASE=false && source %s/etc/profile.d/conda.sh && conda activate %s && export PYTHONPATH="%s"; ezinsar"; exit\n' % (home_dir+'/'+condadir,__condaenv__,pythonpath))        
            fout.write('Icon=%s\n' % (pathim))
            fout.write('Terminal=false\n')
            fout.write('Categories=Utility;\n')

    if config:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_config_whiteback.png')

        with open("%s/.local/share/applications/EZ-InSAR-Config.desktop" % (home_dir),"w") as fout:
            fout.write('[Desktop Entry]\n')
            fout.write('Type=Application\n')
            fout.write('Name=EZ-InSAR-Config\n')
            fout.write('Comment=Run EZ-InSAR configuration\n')
            fout.write('Exec=gnome-terminal -- bash -l -c "source ~/.bashrc && export CONDA_AUTO_ACTIVATE_BASE=false && source %s/etc/profile.d/conda.sh && conda activate %s && export PYTHONPATH="%s"; ezinsar desktop config"; exit\n' % (home_dir+'/'+condadir,__condaenv__,pythonpath))        
            fout.write('Icon=%s\n' % (pathim))
            fout.write('Terminal=false\n')
            fout.write('Categories=Utility;\n')

    if tsdisplayer:
        import ezinsartsdisplayermodule
        pathim = ezinsartsdisplayermodule.__file__.replace('src/ezinsartsdisplayermodule/__init__.py','private/EZ_InSAR_logo_tsdisplayer_whiteback.png')

        with open("%s/.local/share/applications/EZ-InSAR-TSDisplayer.desktop" % (home_dir),"w") as fout:
            fout.write('[Desktop Entry]\n')
            fout.write('Type=Application\n')
            fout.write('Name=EZ-InSAR-TSDisplayer\n')
            fout.write('Comment=Run EZ-InSAR TS Displayer\n')
            fout.write('Exec=gnome-terminal -- bash -l -c "source ~/.bashrc && export CONDA_AUTO_ACTIVATE_BASE=false && source %s/etc/profile.d/conda.sh && conda activate %s && export PYTHONPATH="%s"; ezinsar tsdisplayer"; exit\n' % (home_dir+'/'+condadir,__condaenv__,pythonpath))        
            fout.write('Icon=%s\n' % (pathim))
            fout.write('Terminal=false\n')
            fout.write('Categories=Utility;\n')

    if docs:
        import ezinsardesktopmodule
        pathim = ezinsardesktopmodule.__file__.replace('src/ezinsardesktopmodule/__init__.py','private/EZ_InSAR_logo_desktop_docs_whiteback.png')

        with open("%s/.local/share/applications/EZ-InSAR-Docs.desktop" % (home_dir),"w") as fout:
            fout.write('[Desktop Entry]\n')
            fout.write('Type=Application\n')
            fout.write('Name=EZ-InSAR-Docs\n')
            fout.write('Comment=Run EZ-InSAR Documentation\n')
            fout.write('Exec=gnome-terminal -- bash -l -c "source ~/.bashrc && export CONDA_AUTO_ACTIVATE_BASE=false && source %s/etc/profile.d/conda.sh && conda activate %s && export PYTHONPATH="%s"; ezinsar desktop docs"; exit\n' % (home_dir+'/'+condadir,__condaenv__,pythonpath))        
            fout.write('Icon=%s\n' % (pathim))
            fout.write('Terminal=false\n')
            fout.write('Categories=Utility;\n')

def bundle_Windows(desktop=True,config=True,tsdisplayer=True,docs=True):
    """Bundle for Windows system
    """
    def create_shortcut(path,arguments,working_dir,icon):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = icon
        shortcut.save()

    from win32com.client import Dispatch

    username = os.environ["USERNAME"]
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    config_path = os.path.join(os.environ["USERPROFILE"], "Config")
    tsdisplayer_path = os.path.join(os.environ["USERPROFILE"], "TSDisplayer")

    start_menu_cli = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-CLI")
    os.makedirs(start_menu_cli, exist_ok=True)
    shortcut_name_cli = "EZ-InSAR-CLI.lnk"

    if desktop:
        start_menu_desktop = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-Desktop")
        os.makedirs(start_menu_desktop, exist_ok=True)
        shortcut_name_desktop = "EZ-InSAR-Desktop.lnk"

    if config:
        start_menu_config = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-Config")
        os.makedirs(start_menu_config, exist_ok=True)
        shortcut_name_config = "EZ-InSAR-Config.lnk"

    if tsdisplayer:
        start_menu_tsdisplayer = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-TSDisplayer")
        os.makedirs(start_menu_tsdisplayer, exist_ok=True)
        shortcut_name_tsdisplayer = "EZ-InSAR-TSDisplayer.lnk"

    if docs:
        start_menu_docs = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-Docs")
        os.makedirs(start_menu_docs, exist_ok=True)
        shortcut_name_docs = "EZ-InSAR-Docs.lnk"

    # Shortcut parameters
    target = r"C:\Windows\System32\cmd.exe"

    arguments_cli = (
        r'/K "call %s\miniconda3\Scripts\activate.bat %s && '
        r'set PYTHONPATH=%s && '
        r'ezinsar -h"' % (home_dir.replace('/',os.sep),__condaenv__,pythonpath.replace('/',os.sep))
    )

    if desktop:
        arguments_desktop = (
        r'/K "call %s\miniconda3\Scripts\activate.bat %s && '
        r'set PYTHONPATH=%s && '
        r'ezinsar"' 
        r' && exit' % (home_dir.replace('/',os.sep),__condaenv__,pythonpath.replace('/',os.sep))
        )

    if config:
        arguments_config = (
        r'/K "call %s\miniconda3\Scripts\activate.bat %s && '
        r'set PYTHONPATH=%s && '
        r'ezinsar desktop config"' 
        r' && exit' % (home_dir.replace('/',os.sep),__condaenv__,pythonpath.replace('/',os.sep))
        )

    if tsdisplayer:
        arguments_tsdisplayer = (
        r'/K "call %s\miniconda3\Scripts\activate.bat %s && '
        r'set PYTHONPATH=%s && '
        r'ezinsar tsdisplayer"' 
        r' && exit' % (home_dir.replace('/',os.sep),__condaenv__,pythonpath.replace('/',os.sep))
        )

    if docs:
        arguments_docs = (
        r'/K "call %s\miniconda3\Scripts\activate.bat %s && '
        r'set PYTHONPATH=%s && '
        r'ezinsar desktop docs"' 
        r' && exit' % (home_dir.replace('/',os.sep),__condaenv__,pythonpath.replace('/',os.sep))
        )

    working_dir = r"%s" % (home_dir.replace('/',os.sep))

    # Create the logos
    pathim_cli = __file__.replace('src\\ezinsar\\tools\\bundles_app.py','private\\EZ_InSAR_logo.ico')
    if desktop:
        import ezinsardesktopmodule
        pathim_desktop = ezinsardesktopmodule.__file__.replace('src\\ezinsardesktopmodule\\__init__.py','private\EZ_InSAR_logo_desktop_whiteback.ico')

    if config:
        import ezinsardesktopmodule
        pathim_config = ezinsardesktopmodule.__file__.replace('src\\ezinsardesktopmodule\\__init__.py','private\EZ_InSAR_logo_desktop_config_whiteback.ico')

    if tsdisplayer:
        import ezinsartsdisplayermodule
        pathim_tsdisplayer = ezinsartsdisplayermodule.__file__.replace('src\\ezinsartsdisplayermodule\\__init__.py','private\EZ_InSAR_logo_tsdisplayer_whiteback.ico')

    if docs:
        import ezinsardesktopmodule
        pathim_docs = ezinsardesktopmodule.__file__.replace('src\\ezinsardesktopmodule\\__init__.py','private\EZ_InSAR_logo_desktop_docs_whiteback.ico')

    # Create the shortcuts
    create_shortcut(os.path.join(start_menu_cli, shortcut_name_cli),arguments_cli,working_dir,pathim_cli)
    if desktop:
        create_shortcut(os.path.join(start_menu_desktop, shortcut_name_desktop),arguments_desktop,working_dir,pathim_desktop)

    if config:
        create_shortcut(os.path.join(start_menu_config, shortcut_name_config),arguments_config,working_dir,pathim_config)

    if tsdisplayer:
        create_shortcut(os.path.join(start_menu_tsdisplayer, shortcut_name_tsdisplayer),arguments_tsdisplayer,working_dir,pathim_tsdisplayer)

    if docs:
        create_shortcut(os.path.join(start_menu_docs, shortcut_name_docs),arguments_docs,working_dir,pathim_docs)

if __name__=='__main__':
    bundle_Windows()




