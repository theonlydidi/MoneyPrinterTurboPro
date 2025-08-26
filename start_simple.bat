@echo off
echo Starting MoneyPrinterTurboPro WebUI...
echo.
cd webui
python -m streamlit run main.py --server.port 8501
pause
