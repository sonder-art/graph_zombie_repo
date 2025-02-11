from public.tools.simulator import Simulator
from public.student_code.solution import EvacuationPolicy
from public.visualization.single_run import visualize_simulation

def main():
    # Create simulator with policy name
    sim = Simulator(
        policy_name="EvacuationPolicy",
        n_nodes=30,
        seed=42
    )
    
    # Start an experiment for this run
    sim.data_manager.start_experiment({
        'type': 'single_run',
        'n_nodes': 30,
        'seed': 42
    })
    
    # Create student's policy
    policy = EvacuationPolicy()
    
    # Run simulation
    result, city, proxy_data = sim.run_simulation(policy)
    
    # Get the policy result again for visualization
    policy_result = policy.plan_evacuation(city, proxy_data, max_resources=10)  # This will be ignored as max_resources comes from city
    
    # Visualize results
    visualize_simulation(city, proxy_data, policy_result, result)
    
    # Print detailed results
    print("\nSimulation Results:")
    print(f"Success: {result.success}")
    if result.failure_reason:
        print(f"Failure Reason: {result.failure_reason}")
    print(f"Path Length: {result.path_length:.2f}")
    print(f"Time Taken: {result.time_taken:.2f}")
    print(f"Obstacles Encountered: {result.obstacles_encountered}")
    print("\nResource Usage:")
    for resource_type, usage in result.resources.to_dict()['efficiency'].items():
        print(f"{resource_type.replace('_', ' ').title()}: {usage*100:.1f}% efficient")

if __name__ == "__main__":
    main() 