import random
import os
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime

from public.lib.interfaces import SimulationResult, ResourceTypes
from public.tools.simulator import Simulator
from public.lib.data_manager import DataManager

class BulkRunner:
    """Runs multiple simulations with different parameters"""
    
    def __init__(self, policy_name: str, base_seed: int = None):
        self.policy_name = policy_name
        self.base_seed = base_seed or random.randint(0, 1000000)
        
    def run_batch(self, policy, config: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Run a batch of simulations with different parameters
        
        Args:
            policy: Policy object with plan_evacuation method
            config: Dict with:
                - node_range: Dict with min and max node counts
                - n_runs: int - Number of runs
                
        Returns:
            Tuple of (results dict, experiment_id)
        """
        random.seed(self.base_seed)
        
        # Initialize simulator
        simulator = Simulator(
            policy_name=self.policy_name,
            n_nodes=30,  # Will be overridden
            seed=self.base_seed
        )
        
        # Start new experiment
        experiment_id = simulator.data_manager.start_experiment(config)
        
        # Track aggregated results
        results = {
            'total_runs': 0,
            'successful_runs': 0,
            'avg_path_length': 0.0,
            'avg_time': 0.0,
            'by_size': {},
            'resource_metrics': {
                rt: {
                    'avg_allocated': 0.0,
                    'avg_used': 0.0,
                    'avg_remaining': 0.0,
                    'total_missions': 0
                }
                for rt in ResourceTypes.all_types()
            },
            'proxy_data': {
                'nodes': {},  # Will store aggregated node indicators
                'edges': {}   # Will store aggregated edge indicators
            }
        }
        
        # Run simulations
        for run in range(config['n_runs']):
            # Generate random node count for this run
            n_nodes = random.randint(config['node_range']['min'], 
                                   config['node_range']['max'])
            
            # Initialize size results if not seen before
            if n_nodes not in results['by_size']:
                results['by_size'][n_nodes] = {
                    'n_runs': 0,
                    'successes': 0,
                    'avg_path_length': 0.0,
                    'avg_time': 0.0,
                    'proxy_data': {
                        'nodes': {},
                        'edges': {}
                    },
                    'resource_metrics': {
                        rt: {
                            'avg_used': 0.0,
                            'avg_allocated': 0.0
                        }
                        for rt in ResourceTypes.all_types()
                    }
                }
            
            # Configure simulator for this run
            simulator.n_nodes = n_nodes
            simulator.seed = self.base_seed + run
            
            # Run simulation
            result, city, proxy_data = simulator.run_simulation(policy)
            
            # Get the policy result for this run
            max_resources = simulator.city_gen.calculate_max_resources(n_nodes)
            policy_result = policy.plan_evacuation(city, proxy_data, max_resources)
            
            # Update size-specific results
            size_results = results['by_size'][n_nodes]
            size_results['n_runs'] += 1
            if result.success:
                size_results['successes'] += 1
            
            # Update running averages for basic metrics
            size_results['avg_path_length'] = (
                (size_results['avg_path_length'] * (size_results['n_runs'] - 1) + 
                 result.path_length) / size_results['n_runs']
            )
            size_results['avg_time'] = (
                (size_results['avg_time'] * (size_results['n_runs'] - 1) + 
                 result.time_taken) / size_results['n_runs']
            )
            
            # Aggregate proxy data
            for node, indicators in proxy_data.node_data.items():
                for indicator, value in indicators.items():
                    # Update size-specific aggregation
                    if indicator not in size_results['proxy_data']['nodes']:
                        size_results['proxy_data']['nodes'][indicator] = []
                    size_results['proxy_data']['nodes'][indicator].append(value)
                    
                    # Update overall aggregation
                    if indicator not in results['proxy_data']['nodes']:
                        results['proxy_data']['nodes'][indicator] = []
                    results['proxy_data']['nodes'][indicator].append(value)
            
            for edge, indicators in proxy_data.edge_data.items():
                for indicator, value in indicators.items():
                    # Update size-specific aggregation
                    if indicator not in size_results['proxy_data']['edges']:
                        size_results['proxy_data']['edges'][indicator] = []
                    size_results['proxy_data']['edges'][indicator].append(value)
                    
                    # Update overall aggregation
                    if indicator not in results['proxy_data']['edges']:
                        results['proxy_data']['edges'][indicator] = []
                    results['proxy_data']['edges'][indicator].append(value)
            
            # Update resource metrics
            for rt in ResourceTypes.all_types():
                allocated = result.resources.allocated[rt]
                used = result.resources.used[rt]
                remaining = allocated - used
                
                # Update size-specific metrics
                size_metrics = size_results['resource_metrics'][rt]
                prev_runs = size_results['n_runs'] - 1
                size_metrics['avg_used'] = (
                    (size_metrics['avg_used'] * prev_runs + used) / size_results['n_runs']
                )
                size_metrics['avg_allocated'] = (
                    (size_metrics['avg_allocated'] * prev_runs + allocated) / size_results['n_runs']
                )
                
                # Update overall metrics
                metrics = results['resource_metrics'][rt]
                metrics['total_missions'] += 1
                metrics['avg_allocated'] = (
                    (metrics['avg_allocated'] * (metrics['total_missions'] - 1) + allocated) / 
                    metrics['total_missions']
                )
                metrics['avg_used'] = (
                    (metrics['avg_used'] * (metrics['total_missions'] - 1) + used) / 
                    metrics['total_missions']
                )
                metrics['avg_remaining'] = (
                    (metrics['avg_remaining'] * (metrics['total_missions'] - 1) + remaining) / 
                    metrics['total_missions']
                )
            
            # Calculate success rate for this size
            size_results['success_rate'] = size_results['successes'] / size_results['n_runs']
            
            # Update overall results
            results['total_runs'] += 1
            results['successful_runs'] += 1 if result.success else 0
        
        # Compute overall averages
        results['avg_path_length'] = sum(
            s['avg_path_length'] * s['n_runs'] 
            for s in results['by_size'].values()
        ) / results['total_runs']
        
        results['avg_time'] = sum(
            s['avg_time'] * s['n_runs'] 
            for s in results['by_size'].values()
        ) / results['total_runs']
        
        results['success_rate'] = results['successful_runs'] / results['total_runs']
        
        # Calculate averages for proxy data
        for data_type in ['nodes', 'edges']:
            for indicator in results['proxy_data'][data_type]:
                values = results['proxy_data'][data_type][indicator]
                results['proxy_data'][data_type][indicator] = sum(values) / len(values)
            
            for size in results['by_size']:
                for indicator in results['by_size'][size]['proxy_data'][data_type]:
                    values = results['by_size'][size]['proxy_data'][data_type][indicator]
                    results['by_size'][size]['proxy_data'][data_type][indicator] = sum(values) / len(values)
        
        # Save final results to a single summary file
        summary = {
            'metadata': {
                'policy_name': self.policy_name,
                'experiment_id': experiment_id,
                'config': config
            },
            'results': results
        }
        
        summary_path = os.path.join(
            'data', 'policies', self.policy_name, 
            'experiments', experiment_id, 'summary.json'
        )
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4)
        
        return results, experiment_id 