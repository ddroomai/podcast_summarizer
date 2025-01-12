# src/deployment/setup.py
from pathlib import Path
import logging
import subprocess
import sys
import venv

class SystemSetup:
    """Handles system setup and deployment."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        
    def setup_environment(self):
        """Set up virtual environment and dependencies."""
        try:
            # Create virtual environment
            venv_path = self.base_path / 'venv'
            venv.create(venv_path, with_pip=True)
            
            # Install dependencies
            self.install_dependencies()
            
            # Create necessary directories
            self.create_directories()
            
            # Set up logging
            self.setup_logging()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {str(e)}")
            raise
    def install_dependencies(self):
        """Install project dependencies."""
        try:
            subprocess.run([
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(self.base_path / "requirements.txt")
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {str(e)}")
            raise
            
    def create_directories(self):
        """Create necessary project directories."""
        directories = [
            'logs',
            'cache',
            'output',
            'config',
            'src/core',
            'src/utils',
            'src/deployment',
            'src/monitoring',
            'src/integration',
            'tests/unit',
            'tests/integration'
        ]
        
        for dir_path in directories:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
    def setup_logging(self):
        """Configure logging system."""
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': str(self.base_path / 'logs' / 'setup.log'),
                    'formatter': 'standard'
                }
            },
            'root': {
                'handlers': ['file'],
                'level': 'INFO'
            }
        }
        
        logging.config.dictConfig(log_config)
    def verify_installation(self) -> Dict[str, bool]:
        """Verify system installation and setup."""
        verifications = {
            'venv': self.verify_virtual_environment(),
            'dependencies': self.verify_dependencies(),
            'directories': self.verify_directories(),
            'logging': self.verify_logging(),
            'configs': self.verify_configurations()
        }
        
        return verifications
        
    def verify_virtual_environment(self) -> bool:
        """Verify virtual environment setup."""
        venv_path = self.base_path / 'venv'
        if not venv_path.exists():
            self.logger.error("Virtual environment not found")
            return False
            
        # Check for python executable in venv
        python_exec = venv_path / 'Scripts' / 'python.exe' if sys.platform == 'win32' else venv_path / 'bin' / 'python'
        if not python_exec.exists():
            self.logger.error("Python executable not found in virtual environment")
            return False
            
        return True
        
    def verify_dependencies(self) -> bool:
        """Verify all required dependencies are installed."""
        try:
            # Get installed packages
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True
            )
            
            installed = {
                line.split('==')[0].lower()
                for line in result.stdout.splitlines()
            }
            
            # Check against requirements
            with open(self.base_path / 'requirements.txt') as f:
                required = {
                    line.split('==')[0].lower()
                    for line in f.readlines()
                    if line.strip() and not line.startswith('#')
                }
            
            missing = required - installed
            if missing:
                self.logger.error(f"Missing dependencies: {missing}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify dependencies: {str(e)}")
            return False            
    def verify_configurations(self) -> bool:
        """Verify all configuration files."""
        required_configs = [
            'config.yaml',
            'monitoring.yaml',
            'maintenance.yaml'
        ]
        
        config_dir = self.base_path / 'config'
        missing_configs = []
        
        for config_file in required_configs:
            if not (config_dir / config_file).exists():
                missing_configs.append(config_file)
                
        if missing_configs:
            self.logger.error(f"Missing configuration files: {missing_configs}")
            return False
            
        return True

class DeploymentManager:
    """Manages deployment process."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.setup = SystemSetup(base_path)
        self.logger = logging.getLogger(__name__)
        
    async def deploy(self):
        """Execute deployment process."""
        try:
            # 1. Setup environment
            self.logger.info("Setting up environment...")
            self.setup.setup_environment()
            
            # 2. Verify installation
            self.logger.info("Verifying installation...")
            verification_results = self.setup.verify_installation()
            
            if not all(verification_results.values()):
                raise DeploymentError("Installation verification failed")
                
            # 3. Initialize components
            self.logger.info("Initializing components...")
            await self.initialize_components()
            
            self.logger.info("Deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            raise

# Execution example
if __name__ == "__main__":
    try:
        base_path = Path(__file__).parent.parent.parent  # Get project root
        deployer = DeploymentManager(base_path)
        asyncio.run(deployer.deploy())
        print("Setup and deployment completed successfully")
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        sys.exit(1)    