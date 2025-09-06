import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ConnectionService:
    def __init__(self, scripts_dir: str = "/opt/scripts", terraform_dir: str = "/opt/terraform"):
        self.scripts_dir = Path(scripts_dir)
        self.terraform_dir = Path(terraform_dir)
        self.connect_script_path = self.scripts_dir / "connect-ec2.sh"
        self.disconnect_script_path = self.scripts_dir / "disconnect.sh"
        self.ca_cert_path = None
        self.ca_cert_filename = None

    def set_certificate_info(self, cert_path: Path) -> None:
        """Set the certificate path and filename based on the actual uploaded file"""
        self.ca_cert_path = cert_path
        self.ca_cert_filename = cert_path.name
    
    def validate_certificate_exists(self) -> None:
        """Verify that the CA certificate exists before attempting connection"""
        if not self.ca_cert_path:
            raise FileNotFoundError("Certificate path not set. Please set certificate path first.")
        if not self.ca_cert_path.exists():
            raise FileNotFoundError("CA certificate not found. Please upload a certificate first.")
    
    def validate_script_exists(self) -> None:
        """Verify that the connect script exists and is executable"""
        if not self.connect_script_path.exists():
            raise FileNotFoundError("connect-ec2.sh script not found")
    
        # # Ensure script has proper permissions
        # try:
        #     self.connect_script_path.chmod(0o755)
        # except PermissionError as e:
        #     raise PermissionError(f"Cannot set permissions on script {self.connect_script_path}: {e}")
        
        # Verify the script is actually executable
        if not os.access(self.connect_script_path, os.X_OK):
            raise PermissionError(f"Script {self.connect_script_path} is not executable")

    def validate_disconnect_script_exists(self) -> None:
        """Verify that the disconnect script exists and is executable"""
        if not self.disconnect_script_path.exists():
            raise FileNotFoundError("disconnect.sh script not found")
    
        # # Ensure script has proper permissions
        # try:
        #     self.disconnect_script_path.chmod(0o755)
        # except PermissionError as e:
        #     raise PermissionError(f"Cannot set permissions on script {self.disconnect_script_path}: {e}")
        
        # Verify the script is actually executable
        if not os.access(self.disconnect_script_path, os.X_OK):
            raise PermissionError(f"Script {self.disconnect_script_path} is not executable")
    
    def build_command(self, connection_params: Dict[str, str]) -> list:
        """Build the command array for the connect script"""
        return [
            str(self.connect_script_path),
            "-n", connection_params["name"],
            "-k", connection_params["broker"],
            "-t", connection_params["topic"],
            "-u", connection_params["username"],
            "-p", connection_params["password"],
            "-c", str(self.ca_cert_path),
            "-f", self.ca_cert_path.name
        ]

    def build_disconnect_command(self, connection_name: str) -> list:
        """Build the command array for the disconnect script"""
        return [
            str(self.disconnect_script_path),
            "-n", connection_name
        ]
    
    def setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for the script execution"""
        env = os.environ.copy()
        env['TERRAFORM_DIR'] = str(self.terraform_dir)
        return env
    
    def execute_connection_script(self, connection_params: Dict[str, str]) -> Dict[str, Any]:
        """Execute the connect-ec2.sh script with the given parameters"""
        try:
            # Validate prerequisites
            self.validate_certificate_exists()
            self.validate_script_exists()
            
            # Build command and environment
            cmd = self.build_command(connection_params)
            env = self.setup_environment()
            
            logger.info(f"Executing connection script: {' '.join(cmd)}")
            
            # Execute the script
            result = subprocess.run(
              cmd,
              capture_output=True,
              text=True,
              cwd="/opt",
              env=env
            )
            
            # Enhanced error handling
            if result.returncode != 0:
                error_msg = f"Script execution failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nStderr: {result.stderr}"
                if result.stdout:
                    error_msg += f"\nStdout: {result.stdout}"
            
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        
            # Check for error indicators in stdout (even with return code 0)
            if result.stdout and any(error_indicator in result.stdout.lower() for error_indicator in ['error', 'failed', 'exception']):
              logger.warning(f"Script completed but may have encountered issues: {result.stdout}")
            
            logger.info("Connection script executed successfully")
            
            return {
                "success": True,
                "message": f"Kafka connection '{connection_params['name']}' established successfully",
                "details": result.stdout,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Connection setup failed: {str(e)}")
            raise
    
    def execute_disconnect_script(self, connection_name: str) -> Dict[str, Any]:
        """Execute the disconnect.sh script with the given connection name"""
        try:
            # Validate prerequisites
            self.validate_disconnect_script_exists()
            
            # Build command and environment
            cmd = self.build_disconnect_command(connection_name)
            env = self.setup_environment()
            
            logger.info(f"Executing disconnect script: {' '.join(cmd)}")
            
            # Execute the script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/opt",
                env=env
            )
            
            if result.returncode != 0:
                error_msg = f"Disconnect script execution failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nStderr: {result.stderr}"
                if result.stdout:
                    error_msg += f"\nStdout: {result.stdout}"
                
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            if result.stdout and any(error_indicator in result.stdout.lower() for error_indicator in ['error', 'failed', 'exception']):
                logger.warning(f"Disconnect script completed but may have encountered issues: {result.stdout}")
            
            logger.info("Disconnect script executed successfully")
            
            return {
                "success": True,
                "message": f"Kafka connection '{connection_name}' disconnected successfully",
                "details": result.stdout,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Connection disconnect failed: {str(e)}")
            raise
