"""
AxonBridge — Temporal Worker

Executes Workflow Tasks.
"""

import asyncio
import logging
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from app.core.agent.agent_orchestrator import WorkflowAgent

logger = logging.getLogger(__name__)

# --- Activities ---

@activity.defn
async def execute_workflow_step_activity(params: dict) -> dict:
    """Execute a single workflow step using the Playwright agent."""
    execution_id = params.get("execution_id")
    target_url = params.get("target_url")
    step = params.get("step_config")

    logger.info(f"Executing step {step.get('action')} on {target_url}")

    agent = WorkflowAgent(execution_id, target_url)
    await agent.initialize()
    
    try:
        result = await agent.execute_step(step)
        return result
    finally:
        await agent.close()

# --- Workflows ---

@workflow.defn
class ClinicalAutomationWorkflow:
    @workflow.run
    async def run(self, execution_params: dict) -> dict:
        """Main workflow definition for a clinical automation execution."""
        workflow.logger.info("Starting ClinicalAutomationWorkflow")
        
        execution_id = execution_params["execution_id"]
        target_url = execution_params["target_url"]
        steps = execution_params["steps"]
        
        results = []
        for step in steps:
            # Execute each step as an activity
            result = await workflow.execute_activity(
                execute_workflow_step_activity,
                {
                    "execution_id": execution_id,
                    "target_url": target_url,
                    "step_config": step
                },
                start_to_close_timeout=timedelta(seconds=60),
            )
            results.append(result)
            
            # If a step fails, halt the workflow
            if result.get("status") == "failed":
                return {"status": "failed", "results": results}
                
        return {"status": "completed", "results": results}

# --- Worker Initialization ---

async def start_worker():
    client = await Client.connect("axonbridge-temporal:7233")
    worker = Worker(
        client,
        task_queue="axonbridge-tasks",
        workflows=[ClinicalAutomationWorkflow],
        activities=[execute_workflow_step_activity],
    )
    logger.info("Starting Temporal Worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(start_worker())
