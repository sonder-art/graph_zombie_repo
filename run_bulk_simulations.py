from public.tools.run_bulk import BulkRunner
from public.student_code.solution import EvacuationPolicy
from public.visualization.bulk_analysis import generate_all_visualizations
from public.visualization.city_analysis import analyze_city_scenario, generate_aggregated_data
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run bulk simulations')
    parser.add_argument('--skip-city-analysis', action='store_true',
                      help='Skip individual city analysis to save time')
    args = parser.parse_args()

    # Configuration for bulk runs
    config = {
        'node_range': {
            'min': 20,
            'max': 50
        },
        'n_runs': 10,  # Total number of cities to simulate
        'base_seed': 42  # For reproducibility
    }
    
    policy_name = "EvacuationPolicy"
    
    # Create bulk runner
    runner = BulkRunner(
        policy_name=policy_name,
        base_seed=config['base_seed']
    )
    
    # Create policy
    policy = EvacuationPolicy()
    
    # Run batch of simulations
    results, experiment_id = runner.run_batch(policy, config)
    
    print("\nEvacuation Mission Results:")
    print(f"Total Missions: {results['total_runs']}")
    print(f"Mission Success Rate: {results['success_rate']*100:.1f}%")
    print(f"Average Mission Time: {results['avg_time']:.2f} seconds")
    print(f"Average Path Distance: {results['avg_path_length']:.2f}")
    
    print("\nResource Efficiency:")
    for resource_type, metrics in results['resource_metrics'].items():
        print(f"{resource_type.replace('_', ' ').title()}:")
        print(f"  Average Carried: {metrics['avg_allocated']:.1f}")
        print(f"  Average Remaining: {metrics['avg_remaining']:.1f}")
    
    print("\nResults by City Size:")
    for size, metrics in results['by_size'].items():
        print(f"\nCity Size: {size} nodes")
        print(f"  Success Rate: {metrics['success_rate']*100:.1f}%")
        print(f"  Average Time: {metrics['avg_time']:.2f} seconds")
        print(f"  Average Path Length: {metrics['avg_path_length']:.2f}")
    
    print("\nGenerating experiment-level visualizations...")
    generate_all_visualizations(results, policy_name, experiment_id)
    
    print("\nGenerating aggregated analysis data...")
    generate_aggregated_data(results, policy_name, experiment_id)
    
    if not args.skip_city_analysis:
        print("\nAnalyzing individual city scenarios...")
        exp_dir = os.path.join('data', 'policies', policy_name, 'experiments', experiment_id, 'cities')
        for city_dir in os.listdir(exp_dir):
            if city_dir.startswith('city_'):
                city_id = city_dir.replace('city_', '')
                print(f"  Analyzing {city_id}...")
                analyze_city_scenario(city_id, policy_name, experiment_id)
    
    print("\nAnalysis complete. Results saved in:")
    print(f"data/policies/{policy_name}/experiments/{experiment_id}/")

if __name__ == "__main__":
    main() 