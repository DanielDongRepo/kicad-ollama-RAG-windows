@echo off
REM 确保 KiCad bin 在 PATH 最前面（避免其他版本干扰）这里改为自己的kicad的bin路径
set PATH=C:\kicad\bin;%PATH%

REM 设置 Python 模块路径。假设kicad安装在全部c盘，项目也在c盘，虚拟环境在项目目录下
set PYTHONPATH=C:\kicad\bin\Lib\site-packages;%PYTHONPATH%

REM 激活虚拟环境()
call C:\kicad-ai-inspector\kicad-ai-env\Scripts\activate.bat

REM 进入项目目录
cd /d C:\kicad-ai-inspector

REM 启动交互式命令行

cmd /k
