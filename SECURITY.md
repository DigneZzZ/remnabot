# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please send an email to the project maintainer. Please do not create a public issue.

## Security Best Practices

### Environment Variables

- Never commit `.env` file to the repository
- Use strong passwords for API access
- Change the default PIN code
- Rotate API credentials regularly

### Admin Access

- Limit admin IDs to trusted users only
- Use Telegram's privacy settings
- Enable 2FA on your Telegram account

### API Security

- Use HTTPS for production deployments
- Keep API credentials secure
- Use firewall rules to limit access
- Monitor API access logs

### Docker Security

- Run containers as non-root user (already configured)
- Keep base images updated
- Use Docker secrets for sensitive data in production
- Limit container resources

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Known Security Considerations

1. **PIN Code**: The PIN code is stored in plain text in environment variables. For production use, consider implementing more secure authentication methods.

2. **Admin IDs**: Admin IDs are checked at the application level. Make sure to keep the ADMIN_IDS environment variable secure.

3. **API Credentials**: API credentials are stored in environment variables. Use secure secret management in production.

4. **Logging**: Debug mode logs may contain sensitive information. Use INFO level logging in production.

## Security Updates

Security updates will be released as soon as possible. Please keep your installation up to date.
