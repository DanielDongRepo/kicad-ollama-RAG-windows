@echo off
REM 确保 KiCad bin 在 PATH 最前面（避免其他版本干扰）
set PATH=E:\kicad\bin;%PATH%

REM 设置 Python 模块路径
set PYTHONPATH=E:\kicad\bin\Lib\site-packages;%PYTHONPATH%

REM 激活虚拟环境
call F:\kicad-ai-inspector\kicad-ai-env\Scripts\activate.bat

REM 进入项目目录
cd /d F:\kicad-ai-inspector

REM 启动交互式命令行
cmd /k