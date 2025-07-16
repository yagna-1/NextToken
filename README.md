# NexToken

A modern, secure authentication token system that improves upon JWT with enhanced security, dynamic revocation, and compact binary format.

## Features

- **Enhanced Security**: Uses Ed25519 elliptic curve signatures for stronger security than JWT's common algorithms
- **Dynamic Token Revocation**: Real-time token revocation without relying on expiration alone
- **Compact Token Format**: Uses CBOR (Concise Binary Object Representation) for smaller, more efficient tokens
- **Privacy Features**: Encrypted payload fields to protect sensitive data
- **Developer-Friendly**: Built with FastAPI and Python for easy integration

## Why NexToken?

Unlike traditional JWT tokens, NexToken provides:
- **Better Security**: Ed25519 signatures are more secure and faster than RSA/ECDSA
- **Real-time Control**: Revoke tokens instantly without waiting for expiration
- **Reduced Overhead**: CBOR format is more compact than JSON
- **Privacy**: Sensitive data in tokens can be encrypted

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn nextoken.main:app --reload
```

### Basic Usage

```python
import requests

# Issue a token
response = requests.post("http://localhost:8000/issue", json={
    "user_id": "user123",
    "email": "user@example.com",
    "expires_in": 3600
})
token = response.json()["token"]

# Verify a token
response = requests.post("http://localhost:8000/verify", json={"token": token})
print(response.json())

# Revoke a token
response = requests.post("http://localhost:8000/revoke", json={"token": token})
```

## API Endpoints

- `POST /issue` - Generate a new NexToken
- `POST /verify` - Verify and decode a NexToken
- `POST /revoke` - Revoke a NexToken
- `GET /health` - Health check endpoint

## Architecture

- **Token Structure**: Header + Payload + Signature in CBOR format
- **Encryption**: Ed25519 for signatures, AES for sensitive payload fields
- **Storage**: Redis for token revocation status
- **API**: FastAPI for high-performance REST endpoints

## Security Features

- Ed25519 elliptic curve signatures
- AES encryption for sensitive payload fields
- Token revocation with Redis storage
- Configurable expiration times
- Secure key generation and management

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
NextToken/
├── nextoken/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crypto.py        # Cryptographic operations
│   │   ├── token.py         # Token creation and verification
│   │   └── storage.py       # Redis storage operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── api/
│       ├── __init__.py
│       └── endpoints.py     # API endpoints
├── tests/
│   └── test_token.py        # Unit tests
├── requirements.txt
└── README.md
```

## License

MIT License 