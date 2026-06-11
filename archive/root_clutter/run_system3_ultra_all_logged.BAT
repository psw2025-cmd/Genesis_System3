@echo off
chcp 65001 >nul
set PYTHONUTF8=1
title SYSTEM3 ULTRA - RUN OPTIONS 118-142 ONLY
color 0A

REM ===== Timestamp for new log folder =====
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "LOG_TIMESTAMP=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
set "LOG_DIR=logs\ULTRA_PANEL_118_142_%LOG_TIMESTAMP%"

cd /d "C:\Genesis_System3"
if not exist "logs" mkdir logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo SYSTEM3 ULTRA RUN 118-142 > "%LOG_DIR%\00_overall_summary.txt"
echo Started at %date% %time% >> "%LOG_DIR%\00_overall_summary.txt"

REM ===== Activate virtual environment once =====
call venv\Scripts\activate.bat > "%LOG_DIR%\01_venv_activation.log" 2>&1

REM ===== Numeric options 118-142 ONLY =====
for /L %%N in (118,1,142) do (
    echo ==== Running option %%N ====
    echo Option %%N started at %date% %time%> "%LOG_DIR%\opt_%%N_summary.txt"
    (
        echo %%N
        echo.
        echo 0
    ) | python system3_ultra.py > "%LOG_DIR%\opt_%%N.log" 2>&1
    echo Option %%N ended at %date% %time%>> "%LOG_DIR%\opt_%%N_summary.txt"
)

echo Finished at %date% %time% >> "%LOG_DIR%\00_overall_summary.txt"

echo.
echo DONE. Logs in: %LOG_DIR%
echo.
exit /b 0
