#!/usr/bin/env python3
"""
MoneyPrinterTurboPro - Automated Installation Script
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Any


class Installer:
    """Automated installer for MoneyPrinterTurboPro"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = sys.version_info
        
        # Colors for output
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def print_banner(self):
        """Print installation banner"""
        banner = f"""
{self.colors['cyan']}{self.colors['bold']}
╔══════════════════════════════════════════════════════════════╗
║                    MoneyPrinterTurboPro                     ║
║              The Ultimate AI Video Generation Platform      ║
║                        v2.0.0                              ║
╚══════════════════════════════════════════════════════════════╝
{self.colors['end']}
"""
        print(banner)
    
    def print_step(self, step: str, message: str):
        """Print a step with formatting"""
        print(f"{self.colors['blue']}[{step}]{self.colors['end']} {message}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{self.colors['green']}✅ {message}{self.colors['end']}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠️  {message}{self.colors['end']}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{self.colors['red']}❌ {message}{self.colors['end']}")
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        self.print_step("CHECK", "Python version compatibility")
        
        if self.python_version < (3, 11):
            self.print_error(f"Python 3.11+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        
        self.print_success(f"Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} is compatible")
        return True
    
    def check_system_requirements(self) -> bool:
        """Check system requirements"""
        self.print_step("CHECK", "System requirements")
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            if memory_gb < 8:
                self.print_warning(f"Recommended: 8GB+ RAM, found {memory_gb:.1f}GB")
            else:
                self.print_success(f"RAM: {memory_gb:.1f}GB")
        except ImportError:
            self.print_warning("Could not check memory (psutil not available)")
        
        # Check disk space
        try:
            disk = shutil.disk_usage(self.project_root)
            disk_gb = disk.free / (1024**3)
            
            if disk_gb < 10:
                self.print_warning(f"Recommended: 10GB+ free space, found {disk_gb:.1f}GB")
            else:
                self.print_success(f"Free disk space: {disk_gb:.1f}GB")
        except Exception:
            self.print_warning("Could not check disk space")
        
        return True
    
    def install_system_dependencies(self) -> bool:
        """Install system dependencies"""
        self.print_step("INSTALL", "System dependencies")
        
        if self.system == "windows":
            return self._install_windows_dependencies()
        elif self.system == "darwin":  # macOS
            return self._install_macos_dependencies()
        elif self.system == "linux":
            return self._install_linux_dependencies()
        else:
            self.print_error(f"Unsupported operating system: {self.system}")
            return False
    
    def _install_windows_dependencies(self) -> bool:
        """Install Windows dependencies"""
        try:
            # Check if Chocolatey is installed
            if not shutil.which("choco"):
                self.print_warning("Chocolatey not found. Please install it from https://chocolatey.org/")
                self.print_warning("Then run: choco install ffmpeg imagemagick")
                return False
            
            # Install dependencies
            subprocess.run(["choco", "install", "ffmpeg", "imagemagick", "-y"], check=True)
            self.print_success("Windows dependencies installed")
            return True
            
        except subprocess.CalledProcessError:
            self.print_error("Failed to install Windows dependencies")
            return False
    
    def _install_macos_dependencies(self) -> bool:
        """Install macOS dependencies"""
        try:
            # Check if Homebrew is installed
            if not shutil.which("brew"):
                self.print_warning("Homebrew not found. Please install it from https://brew.sh/")
                self.print_warning("Then run: brew install ffmpeg imagemagick")
                return False
            
            # Install dependencies
            subprocess.run(["brew", "install", "ffmpeg", "imagemagick"], check=True)
            self.print_success("macOS dependencies installed")
            return True
            
        except subprocess.CalledProcessError:
            self.print_error("Failed to install macOS dependencies")
            return False
    
    def _install_linux_dependencies(self) -> bool:
        """Install Linux dependencies"""
        try:
            # Detect package manager
            if shutil.which("apt"):
                # Ubuntu/Debian
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run([
                    "sudo", "apt", "install", "-y",
                    "ffmpeg", "imagemagick", "libmagickwand-dev",
                    "build-essential", "python3-dev"
                ], check=True)
            elif shutil.which("yum"):
                # CentOS/RHEL
                subprocess.run([
                    "sudo", "yum", "install", "-y",
                    "ffmpeg", "ImageMagick", "ImageMagick-devel",
                    "gcc", "gcc-c++", "python3-devel"
                ], check=True)
            elif shutil.which("pacman"):
                # Arch Linux
                subprocess.run([
                    "sudo", "pacman", "-S", "--noconfirm",
                    "ffmpeg", "imagemagick", "base-devel", "python"
                ], check=True)
            else:
                self.print_warning("Unsupported package manager. Please install ffmpeg and imagemagick manually")
                return False
            
            self.print_success("Linux dependencies installed")
            return True
            
        except subprocess.CalledProcessError:
            self.print_error("Failed to install Linux dependencies")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment"""
        self.print_step("CREATE", "Python virtual environment")
        
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            self.print_warning("Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            self.print_success("Virtual environment created")
            return True
        except subprocess.CalledProcessError:
            self.print_error("Failed to create virtual environment")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.print_step("INSTALL", "Python dependencies")
        
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            self.print_error("Virtual environment not found")
            return False
        
        # Determine pip path
        if self.system == "windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
        
        try:
            # Upgrade pip
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            
            # Install requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
                self.print_success("Python dependencies installed")
                return True
            else:
                self.print_error("requirements.txt not found")
                return False
                
        except subprocess.CalledProcessError:
            self.print_error("Failed to install Python dependencies")
            return False
    
    def setup_directories(self) -> bool:
        """Setup necessary directories"""
        self.print_step("SETUP", "Project directories")
        
        directories = [
            "logs",
            "cache",
            "temp",
            "output",
            "storage",
            "models",
            "config"
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
            
            self.print_success("Project directories created")
            return True
        except Exception as e:
            self.print_error(f"Failed to create directories: {e}")
            return False
    
    def setup_configuration(self) -> bool:
        """Setup configuration files"""
        self.print_step("SETUP", "Configuration files")
        
        try:
            # Copy example config
            example_config = self.project_root / "config.example.toml"
            config_file = self.project_root / "config.toml"
            
            if not config_file.exists() and example_config.exists():
                shutil.copy2(example_config, config_file)
                self.print_success("Configuration file created from example")
            else:
                self.print_warning("Configuration file already exists")
            
            return True
        except Exception as e:
            self.print_error(f"Failed to setup configuration: {e}")
            return False
    
    def check_gpu_support(self) -> bool:
        """Check GPU support"""
        self.print_step("CHECK", "GPU support")
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                self.print_success(f"GPU detected: {gpu_name} (Count: {gpu_count})")
                return True
            else:
                self.print_warning("No CUDA GPU detected")
                return False
        except ImportError:
            self.print_warning("PyTorch not available, GPU support disabled")
            return False
    
    def run_tests(self) -> bool:
        """Run basic tests"""
        self.print_step("TEST", "Basic functionality")
        
        try:
            # Test imports
            import moviepy
            import openai
            import anthropic
            import streamlit
            import fastapi
            
            self.print_success("All core modules imported successfully")
            return True
        except ImportError as e:
            self.print_error(f"Import test failed: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for the user"""
        self.print_step("NEXT", "Getting started")
        
        print(f"""
{self.colors['green']}🎉 Installation completed successfully!{self.colors['end']}

{self.colors['bold']}Next steps:{self.colors['end']}

1. {self.colors['cyan']}Configure API Keys{self.colors['end']}
   Edit config.toml and add your API keys for:
   - OpenAI, Anthropic, Google Gemini
   - Pexels, Pixabay, Unsplash
   - Azure Speech, ElevenLabs

2. {self.colors['cyan']}Start the Application{self.colors['end']}
   {self.colors['yellow']}Development mode:{self.colors['end']}
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   python run.py --dev
   
   {self.colors['yellow']}Production mode:{self.colors['end']}
   python run.py

3. {self.colors['cyan']}Access the Application{self.colors['end']}
   - WebUI: http://localhost:8501
   - API: http://localhost:8080/docs
   - Metrics: http://localhost:9090

4. {self.colors['cyan']}Docker Deployment{self.colors['end']}
   docker-compose up -d

{self.colors['bold']}Documentation:{self.colors['end']}
   - GitHub: https://github.com/yourusername/MoneyPrinterTurboPro
   - Issues: https://github.com/yourusername/MoneyPrinterTurboPro/issues
   - Discord: https://discord.gg/moneyprinter-pro

{self.colors['green']}Happy video generating! 🚀{self.colors['end']}
""")
    
    def install(self) -> bool:
        """Run complete installation"""
        self.print_banner()
        
        steps = [
            ("Python Version", self.check_python_version),
            ("System Requirements", self.check_system_requirements),
            ("System Dependencies", self.install_system_dependencies),
            ("Virtual Environment", self.create_virtual_environment),
            ("Python Dependencies", self.install_python_dependencies),
            ("Project Directories", self.setup_directories),
            ("Configuration", self.setup_configuration),
            ("GPU Support", self.check_gpu_support),
            ("Basic Tests", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.print_error(f"Installation failed at step: {step_name}")
                return False
        
        self.print_next_steps()
        return True


def main():
    """Main installation function"""
    installer = Installer()
    
    try:
        success = installer.install()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
