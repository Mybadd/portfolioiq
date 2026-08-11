# API Design

## Overview

PortfolioIQ uses FastAPI to expose the quantitative portfolio
risk engine to the frontend application.

The API acts as an interface between the Next.js frontend and
the Python backend services.

## Current API

### Health Check

**Method:** GET

**Endpoint:**
`/health`

**Purpose:**
Verifies that the PortfolioIQ API is running correctly.

### Create Portfolio

**Method:** POST

**Endpoint:**
`/api/portfolio/create`

**Purpose:**
Creates and validates a portfolio using asset allocation
weights.

**Request:**

```json
{
  "weights": {
    "NFLX": 0.20,
    "PEP": 0.25,
    "WMT": 0.20,
    "UNH": 0.15,
    "DIS": 0.20
  }
}