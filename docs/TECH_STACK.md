# Technology Stack Document

## Agentic Honey-Pot: Scam Intelligence Extraction API

**Version:** 3.0  
**Date:** February 4, 2026

---

## 1. Stack Overview

### 1.1 Design Principles

| Principle      | Rationale                            |
| -------------- | ------------------------------------ |
| Explainability | Traceable decisions, auditable logic |
| Lightweight    | Minimal dependencies, fast startup   |
| Portability    | Free-tier deployment compatible      |
| Reliability    | No external API dependencies         |

### 1.2 Stack Summary

```
┌─────────────────────────────────────┐
│        Technology Stack             │
├─────────────────────────────────────┤
│ Language:        Python 3.9+        │
│ Framework:       FastAPI            │
│ Server:          Uvicorn            │
│ Validation:      Pydantic           │
│ NLP:             Deep Learning      │
│ Configuration:   python-dotenv      │
│ Testing:         pytest             │
│ Deployment:      Container (CUDA)   │
├─────────────────────────────────────┤
│ ML Framework:    PyTorch/Transformers│
│ Architecture:    DistilBERT         │
│ Model Size:      ~260MB             │
│ Inference Style: GPU-Accelerated    │
└─────────────────────────────────────┘
```

---

## 2. Core Technologies

### 2.1 Runtime: Python 3.9+

**Selection Rationale:**

- Native async/await support
- Extensive NLP ecosystem
- Type hints for maintainability
- Cross-platform compatibility

**Version Constraint:** 3.9 minimum for modern syntax and performance

### 2.2 Web Framework: FastAPI

**Selection Rationale:**

| Capability           | Benefit                                       |
| -------------------- | --------------------------------------------- |
| Native Async         | High concurrency without threading complexity |
| OpenAPI Generation   | Automatic API documentation                   |
| Pydantic Integration | Request/response validation                   |
| Performance          | Comparable to Node.js frameworks              |
| Developer Experience | Clear error messages, IDE support             |

**Key Features Used:**

- Route decorators for endpoint definition
- Dependency injection for authentication
- Exception handlers for error responses
- CORS middleware for cross-origin access

### 2.3 ASGI Server: Uvicorn

**Selection Rationale:**

- ASGI compliance for async FastAPI
- Production-ready performance
- Simple configuration
- Built-in hot reload for development

**Deployment Configuration:**
| Mode | Command |
|------|---------|
| Development | `uvicorn app.main:app --reload` |
| Production | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 2.4 Data Validation: Pydantic

**Selection Rationale:**

- Native FastAPI integration
- Runtime type enforcement
- Automatic JSON schema generation
- Clear validation error messages

**Usage:**

- Request body validation
- Response serialization
- Configuration management

### 2.5 Language Detection: langdetect

**Selection Rationale:**

| Criterion    | langdetect                     |
| ------------ | ------------------------------ |
| Size         | < 1MB                          |
| Speed        | < 10ms/message                 |
| Accuracy     | Sufficient for major languages |
| Dependencies | None                           |

**Supported Languages:** 55+ including English, Hindi, Spanish, French

### 2.6 Text Processing: Python Standard Library

**Components Used:**
| Module | Purpose |
|--------|---------|
| `re` | Pattern matching, entity extraction |
| `unicodedata` | Unicode normalization |
| `string` | Character classification |

**Rationale:** Zero external dependencies for core NLP operations

---

## 3. Machine Learning Model Architecture

### 3.1 ML Framework: PyTorch / Transformers

**Selection Rationale:**

| Criterion        | Benefit                       |
| ---------------- | ----------------------------- |
| State-of-the-Art | Context-aware transformations |
| GPU-Accelerated  | Fast inference (CUDA)         |
| Semantic Depth   | Deep embedding VSM support    |
| Portability      | HuggingFace ecosystem         |

### 3.2 Model Components

| Component    | Implementation      | Purpose                       |
| ------------ | ------------------- | ----------------------------- |
| Tokenizer    | DistilBertTokenizer | Convert text to WordPiece IDs |
| Model        | DistilBERT          | Primary feature engine        |
| Preprocessor | Custom Python       | Text normalization            |

### 3.3 Model Specifications

| Specification    | Value                         |
| ---------------- | ----------------------------- |
| Training Samples | 31,705                        |
| Architecture     | Transformer (distilbert-base) |
| Embeddings       | 768-dimensional               |
| Model Accuracy   | **99.11%**                    |
| Model Size       | ~260MB                        |
| Inference Time   | ~25ms (GPU)                   |

### 3.4 Training Pipeline

1. **Data Loading:** Consolidation of 5+ SMS/Email datasets
2. **Preprocessing:** URL/phone/money normalization
3. **Validation:** Automated label flipping detection
4. **Training:** Fine-tuned DistilBERT on NVIDIA GPU
5. **Evaluation:** Cross-dataset validation
6. **Serialization:** Export to HuggingFace format (safetensors)

**Output Artifacts:**

- `models/distilbert_spam/` - Fine-tuned model directory
- `models/distilbert_spam/metadata.json` - Model metrics

---

## 4. Supporting Technologies

### 4.1 Configuration: python-dotenv

**Purpose:** Environment-based configuration management

**Configuration Variables:**
| Variable | Purpose |
|----------|---------|
| API_KEYS | Authorized access keys |
| ENVIRONMENT | Runtime mode |
| PORT | Server port |
| LOG_LEVEL | Logging verbosity |

### 4.2 Testing: pytest

**Purpose:** Unit and integration testing

**Supporting Packages:**
| Package | Purpose |
|---------|---------|
| pytest | Test framework |
| httpx | Async HTTP client for API testing |
| pytest-cov | Coverage reporting |

### 4.3 Code Quality

| Tool   | Purpose              |
| ------ | -------------------- |
| black  | Code formatting      |
| flake8 | Linting              |
| mypy   | Static type checking |

---

## 5. Deployment Technologies

### 5.1 Containerization: Docker

**Base Image:** `python:3.11-slim`

**Container Characteristics:**
| Property | Value |
|----------|-------|
| Image Size | < 200MB |
| Startup Time | < 5 seconds |
| Memory Usage | < 512MB |

### 5.2 Platform Options

| Platform | Characteristics                        |
| -------- | -------------------------------------- |
| Render   | Free tier, auto-deploy, HTTPS included |
| Railway  | Fast deployment, no cold starts        |
| AWS/GCP  | Full control, requires configuration   |

### 5.3 Platform Configuration

**Render (render.yaml):**

```yaml
services:
  - type: web
    name: honeypot-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 6. Dependency Manifest

### 6.1 Production Dependencies

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
langdetect>=1.0.9
python-dotenv>=1.0.0
torch>=2.5.0
transformers>=4.40.0
scikit-learn>=1.3.0
```

### 6.2 Development Dependencies

```
pytest>=7.4.0
httpx>=0.26.0
pytest-cov>=4.1.0
black>=24.1.0
flake8>=7.0.0
mypy>=1.8.0
```

### 6.3 Optional Dependencies

```
pandas>=2.2.0  # Dataset analysis only
```

---

## 7. Technology Exclusions

### 7.1 Excluded Technologies

| Technology                                | Exclusion Rationale              |
| ----------------------------------------- | -------------------------------- |
| LLM APIs (GPT, Claude)                    | Latency, cost, explainability    |
| Databases (PostgreSQL, MongoDB)           | Unnecessary for stateless design |
| Heavy ML frameworks (TensorFlow, PyTorch) | Overkill for text classification |
| External threat APIs                      | Runtime dependency, availability |
| Redis/caching layers                      | Complexity without necessity     |

**Note:** We use **PyTorch** and **Transformers** for state-of-the-art accuracy.

### 7.2 Decision Rationale

**No External LLMs:**

- Explainability: Custom model provides traceable decisions
- Latency: Local processing < 100ms vs 2-5s API calls
- Reliability: No external service dependencies
- Cost: Zero per-request costs

**No Databases:**

- Stateless design requires no persistence
- No message logging for privacy
- Simplified deployment and scaling

---

## 8. Performance Characteristics

### 8.1 Benchmarks

| Metric        | Target  | Achieved    |
| ------------- | ------- | ----------- |
| Cold Start    | < 15s   | ~8s         |
| Warm Request  | < 100ms | ~25ms (GPU) |
| Memory (Idle) | < 512MB | ~350MB      |
| Memory (Load) | < 1GB   | ~750MB      |
| **Accuracy**  | > 98%   | **99.11%**  |

### 8.2 Optimization Techniques

| Technique               | Impact                |
| ----------------------- | --------------------- |
| Pattern pre-compilation | 10x regex performance |
| Lazy loading            | Faster cold start     |
| Async handlers          | Higher concurrency    |
| Minimal dependencies    | Smaller footprint     |

---

## 9. Security Considerations

### 9.1 Dependency Security

- Pin exact versions in production
- Regular vulnerability scanning
- Minimal dependency surface

### 9.2 Runtime Security

- No dynamic code execution
- Input validation at boundary
- Environment-based secrets

---

**Document Status:** Final  
**Last Updated:** February 4, 2026
