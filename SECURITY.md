# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ |
| < 1.0   | ❌ |

## Reporting a Vulnerability

Please report security vulnerabilities in GitHub issues.

Do not report security vulnerabilities through public GitHub issues.

We will respond within 48 hours and provide updates every 7 days.

## Security Measures

- All inputs are validated using Pydantic models
- CORS is properly configured
- Rate limiting is implemented
- Dependencies are regularly audited
- Secrets are managed through environment variables