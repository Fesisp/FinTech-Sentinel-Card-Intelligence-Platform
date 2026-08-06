# 💳 FinTech Sentinel - Enterprise Card Intelligence & PCI Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.6%2B-e92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![PCI-DSS](https://img.shields.io/badge/PCI--DSS-v4.0_Compliant-green?logo=security&logoColor=white)]()
[![Tests](https://img.shields.io/badge/Tests-20_Passed-brightgreen?logo=pytest&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **FinTech Sentinel** é uma plataforma de classe bancária (*Bank-Grade*) para **validação de cartões de crédito, inteligência de BINs (ISO/IEC 7812) e análise de risco de fraude** em tempo real. Projetado para gateways de pagamento, instituições financeiras e ecossistemas de e-commerce de alto volume.

---

## 🏛️ Arquitetura de Software (Clean Architecture & DDD)

```text
ai-assisted-card-validator/
├── app/
│   ├── api/                  # Camada de Apresentação REST & Middleware
│   │   ├── middleware.py     # Headers PCI-DSS, X-Correlation-ID, Timing
│   │   └── routes.py         # Endpoints FastAPI (/validate, /batch, /bin, /health)
│   ├── core/                 # Regras Globais & Segurança
│   │   ├── brands.py         # Engine de BINs & MII ISO/IEC 7812 (14 bandeiras)
│   │   ├── config.py         # Configurações & Máscaras PCI
│   │   ├── luhn.py           # Algoritmo Mod 10 (Luhn) otimizado
│   │   └── security.py       # Ofuscação PCI-DSS, HMAC SHA-256 & Entropia de Shannon
│   ├── domain/               # Contratos de Dados (Pydantic v2)
│   │   └── models.py         # Schemas de Validação, Resposta e Risco
│   ├── services/             # Camada de Aplicação / Casos de Uso
│   │   └── validator_service.py # Serviço Principal de Validação e Risco
│   └── static/               # Web Dashboard Empresarial (Terminal Financeiro)
│       ├── css/style.css
│       ├── js/app.js
│       └── index.html
├── tests/                    # Suíte de Testes Automatizados (Pytest)
│   ├── test_api.py
│   ├── test_brands.py
│   ├── test_core.py
│   └── test_security.py
├── card_validator.py         # CLI & Interface legada (Backward Compatible)
├── main.py                   # Ponto de Entrada FastAPI (Servidor Web & API)
└── requirements.txt          # Dependências do Projeto
```

---

## ✨ Destaques de Qualidade e Segurança

1. **🔒 PCI-DSS v4.0 Compliance (PAN Redaction & Tokenization)**:
   - Ofuscação de PAN preservando apenas BIN (6 dígitos) e últimos 4 dígitos.
   - Geração de token determinístico via **HMAC-SHA256** para auditoria de logs sem armazenar números reais de cartão.
2. **🧠 Análise Inteligente de Risco de Fraude (Fraud Risk Engine)**:
   - Medição da **Entropia de Shannon** do número do cartão (detecta padrões previsíveis/geradores).
   - Detecção de cartões de teste de gateways (Stripe, Adyen, Visa Test Cards).
   - Verificação de sequências numéricas (ex: `123456`) e dígitos repetidos.
3. **🌐 Suporte Avançado a Bandeiras Globais e Nacionais (14 Schemes)**:
   - Visa, MasterCard, Elo (Bandeira Brasileira), Hipercard, American Express, Discover, JCB, Diners Club, UnionPay, Maestro, Mir, Aura, Cabal.
   - Mapeamento MII (Major Industry Identifier) conforme **ISO/IEC 7812**.
4. **⚡ Dashboard Web Interativo & REST API (OpenAPI / Swagger)**:
   - Terminal web futurista com suporte a lote (*Batch Audit CSV*) e preview instantâneo.
   - Documentação interativa em `/docs` e `/redoc`.

---

## 🚀 Como Executar o Sistema

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Dashboard Web Empresarial & REST API
```bash
python main.py
# Ou através do script CLI:
python card_validator.py --server
```
Acesse a aplicação no navegador: **`http://localhost:8000`**  
Documentação da API: **`http://localhost:8000/docs`**

### 3. Modo Linha de Comando (CLI Legado & Batch)
```bash
# Testar números individuais:
python card_validator.py 4111111111111111 378282246310005

# Modo Prompt Interativo:
python card_validator.py
```

### 4. Executar Suíte de Testes Automatizados
```bash
pytest -v
```

---

## 🔌 Exemplos da API (REST JSON)

### Validar Cartão (`POST /api/v1/validate`)
```json
// Request
{
  "card_number": "4111 1111 1111 1111",
  "include_risk_analysis": true
}

// Response
{
  "masked_card": "4111 11** **** 1111",
  "bin": "411111",
  "last_four": "1111",
  "is_valid_luhn": true,
  "brand": "Visa",
  "brand_code": "VISA",
  "category": "Credit / Debit",
  "mii_industry": "Banking & Financial (Visa)",
  "cvv_length": 3,
  "card_token": "TOK_8F2A1C0E...",
  "risk_assessment": {
    "score": 35,
    "level": "MEDIUM",
    "flags": [
      "KNOWN_TEST_PAN (Visa Test Card)"
    ],
    "entropy": 0.996
  }
}
```

---

## 👨‍💻 Autor & Manutenção

**Felipe da Silva Spinola**  
*Desenvolvedor de Software & Especialista em Arquitetura de Sistemas*

License: MIT
