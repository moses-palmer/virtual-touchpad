@echo off

set SCRIPTDIR=%~dp0
set VIRTUALENV_DIR=%1
set PYTHON=%2


:: Create the virtualenv
%PYTHON% -m virtualenv --python=%PYTHON% %VIRTUALENV_DIR% ^
    || exit 1


:: Install packages using Python from the virtualenv
set PIP_REQUIRE_VIRTUALENV=true
call %VIRTUALENV_DIR%\Scripts\activate.bat
python.exe %SCRIPTDIR%\install-packages.py ^
    || exit 1
