@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo Moving all images from subfolders to the current folder...
echo.

:: 循环所有子文件夹（只限一级）
for /d %%D in (*) do (
    if not "%%D"=="%~nx0" (
        echo Processing folder: %%D

        :: 移动常见图片格式（可自行添加）
        move "%%D\*.jpg" ".\" >nul 2>&1
        move "%%D\*.jpeg" ".\" >nul 2>&1
        move "%%D\*.png" ".\" >nul 2>&1
        move "%%D\*.gif" ".\" >nul 2>&1
        move "%%D\*.bmp" ".\" >nul 2>&1
        move "%%D\*.webp" ".\" >nul 2>&1

        :: 删除（可能已经空的）子文件夹
        rd "%%D" 2>nul
    )
)

echo.
echo Images Moved!

:: =============================
:: PART A — 从 CSV 创建文件夹
:: =============================
set "BASE=%~dp0"
set "CSV=%BASE%data.csv"

if not exist "%CSV%" (
    echo data.csv not found.
    pause
    exit /b
)

echo Reading data.csv...

:: 读取 CSV 第一列，同时清除 UTF-8 BOM
for /f "usebackq tokens=1 delims=," %%a in ("%CSV%") do (

    rem 原始读取内容
    set "name=%%a"

    rem ---- 强制去掉 UTF-8 BOM（EF BB BF） ----
    for /f "tokens=* delims=" %%x in ("!name!") do set "name=%%x"
    set "name=!name:﻿=!"
    set "name=!name:ï»¿=!"
    rem ---------------------------------------

    if not "!name!"=="" (
        if not exist "!BASE!!name!" (
            echo Creating folder: !name!
            mkdir "!BASE!!name!" >nul 2>&1
        )
    )
)

echo.
echo Folders created!
echo ---------------------------------------
echo Please place images into the corresponding folders,
echo then enter 0 (Full Rename) or 1 (Rename 1st image only)
echo ---------------------------------------


:: ==================================================
:: 循环等待用户输入 0 或 1
:: ==================================================
:ASK_INPUT
set /p mode=Enter number and press Enter: 

if "%mode%"=="0" goto RUN_B
if "%mode%"=="1" goto RUN_C

echo.
echo Invalid input, please enter 0 or 1.
echo.
goto ASK_INPUT


:: =============================
:: PART B — MAIN + PT01, PT02...
:: =============================
:RUN_B
echo.
echo Mode 0 Started: Full Rename (MAIN, PT01, PT02...)
echo.

for /d %%D in ("%BASE%*") do (
    set "FOLDER=%%~nD"
    set "WorkDir=%%D"
    echo Processing: !FOLDER!

    set COUNT=0
    :: 获取图片并重命名
    for /f "delims=" %%F in (
        'dir /b /on "!WorkDir!\*.jpg" "!WorkDir!\*.jpeg" "!WorkDir!\*.png" "!WorkDir!\*.bmp" 2^>nul'
    ) do (
        set /a COUNT+=1

        if !COUNT! equ 1 (
            set "NEWNAME=!FOLDER!.MAIN"
        ) else (
            set "IDX=0!COUNT!"
            set "IDX=!IDX:~-2!"
            set "NEWNAME=!FOLDER!.PT!IDX!"
        )

        set "EXT=%%~xF"
        
        :: 只有当文件名不同时才重命名
        if /i not "%%F"=="!NEWNAME!!EXT!" (
            echo Renaming: %%F -^> !NEWNAME!!EXT!
            ren "!WorkDir!\%%F" "!NEWNAME!!EXT!"
        )
    )
    echo.
)

echo Rename completed!
goto AFTER_RENAME


:: =============================
:: PART C — 仅将第一张图片命名为 MAIN
:: =============================
:RUN_C
echo.
echo Mode 1 Started: Rename first image to MAIN only
echo.

for /d %%D in ("%BASE%*") do (
    set "FOLDER=%%~nD"
    set "WorkDir=%%D"
    echo Processing: !FOLDER!

    set DONE=0
    for /f "delims=" %%F in (
        'dir /b /on "!WorkDir!\*.jpg" "!WorkDir!\*.jpeg" "!WorkDir!\*.png" "!WorkDir!\*.bmp" 2^>nul'
    ) do (
        if !DONE! equ 0 (
            set "EXT=%%~xF"
            set "NEWNAME=!FOLDER!.MAIN"
            
            if /i not "%%F"=="!NEWNAME!!EXT!" (
                echo Renaming: %%F -^> !NEWNAME!!EXT!
                ren "!WorkDir!\%%F" "!NEWNAME!!EXT!"
            )
            set DONE=1
        )
    )
    echo.
)

echo Rename completed!

:: =============================
:: PART D — 批量打包子文件夹为 ZIP
:: =============================
:AFTER_RENAME
echo.
echo =============================
echo Starting ZIP compression...
echo =============================

:: 这里必须使用全路径调用 powershell，防止环境变数异常
set "PS_CMD=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

for /d %%D in ("%BASE%*") do (
    set "TARGET_DIR=%%D"
    set "FOLDER_NAME=%%~nD"
    set "ZIP_FILE=%BASE%!FOLDER_NAME!.zip"

    :: 简单的检查：如果文件夹里有文件，才压缩
    dir /b /a-d "!TARGET_DIR!\*" >nul 2>&1
    if not errorlevel 1 (
        echo Compressing: !FOLDER_NAME! ...
        
        :: 【关键修改】在路径后添加了 \* 表示只压缩内容
        "%PS_CMD%" -NoProfile -Command "Compress-Archive -Path '!TARGET_DIR!\*' -DestinationPath '!ZIP_FILE!' -Force"
    ) else (
        echo [Skip] Empty folder: !FOLDER_NAME!
    )
)

echo.
echo ---------------------------------------
echo All tasks finished!
pause
exit /b