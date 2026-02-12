# Architecture Rules & Principles - Interlevel

## Document Purpose
This document establishes the architectural rules, principles, and constraints that **MUST** be followed throughout the design, development, and operation of the Interlevel platform. These rules ensure consistency, security, scalability, and maintainability.

---

## 1. Foundational Principles

### 1.1 Serverless-First
**Rule**: All compute workloads MUST use serverless services unless there is a documented exception approved by the architecture team.

**Rationale**: Serverless reduces operational overhead, provides automatic scaling, and aligns costs with usage.

**Implementation**:
- ✅ Use Lambda for all application logic
- ✅ Use API Gateway for HTTP endpoints
- ✅ Use Step Functions for orchestration
- ❌ Do NOT provision EC2 instances or ECS/EKS clusters without explicit approval

**Exceptions**: Long-running processes > 15 minutes may require Step Functions or Fargate.

---

### 1.2 Security by Default
**Rule**: Security measures MUST be implemented by default, not as optional features.

**Requirements**:
- All data at rest MUST be encrypted (S3, DynamoDB, RDS)
- All data in transit MUST use TLS 1.2+
- All API endpoints MUST require authentication
- Secrets MUST NEVER be hardcoded or stored in plain text
- All IAM policies MUST follow least privilege principle
- All generated agent code MUST pass security scanning before deployment

**Tools**:
- AWS Secrets Manager for credentials
- AWS KMS for encryption keys
- Static analysis tools (Bandit, Semgrep)
- Dependency scanning (Safety, Snyk)

---

### 1.3 Multi-Tenancy Isolation
**Rule**: User data and agent execution MUST be logically isolated to prevent cross-tenant access.

**Implementation**:
- Partition Keys: Use `user_id` or `tenant_id` in all DynamoDB tables
- IAM Policies: Scope agent execution roles to specific user resources
- S3 Prefixes: Store objects under `s3://bucket/user_id/...`
- Lambda Environment: Inject user-specific context via environment variables
- API Authorization: Validate JWT claims match resource ownership

**Testing**: Every API endpoint MUST have integration tests verifying tenant isolation.

---

### 1.4 Observability by Design
**Rule**: All services MUST emit structured logs, metrics, and traces.

**Requirements**:
- Use structured JSON logging (not plain text)
- Include correlation IDs in all logs and API responses
- Emit custom CloudWatch metrics for business events
- Use AWS X-Ray for distributed tracing
- Set up CloudWatch alarms for critical metrics

**Standard Log Format**:
```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARN|ERROR",
  "correlation_id": "uuid",
  "user_id": "string",
  "agent_id": "string",
  "message": "string",
  "context": {}
}
```

---

## 2. Development Standards

### 2.1 Infrastructure as Code
**Rule**: ALL infrastructure MUST be defined in code. Manual AWS Console changes are PROHIBITED in production.

**Tooling**:
- Primary: AWS CDK (Python or TypeScript)
- Alternative: AWS SAM for simple Lambda deployments
- Version Control: All IaC MUST be in Git

**Process**:
- Development changes → Pull Request → Code Review → CI/CD → Deployment
- Emergency fixes → Document as incident, remediate in code within 24 hours

---

### 2.2 Code Quality Standards
**Rule**: All code MUST meet quality standards before merging to main branch.

**Python Requirements**:
- Linting: `ruff` or `pylint` (score ≥ 8.0)
- Formatting: `black` with 100-character line length
- Type Hints: All functions MUST have type annotations
- Testing: Minimum 80% code coverage
- Security: Pass `bandit` with no high-severity issues

**Pre-Commit Hooks**:
```yaml
- Black formatting
- Ruff linting
- Type checking (mypy)
- Security scanning (bandit)
- Unit tests
```

---

### 2.3 API Design Standards
**Rule**: All APIs MUST follow RESTful conventions and OpenAPI 3.0 specification.

**Standards**:
- Use standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Use plural nouns for resources (`/agents`, not `/agent`)
- Use kebab-case for URLs (`/agent-configs`, not `/agent_configs`)
- Version APIs in URL (`/v1/agents`)
- Return standard HTTP status codes
- Include pagination for list endpoints (limit, offset, cursor)
- Include rate limiting headers

**Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {},
    "correlation_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

---

### 2.4 Database Design Standards
**Rule**: DynamoDB design MUST optimize for access patterns, not relational normalization.

**Principles**:
- Design tables based on query patterns, not entities
- Use single-table design for related entities when possible
- Always define Global Secondary Indexes (GSIs) for alternate queries
- Partition keys MUST provide even distribution
- Enable Point-in-Time Recovery for all production tables
- Use DynamoDB Streams for audit trails and event sourcing

**Naming Convention**:
- Table names: `interlevel-{environment}-{entity}` (e.g., `interlevel-prod-agents`)
- Attribute names: `snake_case`

---

## 3. Security Rules

### 3.1 Generated Agent Code Security
**Rule**: All generated agent code MUST pass automated security validation before deployment.

**Validations**:
1. **Static Analysis**: Scan for SQL injection, command injection, path traversal
2. **Dependency Check**: No known CVEs in dependencies
3. **Secrets Detection**: No hardcoded credentials or API keys
4. **Network Policy**: Validate allowed egress destinations
5. **IAM Policy**: Verify least privilege permissions

**Prohibited Patterns** (auto-reject):
```python
# ❌ Prohibited
os.system(user_input)
exec(user_input)
eval(user_input)
subprocess.call(shell=True)
# Hardcoded credentials
api_key = "sk-1234..."
```

---

### 3.2 Token Budget Enforcement
**Rule**: All agent executions MUST enforce token budgets to prevent runaway costs.

**Implementation**:
- Pre-execution check: Verify user has sufficient token balance
- Real-time tracking: Increment counter after each LLM call
- Hard limits: Terminate execution if budget exceeded
- Soft limits: Send alerts at 80% threshold
- Default budget: 10K tokens per execution, 100K per agent/month

**Token Calculation**:
```python
total_tokens = prompt_tokens + completion_tokens + (api_calls * 100)
```

---

### 3.3 Secrets Management
**Rule**: Secrets MUST NEVER be logged, stored in code, or exposed in error messages.

**Storage**:
- Use AWS Secrets Manager for third-party API keys
- Use IAM roles for AWS service access
- Rotate secrets every 90 days (automated)
- Inject secrets at runtime via environment variables or SDK

**Access Control**:
- Least privilege IAM policies
- Audit all secret access via CloudTrail
- Revoke secrets immediately upon employee departure

---

## 4. Scalability Rules

### 4.1 Rate Limiting
**Rule**: All user-facing APIs MUST implement rate limiting to prevent abuse.

**Limits** (per user):
- Anonymous: 10 requests/minute
- Authenticated: 100 requests/minute
- Premium: 1000 requests/minute

**Implementation**: AWS API Gateway usage plans + Lambda authorizer for custom limits.

---

### 4.2 Pagination
**Rule**: All list endpoints MUST support pagination.

**Standard Parameters**:
- `limit`: Number of items per page (default 25, max 100)
- `offset` or `cursor`: Pagination token
- Response MUST include `next_token` for subsequent requests

**Example Response**:
```json
{
  "items": [...],
  "count": 25,
  "total": 150,
  "next_token": "cursor_abc123"
}
```

---

### 4.3 Timeout Policies
**Rule**: All external calls MUST have explicit timeout configurations.

**Standard Timeouts**:
- HTTP API calls: 30 seconds
- Database queries: 5 seconds
- LLM calls: 60 seconds
- Lambda execution: 15 minutes (max)

**Implementation**: Use `boto3` and `requests` timeout parameters.

---

## 5. Operational Rules

### 5.1 Environment Strategy
**Rule**: The platform MUST maintain separate environments with strict promotion policies.

**Environments**:
1. **Dev**: Developer experimentation, auto-deployed on commit
2. **Staging**: Pre-production testing, mirrors production config
3. **Production**: Customer-facing, requires approval and smoke tests

**Promotion Flow**:
```
Feature Branch → Dev → Staging → Production
                 (Auto)  (Manual) (Approval)
```

---

### 5.2 Deployment Strategy
**Rule**: All production deployments MUST use blue-green or canary strategies.

**Process**:
1. Deploy new version alongside old (blue-green)
2. Route 10% traffic to new version (canary)
3. Monitor error rates and latency for 15 minutes
4. Rollback automatically if error rate > 2%
5. Gradually increase to 50%, then 100%

**Rollback Criteria**:
- Error rate increase > 2%
- P95 latency increase > 50%
- Any critical alarm triggered

---

### 5.3 Monitoring & Alerting
**Rule**: All production services MUST have health checks and alerting configured.

**Required Alarms**:
- API Gateway 5xx errors > 1% of requests
- Lambda errors > 5% of invocations
- DynamoDB throttling events > 10/minute
- Token budget exceeded for any user
- Agent deployment failures

**Notification Channels**:
- Critical: PagerDuty (immediate escalation)
- High: Slack + Email
- Medium: Email only

---

### 5.4 Incident Response
**Rule**: All production incidents MUST follow the incident response playbook.

**Process**:
1. **Detection**: Alert triggered → On-call engineer notified
2. **Triage**: Assess severity (P0-P3), create incident channel
3. **Mitigation**: Rollback or hotfix to restore service
4. **Resolution**: Root cause analysis, post-mortem document
5. **Prevention**: Action items to prevent recurrence

**Post-Mortem Requirements** (P0/P1 incidents):
- Timeline of events
- Root cause analysis (5 Whys)
- Impact assessment
- Action items with owners and deadlines

---

## 6. Cost Management Rules

### 6.1 Budget Alerts
**Rule**: All AWS accounts MUST have budget alerts configured.

**Thresholds**:
- Alert at 50% of monthly budget
- Alert at 80% of monthly budget
- Alert at 100% of monthly budget
- Alert on any single service exceeding $500/day

---

### 6.2 Resource Tagging
**Rule**: ALL AWS resources MUST be tagged with standard tags.

**Required Tags**:
```yaml
Environment: dev|staging|production
Project: interlevel
Owner: team-name
CostCenter: engineering
ManagedBy: cdk|sam|manual
```

**Enforcement**: Use AWS Config rules to flag untagged resources.

---

### 6.3 Lambda Optimization
**Rule**: All Lambda functions MUST be right-sized for cost efficiency.

**Process**:
1. Use AWS Lambda Power Tuning tool quarterly
2. Review CloudWatch metrics (duration, memory usage)
3. Adjust memory allocation to optimize cost/performance
4. Remove unused functions after 30 days of inactivity

---

## 7. Compliance Rules

### 7.1 Data Retention
**Rule**: User data MUST be retained according to retention policies.

**Policies**:
- Execution logs: 30 days (CloudWatch), 1 year (S3)
- Agent code: Indefinite (versioned in S3)
- User data: Until account deletion + 30 days
- Audit logs: 7 years (compliance requirement)

---

### 7.2 Data Deletion
**Rule**: User data MUST be permanently deleted upon account deletion request.

**Process**:
1. User initiates deletion request
2. 30-day grace period (soft delete, can restore)
3. Hard delete after 30 days:
   - DynamoDB records deleted
   - S3 objects deleted (all versions)
   - Lambda functions deprovisioned
   - IAM roles removed
4. Confirmation sent to user

---

### 7.3 Audit Logging
**Rule**: All sensitive operations MUST be logged to CloudTrail.

**Logged Events**:
- User authentication
- Agent creation/modification/deletion
- IAM policy changes
- Secret access
- Token consumption anomalies
- Budget threshold exceeded

**Retention**: 7 years in S3 with MFA delete protection.

---

## 8. Exception Process

### 8.1 Requesting Exceptions
**Rule**: Deviations from these rules MUST be formally requested and approved.

**Process**:
1. Submit exception request with justification
2. Architecture review board evaluates risk vs. benefit
3. Approved exceptions documented with expiration date
4. Re-evaluate exceptions every 6 months

**Required Information**:
- Rule being violated
- Business/technical justification
- Risk assessment
- Mitigation plan
- Expiration date

---

## 9. Enforcement

### 9.1 Automated Enforcement
**Tools**:
- AWS Config: Tag compliance, encryption checks
- Security Hub: Security best practices
- Pre-commit hooks: Code quality
- CI/CD pipeline: Automated tests and scans

### 9.2 Manual Review
**Process**:
- Architecture review for major features
- Security review for agent deployment changes
- Quarterly audit of exceptions

---

## 10. Document Maintenance

**Review Cadence**: Quarterly
**Owner**: Platform Architecture Team
**Approval**: Required for substantive changes
**Version Control**: Track in Git with changelog

---

**Document Version**: 1.0
**Last Updated**: 2026-02-07
**Next Review**: 2026-05-07
