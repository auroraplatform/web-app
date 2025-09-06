import os
import logging
import re
from pathlib import Path
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CACertificateService:
    def __init__(self, scripts_dir: str = "/opt/scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.ca_cert_path = None
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate that the uploaded file is a certificate file"""
        if not filename:
            return False
        
        valid_extensions = ('.pem', '.crt', '.cer')
        return filename.lower().endswith(valid_extensions)
    
    def validate_certificate_content(self, content: bytes) -> bool:
        """Validate that the file content is a valid certificate"""
        try:
            content_str = content.decode('utf-8')
            return "BEGIN CERTIFICATE" in content_str
        except UnicodeDecodeError:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Return a safe file name: strip paths and keep [A-Za-z0-9._-]."""
        base = Path(filename).name
        base = re.sub(r'[^A-Za-z0-9._-]', '_', base)
        if not base:
            raise ValueError("Invalid filename.")
        return base
    
    def ensure_directory_exists(self) -> None:
        """Ensure the scripts directory exists with proper permissions"""
        if not self.scripts_dir.exists():
          raise RuntimeError(f"Scripts directory {self.scripts_dir} does not exist. Please ensure it was created during deployment.")

        # Check if we have write permissions
        if not os.access(self.scripts_dir, os.W_OK):
          raise RuntimeError(f"No write permission to directory {self.scripts_dir}")

    def save_certificate(self, content: bytes) -> None:
        """Save the certificate file with proper permissions"""
        # Ensure directory exists
        self.ensure_directory_exists()
        
        # Save the file
        with open(self.ca_cert_path, "wb") as f:
            f.write(content)
        
        # Set file permissions to 644 (rw-r--r--)
        self.ca_cert_path.chmod(0o644)
        
        logger.info(f"CA certificate saved to {self.ca_cert_path}")
    
    def verify_saved_file(self) -> bool:
        """Verify the saved file exists and is accessible"""
        if not self.ca_cert_path:
            return False
        return (
            self.ca_cert_path.exists() and 
            self.ca_cert_path.is_file() and 
            os.access(self.ca_cert_path, os.R_OK)
        )
    
    def get_file_info(self) -> dict:
        """Get information about the saved certificate file"""
        if not self.ca_cert_path or not self.ca_cert_path.exists():
            raise FileNotFoundError("Certificate file not found")
        
        stat = self.ca_cert_path.stat()
        return {
            "path": str(self.ca_cert_path),
            "size": stat.st_size,
            "permissions": oct(stat.st_mode)[-3:],
            "modified": stat.st_mtime
        }
    
    def upload_certificate(self, file_content: bytes, filename: str) -> dict:
        """Main method to handle certificate upload process"""
        try:
            # Validate file type
            if not self.validate_file_type(filename):
                logger.error(f"Invalid file type: {filename}")
                raise ValueError("Invalid file type. Please upload a .pem, .crt, or .cer certificate file.")
            
            # Validate certificate content
            if not self.validate_certificate_content(file_content):
                logger.error(f"Invalid certificate content in file: {filename}")
                logger.debug(f"File content preview: {file_content[:200]}...")
                raise ValueError("File doesn't appear to be a valid certificate file.")

            # Determine destination path
            safe_name = self.sanitize_filename(filename)
            self.ca_cert_path = self.scripts_dir / safe_name
            
            # Save the certificate
            logger.info(f"Saving certificate to: {self.ca_cert_path}")
            self.save_certificate(file_content)
            
            # Verify the save operation
            if not self.verify_saved_file():
                logger.error(f"Failed to verify saved file at: {self.ca_cert_path}")
                raise RuntimeError("Failed to save certificate file.")
            
            # Return success information
            file_info = self.get_file_info()
            return {
                "success": True,
                "message": "CA certificate uploaded successfully to web-app EC2",
                "file_info": file_info
            }
            
        except Exception as e:
            logger.error(f"Certificate upload failed: {str(e)}")
            raise
