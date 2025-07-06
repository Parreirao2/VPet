@echo off
echo 🐾 VPet Executable Builder 🐾
echo ================================

echo Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q ".venv"
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment!
    echo Make sure Python is installed and accessible from command line.
    pause
    exit /b 1
)

echo ✅ Virtual environment created successfully!

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing requirements in virtual environment...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements!
    pause
    exit /b 1
)

echo ✅ Requirements installed successfully!

echo.
echo Building executable...
.venv\Scripts\python.exe build_exe.py

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo Deactivating virtual environment...
deactivate

echo.
echo ✅ Build process completed successfully!
echo 📦 Your VPet executable is ready in the 'VPet_Distribution' folder
echo 🗑️  You can safely delete the '.venv' folder if you want to save space
pause