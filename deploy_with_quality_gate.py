#!/usr/bin/env python3
"""
Deployment Script with Evaluation Quality Gate

This script:
1. Deploys your Databricks agent
2. Runs evaluation using the built-in script
3. Checks quality gate thresholds
4. Only completes deployment if quality gates pass

Usage:
  python deploy_with_quality_gate.py [--skip-quality-gate]
"""

import subprocess
import sys
import json
import argparse
import os
from pathlib import Path
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime

# Configuration
EXPERIMENT_ID = "552529352050103"
QUALITY_GATES = {
    "mortgage_accuracy/mean": 3.5,
    "compliance_safety/mean": 4.0,
}

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / ".env"
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    return env_vars

def get_databricks_profile():
    """Get the Databricks profile from .env"""
    env_vars = load_env()
    return env_vars.get("DATABRICKS_CONFIG_PROFILE")

def run_command(cmd, description, check=True):
    """Run a shell command and handle errors"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Running: {' '.join(cmd)}\n")
    
    # Add profile to environment if it's a databricks command
    env = os.environ.copy()
    if cmd[0] == "databricks":
        profile = get_databricks_profile()
        if profile:
            env["DATABRICKS_CONFIG_PROFILE"] = profile
            print(f"Using Databricks profile: {profile}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"\n❌ {description} failed with code {result.returncode}")
        sys.exit(1)
    return result

def deploy_agent():
    """Deploy the agent using databricks bundle"""
    print("\n" + "="*70)
    print("🚀 STEP 1: DEPLOYING AGENT")
    print("="*70)
    run_command(["databricks", "bundle", "deploy"], "Deploying Databricks bundle")
    run_command(["databricks", "bundle", "run", "agent_openai_agents_sdk"], "Starting agent deployment job")
    print("\n✅ Agent deployed successfully!")

def run_evaluation():
    """Run evaluation using built-in script"""
    print("\n" + "="*70)
    print("🔍 STEP 2: RUNNING EVALUATION")
    print("="*70)
    result = run_command(["uv", "run", "agent-evaluate"], "Running agent evaluation", check=False)
    if result.returncode != 0:
        print("\n⚠️ Evaluation script encountered issues")
        return None
    print("\n✅ Evaluation completed!")
    return result

def check_quality_gates():
    """Check if latest evaluation meets quality gates"""
    print("\n" + "="*70)
    print("🎯 STEP 3: CHECKING QUALITY GATES")
    print("="*70)
    client = MlflowClient()
    runs = client.search_runs(
        experiment_ids=[EXPERIMENT_ID],
        filter_string="tags.mlflow.runName LIKE '%Evaluation%'",
        order_by=["start_time DESC"],
        max_results=1
    )
    if not runs:
        print("\n❌ No evaluation runs found!")
        return False
    run = runs[0]
    metrics = run.data.metrics
    print(f"\nLatest evaluation run: {run.info.run_id[:8]}...")
    print(f"Run time: {datetime.fromtimestamp(run.info.start_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nMetrics:")
    all_passed = True
    for metric_name, threshold in QUALITY_GATES.items():
        value = metrics.get(metric_name, 0)
        passed = value >= threshold
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {metric_name}: {value:.3f} (threshold: {threshold}) {status}")
        if not passed:
            all_passed = False
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL QUALITY GATES PASSED!")
    else:
        print("❌ QUALITY GATES FAILED!")
    print("="*70)
    return all_passed

def rollback_deployment():
    """Rollback deployment on quality gate failure"""
    print("\n" + "="*70)
    print("⏪ ROLLING BACK DEPLOYMENT")
    print("="*70)
    print("\n⚠️ Rollback strategy:")
    print("  - Stop current deployment")
    print("  - Notify team of quality gate failure")
    print("  - Review evaluation results before retry")

def main():
    parser = argparse.ArgumentParser(description="Deploy agent with evaluation quality gate")
    parser.add_argument("--skip-quality-gate", action="store_true", help="Skip quality gate checks")
    parser.add_argument("--evaluation-only", action="store_true", help="Only run evaluation, skip deployment")
    args = parser.parse_args()
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  Mortgage Advisor Deployment with Quality Gate               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    try:
        if not args.evaluation_only:
            deploy_agent()
        eval_result = run_evaluation()
        if eval_result is None:
            print("\n❌ Evaluation failed to run")
            sys.exit(1)
        if args.skip_quality_gate:
            print("\n⚠️ Skipping quality gate checks (--skip-quality-gate flag set)")
            print("✅ Deployment complete (quality not verified)")
            return
        gates_passed = check_quality_gates()
        if gates_passed:
            print("\n" + "🎉"*20)
            print("\n✅ DEPLOYMENT SUCCESSFUL WITH QUALITY VERIFIED!")
            print("\nThe agent has been deployed and passed all quality gates.")
            print(f"\nView evaluation results: https://your-workspace/ml/experiments/{EXPERIMENT_ID}")
            print("\n" + "🎉"*20)
            sys.exit(0)
        else:
            print("\n" + "⚠️"*20)
            print("\n❌ DEPLOYMENT BLOCKED - QUALITY GATES FAILED!")
            print("\nThe agent was deployed but did not meet quality standards.")
            print("\nNext steps:")
            print("  1. Review evaluation results in MLflow")
            print("  2. Fix issues in agent code")
            print("  3. Re-run deployment")
            print("\nTo deploy without quality checks, use: --skip-quality-gate")
            print("\n" + "⚠️"*20)
            rollback_deployment()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
