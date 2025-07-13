# Security Guide for Crypto/Stock Price Tracker

## Overview

This document outlines the security measures implemented in the Crypto/Stock Price Tracker application and provides guidance for secure deployment.

## Security Features Implemented

### 1. Input Validation
- **Symbol Validation**: All asset symbols are validated against a whitelist and pattern matching
- **Numeric Validation**: Price and percentage values are validated for reasonable ranges
- **Type Checking**: All inputs are type-checked before processing
- **Length Limits**: Input strings are limited to prevent buffer overflow attacks

### 2. SQL Injection Prevention
- **Parameterized Queries**: All database queries use parameterized statements
- **Input Sanitization**: User inputs are sanitized before database operations
- **Validation**: Database inputs are validated before insertion

### 3. Rate Limiting
- **API Rate Limiting**: Web endpoints are protected with rate limiting (60 requests/minute)
- **API Rate Limiting**: CoinGecko API calls are rate-limited to prevent abuse
- **Cooldown Periods**: Alert system implements cooldown periods to prevent spam

### 4. Web Security
- **Flask Debug Mode**: Disabled in production configuration
- **Security Headers**: Implemented security headers for web responses
- **Input Validation**: All API endpoints validate inputs
- **Error Handling**: Generic error messages prevent information disclosure

### 5. Configuration Security
- **Environment Variables**: Sensitive data stored in environment variables
- **No Hardcoded Credentials**: Passwords and keys are not hardcoded
- **Secure Defaults**: Configuration defaults prioritize security

### 6. Data Validation
- **Price Validation**: Prices are validated for reasonable ranges
- **Change Validation**: Percentage changes are validated for realistic values
- **Asset Type Validation**: Asset types are restricted to 'crypto' or 'stock'

## Security Configuration

### Environment Variables
Set these environment variables for secure operation:

```bash
# Email configuration (optional)
export EMAIL_PASSWORD="your-email-password"

# Database configuration (optional)
export DATABASE_URL="sqlite:///database/price_data.db"

# Flask secret key (recommended)
export SECRET_KEY="your-secret-key-here"
```

### File Permissions
Ensure proper file permissions:

```bash
# Set secure permissions for critical files
chmod 600 config.py
chmod 600 database/price_data.db
chmod 600 logs/price_logs.csv
```

### Network Security
- **Local Access Only**: By default, Flask binds to 127.0.0.1 (localhost only)
- **Firewall**: Consider using a firewall to restrict access
- **HTTPS**: Use HTTPS in production with proper SSL certificates

## Security Audit

Run the security audit script to check for issues:

```bash
python security_audit.py
```

This will check for:
- File permissions
- Configuration security
- Database security
- Dependency vulnerabilities
- Environment variable security

## Security Best Practices

### 1. Deployment
- Use HTTPS in production
- Set up proper firewall rules
- Use environment variables for secrets
- Regularly update dependencies
- Monitor logs for suspicious activity

### 2. Configuration
- Disable debug mode in production
- Use strong passwords for email/webhook services
- Limit database access
- Set appropriate file permissions

### 3. Monitoring
- Monitor application logs
- Set up alerts for unusual activity
- Regularly backup data
- Check for dependency updates

## Known Limitations

### 1. Authentication
- The application does not implement user authentication
- Consider adding authentication for production use

### 2. Authorization
- No role-based access control
- All users have full access to all features

### 3. Data Encryption
- Database is not encrypted at rest
- Consider encrypting sensitive data

## Security Recommendations

### For Development
1. Use virtual environments
2. Keep dependencies updated
3. Use security audit tools
4. Follow secure coding practices

### For Production
1. Use a reverse proxy (nginx)
2. Implement SSL/TLS
3. Set up monitoring and alerting
4. Regular security audits
5. Backup and recovery procedures

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** create a public issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for assessment and fix

## Security Checklist

Before deploying to production:

- [ ] Run security audit (`python security_audit.py`)
- [ ] Set environment variables
- [ ] Configure file permissions
- [ ] Disable debug mode
- [ ] Set up HTTPS
- [ ] Configure firewall rules
- [ ] Update dependencies
- [ ] Set up monitoring
- [ ] Test backup procedures

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Documentation](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

## Version History

- **v1.0**: Initial security implementation
- **v1.1**: Added input validation and rate limiting
- **v1.2**: Enhanced error handling and security headers
- **v1.3**: Added security audit script and documentation 