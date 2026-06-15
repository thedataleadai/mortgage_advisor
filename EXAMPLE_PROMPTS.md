# Example Prompts for Mortgage Advisor System

This guide provides practical prompts to test and use the Mortgage Advisor Multi-Agent System. Prompts are organized by complexity and use case.

---

## 🔢 Simple Calculations (Coordinator handles directly)

### Monthly Payment Queries

* "What's the monthly payment on a $350,000 loan at 7% for 30 years?"
* "Calculate monthly payment for a $500k mortgage at 6.5% over 15 years"
* "How much would I pay per month on a $280,000 loan at 7.25% for 20 years?"
* "What are the monthly payments for $400k at 6.75% over 30 years?"

### Quick Comparisons

* "Compare a 15-year vs 30-year mortgage for a $400,000 loan at 7%"
* "Show me the difference between 6.5% and 7% on a $350k loan"
* "Compare these options: $300k at 6.5% for 15 years, 7% for 30 years, and 6.75% for 20 years"

---

## 🏡 Affordability Analysis (Full workflow - all agents)

### Basic Affordability

* "I make $120,000 per year with $500 in monthly debts. I have $60,000 saved. What home can I afford?"
* "My annual income is $95k, monthly debts are $400, and I have $40k for down payment. What's my budget?"
* "I earn $150,000 with no debt and $80,000 saved. What's my maximum home price?"
* "Annual income: $200k, monthly debts: $1,200, down payment: $100k. What can I afford?"

### Detailed Scenarios

* "I make $130k with $600 in debts and $50k saved. Show me scenarios with 10%, 15%, and 20% down payments"
* "My household income is $175k, we have $800/month in debts and $90k saved. What if we put down 5% vs 20%?"
* "Earning $110k annually with $450 in monthly debts. I have $55k saved. Compare my options with different down payment amounts"

---

## 🔄 Refinancing Analysis

### Basic Refinance

* "I have $280,000 left on my mortgage at 8% with 25 years remaining. Current rates are 6.5%. Should I refinance?"
* "My current mortgage: $350k balance, 7.5% rate, 28 years left. New rates are 6.75% for 30 years. Is it worth it?"
* "I owe $420k at 8.25% with 22 years remaining. Can I save money by refinancing to 7% for 30 years?"

### Complex Refinance

* "I have $300k remaining at 7.8% with 27 years left. Compare refinancing to: 6.5% for 30 years, 6% for 15 years, and 6.25% for 20 years"
* "Current balance $250k at 8%, 20 years left. Should I refinance to 6.75% for 30 years or 6.25% for 15 years? Include breakeven analysis"

---

## 📊 Scenario Comparisons

### Loan Term Comparisons

* "Compare a $400,000 loan at: 15 years at 6.5%, 20 years at 6.75%, and 30 years at 7%"
* "Show me the total cost difference between 15-year and 30-year loans for $500k at current rates"
* "For a $350k loan, compare 10-year, 15-year, 20-year, and 30-year mortgages"

### Rate Shopping

* "I got three quotes for a $450k loan: 6.5% for 30yr, 6.25% for 15yr, and 6.75% with 2 points. Which is best?"
* "Compare $380k loan at: 7% with no points, 6.75% with 1 point, 6.5% with 2 points"

---

## 🎯 First-Time Homebuyer Scenarios

* "I'm a first-time buyer making $85k with $300 in monthly debts and $25k saved. What are my options?"
* "First-time buyer, income $100k, no debts, $35k down payment. What programs should I consider?"
* "I make $75k annually with $500 in debts and only $15k saved. Can I still buy a home? What programs can help?"
* "Military veteran, $110k income, $600 monthly debts, $40k saved. What VA loan options do I have?"

---

## 💰 Down Payment Strategy

* "I have $70k saved. Should I put 20% down to avoid PMI or keep more savings as emergency fund?"
* "Compare putting 5%, 10%, 15%, and 20% down on a $400k home with my income of $120k"
* "I can afford either $50k down on a $350k house or $80k down on a $400k house. Which is better?"

---

## 🏘️ Market Context Questions

* "What are current mortgage rates for 30-year fixed loans?"
* "What's the typical rate for a 15-year mortgage right now?"
* "I'm looking in Seattle. What are property market trends and typical rates?"
* "What economic factors should I consider before locking in a rate?"

---

## 🧮 Advanced Calculations

### DTI and Budget Analysis

* "My income is $140k and debts are $1,500/month. What's my debt-to-income ratio and how does it affect my loan?"
* "I make $125k with $800 in debts. What's the maximum monthly payment I can handle under the 28/36 rule?"
* "Calculate my DTI: $160k income, $2,000 monthly debts. Can I afford a $3,500 mortgage payment?"

### Total Cost Analysis

* "What's the total cost including interest for a $500k loan at 7% over 30 years?"
* "How much interest will I pay on a $350k mortgage at 6.75% for 20 years?"
* "Compare total interest paid: $400k at 7% for 30 years vs 6.5% for 15 years"

---

## 🤔 Advisory Questions

### Property Type Specific

* "I'm buying a condo for $450k. What should I consider for HOA fees in my budget?"
* "Looking at a $550k house with high property taxes (2%). How does this affect affordability?"
* "Buying a fixer-upper for $300k but need $50k in repairs. How should I structure financing?"

### Credit and Risk

* "My credit score is 680. How does this affect my rates and what can I do to improve my situation?"
* "I'm self-employed with variable income. How should I approach mortgage pre-approval?"
* "What if I lose my job during the mortgage process? What protections should I have?"

---

## 💬 Multi-Turn Conversations

### Progressive Consultation Example

**Turn 1:**
```
User: "Hi, I want to buy my first home but don't know where to start"
```

**Expected Response:** System asks for income, debts, savings, location

**Turn 2:**
```
User: "I make $105k, have $450/month in student loans and $45k saved"
```

**Expected Response:** System calculates affordability, provides scenarios

**Turn 3:**
```
User: "That seems high. What if I only put 10% down?"
```

**Expected Response:** System recalculates with PMI considerations

**Turn 4:**
```
User: "Show me 15-year vs 30-year options"
```

**Expected Response:** System compares scenarios with recommendations

### Problem-Solving Conversation Example

**Turn 1:**
```
User: "I was pre-approved for $450k but found a house for $500k. What are my options?"
```

**Expected Response:** System analyzes gap and suggests solutions

**Turn 2:**
```
User: "Can I use a gift from parents for down payment?"
```

**Expected Response:** System explains gift rules and recalculates

**Turn 3:**
```
User: "How much would I need to save monthly to increase my budget in 6 months?"
```

**Expected Response:** System creates savings plan

---

## 🎪 Edge Cases and Complex Scenarios

* "I'm buying a duplex for $600k and will rent out one unit for $2,000/month. How does rental income affect my qualification?"
* "I have two job offers: $120k in Seattle or $100k in Austin. Compare affordability in both markets"
* "My partner and I have combined income $180k but they have $1,200 in monthly debts. Joint vs individual application?"
* "I'm getting a $20k signing bonus. Should I use it for down payment, paying off debt, or emergency fund?"
* "I need to sell my current house first. Should I get a bridge loan or wait? Current mortgage $250k, new house $500k"

---

## 🚀 Quick Test Suite

Use these prompts to verify each agent is working correctly:

| Prompt | What It Tests | Expected Agent |
|--------|---------------|----------------|
| "What's my monthly payment on $300k at 7% for 30 years?" | Basic calculation | Coordinator (direct) |
| "I make $100k with $500 debts and $50k saved. What can I afford?" | Full workflow | All 3 agents |
| "Compare 15yr at 6.5% vs 30yr at 7% for $400k" | Scenario analysis | Analyst + Coordinator |
| "What are current mortgage rates?" | Market research | Data Researcher |
| "Should I refinance from 8% to 6.5% with $280k left?" | Complex analysis | All 3 agents |

---

## 💡 Pro Tips for Best Results

### Be Specific About:

* **Annual income** (gross, not net)
* **Monthly debts** (car loans, credit cards, student loans)
* **Down payment amount** available
* **Credit score range** if known
* **Property location** if relevant
* **Loan type preferences** (FHA, VA, conventional)

### Example of a Well-Structured Query:

```
"I'm a first-time homebuyer in Austin, TX. My details:
- Annual income: $95,000 (gross)
- Monthly debts: $450 (student loans) + $300 (car payment)
- Down payment saved: $35,000
- Credit score: ~720
- Looking for single-family home

What can I afford and what are my best loan options?"
```

**The more details you provide, the better the personalized recommendations!**

---

## 🧪 Testing via API

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

### Multi-Turn Conversation
```bash
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      {"role": "user", "content": "What home can I afford making $100k with no debts?"},
      {"role": "assistant", "content": "Based on $100k income with no debts..."},
      {"role": "user", "content": "What if I put down 10% instead of 20%?"}
    ]
  }'
```

---

## 📝 Custom Prompt Templates

### Template: Basic Affordability
```
I make $[INCOME] per year with $[MONTHLY_DEBTS] in monthly debts. 
I have $[DOWN_PAYMENT] saved. What home can I afford?
```

### Template: Refinancing Decision
```
I have $[BALANCE] left on my mortgage at [CURRENT_RATE]% with [YEARS_LEFT] years remaining. 
Current rates are [NEW_RATE]%. Should I refinance?
```

### Template: Scenario Comparison
```
Compare a $[LOAN_AMOUNT] loan with these options:
- [TERM_1] years at [RATE_1]%
- [TERM_2] years at [RATE_2]%
- [TERM_3] years at [RATE_3]%
```

### Template: First-Time Buyer
```
I'm a first-time homebuyer with:
- Annual income: $[INCOME]
- Monthly debts: $[DEBTS]
- Down payment: $[DOWN_PAYMENT]
- Credit score: [SCORE]
What programs should I consider?
```

---

## 🎯 Expected Response Quality

Good responses should include:

* **Numbers**: Specific dollar amounts, percentages, timelines
* **Scenarios**: At least 2-3 options to compare
* **Explanations**: Why certain options are recommended
* **Disclaimers**: Reminders about rate volatility, pre-approval importance
* **Next Steps**: Clear action items for the customer
* **Tables**: For scenario comparisons (markdown format)
* **Personalization**: Tailored to the customer's specific situation

---

## 🔍 Troubleshooting

### If the agent asks for more information:
✅ **Good** - The agent is being thorough and personalized

### If calculations seem off:
* Verify the inputs (annual income, not monthly)
* Check that interest rates are percentages (7.0 = 7%)
* Ensure loan term is in years, not months

### If the agent doesn't delegate to sub-agents:
* Try a more complex query that requires research and multiple scenarios
* Simple calculations should be handled by Coordinator directly (this is expected)

---

## 📚 Additional Resources

* [README.md](./README.md) - Full system documentation
* [MORTGAGE_EXAMPLES.md](./MORTGAGE_EXAMPLES.md) - Detailed usage examples with expected outputs
* [agent.py](./agent_server/agent.py) - Agent implementation code
* [databricks.yml](./databricks.yml) - Deployment configuration

---

**Ready to test? Start with a simple prompt and work your way up to complex scenarios!** 🏡✨
