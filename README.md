# kicad-ollama-RAG-windows
本地大模型自动检测pcb板是否符合自己公司规范的项目

 项目目录结构（建议放在非中文路径）
C:\kicad-ai-inspector\
├── docs\
│   └── pcb_design_rules.txt          ← 你的设计规范
├── designs\
│   └── my_board.kicad_pcb            ← 你的 KiCad 项目文件
├── extract_pcb.py                    ← 提取 PCB 数据
├── build_rag.py                      ← 构建知识库
├── inspect_pcb.py                    ← 生成检查报告
├── requirements.txt                  ← 依赖列表
└── run_with_kicad.bat                ← 启动脚本

第一步：安装软件
1. 安装 KiCad（含 Python 支持）
- 从 https://www.kicad.org/download/windows/ 下载安装
- 默认安装即可，KiCad 7+ 自带嵌入式 Python 3.11（位于 C:\KiCad\bin）
2. 安装 Ollama for Windows
- 下载地址：https://ollama.com/download/OllamaSetup.exe
- 安装后重启终端，验证
ollama --version
3. 安装 Python（独立版本）
- 从 https://www.python.org/downloads/ 下载 Python 3.10.x
- 安装时勾选 Add to PATH
- 验证：
python --version
pip --version

第二步：配置 Python 环境
让 Python 能找到 KiCad 的 pcbnew 模块
进入项目目录并创建虚拟环境
cd C:\kicad-ai-inspector
# 使用 KiCad 的 python.exe 创建虚拟环境
& "C:\kicad\bin\python.exe" -m venv kicad-ai-env
激活虚拟环境
.\kicad-ai-env\Scripts\Activate.ps1
python -c "import pcbnew; print('✅ Success!')"



添加 KiCad 的 Python 路径
KiCad 的 Python 模块不在系统 PATH 中，需手动添加。
创建一个批处理文件 run_with_kicad.bat（放在项目根目录）：
@echo off
REM 确保 KiCad bin 在 PATH 最前面（避免其他版本干扰）
set PATH=C:\kicad\bin;%PATH%
REM 设置 Python 模块路径
set PYTHONPATH=C:\kicad\bin\Lib\site-packages;%PYTHONPATH%
REM 激活虚拟环境
call C:\kicad-ai-inspector\kicad-ai-env\Scripts\activate.bat
REM 进入项目目录
cd /d C:\kicad-ai-inspector
REM 启动交互式命令行
cmd /k

第三步：准备文件
1. docs/pcb_design_rules.txt
内容同前（公司规范）
2. requirements.txt


第四步：运行流程（Windows）
1. 启动配置好的终端
双击运行 run_with_kicad.bat
→ 会打开一个新命令行窗口，已激活虚拟环境 + 加载 KiCad 路径
Python extract_pcb.py运行脚本
2. 安装依赖（首次）
conda create -n rag-env-311 python=3.11 -y
conda activate rag-env-311
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
以后就在这个环境中运行build RAG和inspector就行
3. 拉取 Ollama 模型
ollama pull qwen3:4b
ollama pull nomic-embed-text


方案：使用系统 Python 处理 RAG
1. PCB 数据提取 → 用 KiCad 环境（extract_pcb.py）
2. RAG 向量库构建 → 用系统完整 Python 环境
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple langchain==0.3.7 langchain-community==0.3.7 langchain-core==0.3.17 langchain-text-splitters==0.3.0 chromadb==0.5.18 numpy==1.26.4 ollama==0.3.3 unstructured==0.18.27 PyYAML==6.0.2 requests==2.32.3 tqdm==4.66.6 pypdf==5.1.0
4. 构建知识库
python build_RAG.py
6. 生成检查报告
python inspect_pcb.py

⚠️ Windows 常见问题解决
❌ 问题1：ImportError: No module named 'pcbnew'
原因：未通过 run_with_kicad.bat 启动
解决：务必双击该 .bat 文件启动终端

---
❌ 问题2：ChromaDB 报错 sqlite3.OperationalError
原因：Windows 上 ChromaDB 默认使用 SQLite，多进程冲突
解决：在 build_rag.py 和 inspect_pcb.py 开头加：
import os
os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"  # 或直接用内存模式

---
❌ 问题3：中文乱码
确保所有 .txt 文件保存为 UTF-8 编码（用 VS Code 或 Notepad++ 设置）

---
❌ 问题4：Ollama 无法访问
- 确保 Ollama 已启动（任务栏有图标）
- 在 PowerShell 中测试：
curl http://localhost:11434/api/tags

---
✅ 最终效果
在 Windows 命令行中看到类似输出：
📋 PCB 智能检查报告:
==================================================
1. 发现 3 处走线宽度为 0.12mm，低于规范要求的 0.15mm。
2. 未检测到去耦电容信息，建议检查 U1～U5 电源引脚。
...

---
📌 总结：Windows 部署要点
所有print日志文件保存到txt或者log，因为kicad不支持打印

清理现有环境
# 删除旧环境
rd /s /q C:\kicad-ai-inspector\rag-env
# 创建新虚拟环境（使用你的 Anaconda Python 3.13）
python -m venv rag-env
.\rag-env\Scripts\Activate.ps1


总结：先用kicad里边自带的python创建一个虚拟环境，因为里边包含一个pcbnew包，而系统python没有，然后需要另一个环境推荐python3.1.1，按照requestments里边安装，创建环境，运行build_RAG.py生成build_RAG.log和chroma_db文件夹，运行inspect_pcb.py成功构建知识库后，调用本地大模型生成报告pcb_analysis_report.txt
