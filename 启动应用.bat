@echo off
chcp 65001 >nul
echo ========================================
echo   AI 公文智能优化助手 - 快速启动
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 20+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] 安装后端依赖...
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，尝试继续...
)
cd ..

echo [2/4] 启动后端服务...
start "AI公文助手-后端" cmd /c "cd backend && python main.py"
timeout /t 3 /nobreak >nul

echo [3/4] 安装前端依赖...
cd frontend
if not exist node_modules (
    call npm install --silent
)

echo [4/4] 启动前端应用...
call npm run electron:dev
cd ..
