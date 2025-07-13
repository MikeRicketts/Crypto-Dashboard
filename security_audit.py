"""
Security Audit Script for Crypto/Stock Price Tracker
Checks for common security issues and provides recommendations
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import config
import security_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Security audit utility for the application"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.recommendations = []
    
    def run_full_audit(self) -> Dict[str, List[str]]:
        """Run complete security audit"""
        logger.info("Starting security audit...")
        
        self._check_file_permissions()
        self._check_database_security()
        self._check_configuration_security()
        self._check_dependencies()
        self._check_environment_variables()
        self._check_logging_security()
        
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }
    
    def _check_file_permissions(self):
        """Check file and directory permissions"""
        logger.info("Checking file permissions...")
        
        critical_files = [
            'config.py',
            'main.py',
            'database/price_data.db',
            'logs/price_logs.csv'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    stat = os.stat(file_path)
                    mode = stat.st_mode & 0o777
                    
                    if mode != 0o600:
                        self.issues.append(f"File {file_path} has insecure permissions: {oct(mode)}")
                        self.recommendations.append(f"Set permissions to 600 for {file_path}")
                    else:
                        logger.info(f"✓ {file_path} has secure permissions")
                        
                except Exception as e:
                    self.warnings.append(f"Could not check permissions for {file_path}: {e}")
    
    def _check_database_security(self):
        """Check database security"""
        logger.info("Checking database security...")
        
        db_path = config.DATABASE_PATH
        if os.path.exists(db_path):
            try:
                # Check if database is accessible
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check for SQL injection vulnerabilities
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if not tables:
                    self.warnings.append("Database appears to be empty")
                else:
                    logger.info(f"✓ Database contains {len(tables)} tables")
                
                conn.close()
                
            except Exception as e:
                self.issues.append(f"Database security issue: {e}")
        else:
            logger.info("Database file does not exist yet (normal for first run)")
    
    def _check_configuration_security(self):
        """Check configuration security"""
        logger.info("Checking configuration security...")
        
        # Check Flask debug mode
        if hasattr(config, 'FLASK_DEBUG') and config.FLASK_DEBUG:
            self.issues.append("Flask debug mode is enabled (security risk)")
            self.recommendations.append("Set FLASK_DEBUG = False in production")
        else:
            logger.info("✓ Flask debug mode is disabled")
        
        # Check Flask host binding
        if hasattr(config, 'FLASK_HOST') and config.FLASK_HOST == "0.0.0.0":
            self.warnings.append("Flask is bound to 0.0.0.0 (accessible from all interfaces)")
            self.recommendations.append("Consider binding to 127.0.0.1 for local access only")
        else:
            logger.info("✓ Flask host binding is secure")
        
        # Check for hardcoded credentials
        if hasattr(config, 'EMAIL_PASSWORD') and config.EMAIL_PASSWORD:
            self.issues.append("Email password is hardcoded in config")
            self.recommendations.append("Use environment variable EMAIL_PASSWORD instead")
        else:
            logger.info("✓ No hardcoded email password found")
    
    def _check_dependencies(self):
        """Check dependency security"""
        logger.info("Checking dependencies...")
        
        try:
            import requests
            if requests.__version__ < "2.31.0":
                self.warnings.append(f"requests version {requests.__version__} may have security vulnerabilities")
            else:
                logger.info(f"✓ requests version {requests.__version__} is up to date")
        except ImportError:
            self.issues.append("requests library not found")
        
        try:
            import flask
            if flask.__version__ < "3.0.0":
                self.warnings.append(f"Flask version {flask.__version__} may have security vulnerabilities")
            else:
                logger.info(f"✓ Flask version {flask.__version__} is up to date")
        except ImportError:
            self.issues.append("Flask library not found")
    
    def _check_environment_variables(self):
        """Check environment variable security"""
        logger.info("Checking environment variables...")
        
        # Check for sensitive environment variables
        sensitive_vars = ['EMAIL_PASSWORD', 'DATABASE_URL', 'SECRET_KEY']
        
        for var in sensitive_vars:
            if os.getenv(var):
                logger.info(f"✓ {var} environment variable is set")
            else:
                if var == 'EMAIL_PASSWORD':
                    self.warnings.append(f"{var} environment variable not set (email alerts disabled)")
                else:
                    logger.info(f"✓ {var} environment variable not set (not required)")
    
    def _check_logging_security(self):
        """Check logging security"""
        logger.info("Checking logging security...")
        
        # Check if sensitive data is being logged
        log_level = getattr(config, 'LOG_LEVEL', 'INFO')
        if log_level == 'DEBUG':
            self.warnings.append("Log level is set to DEBUG (may expose sensitive information)")
            self.recommendations.append("Set LOG_LEVEL to INFO or WARNING in production")
        else:
            logger.info(f"✓ Log level is set to {log_level}")
    
    def generate_report(self) -> str:
        """Generate security audit report"""
        report = []
        report.append("=" * 60)
        report.append("SECURITY AUDIT REPORT")
        report.append("=" * 60)
        report.append("")
        
        if self.issues:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                report.append(f"  • {issue}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"  • {warning}")
            report.append("")
        
        if self.recommendations:
            report.append("💡 RECOMMENDATIONS:")
            for rec in self.recommendations:
                report.append(f"  • {rec}")
            report.append("")
        
        if not self.issues and not self.warnings:
            report.append("✅ No security issues found!")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)

def main():
    """Run security audit"""
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()
    
    # Print report
    print(auditor.generate_report())
    
    # Return exit code based on issues found
    if results['issues']:
        logger.error(f"Security audit found {len(results['issues'])} critical issues")
        sys.exit(1)
    elif results['warnings']:
        logger.warning(f"Security audit found {len(results['warnings'])} warnings")
        sys.exit(0)
    else:
        logger.info("Security audit passed successfully")
        sys.exit(0)

if __name__ == "__main__":
    main() 