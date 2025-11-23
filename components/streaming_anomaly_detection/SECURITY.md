# Security Policy

## Overview

This document outlines security considerations, vulnerabilities, and best practices for the Real-Time Anomaly Detection on Streaming Data project.

**⚠️ IMPORTANT**: This is a **demonstration/portfolio project** designed for educational purposes and local development. It is **NOT production-ready** without implementing the security hardening measures described below.

## Security Status

### ✅ Implemented Security Measures

1. **Input Validation**
   - All API endpoint parameters are validated using Pydantic models
   - `item_id` parameters use regex validation to prevent injection (alphanumeric, hyphens, underscores only, max 50 chars)
   - Numeric parameters have reasonable bounds:
     - `mean`: -1000 to 1000
     - `variance`: 0 to 1000 (non-negative enforced)
     - `interval_sec`: 0.01 to 60 seconds (prevents resource exhaustion)

2. **Error Handling**
   - Custom exception handlers prevent information leakage
   - Detailed errors logged server-side, generic errors returned to clients
   - Stack traces not exposed in production mode

3. **Security Headers**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security` (HSTS)
   - `Content-Security-Policy: default-src 'self'`
   - Server header removed

4. **CORS Configuration**
   - CORS middleware configured (currently permissive for development)
   - Configurable allowed origins, methods, headers

5. **Resource Limits**
   - Message rate limited to max 100 msg/sec (interval_sec >= 0.01)
   - Parameter bounds prevent memory exhaustion

6. **Dependency Management**
   - Dependencies pinned to specific versions
   - Regular updates recommended

### ⚠️ Known Security Limitations

#### 1. **No Authentication / Authorization**

**Risk**: CRITICAL
- All API endpoints are publicly accessible
- Anyone can start/stop samplers
- No user isolation or access control

**Mitigation for Production**:
```python
# Add FastAPI dependency for API key authentication
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Then add dependency to endpoints:
@router.post("/endpoint", dependencies=[Depends(verify_api_key)])
```

Or use OAuth2/JWT:
```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

####  2. **Hardcoded Credentials**

**Risk**: HIGH
- OpenSearch config contains default credentials (admin/CHANGE_ME_IN_PRODUCTION)
- These are placeholders and **must not** be used in production

**Mitigation for Production**:
```bash
# Use environment variables
export OPENSEARCH_USER="secure_username"
export OPENSEARCH_PASSWORD="$(openssl rand -base64 32)"

# Or use secrets management
aws secretsmanager get-secret-value --secret-id opensearch-creds
```

Update Java code to read from environment:
```java
public static final String USER = System.getenv().getOrDefault("OPENSEARCH_USER", parameters.get("user"));
public static final String PASSWORD = System.getenv().getOrDefault("OPENSEARCH_PASSWORD", parameters.get("password"));
```

#### 3. **No Rate Limiting**

**Risk**: MEDIUM
- No global rate limiting on API endpoints
- Susceptible to DoS attacks

**Mitigation for Production**:
```bash
# Install slowapi
pip install slowapi

# Add to main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to endpoints:
@limiter.limit("5/minute")
@app.post("/endpoint")
async def endpoint(request: Request):
    ...
```

Or use API Gateway/nginx rate limiting.

#### 4. **No TLS/SSL**

**Risk**: HIGH (for production)
- HTTP only, no encryption in transit
- Credentials/data sent in clear text

**Mitigation for Production**:
```bash
# Use reverse proxy (nginx, Caddy) with TLS
# Or uvicorn with SSL:
uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem

# Generate self-signed cert for testing:
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

#### 5. **No Request Size Limits**

**Risk**: MEDIUM
- No explicit limits on request body size
- Could lead to memory exhaustion

**Mitigation for Production**:
```python
# Add to main.py:
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add nginx config:
client_max_body_size 1M;
```

#### 6. **Kafka Not Secured**

**Risk**: MEDIUM
- No authentication on Kafka broker
- No encryption (PLAINTEXT protocol)
- Anyone on network can produce/consume messages

**Mitigation for Production**:
```properties
# Enable SASL/SSL in Kafka
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="user" password="password";
ssl.truststore.location=/path/to/truststore.jks
ssl.truststore.password=password
```

#### 7. **No Audit Logging**

**Risk**: LOW
- User actions not logged for audit trail
- Difficult to track unauthorized access

**Mitigation for Production**:
```python
# Add audit logging middleware
@app.middleware("http")
async def audit_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    audit_logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
        "status_code": response.status_code,
        "duration_ms": duration * 1000,
        "user_agent": request.headers.get("user-agent")
    })
    return response
```

#### 8. **No Input Sanitization for Logging**

**Risk**: LOW
- User input logged directly (potential log injection)

**Mitigation**: Sanitize before logging:
```python
def sanitize_for_log(value: str) -> str:
    """Remove newlines and control characters."""
    return re.sub(r'[\n\r\t]', '', str(value))

logger.info(f"Processing: {sanitize_for_log(user_input)}")
```

## Vulnerability Reporting

### Supported Versions

This is a demonstration project. Security updates are provided on a best-effort basis.

### Reporting a Vulnerability

**Please do not open public issues for security vulnerabilities.**

Instead, email: digangidomenico@gmail.com

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

Response time: 7-14 days

## Security Checklist for Production Deployment

- [ ] **Authentication**
  - [ ] Implement API key or OAuth2/JWT authentication
  - [ ] Add role-based access control (RBAC)
  - [ ] Use secure session management

- [ ] **Network Security**
  - [ ] Enable TLS/SSL for all communications
  - [ ] Configure firewall rules
  - [ ] Use private networks/VPCs
  - [ ] Enable Kafka SSL/SASL

- [ ] **Secrets Management**
  - [ ] Remove all hardcoded credentials
  - [ ] Use environment variables (minimum)
  - [ ] Prefer AWS Secrets Manager / HashiCorp Vault
  - [ ] Rotate credentials regularly
  - [ ] Never commit secrets to version control

- [ ] **Input Validation**
  - [ ] Review and tighten all parameter bounds
  - [ ] Add request size limits
  - [ ] Implement rate limiting (global + per-endpoint)
  - [ ] Add CAPTCHA for public endpoints (if applicable)

- [ ] **Logging & Monitoring**
  - [ ] Implement audit logging
  - [ ] Set up security monitoring/SIEM
  - [ ] Configure alerts for suspicious activity
  - [ ] Sanitize logs to prevent injection

- [ ] **Infrastructure**
  - [ ] Keep dependencies updated
  - [ ] Run security scanners (Bandit, Safety, Snyk)
  - [ ] Use container scanning (Trivy, Clair)
  - [ ] Enable security patches auto-update

- [ ] **Application**
  - [ ] Disable debug mode in production
  - [ ] Remove unnecessary endpoints
  - [ ] Implement proper error handling
  - [ ] Add health/readiness probes

- [ ] **Data Protection**
  - [ ] Encrypt sensitive data at rest
  - [ ] Use HTTPS/TLS for data in transit
  - [ ] Implement data retention policies
  - [ ] Comply with GDPR/privacy regulations (if applicable)

- [ ] **Testing**
  - [ ] Run OWASP ZAP or Burp Suite scans
  - [ ] Perform penetration testing
  - [ ] Conduct security code review
  - [ ] Test disaster recovery procedures

## Security Tools

### Recommended Scanners

```bash
# Python dependency checker
pip install safety
safety check

# Python security linter
pip install bandit
bandit -r data-simulator/

# Container scanning
trivy image your-image:tag

# OWASP dependency check (Java)
mvn org.owasp:dependency-check-maven:check

# Secret scanning
git secrets --scan
trufflehog git file://. --only-verified
```

### Docker Security

```dockerfile
# Use specific versions, not 'latest'
FROM python:3.11.6-slim

# Run as non-root user
RUN useradd -m appuser
USER appuser

# Read-only filesystem (where possible)
# In docker-compose:
read_only: true

# Drop capabilities
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

## Compliance

### OWASP Top 10 2021

| Risk | Status | Notes |
|------|--------|-------|
| A01: Broken Access Control | ⚠️ Not Implemented | No authentication |
| A02: Cryptographic Failures | ⚠️ Partial | No TLS, hardcoded secrets |
| A03: Injection | ✅ Mitigated | Input validation implemented |
| A04: Insecure Design | ⚠️ Needs Review | Demo-focused, not production-hardened |
| A05: Security Misconfiguration | ⚠️ Needs Review | Debug mode, permissive CORS |
| A06: Vulnerable Components | ✅ Managed | Pinned dependencies |
| A07: Authentication Failures | ❌ Not Implemented | No authentication |
| A08: Data Integrity Failures | ⚠️ Partial | No signing/verification |
| A09: Logging Failures | ⚠️ Partial | Basic logging, no audit trail |
| A10: Server-Side Request Forgery | ✅ Not Applicable | No SSRF vectors |

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Kafka Security](https://kafka.apache.org/documentation/#security)
- [Flink Security](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/security/)
- [Docker Security](https://docs.docker.com/engine/security/)

## License

This security policy is part of the project licensed under Apache License 2.0.

---

**Last Updated**: 2025-11-23
**Next Review**: Quarterly (or after significant changes)
