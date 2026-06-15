# Mortgage Advisor - Evaluation Guide

## Quick Access Links

### 1. Evaluation Datasets
**Access via MLflow UI:**
- Navigate to: Machine Learning → MLflow → Experiments
- Select experiment: `552529352050103`
- Filter runs by tag: `mlflow.data.context=evaluation`
- View registered datasets under "Datasets" tab

**Or via CLI:**
```python
from mlflow.tracking import MlflowClient
client = MlflowClient()
datasets = client.search_datasets(experiment_ids=["552529352050103"])
```

---

### 2. Judges (LLM Evaluators)
**Custom Judges Created:**
- `mortgage_accuracy` - Evaluates calculation accuracy and regulatory correctness
- `compliance_safety` - Checks lending regulation compliance and safety

**Built-in Judges Available:**
- `faithfulness` - Response grounded in retrieved context
- `relevance` - Response relevance to query
- `answer_correctness` - Overall answer quality

**Usage:**
```python
from mlflow.metrics.genai import make_genai_metric

results = mlflow.evaluate(
    model=app_url,
    data=eval_data,
    extra_metrics=[mortgage_accuracy, compliance_judge]
)
```

---

### 3. Evaluation Runs
**View in MLflow:**
1. Go to: Machine Learning → MLflow → Experiments
2. Select experiment: `552529352050103`
3. Filter for evaluation runs:
   - Look for runs with `mlflow.runName` containing "Evaluation"
   - Check "Metrics" column for judge scores

**Programmatic Access:**
```python
from mlflow.tracking import MlflowClient
client = MlflowClient()

runs = client.search_runs(
    experiment_ids=["552529352050103"],
    filter_string="tags.mlflow.runName LIKE 'Mortgage Advisor Evaluation%'",
    order_by=["metrics.mortgage_accuracy/mean DESC"]
)
```

**Key Metrics to Track:**
- `mortgage_accuracy/mean` - Average accuracy score (1-5)
- `compliance_safety/mean` - Average compliance score (1-5)
- `latency_p50` - Median response time
- `token_count` - Tokens used per request

---

### 4. Labeling Schemas
**What They Define:**
- Rating scales (1-5 for quality)
- Boolean flags (compliance correct: yes/no)
- Multi-select options (issues found)
- Free-text feedback fields

**Our Schema Fields:**
1. `calculation_accuracy` - Rating 1-5
2. `tool_usage` - Select from 4 options
3. `compliance_correct` - Boolean
4. `response_quality` - Rating 1-5
5. `issues_found` - Multi-select
6. `feedback` - Free text

**Register Schema:**
```python
from mlflow.entities import LabelingSchema

schema = LabelingSchema(
    name="mortgage_advisor_quality",
    schema=labeling_schema,
    version="1.0"
)
mlflow.register_labeling_schema(schema)
```

---

### 5. Labeling Sessions
**Create a Session:**

**Option A: Via UI**
1. Go to MLflow Experiment: `552529352050103`
2. Select an evaluation run
3. Click "Label" button
4. Select labeling schema: `mortgage_advisor_quality`
5. Invite reviewers
6. Start labeling!

**Option B: Programmatically**
```python
from mlflow.entities import LabelingSession

session = LabelingSession(
    name="Q1 2026 Quality Review",
    schema_id="mortgage_advisor_quality",
    data_source=eval_run_id,
    reviewers=["user1@company.com", "user2@company.com"],
    deadline="2026-03-31"
)

mlflow.create_labeling_session(session)
```

**Labeling Workflow:**
1. Reviewer opens session
2. Sees agent request + response
3. Fills out schema fields
4. Submits label
5. System tracks who labeled what and when

**Export Labels:**
```python
labels = mlflow.get_labeling_session(session_id).get_labels()
labels_df = pd.DataFrame(labels)
```

---

## Complete Evaluation Workflow

### Step 1: Create Test Dataset
```python
import mlflow
import pandas as pd

test_cases = [
    {"request": "Calculate mortgage for $300k at 7%", "tags": "calculation"},
    {"request": "What's the FHA credit requirement?", "tags": "compliance"},
    # ... more cases
]

eval_df = pd.DataFrame(test_cases)
dataset = mlflow.data.from_pandas(eval_df, name="test_v1")
```

### Step 2: Define Judges
```python
from mlflow.metrics.genai import make_genai_metric

accuracy_judge = make_genai_metric(
    name="accuracy",
    definition="Evaluates calculation and compliance accuracy",
    grading_prompt="Rate 1-5 on accuracy...",
    model="endpoints:/databricks-meta-llama-3-1-70b-instruct"
)
```

### Step 3: Run Evaluation
```python
with mlflow.start_run(run_name="Weekly Eval"):
    results = mlflow.evaluate(
        data=eval_df,
        model="https://agent-mortgage-advisor-2893683289492793.aws.databricksapps.com/invocations",
        model_type="databricks-agent",
        extra_metrics=[accuracy_judge]
    )
    print(results.metrics)
```

### Step 4: Human Review (Optional)
```python
# Create labeling session for low-scoring cases
low_quality = results.tables["eval_results_table"].filter(
    lambda x: x["accuracy"] < 3
)

session = mlflow.create_labeling_session(
    name="Review Low Quality Responses",
    data=low_quality,
    schema="mortgage_advisor_quality"
)
```

### Step 5: Track Metrics Over Time
```python
import matplotlib.pyplot as plt

# Get historical eval runs
runs = client.search_runs(
    experiment_ids=["552529352050103"],
    filter_string="tags.eval_type = 'weekly'",
    order_by=["start_time ASC"]
)

scores = [r.data.metrics.get("accuracy/mean") for r in runs]
dates = [r.info.start_time for r in runs]

plt.plot(dates, scores)
plt.title("Mortgage Advisor Quality Over Time")
plt.ylabel("Accuracy Score")
plt.show()
```

---

## Best Practices

### Dataset Management
- **Version your datasets**: Add date or version suffix
- **Tag by category**: `affordability`, `compliance`, `comparison`
- **Include edge cases**: High DTI, low credit, jumbo loans
- **Update regularly**: Add new patterns as you see them in production

### Judge Design
- **Be specific**: "Check if DTI calculation uses correct formula"
- **Provide examples**: Show 5-star and 1-star responses
- **Use multiple judges**: Accuracy, compliance, helpfulness, etc.
- **Calibrate regularly**: Compare judge scores to human labels

### Evaluation Frequency
- **Daily**: Smoke tests on critical flows
- **Weekly**: Full evaluation suite
- **Before deployment**: Regression testing
- **After incidents**: Root cause analysis

### Labeling Sessions
- **Start small**: 20-30 cases per session
- **Use multiple reviewers**: Get inter-rater reliability
- **Provide context**: Include expected behavior in UI
- **Close the loop**: Use labels to retrain or improve prompts

---

## Integration with CI/CD

### Pre-Deployment Gate
```yaml
# In your deployment pipeline
steps:
  - name: Run Evaluation
    run: |
      python run_evaluation.py
      
  - name: Check Quality Gate
    run: |
      if [ $(mlflow runs describe $RUN_ID | jq '.data.metrics."accuracy/mean"') < 4.0 ]; then
        echo "Quality gate failed!"
        exit 1
      fi
      
  - name: Deploy App
    if: success()
    run: databricks apps deploy agent-mortgage-advisor
```

### Continuous Monitoring
```python
# Scheduled job every 6 hours
import mlflow
from datetime import datetime

with mlflow.start_run(run_name=f"Monitor {datetime.now()}"):
    results = mlflow.evaluate(
        model=PRODUCTION_URL,
        data=smoke_test_dataset,
        evaluators="default"
    )
    
    # Alert if quality drops
    if results.metrics["accuracy/mean"] < 4.0:
        send_slack_alert("Mortgage advisor quality degraded!")
```

---

## Useful Resources

- **MLflow Evaluate Docs**: https://mlflow.org/docs/latest/llms/llm-evaluate/index.html
- **Judge Creation**: https://mlflow.org/docs/latest/llms/llm-evaluate/index.html#creating-custom-llm-evaluation-metrics
- **Dataset Management**: https://mlflow.org/docs/latest/python_api/mlflow.data.html
- **Your Experiment**: `/ml/experiments/552529352050103`
- **Your App**: https://agent-mortgage-advisor-2893683289492793.aws.databricksapps.com

---

## Quick Commands Reference

```python
# Log dataset
dataset = mlflow.data.from_pandas(df, name="test_v1")
mlflow.log_input(dataset, context="evaluation")

# Create judge
judge = make_genai_metric(name="accuracy", definition="...", grading_prompt="...")

# Run evaluation
results = mlflow.evaluate(data=df, model=url, extra_metrics=[judge])

# Get evaluation runs
runs = client.search_runs(experiment_ids=[EXP_ID], filter_string="tags.eval = 'true'")

# Create labeling session
session = mlflow.create_labeling_session(name="Review", data=df, schema="quality_v1")

# Export labels
labels = mlflow.get_labeling_session(session_id).get_labels()
```