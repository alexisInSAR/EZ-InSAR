osascript -e 'tell app "Terminal"
    reopen
    activate
    delay 1
    #do script "cd /Users/alexis_hrysiewicz/Applications/GUI_ISCE_StaMPS" in front window
    do script "conda activate InSARenv" in front window
    do script "export DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/geos/3.9.1/lib" in front window
    do script "cd /Users/alexis_hrysiewicz/Work/ISPS_Link/Development/isps-link-isce-stamps" in front window
    do script "./scripttoeval.sh" in front window
    do script "exit" in front window
end tell'
