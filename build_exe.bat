@echo off
echo Installing requirements...
pip install -r requirements.txt
echo Generating icon and building Notes Hamza.exe...
python -c "from main import generate_app_icon; generate_app_icon()"
pyinstaller --noconsole --onefile --icon=icon.ico --name "Notes Hamza" main.py
echo Done! Check the 'dist' folder.
pause
