@echo off
mode con cols=50 lines=50

:: 需要编译的文件和执行编译的软件位置
set MAIN_PY_NAME=app.py
set SOFT_PATHS="E:\Pyqt5_Python\Scripts"
set SOFT_VERSION=v2.3.2.zip

:: 设置文件夹
set PROJECT_NAME=%~dp0..
set PY_WORKPATH="%PROJECT_NAME%\Demo"
set GAU_TEMPLATE="%PROJECT_NAME%\Demo\Template"
set PY_VERSION="%PY_WORKPATH%\%MAIN_PY_NAME%"
set RELEASE_PATHS="%PROJECT_NAME%\release"
set RELEASE_VERSION_PATHS="%PROJECT_NAME%\release\dist"
set RELEASE_VERSION_APP_PATHS="%PROJECT_NAME%\release\dist\app"
set RELEASE_INFO="%PROJECT_NAME%\Demo\Release_info"

:: 查看是否存在文件夹
cd %PY_WORKPATH%
rd /s /q %RELEASE_PATHS%
if not exist %RELEASE_PATHS% (mkdir %RELEASE_PATHS%)

:: 激活虚拟环境
cd %SOFT_PATHS%
call activate.bat

::编译文件
cd %RELEASE_PATHS%
mkdir "Release_info"
copy %RELEASE_INFO%\ Release_info\
call pyinstaller.exe --version-file .\Release_info\version_info.txt --icon=.\Release_info\soft.ico --splash=.\Release_info\start.png -Dw %PY_VERSION%

if %ERRORLEVEL% == 1 (
    goto Failure1
) else (
    echo exe file has been converted
    :: 复制文件
    cd %RELEASE_VERSION_APP_PATHS% 
    mkdir "Template"
    copy %GAU_TEMPLATE%\ Template\
    echo template files have been copied
    :: 发行版本
    cd %RELEASE_VERSION_PATHS%
    call rar.exe a %RELEASE_PATHS%\%SOFT_VERSION% "app"

    if %ERRORLEVEL% == 1 goto Failure2
    echo rar file has been generated 
    exit
)

::删除多余文件
cd %RELEASE_PATHS%
rmdir "Release_info"

:Failure1
@echo exe file ERR
pause
exit

:Failure2
@echo rar file ERR
pause
exit