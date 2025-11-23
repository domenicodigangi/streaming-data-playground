# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the streaming anomaly detection project.

## Workflows

### 1. CI Workflow (`ci.yml`)

**Triggers**: Push to main/develop/claude/* branches, Pull requests to main/develop

**Jobs**:
- ✅ **test-data-simulator**: Runs Python tests with coverage
  - Uses Python 3.11
  - Installs dependencies via Poetry
  - Runs pytest with coverage reporting
  - Uploads coverage to Codecov

- ✅ **lint-python**: Lints Python code
  - Black (code formatter)
  - Flake8 (style guide)
  - Bandit (security linter)
  - Safety (dependency vulnerability scanner)

- ✅ **build-flink-job**: Builds Flink JAR
  - Uses Java 11
  - Maven build with caching
  - Uploads JAR as artifact

- ✅ **docker-build-test**: Tests Docker builds
  - Builds all Docker images
  - Validates docker-compose configuration

- ✅ **markdown-lint**: Lints Markdown files
  - Checks documentation quality

### 2. Security Workflow (`security.yml`)

**Triggers**: Push to main/develop, Pull requests, Weekly schedule (Mondays)

**Jobs**:
- 🔒 **python-security**: Python security scanning
  - Bandit (SAST for Python)
  - Safety (dependency vulnerabilities)
  - pip-audit (package vulnerabilities)

- 🔒 **java-security**: Java security scanning
  - OWASP Dependency Check
  - Scans for known CVEs in dependencies

- 🔒 **docker-security**: Docker image scanning
  - Trivy (container vulnerability scanner)
  - Uploads results to GitHub Security tab

- 🔒 **secrets-scan**: Secret detection
  - TruffleHog (scans for exposed secrets)
  - Checks entire git history

## Testing Workflows Locally

### Option 1: Using `act` (GitHub Actions locally)

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run CI workflow
act push

# Run specific job
act -j test-data-simulator

# Run with specific event
act pull_request
```

### Option 2: Manual Component Testing

#### Test Python Code
```bash
cd components/streaming_anomaly_detection/data-simulator

# Install dependencies
poetry install --with dev

# Run tests
poetry run pytest --cov=simulator --cov-report=term -v

# Run linters
poetry run black --check src/ tests/
poetry run flake8 src/ tests/ --max-line-length=120
poetry run bandit -r src/

# Security scan
poetry run safety check
```

#### Build Flink JAR
```bash
cd components/streaming_anomaly_detection/flink/streamingad
mvn clean package -DskipTests
```

#### Test Docker Builds
```bash
cd components/streaming_anomaly_detection

# Build individual images
docker build -t data-simulator:test data-simulator/
docker build -t streamlit-gui:test gui/streamlit_streaming_ad/
docker build -t flink-job:test flink/

# Validate docker-compose
docker-compose config
```

### Option 3: Validate Workflow Syntax

```bash
# Install yamllint
pip install yamllint

# Validate YAML syntax
yamllint .github/workflows/*.yml

# Or use Python
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
python -c "import yaml; yaml.safe_load(open('.github/workflows/security.yml'))"
```

## Workflow Status

Once merged to main, workflow status will be visible at:
```
https://github.com/domenicodigangi/streaming-data-playground/actions
```

## Adding Badges to README

Add these badges to show workflow status:

```markdown
[![CI](https://github.com/domenicodigangi/streaming-data-playground/workflows/CI/badge.svg)](https://github.com/domenicodigangi/streaming-data-playground/actions/workflows/ci.yml)
[![Security Scan](https://github.com/domenicodigangi/streaming-data-playground/workflows/Security%20Scan/badge.svg)](https://github.com/domenicodigangi/streaming-data-playground/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/domenicodigangi/streaming-data-playground/branch/main/graph/badge.svg)](https://codecov.io/gh/domenicodigangi/streaming-data-playground)
```

## Troubleshooting

### Job Fails: "Poetry not found"
- Check Python version (must be 3.11+)
- Verify Poetry installation step runs correctly

### Job Fails: "Maven build failed"
- Ensure Java 11 is being used
- Check if pom.xml is valid
- Verify dependencies are accessible

### Docker Build Fails
- Check Dockerfile syntax
- Ensure all COPY paths exist
- Verify base images are available

### Security Scan False Positives
- Review Bandit report JSON for details
- Update `.bandit` config to exclude false positives
- Document exceptions in SECURITY.md

## Continuous Improvement

### To Add:
- [ ] Code coverage requirements (e.g., minimum 80%)
- [ ] Automatic dependency updates (Dependabot)
- [ ] Release automation
- [ ] Docker image publishing to registry
- [ ] Performance benchmarking
- [ ] Integration tests with actual Kafka/Flink

### To Configure:
- [ ] Branch protection rules requiring CI to pass
- [ ] CODEOWNERS file for PR reviews
- [ ] Issue templates
- [ ] PR templates

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Act (local testing)](https://github.com/nektos/act)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [Trivy](https://github.com/aquasecurity/trivy)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
