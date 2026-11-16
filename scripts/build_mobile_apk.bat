@echo off
echo ========================================================
echo SchoolGPT - Android Mobile APK Build (RSR Technologies)
echo ========================================================

cd apps\mobile

echo Checking dependencies...
call npm install

echo Building Android APK via Expo Application Services (EAS)...
call eas build -p android --profile preview

echo Build process submitted to Expo Cloud!
echo Check your Expo Dashboard or terminal output for the direct APK download link.
pause
