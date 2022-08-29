@echo off
python -m pip freeze > "global_modules.txt"
python -m pip uninstall -r "global_modules.txt" -y
DEL "global_modules.txt"
