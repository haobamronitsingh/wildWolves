@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
title WildWolves network server

for /f "delims=" %%I in ('powershell -NoProfile -Command "$route = Get-NetRoute -AddressFamily IPv4 -DestinationPrefix ''0.0.0.0/0'' -ErrorAction SilentlyContinue | Sort-Object RouteMetric, ifMetric | Select-Object -First 1; if ($route) { (Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $route.InterfaceIndex -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notlike ''127.*'' -and $_.IPAddress -notlike ''169.254.*'' } | Select-Object -First 1).IPAddress }"') do set "LAN_IP=%%I"

if not defined LAN_IP (
    echo Could not determine the active network IPv4 address.
    echo Start Django manually with: python manage.py runserver 0.0.0.0:8000
    pause
    exit /b 1
)

netsh advfirewall firewall show rule name="WildWolves Django Server" >nul 2>&1
if errorlevel 1 (
    echo Configuring Windows Firewall for port 8000...
    netsh advfirewall firewall add rule name="WildWolves Django Server" dir=in action=allow protocol=TCP localport=8000 profile=any >nul
    if errorlevel 1 (
        echo.
        echo Administrator permission is required. A Windows permission prompt will appear.
        powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile -Command New-NetFirewallRule -DisplayName ''WildWolves Django Server'' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -Profile Any'"
    )
    netsh advfirewall firewall show rule name="WildWolves Django Server" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo Windows Firewall permission was not granted. The server was not started.
        echo You can run this command in PowerShell as Administrator:
        echo netsh advfirewall firewall add rule name="WildWolves Django Server" dir=in action=allow protocol=TCP localport=8000 profile=any
        echo.
        pause
        exit /b 1
    )
)

netsh advfirewall firewall show rule name="WildWolves Django Server" >nul 2>&1
if errorlevel 1 (
    echo The Windows Firewall rule could not be verified. The server was not started.
    pause
    exit /b 1
)

set "PUBLIC_ORIGIN=http://%LAN_IP%:8000"
echo.
echo Open on this computer: http://127.0.0.1:8000
echo Open on devices connected to this hotspot: %PUBLIC_ORIGIN%
echo.
echo Make sure the other device is connected to the same mobile hotspot.
echo Keep this window open while using the site.
echo.
python manage.py runserver 0.0.0.0:8000
if errorlevel 1 (
    echo.
    echo Django stopped unexpectedly. Check the error above.
    pause
)
