# NetSentinel Windows Service Installer
# Requires: NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "uninstall", "start", "stop", "status")]
    [string]$Action = "install"
)

$ServiceName = "NetSentinel"
$DisplayName = "NetSentinel IDS"
$Description = "NetSentinel Intrusion Detection System"
$InstallDir = "C:\Program Files\NetSentinel"
$PythonExe = (Get-Command python).Source
$MainScript = Join-Path $InstallDir "main.py"

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "❌ This script requires administrator privileges" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

function Install-Service {
    Write-Host "======================================"
    Write-Host "NetSentinel Service Installer"
    Write-Host "======================================"
    Write-Host ""
    
    # Check if NSSM is installed
    if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
        Write-Host "❌ NSSM not found!" -ForegroundColor Red
        Write-Host "Please install NSSM from: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "Or use: choco install nssm" -ForegroundColor Yellow
        exit 1
    }
    
    # Create installation directory
    Write-Host "📦 Creating installation directory..."
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    
    # Copy files
    Write-Host "📋 Copying files..."
    $SourceDir = Split-Path -Parent $PSScriptRoot
    Copy-Item -Path "$SourceDir\*" -Destination $InstallDir -Recurse -Force
    
    # Install Python dependencies
    Write-Host "📦 Installing Python dependencies..."
    & $PythonExe -m pip install -r "$InstallDir\requirements.txt"
    
    # Install service using NSSM
    Write-Host "⚙️  Installing Windows service..."
    & nssm install $ServiceName $PythonExe $MainScript
    & nssm set $ServiceName DisplayName $DisplayName
    & nssm set $ServiceName Description $Description
    & nssm set $ServiceName AppDirectory $InstallDir
    & nssm set $ServiceName Start SERVICE_AUTO_START
    
    # Configure logging
    $LogDir = Join-Path $InstallDir "logs"
    & nssm set $ServiceName AppStdout "$LogDir\service-stdout.log"
    & nssm set $ServiceName AppStderr "$LogDir\service-stderr.log"
    & nssm set $ServiceName AppRotateFiles 1
    & nssm set $ServiceName AppRotateBytes 10485760  # 10MB
    
    Write-Host ""
    Write-Host "✅ Service installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  Start:   net start $ServiceName"
    Write-Host "  Stop:    net stop $ServiceName"
    Write-Host "  Status:  sc query $ServiceName"
    Write-Host ""
    Write-Host "Dashboard: http://localhost:5000"
    Write-Host ""
}

function Uninstall-Service {
    Write-Host "🗑️  Uninstalling NetSentinel service..."
    
    # Stop service if running
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        Write-Host "Stopping service..."
        Stop-Service -Name $ServiceName
    }
    
    # Remove service
    & nssm remove $ServiceName confirm
    
    Write-Host "✅ Service uninstalled" -ForegroundColor Green
}

function Start-NetSentinelService {
    Write-Host "▶️  Starting NetSentinel service..."
    Start-Service -Name $ServiceName
    Write-Host "✅ Service started" -ForegroundColor Green
}

function Stop-NetSentinelService {
    Write-Host "⏹️  Stopping NetSentinel service..."
    Stop-Service -Name $ServiceName
    Write-Host "✅ Service stopped" -ForegroundColor Green
}

function Get-ServiceStatus {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Service Status: $($service.Status)" -ForegroundColor Cyan
        Write-Host "Display Name: $($service.DisplayName)"
        Write-Host "Start Type: $($service.StartType)"
    } else {
        Write-Host "❌ Service not installed" -ForegroundColor Red
    }
}

# Execute action
switch ($Action) {
    "install"   { Install-Service }
    "uninstall" { Uninstall-Service }
    "start"     { Start-NetSentinelService }
    "stop"      { Stop-NetSentinelService }
    "status"    { Get-ServiceStatus }
}
