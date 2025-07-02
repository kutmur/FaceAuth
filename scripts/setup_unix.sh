#!/bin/bash

# FaceAuth Setup Script for macOS/Linux
# Automated installation and environment setup for FaceAuth platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Function to install Python on macOS
install_python_macos() {
    print_status "Installing Python on macOS..."
    
    # Check if Homebrew is installed
    if ! command_exists brew; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Python
    brew install python@3.9
    print_success "Python installed via Homebrew"
}

# Function to install Python on Linux
install_python_linux() {
    print_status "Installing Python on Linux..."
    
    # Detect Linux distribution
    if command_exists apt-get; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip python3-venv python3-devel
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y python3 python3-pip python3-venv python3-devel
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -S python python-pip
    else
        print_error "Unsupported Linux distribution. Please install Python 3.8+ manually."
        exit 1
    fi
    
    print_success "Python installed via system package manager"
}

# Function to install system dependencies
install_system_deps() {
    local os_type=$1
    print_status "Installing system dependencies..."
    
    if [[ "$os_type" == "macos" ]]; then
        # macOS dependencies
        if command_exists brew; then
            brew install cmake pkg-config
            # OpenCV dependencies
            brew install opencv
        else
            print_warning "Homebrew not found. Some dependencies may need manual installation."
        fi
    elif [[ "$os_type" == "linux" ]]; then
        # Linux dependencies
        if command_exists apt-get; then
            sudo apt-get install -y \
                build-essential \
                cmake \
                pkg-config \
                libopencv-dev \
                python3-opencv \
                libgtk-3-dev \
                libboost-all-dev
        elif command_exists yum; then
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y cmake opencv-devel gtk3-devel boost-devel
        elif command_exists dnf; then
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install -y cmake opencv-devel gtk3-devel boost-devel
        elif command_exists pacman; then
            sudo pacman -S base-devel cmake opencv gtk3 boost
        fi
    fi
    
    print_success "System dependencies installed"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv faceauth_env
    
    # Activate virtual environment
    source faceauth_env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Python virtual environment created and activated"
}

# Function to install FaceAuth
install_faceauth() {
    print_status "Installing FaceAuth and dependencies..."
    
    # Ensure we're in the virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source faceauth_env/bin/activate
    fi
    
    # Install requirements
    pip install -r requirements.txt
    
    # Install FaceAuth in development mode
    pip install -e .
    
    print_success "FaceAuth installed successfully"
}

# Function to run tests
run_tests() {
    print_status "Running tests to verify installation..."
    
    # Ensure we're in the virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source faceauth_env/bin/activate
    fi
    
    # Run basic tests
    python -m pytest tests/ -v
    
    print_success "All tests passed"
}

# Function to create desktop shortcut (Linux only)
create_desktop_shortcut() {
    if [[ "$(detect_os)" == "linux" ]]; then
        print_status "Creating desktop shortcut..."
        
        cat > ~/Desktop/FaceAuth.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FaceAuth Demo
Comment=Privacy-first local face authentication
Exec=$(pwd)/faceauth_env/bin/python $(pwd)/demo.py
Icon=$(pwd)/assets/faceauth-icon.png
Terminal=true
Categories=Security;Utility;
EOF
        
        chmod +x ~/Desktop/FaceAuth.desktop
        print_success "Desktop shortcut created"
    fi
}

# Function to setup data directories
setup_directories() {
    print_status "Setting up data directories..."
    
    # Create necessary directories
    mkdir -p data/faces
    mkdir -p data/encrypted
    mkdir -p logs
    
    # Set appropriate permissions
    chmod 700 data/faces
    chmod 700 data/encrypted
    chmod 755 logs
    
    print_success "Data directories created with secure permissions"
}

# Main installation function
main() {
    print_status "Starting FaceAuth setup for $(detect_os)..."
    
    # Check if we're in the right directory
    if [[ ! -f "requirements.txt" ]]; then
        print_error "Please run this script from the FaceAuth root directory"
        exit 1
    fi
    
    local os_type=$(detect_os)
    
    if [[ "$os_type" == "unknown" ]]; then
        print_error "Unsupported operating system"
        exit 1
    fi
    
    # Check Python installation
    if ! command_exists python3; then
        print_warning "Python 3 not found. Installing..."
        if [[ "$os_type" == "macos" ]]; then
            install_python_macos
        else
            install_python_linux
        fi
    else
        # Check Python version
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_status "Found Python $python_version"
        
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8+ required. Found $python_version"
            exit 1
        fi
    fi
    
    # Install system dependencies
    install_system_deps "$os_type"
    
    # Setup Python environment
    setup_python_env
    
    # Setup directories
    setup_directories
    
    # Install FaceAuth
    install_faceauth
    
    # Run tests
    if [[ "${1:-}" != "--skip-tests" ]]; then
        run_tests
    fi
    
    # Create desktop shortcut (Linux only)
    create_desktop_shortcut
    
    print_success "FaceAuth setup completed successfully!"
    echo
    print_status "To get started:"
    echo "  1. Activate the virtual environment: source faceauth_env/bin/activate"
    echo "  2. Run the demo: python demo.py"
    echo "  3. Or try the enhanced demo: python enhanced_demo.py"
    echo
    print_status "For more information, see:"
    echo "  - README.md for overview"
    echo "  - docs/SETUP_GUIDE.md for detailed setup"
    echo "  - docs/USER_GUIDE.md for usage instructions"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help|-h)
            echo "FaceAuth Setup Script"
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-tests    Skip running tests after installation"
            echo "  --help, -h      Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main installation
main "$@"
