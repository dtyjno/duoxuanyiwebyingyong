# 进入项目根目录
cd /path/to/your_project

# 设置Python路径（关键步骤！）
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%cd%         # Windows

# 运行主程序
python main.py
