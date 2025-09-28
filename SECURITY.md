# Takeo-ORM Security Guide

## 🔒 Security Best Practices

### Environment Variables
- **NEVER** commit `.env` files
- Use `.env.example` as a template 
- Set real values only in local `.env` files
- Use secure passwords for production

### Database Configuration
```bash
# Copy the template
cp .env.example .env

# Edit with your secure values
DB_HOST=localhost
DB_PASSWORD=your_very_secure_password_here
```

### Pre-commit Security Scanning
This repository includes a pre-commit hook that scans for:
- Hardcoded passwords
- Database connection strings with credentials  
- API keys and tokens
- Other sensitive patterns

### Git History Cleanup
If you accidentally commit sensitive data:
```bash
# Create backup branch first
git branch backup-before-cleanup

# Use git filter-branch or BFG to clean history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Force push cleaned history
git push --force-with-lease origin main
```

### Production Deployment
1. Use environment variables or secret management systems
2. Enable SSL/TLS for database connections
3. Use restricted database users with minimal permissions
4. Regular password rotation
5. Monitor for exposed credentials in logs

### Security Checklist
- [ ] No hardcoded passwords in source code
- [ ] `.env` files in `.gitignore`  
- [ ] Environment variables used for all sensitive config
- [ ] Pre-commit hooks enabled
- [ ] SSL enabled for production databases
- [ ] Regular security audits of dependencies

## 🚨 Emergency Response
If sensitive data is exposed:
1. **Immediate**: Change all affected passwords
2. **Clean**: Remove from Git history using this guide
3. **Audit**: Check what was exposed and for how long  
4. **Learn**: Update processes to prevent recurrence

## 📞 Security Contact
Report security issues responsibly by creating a private issue or contacting the maintainers directly.