@echo off

:: Streamlit Dashboard 启动脚本
:: 双击运行此脚本启动Dashboard

cd /d "%~dp0"

echo ===========================================
echo   投资Dashboard 启动中...
echo ===========================================
echo.
echo 访问地址:
echo   本地: http://192.168.31.157:8501
echo   外部: http://112.4.45.29:8501
echo.
echo 按 Ctrl+C 可停止服务
echo ===========================================
echo.

streamlit run app.py --server.headless=True

pause
