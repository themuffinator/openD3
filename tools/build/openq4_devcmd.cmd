@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%opend3_devcmd.cmd" (
    call "%SCRIPT_DIR%opend3_devcmd.cmd"
    exit /b %ERRORLEVEL%
)

echo [openq4] Legacy wrapper could not find opend3_devcmd.cmd.
exit /b 1
