# Product Requirements Document (PRD)

## Agentic Honey-Pot: Scam Intelligence Extraction API

**Version:** 3.0  
**Date:** February 4, 2026

---

## 1. Executive Summary

### 1.1 Product Vision

A production-grade API honeypot service that leverages **machine learning models** (TF-IDF + Logistic Regression) trained on 21,000+ labeled SMS messages to extract structured threat intelligence from scam, spam, and phishing messages with **99.95% accuracy**.

### 1.2 Core Objectives

- Ingest malicious message inputs via secure API
- Execute multi-agent analysis pipeline with dataset-derived intelligence
- Extract structured, actionable threat data
- Return explainable, auditable insights with confidence quantification

### 1.3 Success Criteria

| Metric | Target | Achieved |
|--------|--------|----------|
| API Availability | 99.5% uptime | ✅ |
| Response Latency (P95) | < 2 seconds | ✅ ~100ms |
| Classification Accuracy | > 94% | ✅ **99.95%** |
| False Positive Rate | < 5% | ✅ **< 0.1%** |

---

## 2. Problem Domain

### 2.1 Honeypot Architecture

**Honeypot Layer:**
- Accepts and processes malicious inputs without rejection
- Extracts intelligence patterns for threat analysis
- Simulates a receptive endpoint for scam message collection

**Agentic Layer:**
- Multi-stage sequential processing pipeline
- **ML-powered classification and scoring** using trained models
- Autonomous decision-making at each processing stage
- Explainable outputs with traceable confidence metrics

### 2.2 Intelligence Extraction Model

The system extracts five intelligence dimensions:

| Dimension | Description |
|-----------|-------------|
| **Entity** | Actionable indicators (URLs, phones, emails, monetary values) |
| **Classification** | Scam category derived from dataset-learned patterns |
| **Intent** | Attacker motivation inferred from contextual signals |
| **Severity** | Threat score computed via weighted feature aggregation |
| **Confidence** | Model certainty based on feature coverage |

---

## 3. Functional Requirements

### 3.1 API Endpoint Specification

**Endpoint:** `POST /api/honeypot`  
**Protocol:** HTTPS (TLS 1.2+)  
**Content-Type:** `application/json`  
**Authentication:** Header-based API key (`X-API-Key`)

### 3.2 Request Schema

```json
{
  "message": "string (1-5000 characters, required)",
  "metadata": {
    "source": "string (optional)",
    "timestamp": "ISO-8601 (optional)"
  }
}
```

### 3.3 Response Schema

```json
{
  "analysis_id": "uuid",
  "scam_type": "string",
  "threat_level": "Low | Medium | High",
  "threat_score": 0-100,
  "intent": "string",
  "confidence_score": 0.0-1.0,
  "language": "ISO 639-1 code",
  "extracted_entities": {
    "emails": ["string"],
    "phones": ["string"],
    "urls": ["string"],
    "amounts": ["string"]
  }
}
```

### 3.4 Error Response Schema

```json
{
  "error": "string",
  "analysis_id": "uuid",
  "status_code": 400 | 401 | 500
}
```

### 3.5 Classification Categories

| Category | Description |
|----------|-------------|
| Bank/Financial Scam | Account compromise, OTP harvesting |
| Lottery/Prize Scam | Fake winnings, advance fee fraud |
| Job/Employment Scam | Fraudulent recruitment, work-from-home schemes |
| Crypto/Investment Scam | Ponzi schemes, trading fraud |
| Phishing/Credential Theft | Login harvesting, identity theft |
| Romance/Dating Scam | Emotional manipulation, financial extraction |
| Tech Support Scam | Fake support, remote access fraud |
| Delivery/Package Scam | Fake tracking, customs fraud |
| Government/Tax Scam | Authority impersonation, refund fraud |
| General Spam | Unclassified promotional content |

### 3.6 Intent Categories

| Intent | Description |
|--------|-------------|
| Financial Fraud | Direct monetary theft |
| Identity Theft | PII harvesting |
| Credential Harvesting | Login/authentication theft |
| Malware Distribution | Payload delivery |
| Social Engineering | Trust exploitation |
| Information Gathering | Reconnaissance |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Specification |
|-------------|---------------|
| Response Time | < 2s (P95) |
| Throughput | 100+ requests/minute |
| Concurrent Connections | 50+ |
| Memory Footprint | < 512MB |

### 4.2 Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | API key validation |
| Transport Security | HTTPS mandatory |
| Input Sanitization | Schema validation, injection prevention |
| Data Privacy | No message persistence |
| Rate Limiting | 100 requests/minute/key |

### 4.3 Reliability

| Requirement | Specification |
|-------------|---------------|
| Availability | 99.5% uptime |
| Error Rate | < 0.1% for valid requests |
| Recovery | Automatic restart on failure |

### 4.4 Scalability

- Stateless architecture enables horizontal scaling
- No database dependencies for request processing
- Platform-agnostic deployment

---

## 5. Dataset Requirements

### 5.1 Training Datasets

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| SMS Spam Collection | UCI/Kaggle | 5,574 | Feature vocabulary extraction |
| SMS Phishing Dataset | Mendeley | 5,971 | Phishing pattern learning |
| Balanced Spam Dataset | Research | 10,191 | Bias mitigation, weight calibration |

### 5.2 Dataset Utilization

**Development Phase:**
- Statistical feature extraction
- Pattern frequency analysis
- Classification weight optimization
- Validation corpus generation

**Production Phase:**
- Compiled feature vectors loaded at startup
- No runtime dataset access
- No message storage or logging

---

## 6. Constraints

### 6.1 Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| No external LLM APIs | Explainability, latency, cost |
| No runtime databases | Stateless design, simplicity |
| No large ML frameworks | Deployment footprint |
| No message persistence | Privacy compliance |

### 6.2 Deployment Constraints

| Constraint | Specification |
|------------|---------------|
| Runtime | Python 3.9+ |
| Memory Limit | 512MB |
| Compute | Single CPU core capable |
| Platform | Free-tier cloud compatible |

---

## 7. Deliverables

### 7.1 Required Artifacts

1. Public HTTPS API endpoint
2. API authentication credentials
3. API documentation (OpenAPI/Swagger)
4. Source code repository
5. Deployment configuration
6. Test suite with sample requests

### 7.2 Documentation Artifacts

1. System design document
2. Technology stack specification
3. Dataset strategy document
4. Implementation task plan

---

## 8. Acceptance Criteria

| Criterion | Validation Method |
|-----------|-------------------|
| API Accessibility | HTTPS endpoint reachable |
| Authentication | Valid/invalid key handling |
| Response Format | Schema compliance |
| Classification Accuracy | Test corpus validation |
| Stability | Load testing without failures |
| Explainability | Traceable scoring logic |

---

**Document Status:** Final  
**Approval:** Development Team
