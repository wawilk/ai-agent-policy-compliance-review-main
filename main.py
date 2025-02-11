import sys
import asyncio
import os
import time
from src.policy_compliance_agent import PolicyComplianceAgent

async def run(underlier_policy: str, master_policy: str):
    # Create the policy compliance agent
    agent = PolicyComplianceAgent(underlier_policy=underlier_policy, master_policy=master_policy)
    response = await agent.run()
    return response

async def main():
    # Check for the correct number of arguments and pass them to the run function
    if len(sys.argv) < 2:
        print("Usage: python main.py 'underlier_policy.ext' 'master_policy.ext'")  
        sys.exit(1)
        
    underlier_policy = sys.argv[1]
    master_policy = sys.argv[2]

    print("Running Policy Compliance Validation. This may take a several minutes...")
    start_time = time.time()
    response = await run(underlier_policy, master_policy)
    end_time = time.time()
    print("starting output report")
    report_output_path = os.path.join(os.getenv('OUTPUT_DIR'), underlier_policy.split('.')[0] + '_report.json')
    print("report_output_path=",report_output_path) 
    print("response.content=", response.content)   
    with open(report_output_path, 'w') as file:
        file.write(response.content)

    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"Policy Compliance Validation finished in {minutes} minutes and {seconds:02.0f} seconds.")
    print(f"\nReport saved to {report_output_path}")
        
if __name__ == "__main__":
    asyncio.run(main())