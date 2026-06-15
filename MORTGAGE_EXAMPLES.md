# Mortgage Advisor System - Usage Examples

This guide demonstrates how to use the Mortgage Advisor multi-agent system for various scenarios.

## Quick Start Examples

### 1. Basic Affordability Analysis

**Customer Question**: "I make $120,000 per year with $500/month in existing debts. I have $60,000 saved for a down payment. What home can I afford?"

**What Happens**:
1. **Coordinator** receives the request and routes to **Mortgage Analyst**
2. **Analyst** calculates affordability using the 28/36 rule
3. **Report Writer** generates personalized recommendations

**Expected Output**:
- Maximum home price: ~$450,000-$500,000
- Maximum loan amount: ~$390,000-$440,000
- Estimated monthly payment: ~$2,800
- Debt-to-income ratio: ~28-32%

### 2. Mortgage Scenario Comparison

Compare different loan options side-by-side with detailed breakdowns of costs and recommendations.

### 3. Simple Monthly Payment Calculation

Quick calculations for specific loan amounts, rates, and terms.

### 4. Market Research Request

Query current rates and regional market trends.

### 5. Refinancing Analysis

Evaluate whether refinancing makes financial sense.

## Testing via API

### Streaming Request
```bash
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "content": "I earn $150k with $800 in debts and $80k saved. What can I afford?"
    }],
    "stream": true
  }'
```

### Non-Streaming Request
```bash
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "content": "Compare $500k loan: 15yr at 6.5% vs 30yr at 7%"
    }]
  }'
```

## Common Questions

### Q: How does the 28/36 rule work?
**A**: Housing costs should not exceed 28% of gross income, and total debt should not exceed 36%.

### Q: Can the system handle FHA, VA, or USDA loans?
**A**: The current version handles conventional loans. Special programs can be added by modifying the Analyst agent.

### Q: How do I add live mortgage rate data?
**A**: Create Unity Catalog tables with rate data and uncomment the MCP server code in agent.py.

## Deployment Checklist

- [ ] Test all calculation tools
- [ ] Verify agent responses
- [ ] Configure proper permissions
- [ ] Set up MLflow experiment
- [ ] Run evaluation suite
- [ ] Test API endpoints
