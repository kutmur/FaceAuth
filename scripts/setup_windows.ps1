# FaceAuth Windows Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File setup_windows.ps1

param(
    [switch]$SkipDependencies,
    [switch]$DevMode,
    [string]$InstallPath = "$env:USERPROFILE\FaceAuth"
)

Write-Host "🔐 FaceAuth Windows Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "❌ PowerShell 5.0 or later required" -ForegroundColor Red
    exit 1
}

# Check if running as administrator for system-wide install
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

Write-Host "📋 Setup Information:" -ForegroundColor Yellow
Write-Host "   Install Path: $InstallPath"
Write-Host "   Admin Mode: $isAdmin"
Write-Host "   Development Mode: $DevMode"

# Function to check command availability
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check Python installation
Write-Host "`n🐍 Checking Python installation..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "❌ Python not found. Installing Python..." -ForegroundColor Red
    
    # Download and install Python
    $pythonUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    try {
        Write-Host "📥 Downloading Python 3.11.5..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        
        Write-Host "🔧 Installing Python..." -ForegroundColor Yellow
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Remove-Item $pythonInstaller -Force
    } catch {
        Write-Host "❌ Failed to install Python: $_" -ForegroundColor Red
        exit 1
    }
}

# Verify Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.8+
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($matches) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "❌ Python 3.8+ required, found $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python version check failed" -ForegroundColor Red
    exit 1
}

# Check Git installation
Write-Host "`n📦 Checking Git installation..." -ForegroundColor Yellow

if (-not (Test-Command "git")) {
    Write-Host "❌ Git not found. Please install Git from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
} else {
    $gitVersion = git --version
    Write-Host "✅ $gitVersion" -ForegroundColor Green
}

# Create installation directory
Write-Host "`n📁 Creating installation directory..." -ForegroundColor Yellow

if (-not (Test-Path $InstallPath)) {
    try {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Host "✅ Created directory: $InstallPath" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create directory: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Directory exists: $InstallPath" -ForegroundColor Green
}

# Clone or update repository
Write-Host "`n📥 Setting up FaceAuth repository..." -ForegroundColor Yellow

Set-Location $InstallPath

if (Test-Path ".git") {
    Write-Host "🔄 Updating existing repository..." -ForegroundColor Yellow
    git pull origin main
} else {
    Write-Host "📥 Cloning FaceAuth repository..." -ForegroundColor Yellow
    git clone https://github.com/your-username/faceauth.git .
}

# Create virtual environment
Write-Host "`n🏗️ Creating virtual environment..." -ForegroundColor Yellow

$venvPath = "faceauth_env"
if (Test-Path $venvPath) {
    Write-Host "🔄 Virtual environment exists, updating..." -ForegroundColor Yellow
} else {
    python -m venv $venvPath
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n🔧 Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
if (-not $SkipDependencies) {
    Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
    
    try {
        # Install core dependencies first
        Write-Host "   Installing core dependencies..." -ForegroundColor Yellow
        pip install numpy opencv-python
        
        # Install PyTorch (CPU version for compatibility)
        Write-Host "   Installing PyTorch..." -ForegroundColor Yellow
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
        
        # Install remaining dependencies
        Write-Host "   Installing remaining dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        # Install development dependencies if in dev mode
        if ($DevMode -and (Test-Path "requirements-dev.txt")) {
            Write-Host "   Installing development dependencies..." -ForegroundColor Yellow
            pip install -r requirements-dev.txt
        }
        
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
        Write-Host "💡 Try running with -SkipDependencies and install manually" -ForegroundColor Yellow
    }
}

# Initialize configuration
Write-Host "`n⚙️ Initializing FaceAuth configuration..." -ForegroundColor Yellow

try {
    python main.py config-init
    Write-Host "✅ Configuration initialized" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Configuration initialization failed, will be created on first run" -ForegroundColor Yellow
}

# Run system check
Write-Host "`n🔍 Running system compatibility check..." -ForegroundColor Yellow

try {
    python main.py system-check
    Write-Host "✅ System check completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ System check failed, some features may not work properly" -ForegroundColor Yellow
}

# Set up Windows-specific features
Write-Host "`n🏠 Configuring Windows-specific features..." -ForegroundColor Yellow

# Add to PATH if needed
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$faceAuthPath = $InstallPath
if ($currentPath -notlike "*$faceAuthPath*") {
    Write-Host "   Adding FaceAuth to user PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$faceAuthPath", "User")
}

# Create desktop shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\FaceAuth.lnk"

try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "$InstallPath\demo.py"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.IconLocation = "$InstallPath\assets\faceauth.ico"
    $Shortcut.Description = "FaceAuth Privacy-First Face Authentication"
    $Shortcut.Save()
    Write-Host "✅ Desktop shortcut created" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not create desktop shortcut" -ForegroundColor Yellow
}

# Create Windows Defender exclusion (if admin)
if ($isAdmin) {
    Write-Host "`n🛡️ Configuring Windows Defender..." -ForegroundColor Yellow
    try {
        Add-MpPreference -ExclusionPath $InstallPath -ErrorAction SilentlyContinue
        Write-Host "✅ Added Windows Defender exclusion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not add Windows Defender exclusion" -ForegroundColor Yellow
    }
}

# Final setup verification
Write-Host "`n🎯 Final verification..." -ForegroundColor Yellow

$errors = @()

# Check Python works
try {
    $result = python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    Write-Host "✅ Python: $result" -ForegroundColor Green
} catch {
    $errors += "Python verification failed"
}

# Check core imports
try {
    python -c "import cv2, numpy, torch; print('Core dependencies OK')" | Out-Null
    Write-Host "✅ Core dependencies working" -ForegroundColor Green
} catch {
    $errors += "Core dependencies missing or broken"
}

# Check FaceAuth imports
try {
    python -c "from faceauth.core.enrollment import FaceEnrollmentManager; print('FaceAuth modules OK')" | Out-Null
    Write-Host "✅ FaceAuth modules working" -ForegroundColor Green
} catch {
    $errors += "FaceAuth modules not working"
}

# Setup completion
Write-Host "`n" -NoNewline
if ($errors.Count -eq 0) {
    Write-Host "🎉 FaceAuth setup completed successfully!" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    
    Write-Host "`n📚 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Run the demo: python demo.py" -ForegroundColor White
    Write-Host "2. Enroll your face: python main.py enroll-face your-username" -ForegroundColor White
    Write-Host "3. Test authentication: python main.py verify-face your-username" -ForegroundColor White
    Write-Host "4. Read documentation: docs\README.md" -ForegroundColor White
    
    Write-Host "`n🔗 Useful Commands:" -ForegroundColor Cyan
    Write-Host "   System check: python main.py system-check" -ForegroundColor White
    Write-Host "   List users: python main.py list-users" -ForegroundColor White
    Write-Host "   Get help: python main.py --help" -ForegroundColor White
    
} else {
    Write-Host "⚠️ Setup completed with warnings:" -ForegroundColor Yellow
    foreach ($error in $errors) {
        Write-Host "   • $error" -ForegroundColor Red
    }
    Write-Host "`nPlease check the troubleshooting guide: docs\TROUBLESHOOTING.md" -ForegroundColor Yellow
}

Write-Host "`n🏠 Installation Location: $InstallPath" -ForegroundColor Cyan
Write-Host "📖 Documentation: $InstallPath\docs\" -ForegroundColor Cyan
Write-Host "🆘 Support: https://github.com/your-username/faceauth/issues" -ForegroundColor Cyan

# Pause to show results
Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
