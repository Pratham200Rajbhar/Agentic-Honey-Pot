# System Design Document

## Agentic Honey-Pot: Scam Intelligence Extraction API

**Version:** 3.0  
**Date:** February 4, 2026

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL CLIENTS                            │
│         (Evaluation Systems, API Consumers, Web Apps)            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS (TLS 1.2+)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ FastAPI Application                                         │ │
│  │ • CORS Middleware • Request Logging • Exception Handling   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                          │
│  • API Key Extraction • Validation • Access Control             │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT VALIDATION LAYER                        │
│  • Schema Validation • Type Checking • Constraint Enforcement   │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATOR LAYER                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             MULTI-AGENT PROCESSING PIPELINE                 │ │
│  │                                                              │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │ │
│  │  │  Language    │───▶│    Text      │───▶│   Feature    │  │ │
│  │  │  Detection   │    │ Normalization│    │  Extraction  │  │ │
│  │  └──────────────┘    └──────────────┘    └──────────────┘  │ │
│  │                                                 │           │ │
│  │         ┌───────────────────────────────────────┘           │ │
│  │         ▼                                                   │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │ │
│  │  │Classification│───▶│   Threat     │───▶│    Intent    │  │ │
│  │  │    Agent     │    │   Scoring    │    │  Inference   │  │ │
│  │  └──────────────┘    └──────────────┘    └──────────────┘  │ │
│  │                                                 │           │ │
│  │         ┌───────────────────────────────────────┘           │ │
│  │         ▼                                                   │ │
│  │  ┌──────────────┐    ┌──────────────┐                      │ │
│  │  │  Confidence  │───▶│   Response   │                      │ │
│  │  │  Estimation  │    │  Aggregator  │                      │ │
│  │  └──────────────┘    └──────────────┘                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE LAYER                                │
│  • Schema Formatting • Status Code Assignment • JSON Encoding   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 API Gateway Layer

**Responsibilities:**

- HTTP request reception and routing
- CORS policy enforcement
- Global exception handling
- Request/response logging

**Configuration:**
| Parameter | Value |
|-----------|-------|
| CORS Origins | Configurable (default: permissive for evaluation) |
| Max Request Size | 10KB |
| Request Timeout | 30 seconds |

### 2.2 Authentication Layer

**Mechanism:** Stateless API key validation

**Flow:**

1. Extract `X-API-Key` header
2. Validate against authorized key set
3. Proceed on success; return 401 on failure

**Security Measures:**

- Keys stored in environment variables
- Constant-time comparison (timing attack prevention)
- Partial key logging only (first 8 characters)

### 2.3 Input Validation Layer

**Validation Rules:**
| Field | Constraint |
|-------|------------|
| message | Required, string, 1-5000 characters |
| metadata | Optional, object |

**Error Handling:**

- Malformed JSON → 400
- Missing required fields → 400
- Constraint violations → 400 with descriptive error

---

## 3. Agent Pipeline Design

### 3.1 Language Detection Agent

**Purpose:** Identify message language for downstream processing optimization

**Input:** Raw message text  
**Output:** ISO 639-1 language code

**Behavior:**

- Primary detection via character n-gram analysis
- Fallback to default (English) on detection failure
- Support for mixed-language content detection

### 3.2 Text Normalization Agent

**Purpose:** Standardize input for consistent feature extraction

**Operations:**
| Operation | Description |
|-----------|-------------|
| Unicode Normalization | NFC form standardization |
| Whitespace Normalization | Collapse multiple spaces, trim |
| Case Normalization | Lowercase conversion (entity-preserving) |
| Character Filtering | Remove control characters |

**Preservation Rules:**

- URLs preserved verbatim
- Email addresses preserved verbatim
- Phone numbers preserved verbatim

### 3.3 Feature Extraction Agent

**Purpose:** Extract structured features for classification and scoring

**Entity Extraction:**

| Entity Type      | Extraction Method                            |
| ---------------- | -------------------------------------------- |
| Email Addresses  | RFC 5322 pattern matching                    |
| Phone Numbers    | International format patterns (ITU-T E.164)  |
| URLs             | URI specification patterns (RFC 3986)        |
| Monetary Amounts | Multi-currency symbol and format recognition |

**Linguistic Feature Extraction:**

| Feature Category    | Description                                        |
| ------------------- | -------------------------------------------------- |
| Lexical Features    | Token frequency, vocabulary overlap with dataset   |
| Structural Features | Capitalization ratio, punctuation density          |
| Semantic Indicators | Presence of category-associated linguistic markers |

### 3.4 Classification Agent (Transformer-Powered)

**Purpose:** Categorize message into scam taxonomy using semantic embeddings and VSM.

**Model Type:** Fine-tuned DistilBERT + Vector Space Model (99.11% accuracy)

**Classification Categories:**

1. Bank/Financial Scam
2. Lottery/Prize Scam
3. Job/Employment Scam
4. Crypto/Investment Scam
5. Phishing/Credential Theft
6. Romance/Dating Scam
7. Tech Support Scam
8. Delivery/Package Scam
9. Government/Tax Scam
10. General Spam

**Classification Process:**

1. Tokenize text using DistilBertTokenizer.
2. Extract **Contextual Embeddings** (CLS token) via GPU inference.
3. Calculate **Cosine Similarity** against semantic prototypes in Vector Space.
4. Return category with the highest semantic match and confidence score.

**ML Model Details:**
| Parameter | Value |
|-----------|-------|
| Base Model | distilbert-base-uncased |
| Layers | 6 Transformer Blocks |
| Embedding Size | 768 dimensions |
| Inference | GPU-Accelerated (CUDA) |

### 3.5 Threat Scoring Agent (Transformer-Powered)

**Purpose:** Quantify message threat severity using Transformer probabilities.

**Scoring Model:**
The threat score is derived directly from the Transformer's classification head, which is fine-tuned to recognize the nuance of social engineering.

| Component          | Description                                   |
| ------------------ | --------------------------------------------- |
| Transformer Proba  | Primary source of truth for scam probability  |
| Contextual Signals | Built-in recognition of urgency and coercion  |
| Identity Signals   | Recognition of credential harvesting patterns |

**Score Computation:**

1. Get ML spam probability (0.0-1.0)
2. Convert to base score (probability × 100)
3. Add heuristic boosts for threat indicators
4. Normalize to 0-100 range

**Threat Level Thresholds:**
| Level | Score Range |
|-------|-------------|
| High | ≥ 70 |
| Medium | 30-69 |
| Low | < 30 |

### 3.6 Intent Inference Agent

**Purpose:** Determine attacker motivation

**Intent Taxonomy:**
| Intent | Description |
|--------|-------------|
| Financial Fraud | Direct monetary extraction |
| Identity Theft | PII collection |
| Credential Harvesting | Authentication data theft |
| Malware Distribution | Payload delivery |
| Social Engineering | Trust/relationship exploitation |
| Information Gathering | Reconnaissance activity |

**Inference Logic:**

- Primary: Mapped from scam category
- Override: Entity composition analysis (e.g., URL-only → Malware Distribution)

### 3.7 Confidence Estimation Agent

**Purpose:** Quantify classification certainty

**Confidence Factors:**
| Factor | Effect |
|--------|--------|
| Feature coverage | Higher coverage → Higher confidence |
| Score margin | Larger margin → Higher confidence |
| Message length | Adequate length → Higher confidence |
| Entity presence | Entities present → Higher confidence |

**Output:** Probability value in [0.0, 1.0] range

---

## 4. Data Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/honeypot
       │ {"message": "..."}
       ▼
┌─────────────────────┐
│   Authentication    │──── Invalid ──→ 401 Response
└──────┬──────────────┘
       │ Valid
       ▼
┌─────────────────────┐
│    Validation       │──── Invalid ──→ 400 Response
└──────┬──────────────┘
       │ Valid
       ▼
┌─────────────────────┐
│    Orchestrator     │
│    ┌────────────┐   │
│    │ Language   │───│───▶ "en"
│    │ Detection  │   │
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Normalize  │───│───▶ normalized_text
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Extract    │───│───▶ {entities, features}
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Classify   │───│───▶ "Bank Scam"
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Score      │───│───▶ 85
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Infer      │───│───▶ "Credential Harvesting"
│    └────────────┘   │
│    ┌────────────┐   │
│    │ Confidence │───│───▶ 0.85
│    └────────────┘   │
└──────┬──────────────┘
       ▼
┌─────────────────────┐
│  Response Builder   │
└──────┬──────────────┘
       ▼
       JSON Response
```

---

## 5. Error Handling

### 5.1 Error Categories

| Category             | Status Code | Condition                             |
| -------------------- | ----------- | ------------------------------------- |
| Authentication Error | 401         | Missing or invalid API key            |
| Validation Error     | 400         | Invalid request format or constraints |
| Processing Error     | 500         | Internal pipeline failure             |

### 5.2 Error Response Format

```json
{
  "error": "Error description",
  "analysis_id": "uuid",
  "status_code": 4xx|5xx
}
```

### 5.3 Graceful Degradation

- Agent failures isolated to affected agent
- Partial results returned when possible
- Comprehensive logging for debugging

---

## 6. Performance Architecture

### 6.1 Optimization Strategies

| Strategy                | Implementation                                     |
| ----------------------- | -------------------------------------------------- |
| Pattern Pre-compilation | Regex compilation at startup                       |
| ML Model Caching        | Singleton pattern for model loading                |
| Lazy Loading            | Feature weights loaded on first request            |
| Async Processing        | Non-blocking I/O for all agents                    |
| Model Serialization     | joblib for fast model load (~1s)                   |
| Early Termination       | Skip optional agents when confidence threshold met |

### 6.2 Resource Constraints

| Resource           | Limit               |
| ------------------ | ------------------- |
| Memory             | < 512MB             |
| CPU                | Single core capable |
| Startup Time       | < 5 seconds         |
| Request Processing | < 2 seconds         |

---

## 7. Security Architecture

### 7.1 Security Layers

| Layer          | Protection                      |
| -------------- | ------------------------------- |
| Transport      | TLS 1.2+ encryption             |
| Authentication | API key validation              |
| Input          | Schema validation, sanitization |
| Data           | No persistence, stateless       |

### 7.2 Threat Mitigations

| Threat              | Mitigation                             |
| ------------------- | -------------------------------------- |
| Unauthorized Access | API key requirement                    |
| Injection Attacks   | Input validation, no dynamic execution |
| Data Leakage        | No message storage, no PII logging     |
| DoS                 | Request size limits, rate limiting     |

---

## 8. Deployment Architecture

### 8.1 Deployment Models

| Model     | Configuration                      |
| --------- | ---------------------------------- |
| Container | Docker with Python base image      |
| PaaS      | Render/Railway with build commands |
| VM        | Direct Uvicorn execution           |

### 8.2 Environment Configuration

| Variable    | Purpose                               |
| ----------- | ------------------------------------- |
| API_KEYS    | Authorized key list                   |
| ENVIRONMENT | Runtime mode (development/production) |
| PORT        | Server binding port                   |
| LOG_LEVEL   | Logging verbosity                     |

### 8.3 Health Monitoring

**Health Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "ISO-8601",
  "version": "1.0.0"
}
```

---

## 9. Observability

### 9.1 Logging Strategy

| Event               | Log Level | Content                                    |
| ------------------- | --------- | ------------------------------------------ |
| Request Received    | INFO      | Timestamp, partial API key, message length |
| Processing Complete | INFO      | Duration, scam type, threat level          |
| Validation Failure  | WARNING   | Error type, field                          |
| Processing Failure  | ERROR     | Exception details                          |

### 9.2 Metrics

| Metric                      | Type                 |
| --------------------------- | -------------------- |
| Request Count               | Counter              |
| Response Latency            | Histogram            |
| Error Rate                  | Gauge                |
| Classification Distribution | Counter per category |

---

## 10. Testing Strategy

### 10.1 Test Categories

| Category          | Coverage Target        |
| ----------------- | ---------------------- |
| Unit Tests        | 90% for agents         |
| Integration Tests | All API endpoints      |
| Performance Tests | Latency and throughput |

### 10.2 Test Scenarios

| Scenario                  | Expected Outcome                   |
| ------------------------- | ---------------------------------- |
| Valid high-threat message | Correct classification, high score |
| Valid low-threat message  | Correct classification, low score  |
| Invalid API key           | 401 response                       |
| Malformed request         | 400 response                       |
| Edge case: Maximum length | Successful processing              |
| Edge case: Minimum length | Successful processing              |

---

## 11. Limitations

### 11.1 Known Limitations

| Limitation            | Impact                                |
| --------------------- | ------------------------------------- |
| Text-only processing  | No image/attachment analysis          |
| Language support      | Primary English, limited multilingual |
| Novel attack patterns | May not detect zero-day scam types    |
| Deep semantics        | Limited contextual understanding      |

### 11.2 Future Considerations

- Multi-modal input processing
- Expanded language support
- Feedback loop for model improvement
- Real-time threat feed integration

---

**Document Status:** Final  
**Last Updated:** February 3, 2026
