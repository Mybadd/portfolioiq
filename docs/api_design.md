# API Design

## Overview

PortfolioIQ uses FastAPI to expose the quantitative portfolio
risk engine to the frontend application.

The API acts as an interface between the Next.js frontend and
the Python backend services.

---

## Current API

### Health Check

**Method:** GET

**Endpoint:**

`/health`

**Purpose:**

Verifies that the PortfolioIQ API is running correctly.

---

# Portfolio APIs

## Create Portfolio from Weights

**Method:** POST

**Endpoint:**

`/api/portfolio/create`

**Purpose:**

Creates and validates a portfolio using user-specified asset
allocation weights.

The frontend accepts percentages, while the backend expects
normalized decimal weights.

### Request

```json
{
  "weights": {
    "NFLX": 0.10,
    "PEP": 0.20,
    "WMT": 0.15,
    "UNH": 0.40,
    "DIS": 0.15
  }
}