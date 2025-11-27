@echo off
echo ========================================
echo   ICGS Complaints System - Deployment
echo ========================================
echo.

echo Step 1: Committing changes to Git...
git add .
git commit -m "Deploy ICGS Complaints System"
echo.

echo Step 2: Checking if Railway CLI is installed...
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Railway CLI not found. Installing...
    npm install -g @railway/cli
    echo.
)

echo Step 3: Initializing Railway project...
railway init
echo.

echo Step 4: Deploying to Railway...
railway up
echo.

echo Step 5: Setting up domain...
railway domain
echo.

echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your app is now live!
echo Run 'railway open' to view your app
echo.
pause
