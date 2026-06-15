import asyncio
import logging
import os
from pathlib import Path

import mlflow
from dotenv import load_dotenv
from mlflow.genai.agent_server import get_invoke_function
from mlflow.genai.scorers import (
    Completeness,
    ConversationalSafety,
    ConversationCompleteness,
    Fluency,
    KnowledgeRetention,
    RelevanceToQuery,
    Safety,
    ToolCallCorrectness,
    UserFrustration,
)
from mlflow.genai.simulators import ConversationSimulator
from mlflow.types.responses import ResponsesAgentRequest

# Detect if running in Databricks workspace
is_databricks = "DATABRICKS_RUNTIME_VERSION" in os.environ

if is_databricks:
    print("✓ Running in Databricks workspace - using built-in authentication")
    # Don't load .env file - use workspace authentication
    
    # Set MLflow tracking URI for Databricks
    mlflow.set_tracking_uri("databricks")
    
    # Ensure artifact directory exists and is writable
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    artifact_dir = project_root / "mlruns" / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Artifact directory: {artifact_dir}")
    
    # Set the experiment ID
    mlflow.set_experiment(experiment_id="552529352050103")
    print("✓ Using MLflow experiment: 552529352050103")
else:
    print("✓ Running locally - loading .env for authentication")
    
    # Load environment variables from .env - try multiple paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"✓ Loaded .env from: {env_path}")
    else:
        cwd_env = Path.cwd() / ".env"
        if cwd_env.exists():
            load_dotenv(dotenv_path=cwd_env, override=True)
            print(f"✓ Loaded .env from: {cwd_env}")
        else:
            print(f"⚠️ Warning: .env file not found at {env_path} or {cwd_env}")
    
    # Set MLflow experiment from environment
    experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID", "552529352050103")
    mlflow.set_experiment(experiment_id=experiment_id)
    print(f"✓ Using MLflow experiment: {experiment_id}")

logging.getLogger("mlflow.utils.autologging_utils").setLevel(logging.ERROR)

# need to import agent for our @invoke-registered function to be found
from agent_server import agent  # noqa: F401

# ============================================================================
# MORTGAGE-SPECIFIC EVALUATION TEST CASES
# ============================================================================
# NOTE: Using 2 test cases and 3 turns to avoid rate limits
# Increase after confirming evaluation works
test_cases = [
    {
        "goal": "Determine if I can afford a $400,000 home with my income",
        "persona": "A first-time homebuyer earning $85,000/year with $1,500/month in existing debts and $50,000 saved for down payment.",
        "simulation_guidelines": [
            "Initially ask about my income, debts, and down payment.",
            "Ask follow-up questions about employment stability and credit score.",
            "Prefer conversational, easy-to-understand explanations.",
        ],
    },
    {
        "goal": "Calculate monthly payment for a specific loan scenario",
        "persona": "A buyer who already found a property and needs exact payment calculations.",
        "simulation_guidelines": [
            "Provide specific numbers: $275,000 loan at 6.75% for 30 years.",
            "Ask about property taxes, insurance, and HOA fees if applicable.",
            "Want precise numbers to plan budget.",
        ],
    },
]

print(f"ℹ️ Running {len(test_cases)} test cases with reduced turns to avoid rate limits")
print("   Increase test_cases and max_turns in evaluate_agent.py after confirming it works\n")

simulator = ConversationSimulator(
    test_cases=test_cases,
    max_turns=3,  # Reduced from 5 to avoid rate limits
    user_model="endpoints:/databricks-meta-llama-3-3-70b-instruct",  # Using Llama (higher rate limits than Claude)
)

# Get the invoke function that was registered via @invoke decorator in your agent
invoke_fn = get_invoke_function()
assert invoke_fn is not None, (
    "No function registered with the `@invoke` decorator found."
    "Ensure you have a function decorated with `@invoke()`."
)

# if invoke function is async, wrap it in a sync function.
# The simulator may already be running an event loop, so we use nest_asyncio
# to allow nested run_until_complete() calls without deadlocking.
if asyncio.iscoroutinefunction(invoke_fn):
    import nest_asyncio

    nest_asyncio.apply()

    def predict_fn(input: list[dict], **kwargs) -> dict:
        """Prediction function that handles conversation messages"""
        # Debug print to see what we're receiving
        print(f"DEBUG predict_fn received input type: {type(input)}")
        if isinstance(input, list) and len(input) > 0:
            print(f"DEBUG first item type: {type(input[0])}")
        
        try:
            req = ResponsesAgentRequest(input=input)
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(invoke_fn(req))
            result = response.model_dump()
            print(f"DEBUG predict_fn returning type: {type(result)}")
            return result
        except Exception as e:
            print(f"ERROR in predict_fn: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
else:

    def predict_fn(input: list[dict], **kwargs) -> dict:
        """Prediction function that handles conversation messages"""
        # Debug print to see what we're receiving
        print(f"DEBUG predict_fn received input type: {type(input)}")
        if isinstance(input, list) and len(input) > 0:
            print(f"DEBUG first item type: {type(input[0])}")
        
        try:
            req = ResponsesAgentRequest(input=input)
            response = invoke_fn(req)
            result = response.model_dump()
            print(f"DEBUG predict_fn returning type: {type(result)}")
            return result
        except Exception as e:
            print(f"ERROR in predict_fn: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise


def evaluate():
    mlflow.genai.evaluate(
        data=simulator,
        predict_fn=predict_fn,
        scorers=[
            Completeness(),
            ConversationCompleteness(),
            ConversationalSafety(),
            KnowledgeRetention(),
            UserFrustration(),
            Fluency(),
            RelevanceToQuery(),
            Safety(),
            ToolCallCorrectness(),
        ],
    )


if __name__ == "__main__":
    evaluate()
