@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

rem 当前目录（a 文件夹）
set "BASE=%~dp0"

rem CSV 文件路径
set "CSV=%BASE%data.csv"

if not exist "%CSV%" (
    echo data.csv not found
    pause
    exit /b
)

echo Reading data.csv...
echo.

rem 逐行读取 CSV，每行两列： folder,keyword
for /f "usebackq tokens=1,2 delims=, " %%A in ("%CSV%") do (
    set "FOLDER=%%A"
    set "KEY=%%B"

    rem 去掉行首的 U+FEFF（你 CSV 第一行的不可见字符）
    set "FOLDER=!FOLDER:﻿=!"

    rem 忽略空行
    if not "!FOLDER!"=="" (
        echo Mapping: Folder [!FOLDER!]  ←  Keyword [!KEY!]

        rem 遍历当前目录所有图片（不进入子文件夹）
        for %%I in ("%BASE%*.jpg" "%BASE%*.jpeg" "%BASE%*.png" "%BASE%*.bmp" "%BASE%*.gif") do (

            rem 如果文件不存在（某种扩展名没有匹配项）则跳过
            if exist "%%~fI" (
                set "IMG=%%~nxI"

                rem 判断文件名是否包含 KEY
                echo !IMG! | findstr /i "!KEY!" >nul
                if !errorlevel! == 0 (
                    echo    → Matched: Moving !IMG! to !FOLDER!
                    move "%%~fI" "%BASE%!FOLDER!\" >nul
                )
            )
        )
        echo.
    )
)

echo Done.
pause
