import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os
import pandas as pd
from matplotlib.table import Table

def save_plot(plt, name: str, policy_name: str, experiment_id: str):
    """
    Save plot to the correct location in the data structure.
    
    Args:
        plt: matplotlib plot object
        name: name of the visualization
        policy_name: name of the policy being tested
        experiment_id: ID of the current experiment
    """
    # Construct the correct path following the data structure
    vis_path = os.path.join(
        "data/policies",
        policy_name,
        "experiments",
        experiment_id,
        "visualizations"
    )
    os.makedirs(vis_path, exist_ok=True)
    
    # Save the plot
    plt.savefig(os.path.join(vis_path, f"{name}.png"), 
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_success_rates(results: Dict, policy_name: str, experiment_id: str):
    """
    Visualize success rates across different city sizes.
    Shows how mission success varies with complexity of the environment.
    """
    plt.figure(figsize=(12, 6))
    sizes = sorted(results['by_size'].keys())
    success_rates = [results['by_size'][size]['success_rate'] * 100 for size in sizes]
    
    plt.bar(sizes, success_rates, alpha=0.7, color='skyblue')
    plt.axhline(y=results['success_rate'] * 100, color='r', linestyle='--',
                label=f'Overall: {results["success_rate"]*100:.1f}%')
    
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Success Rate (%)')
    plt.title('Mission Success by City Size\n' + 
             'Analysis of how environment complexity affects mission outcomes')
    plt.legend()
    
    save_plot(plt, "success_rates", policy_name, experiment_id)

def plot_resource_efficiency(results: Dict, policy_name: str, experiment_id: str):
    """
    Analyze resource usage patterns.
    Shows how effectively different resources are being utilized.
    """
    plt.figure(figsize=(12, 6))
    resource_types = list(results['resource_metrics'].keys())
    x = range(len(resource_types))
    
    carried = [metrics['avg_allocated'] for metrics in results['resource_metrics'].values()]
    remaining = [metrics['avg_remaining'] for metrics in results['resource_metrics'].values()]
    used = [c - r for c, r in zip(carried, remaining)]
    
    plt.bar(x, carried, alpha=0.4, label='Carried', color='lightblue')
    plt.bar(x, used, alpha=0.8, label='Used', color='blue')
    
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Average Amount')
    plt.title('Resource Usage Analysis\n' +
             'Comparison of resource allocation vs actual usage')
    
    # Add efficiency percentages
    for i, (c, u) in enumerate(zip(carried, used)):
        if c > 0:
            efficiency = (u / c) * 100
            plt.text(i, c, f'{efficiency:.1f}%\nefficient', 
                    ha='center', va='bottom')
    
    plt.legend()
    
    save_plot(plt, "resource_efficiency", policy_name, experiment_id)

def plot_proxy_success_correlation(results: Dict, policy_name: str, experiment_id: str):
    """
    Analyze how different proxy indicators correlate with mission performance metrics.
    Shows which environmental factors are most predictive of mission outcomes.
    """
    plt.figure(figsize=(15, 10))
    
    # Collect proxy data and performance metrics by city size
    proxy_correlations = {
        'time': {},      # Correlations with mission time
        'efficiency': {} # Correlations with resource efficiency
    }
    
    # Process node indicators
    for indicator in results['proxy_data']['nodes'].keys():
        proxy_correlations['time'][f"node_{indicator}"] = []
        proxy_correlations['efficiency'][f"node_{indicator}"] = []
        
        for size, size_data in results['by_size'].items():
            if indicator in size_data['proxy_data']['nodes']:
                # Correlation with time
                proxy_correlations['time'][f"node_{indicator}"].append({
                    'value': size_data['proxy_data']['nodes'][indicator],
                    'metric': size_data['avg_time']
                })
                
                # Calculate resource efficiency for this size
                total_used = sum(
                    metrics['avg_used']
                    for metrics in size_data['resource_metrics'].values()
                )
                total_allocated = sum(
                    metrics['avg_allocated']
                    for metrics in size_data['resource_metrics'].values()
                )
                efficiency = total_used / total_allocated if total_allocated > 0 else 0
                
                proxy_correlations['efficiency'][f"node_{indicator}"].append({
                    'value': size_data['proxy_data']['nodes'][indicator],
                    'metric': efficiency
                })
    
    # Process edge indicators
    for indicator in results['proxy_data']['edges'].keys():
        proxy_correlations['time'][f"edge_{indicator}"] = []
        proxy_correlations['efficiency'][f"edge_{indicator}"] = []
        
        for size, size_data in results['by_size'].items():
            if indicator in size_data['proxy_data']['edges']:
                # Correlation with time
                proxy_correlations['time'][f"edge_{indicator}"].append({
                    'value': size_data['proxy_data']['edges'][indicator],
                    'metric': size_data['avg_time']
                })
                
                # Calculate resource efficiency
                total_used = sum(
                    metrics['avg_used']
                    for metrics in size_data['resource_metrics'].values()
                )
                total_allocated = sum(
                    metrics['avg_allocated']
                    for metrics in size_data['resource_metrics'].values()
                )
                efficiency = total_used / total_allocated if total_allocated > 0 else 0
                
                proxy_correlations['efficiency'][f"edge_{indicator}"].append({
                    'value': size_data['proxy_data']['edges'][indicator],
                    'metric': efficiency
                })
    
    # Calculate correlations
    correlations = {
        'time': {},
        'efficiency': {}
    }
    
    for metric_type in ['time', 'efficiency']:
        for indicator, data in proxy_correlations[metric_type].items():
            if data:  # Only process if we have data
                values = [d['value'] for d in data]
                metrics = [d['metric'] for d in data]
                if any(values) and any(metrics):  # Ensure non-zero data
                    correlation = np.corrcoef(values, metrics)[0, 1]
                    if not np.isnan(correlation):
                        correlations[metric_type][indicator] = correlation
    
    # Plot correlations
    plt.subplot(2, 1, 1)
    plot_correlation_bars(correlations['time'], 'Mission Time',
                         'How environmental factors affect mission duration')
    
    plt.subplot(2, 1, 2)
    plot_correlation_bars(correlations['efficiency'], 'Resource Efficiency',
                         'How environmental factors affect resource utilization')
    
    plt.tight_layout()
    save_plot(plt, "proxy_correlations", policy_name, experiment_id)

def plot_correlation_bars(correlations: Dict, metric_name: str, subtitle: str):
    """Helper function to plot correlation bars"""
    indicators = list(correlations.keys())
    correlation_values = list(correlations.values())
    
    plt.barh(range(len(indicators)), correlation_values, alpha=0.7)
    plt.yticks(range(len(indicators)), 
               [ind.replace('_', ' ').replace('node ', '').replace('edge ', '').title() 
                for ind in indicators])
    
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    plt.xlabel(f'Correlation with {metric_name}')
    plt.title(f'Environmental Indicators vs {metric_name}\n{subtitle}')
    
    # Add correlation values
    for i, corr in enumerate(correlation_values):
        plt.text(corr, i, f' {corr:.2f}', 
                va='center', ha='left' if corr >= 0 else 'right')

def plot_proxy_resource_patterns(results: Dict, policy_name: str, experiment_id: str):
    """
    Analyze relationship between proxy indicators and resource usage.
    Shows how environmental conditions influence resource allocation.
    """
    plt.figure(figsize=(15, 8))
    
    # Collect all indicators and resources
    node_indicators = list(results['proxy_data']['nodes'].keys())
    edge_indicators = list(results['proxy_data']['edges'].keys())
    all_indicators = [(ind, 'node') for ind in node_indicators] + [(ind, 'edge') for ind in edge_indicators]
    
    resource_types = list(results['resource_metrics'].keys())
    
    # Create correlation matrix
    correlation_matrix = np.zeros((len(all_indicators), len(resource_types)))
    
    # Calculate correlations between indicators and resource usage
    for i, (indicator, ind_type) in enumerate(all_indicators):
        for j, resource in enumerate(resource_types):
            indicator_values = []
            resource_values = []
            
            for size, size_data in results['by_size'].items():
                # Get indicator value
                if ind_type == 'node' and indicator in size_data['proxy_data']['nodes']:
                    ind_val = size_data['proxy_data']['nodes'][indicator]
                elif ind_type == 'edge' and indicator in size_data['proxy_data']['edges']:
                    ind_val = size_data['proxy_data']['edges'][indicator]
                else:
                    continue
                
                # Get resource usage
                if resource in size_data['resource_metrics']:
                    res_val = size_data['resource_metrics'][resource]['avg_used']
                else:
                    continue
                
                indicator_values.append(ind_val)
                resource_values.append(res_val)
            
            # Calculate correlation if we have data
            if indicator_values and resource_values:
                correlation = np.corrcoef(indicator_values, resource_values)[0, 1]
                if not np.isnan(correlation):
                    correlation_matrix[i, j] = correlation
    
    # Plot correlation matrix
    plt.imshow(correlation_matrix, aspect='auto', cmap='RdYlBu')
    plt.colorbar(label='Correlation Strength')
    
    # Create labels
    indicator_labels = [
        f"{'Node' if t == 'node' else 'Edge'}: {ind.replace('_', ' ').title()}"
        for ind, t in all_indicators
    ]
    
    plt.yticks(range(len(all_indicators)), indicator_labels)
    plt.xticks(range(len(resource_types)), 
               [rt.replace('_', ' ').title() for rt in resource_types],
               rotation=45)
    
    plt.title('Environmental Indicators vs Resource Usage\n' +
             'How different factors influence resource requirements')
    
    # Add correlation values
    for i in range(len(all_indicators)):
        for j in range(len(resource_types)):
            plt.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                    ha='center', va='center')
    
    plt.tight_layout()
    save_plot(plt, "proxy_resource_patterns", policy_name, experiment_id)

def plot_time_distance_relationship(results: Dict, policy_name: str, experiment_id: str):
    """
    Analyze relationship between mission time and path length.
    Shows how mission duration correlates with distance traveled.
    """
    plt.figure(figsize=(12, 6))
    sizes = sorted(results['by_size'].keys())
    times = [results['by_size'][size]['avg_time'] for size in sizes]
    distances = [results['by_size'][size]['avg_path_length'] for size in sizes]
    success_rates = [results['by_size'][size]['success_rate'] for size in sizes]
    
    scatter = plt.scatter(distances, times, c=success_rates, 
                         cmap='RdYlBu', s=100, alpha=0.6)
    plt.colorbar(scatter, label='Success Rate')
    
    # Add trend line if we have enough data points
    if len(distances) > 1:
        z = np.polyfit(distances, times, 1)
        p = np.poly1d(z)
        plt.plot(distances, p(distances), "r--", alpha=0.8, 
                label=f'Trend: {z[0]:.2f}x + {z[1]:.2f}')
    
    plt.xlabel('Path Length')
    plt.ylabel('Time Taken (seconds)')
    plt.title('Mission Time vs Path Length Analysis\n' +
             'Impact of route length on mission duration')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    save_plot(plt, "time_distance", policy_name, experiment_id)

def plot_resource_impact(results: Dict, policy_name: str, experiment_id: str):
    """
    Analyze how resource allocation impacts mission success.
    Shows the relationship between resource usage and outcomes.
    """
    plt.figure(figsize=(12, 6))
    resource_types = list(results['resource_metrics'].keys())
    
    # Calculate usage ratios and success correlation
    usage_ratios = []
    for rt in resource_types:
        metrics = results['resource_metrics'][rt]
        if metrics['avg_allocated'] > 0:
            ratio = (metrics['avg_allocated'] - metrics['avg_remaining']) / metrics['avg_allocated']
            usage_ratios.append(ratio * 100)
        else:
            usage_ratios.append(0)
    
    # Create grouped bar chart
    x = range(len(resource_types))
    plt.bar(x, usage_ratios, alpha=0.7)
    
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Usage Ratio (%)')
    plt.title('Resource Usage Impact Analysis\n' +
             'How different resources contribute to mission execution')
    
    # Add percentage labels
    for i, ratio in enumerate(usage_ratios):
        plt.text(i, ratio, f'{ratio:.1f}%', ha='center', va='bottom')
    
    save_plot(plt, "resource_impact", policy_name, experiment_id)

def plot_metrics_summary(results: Dict, policy_name: str, experiment_id: str):
    """
    Create a simple table visualization of key metrics.
    Shows core performance indicators in an easy-to-read format.
    """
    plt.figure(figsize=(10, 6))
    
    # Prepare data for the table
    data = [
        ['Success Rate', f"{results['success_rate']*100:.1f}%"],
        ['Average Time', f"{results['avg_time']:.2f} units"],
        ['Average Path Length', f"{results['avg_path_length']:.2f} units"]
    ]
    
    # Add resource metrics
    for resource_type, metrics in results['resource_metrics'].items():
        allocated = metrics['avg_allocated']
        used = allocated - metrics['avg_remaining']
        efficiency = (used / allocated * 100) if allocated > 0 else 0
        data.append([
            f"{resource_type.replace('_', ' ').title()} Efficiency",
            f"{efficiency:.1f}% ({used:.1f}/{allocated:.1f})"
        ])

    # Create table
    ax = plt.gca()
    ax.axis('off')
    table = Table(ax, bbox=[0.1, 0.1, 0.8, 0.8])
    
    # Add cells
    n_rows = len(data)
    width = 0.4
    height = 0.8 / n_rows
    
    for i, (metric, value) in enumerate(data):
        table.add_cell(i, 0, width, height, text=metric,
                      loc='left', facecolor='lightgray')
        table.add_cell(i, 1, width, height, text=value,
                      loc='right')
    
    ax.add_table(table)
    plt.title('Mission Performance Summary\nKey Metrics Overview', pad=20)
    
    save_plot(plt, "metrics_summary", policy_name, experiment_id)

def plot_metric_correlations(results: Dict, policy_name: str, experiment_id: str):
    """
    Create a correlation matrix between key performance metrics and environmental factors.
    Shows relationships between mission outcomes and various indicators.
    """
    plt.figure(figsize=(12, 10))
    
    # Prepare correlation data
    metrics_by_size = {
        size: {
            'success_rate': data['success_rate'],
            'avg_time': data['avg_time'],
            'avg_path_length': data['avg_path_length'],
            'resource_efficiency': sum(
                m['avg_used'] / m['avg_allocated']
                if m['avg_allocated'] > 0 else 0
                for m in data['resource_metrics'].values()
            ) / len(data['resource_metrics'])
        }
        for size, data in results['by_size'].items()
    }
    
    # Add environmental indicators
    for size, data in results['by_size'].items():
        # Add node indicators
        for indicator, value in data['proxy_data']['nodes'].items():
            metrics_by_size[size][f'node_{indicator}'] = value
        
        # Add edge indicators
        for indicator, value in data['proxy_data']['edges'].items():
            metrics_by_size[size][f'edge_{indicator}'] = value
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(metrics_by_size, orient='index')
    
    # Calculate correlation matrix
    core_metrics = ['success_rate', 'avg_time', 'avg_path_length', 'resource_efficiency']
    correlation_matrix = []
    labels_y = []
    
    for metric in core_metrics:
        correlations = []
        for col in df.columns:
            if col not in core_metrics:  # Correlate with environmental indicators
                corr = df[metric].corr(df[col])
                if not pd.isna(corr):
                    correlations.append(corr)
                    if metric == core_metrics[0]:  # Only add label once
                        labels_y.append(col.replace('node_', 'Node: ').replace('edge_', 'Edge: ')
                                     .replace('_', ' ').title())
    
        correlation_matrix.append(correlations)
    
    # Plot correlation matrix
    im = plt.imshow(correlation_matrix, aspect='auto', cmap='RdYlBu')
    plt.colorbar(im, label='Correlation Strength')
    
    # Add labels
    plt.yticks(range(len(core_metrics)), 
              [m.replace('_', ' ').title() for m in core_metrics])
    plt.xticks(range(len(labels_y)), labels_y, rotation=45, ha='right')
    
    # Add correlation values
    for i in range(len(core_metrics)):
        for j in range(len(labels_y)):
            text = f'{correlation_matrix[i][j]:.2f}'
            plt.text(j, i, text, ha='center', va='center')
    
    plt.title('Core Metrics vs Environmental Indicators\n' +
              'Correlation Analysis of Mission Performance Factors')
    
    plt.tight_layout()
    save_plot(plt, "metric_correlations", policy_name, experiment_id)

def generate_all_visualizations(results: Dict, policy_name: str, experiment_id: str):
    """Generate and save all visualization types with explanations"""
    print("\nGenerating Visualizations...")
    
    # Success Rate Analysis
    print("\n1. Success Rate Analysis:")
    plot_success_rates(results, policy_name, experiment_id)
    print("- Shows how mission success varies with city size")
    print("- Helps identify optimal operational scale")
    print("- Highlights potential complexity thresholds")
    
    # Resource Efficiency
    print("\n2. Resource Efficiency Analysis:")
    plot_resource_efficiency(results, policy_name, experiment_id)
    print("- Compares resource allocation vs actual usage")
    print("- Identifies potential over/under-allocation")
    print("- Highlights resource utilization patterns")
    
    # Proxy Data Correlations
    print("\n3. Environmental Indicator Analysis:")
    plot_proxy_success_correlation(results, policy_name, experiment_id)
    print("- Shows how different factors predict mission outcomes")
    print("- Identifies key environmental indicators")
    print("- Helps in risk assessment and planning")
    
    # Time-Distance Relationship
    print("\n4. Time-Distance Analysis:")
    plot_time_distance_relationship(results, policy_name, experiment_id)
    print("- Reveals relationship between path length and mission time")
    print("- Helps in mission duration estimation")
    print("- Identifies efficiency outliers")
    
    # Resource Impact
    print("\n5. Resource Impact Analysis:")
    plot_resource_impact(results, policy_name, experiment_id)
    print("- Shows effectiveness of different resources")
    print("- Helps optimize resource allocation")
    print("- Identifies critical resources")
    
    # Proxy-Resource Patterns
    print("\n6. Environmental-Resource Patterns:")
    plot_proxy_resource_patterns(results, policy_name, experiment_id)
    print("- Shows how environmental factors affect resource needs")
    print("- Helps predict resource requirements")
    print("- Identifies key resource drivers")
    
    # Metrics Summary
    print("\n7. Metrics Summary Table:")
    plot_metrics_summary(results, policy_name, experiment_id)
    print("- Shows key performance indicators")
    print("- Provides quick overview of mission outcomes")
    print("- Highlights resource utilization efficiency")
    
    # Metric Correlations
    print("\n8. Metric Correlations Analysis:")
    plot_metric_correlations(results, policy_name, experiment_id)
    print("- Shows relationships between core metrics and environmental factors")
    print("- Helps identify key performance drivers")
    print("- Reveals environmental impact on mission success")
    
    vis_path = os.path.join("data/policies", policy_name, "experiments", experiment_id, "visualizations")
    print(f"\nAll visualizations have been saved to '{vis_path}/'")

def visualize_bulk_results(results: Dict):
    """
    Create comprehensive visualizations of bulk simulation results
    showing patterns and relationships between environmental indicators
    """
    plt.figure(figsize=(20, 15))
    
    # 1. Success Rate Analysis
    plt.subplot(3, 2, 1)
    sizes = sorted(results['by_size'].keys())
    success_rates = [results['by_size'][size]['success_rate'] * 100 for size in sizes]
    
    plt.bar(sizes, success_rates, alpha=0.7)
    plt.axhline(y=results['success_rate'] * 100, color='r', linestyle='--',
                label=f'Overall: {results["success_rate"]*100:.1f}%')
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Success Rate (%)')
    plt.title('Mission Success by City Size')
    plt.legend()
    
    # 2. Resource Efficiency Analysis
    plt.subplot(3, 2, 2)
    resource_types = list(results['resource_metrics'].keys())
    x = range(len(resource_types))
    
    carried = [metrics['avg_allocated'] for metrics in results['resource_metrics'].values()]
    remaining = [metrics['avg_remaining'] for metrics in results['resource_metrics'].values()]
    used = [c - r for c, r in zip(carried, remaining)]
    
    plt.bar(x, carried, alpha=0.4, label='Carried', color='lightblue')
    plt.bar(x, used, alpha=0.8, label='Used', color='blue')
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Average Amount')
    plt.title('Resource Usage Patterns')
    plt.legend()
    
    # 3. Environmental Risk Patterns
    plt.subplot(3, 2, 3)
    risk_metrics = ['avg_structural_risk', 'avg_path_difficulty', 'avg_resource_demand']
    risk_data = {
        size: [results['by_size'][size]['proxy_metrics'][m] for m in risk_metrics]
        for size in sizes
    }
    
    x = np.arange(len(sizes))
    width = 0.25
    
    for i, metric in enumerate(risk_metrics):
        values = [risk_data[size][i] for size in sizes]
        plt.bar(x + i*width, values, width, alpha=0.7,
                label=metric.replace('avg_', '').replace('_', ' ').title())
    
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Risk Level')
    plt.title('Environmental Risk Patterns by City Size')
    plt.xticks(x + width, sizes)
    plt.legend()
    
    # 4. Time vs Distance Analysis
    plt.subplot(3, 2, 4)
    times = [results['by_size'][size]['avg_time'] for size in sizes]
    distances = [results['by_size'][size]['avg_path_length'] for size in sizes]
    success_sizes = [s for s, r in zip(sizes, success_rates) if r > 0]
    success_times = [t for t, r in zip(times, success_rates) if r > 0]
    success_distances = [d for d, r in zip(distances, success_rates) if r > 0]
    
    plt.scatter(success_distances, success_times, c=success_sizes, 
                cmap='viridis', s=100, alpha=0.6)
    plt.colorbar(label='City Size (Nodes)')
    plt.xlabel('Path Length')
    plt.ylabel('Time Taken')
    plt.title('Mission Time vs Path Length\n(Successful Missions)')
    
    # 5. Risk Correlation Analysis
    plt.subplot(3, 2, (5, 6))
    metrics = ['structural_risk', 'path_difficulty', 'resource_demand']
    n_metrics = len(metrics)
    correlation_matrix = np.zeros((n_metrics, n_metrics))
    
    # Calculate correlations between metrics
    for i, m1 in enumerate(metrics):
        for j, m2 in enumerate(metrics):
            values1 = [results['by_size'][size]['proxy_metrics'][f'avg_{m1}'] 
                      for size in sizes]
            values2 = [results['by_size'][size]['proxy_metrics'][f'avg_{m2}']
                      for size in sizes]
            correlation_matrix[i, j] = np.corrcoef(values1, values2)[0, 1]
    
    plt.imshow(correlation_matrix, cmap='RdYlBu', aspect='auto')
    plt.colorbar(label='Correlation')
    plt.xticks(range(n_metrics), [m.replace('_', ' ').title() for m in metrics])
    plt.yticks(range(n_metrics), [m.replace('_', ' ').title() for m in metrics])
    plt.title('Risk Metric Correlations')
    
    # Add correlation values
    for i in range(n_metrics):
        for j in range(n_metrics):
            plt.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                    ha='center', va='center')
    
    plt.tight_layout()
    plt.show()

def visualize_pattern_analysis(results: Dict):
    """
    Analyze and visualize specific environmental patterns and their impact
    """
    plt.figure(figsize=(20, 10))
    
    # 1. Resource Demand vs Environmental Factors
    plt.subplot(2, 2, 1)
    sizes = sorted(results['by_size'].keys())
    
    structural = [results['by_size'][size]['proxy_metrics']['avg_structural_risk']
                 for size in sizes]
    resource_demand = [results['by_size'][size]['proxy_metrics']['avg_resource_demand']
                      for size in sizes]
    success_rates = [results['by_size'][size]['success_rate'] for size in sizes]
    
    plt.scatter(structural, resource_demand, c=success_rates, 
                s=100, alpha=0.6, cmap='RdYlBu')
    plt.colorbar(label='Success Rate')
    plt.xlabel('Structural Risk')
    plt.ylabel('Resource Demand')
    plt.title('Resource Demand vs Structural Risk')
    
    # 2. Path Difficulty Distribution
    plt.subplot(2, 2, 2)
    difficulties = [results['by_size'][size]['proxy_metrics']['avg_path_difficulty']
                   for size in sizes]
    
    plt.hist(difficulties, bins=10, alpha=0.7)
    plt.axvline(np.mean(difficulties), color='r', linestyle='--',
                label=f'Mean: {np.mean(difficulties):.2f}')
    plt.xlabel('Path Difficulty')
    plt.ylabel('Frequency')
    plt.title('Distribution of Path Difficulties')
    plt.legend()
    
    # 3. Success Rate vs Resource Allocation
    plt.subplot(2, 2, 3)
    resource_types = list(results['resource_metrics'].keys())
    allocation_ratios = []
    
    for rt in resource_types:
        metrics = results['resource_metrics'][rt]
        ratio = metrics['avg_remaining'] / metrics['avg_allocated']
        allocation_ratios.append(ratio)
    
    plt.bar(range(len(resource_types)), allocation_ratios, alpha=0.7)
    plt.xticks(range(len(resource_types)), 
               [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Remaining/Allocated Ratio')
    plt.title('Resource Allocation Efficiency')
    
    # 4. Risk Factor Analysis
    plt.subplot(2, 2, 4)
    metrics = ['structural_risk', 'path_difficulty', 'resource_demand']
    success_threshold = 0.7
    
    high_success = [size for size in sizes 
                   if results['by_size'][size]['success_rate'] >= success_threshold]
    low_success = [size for size in sizes 
                  if results['by_size'][size]['success_rate'] < success_threshold]
    
    def get_avg_metrics(size_group):
        return [
            np.mean([results['by_size'][size]['proxy_metrics'][f'avg_{m}']
                    for size in size_group])
            for m in metrics
        ]
    
    high_metrics = get_avg_metrics(high_success)
    low_metrics = get_avg_metrics(low_success)
    
    x = np.arange(len(metrics))
    width = 0.35
    
    plt.bar(x - width/2, high_metrics, width, label=f'Success ≥ {success_threshold*100}%',
            alpha=0.7)
    plt.bar(x + width/2, low_metrics, width, label=f'Success < {success_threshold*100}%',
            alpha=0.7)
    
    plt.xticks(x, [m.replace('_', ' ').title() for m in metrics])
    plt.ylabel('Average Risk Level')
    plt.title('Risk Factors: High vs Low Success Missions')
    plt.legend()
    
    plt.tight_layout()
    plt.show() 