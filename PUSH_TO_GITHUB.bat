@echo off
cd /d v:\PARIVESH
echo Pushing PARIVESH monitor to GitHub...
git init
git add .
git status
git commit -m "PARIVESH EC monitor - 24/7 deploy" 2>nul || git commit -m "PARIVESH EC monitor - 24/7 deploy"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/VIGNESH-1996-A/parivesh-monitor.git
git push -u origin main
if errorlevel 1 (
  echo.
  echo If repo already has files, try: git pull origin main --allow-unrelated-histories
  echo Then run this batch again, or run: git push -u origin main
)
echo.
echo Done. If push asked for login, use GitHub username and a Personal Access Token (not password).
pause
