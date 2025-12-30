@echo off
echo Starting Digital Product Maturity Assessment System...
echo.

REM Start Backend
echo Starting Backend Server...
start cmd /k "cd backend\digital_product_maturity_project && python manage.py runserver"

REM Wait a bit for backend to start
timeout /t 5

REM Start Frontend
echo Starting Frontend Server...
start cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://127.0.0.1:8000/
echo Frontend: http://localhost:3000/
echo.
pause

