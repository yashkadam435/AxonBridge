import asyncio
from app.core.agent.browser_manager import init_browser, stop_browser
from app.core.agent.agent_orchestrator import WorkflowAgent

async def run_agent_test():
    print("========================================")
    print("AxonBridge Phase 2: Agent Orchestrator Test")
    print("========================================\n")
    
    # 1. Initialize Browser
    print("[1/3] Starting headless browser...")
    await init_browser()
    print("  ✅ Browser started")

    # 2. Setup Agent
    print("[2/3] Initializing Agent for Mock Portal...")
    # Point to the local mock portal file since the frontend container doesn't have a volume mount
    agent = WorkflowAgent("test-exec-001", "file:///app/mock-portal.html")
    await agent.initialize()
    print("  ✅ Agent initialized")

    # 3. Execute Steps
    print("[3/3] Executing Workflow Steps...")
    
    steps = [
        {"action": "navigate"},
        {"action": "extract", "selector": "#mrn"},
        {"action": "type", "selector": "#diagnosis", "value": "J01.90 (Acute sinusitis)"},
        {"action": "click", "selector": "#saveBtn"},
    ]

    for i, step in enumerate(steps):
        print(f"     Executing step {i+1}: {step['action']}")
        result = await agent.execute_step(step)
        if result["status"] == "failed":
            print(f"  ❌ Step failed: {result.get('error')}")
            break
        print(f"     ✅ Result: {result}")
        await asyncio.sleep(1) # wait for animations

    await agent.close()
    await stop_browser()
    
    print("\n========================================")
    print("🎉 Phase 2 Agent E2E Test Completed!")
    print("========================================\n")

if __name__ == "__main__":
    asyncio.run(run_agent_test())
