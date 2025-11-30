@echo off
echo ===================================================
echo 🚀 Starting PolicyPARAKH (Capstone Project)
echo ===================================================

echo.
echo [1/2] Starting Backend (FastAPI)...
start cmd /k "cd backend && pip install -r requirements.txt && uvicorn main:app --reload"

echo.
echo [2/2] Starting Frontend (Next.js)...
start cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ✅ System is booting up! 
echo 🌐 Please wait a moment, then open: http://localhost:3000
echo.
pause
