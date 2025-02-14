import random
from typing import Dict, List, Tuple

from public.lib.interfaces import (
    CityGraph, ProxyData, SimulationResult, 
    ResourceTypes, ResourceUsage
)

class PathEvaluator:
    """Evaluates the success of an evacuation path"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            
    def _check_resource_usage(self, path: List[int], resources: Dict[str, int], max_resources:int) -> Tuple[bool, str, ResourceUsage, List[Tuple[int, str]]]:
        """Check if resources are sufficient for the given path."""
        resource_usage = ResourceUsage()
        events = []  # List of (step_number, event_description)
        
        # Initialize allocated resources
        total_allocated_resources = 0
        for rt, amount in resources.items():
            total_allocated_resources+= amount
            resource_usage.allocated[rt] = amount
            resource_usage.used[rt] = 0
            resource_usage.needed[rt] = 0
            resource_usage.effective_uses[rt] = 0
        
        # Log mission start
        events.append((0, f"Mission started at node {path[0]}"))
        if amount> max_resources:
            events.append((1, f'Mission Failed, you exceeded the amout of allowed resources and your team was killed by the population due to their greed.'))
            for rt, amount in resources.items(): # Loose all the reources
                resource_usage.allocated[rt] = amount
                resource_usage.used[rt] = amount
                resource_usage.needed[rt] = 0
                resource_usage.effective_uses[rt] = 0
            return False, f"Your team was killed due to excesive greed by the population in at the start", resource_usage, events
        # Track resource usage at each node
        for i, node in enumerate(path, 1):
            events.append((i, f"Arrived at node {node}"))
            
            # Check radiation suit usage
            if self.radiation[node] > 0.35:  # Lowered from 0.4
                events.append((i, f"High radiation detected (level: {self.radiation[node]:.2f})"))
                resource_usage.needed['radiation_suits'] += 1
                if resource_usage.allocated['radiation_suits'] <= resource_usage.used['radiation_suits']:
                    events.append((i, f"TEAM DIED - Ran out of radiation suits"))
                    return False, f"Ran out of radiation suits at node {node}", resource_usage, events
                resource_usage.used['radiation_suits'] += 1
                resource_usage.effective_uses['radiation_suits'] += 1
                events.append((i, f"Used radiation suit successfully"))
                
            # Check ammo usage for zombies
            if self.zombies[node] > 0.45:  # Lowered from 0.5
                events.append((i, f"Zombie horde encountered (level: {self.zombies[node]:.2f})"))
                resource_usage.needed['ammo'] += 1
                if resource_usage.allocated['ammo'] <= resource_usage.used['ammo']:
                    events.append((i, f"TEAM DIED - Ran out of ammo"))
                    return False, f"Ran out of ammo at node {node}", resource_usage, events
                # 35% chance ammo fails to clear zombies (increased from 20%)
                if random.random() < 0.35:
                    events.append((i, f"TEAM DIED - Ammo failed to clear zombies"))
                    return False, f"Ammo failed to clear zombies at node {node}", resource_usage, events
                resource_usage.used['ammo'] += 1
                resource_usage.effective_uses['ammo'] += 1
                events.append((i, f"Used ammo successfully against zombies"))
                
            # Check explosives for blockages
            if i < len(path) - 1:
                edge = tuple(sorted((path[i], path[i+1])))
                if edge in self.blockages and self.blockages[edge]:
                    events.append((i, f"Path blocked to node {path[i+1]} (blockage detected)"))
                    resource_usage.needed['explosives'] += 1
                    if resource_usage.allocated['explosives'] <= resource_usage.used['explosives']:
                        events.append((i, f"TEAM DIED - Ran out of explosives"))
                        return False, f"Ran out of explosives at edge {edge}", resource_usage, events
                    # 25% chance explosives fail (increased from 10%)
                    if random.random() < 0.25:
                        events.append((i, f"TEAM DIED - Explosives failed to clear blockage"))
                        return False, f"Explosives failed to clear blockage at edge {edge}", resource_usage, events
                    resource_usage.used['explosives'] += 1
                    resource_usage.effective_uses['explosives'] += 1
                    events.append((i, f"Used explosives successfully to clear path"))
                
            # Random events that consume resources
            if random.random() < 0.15:  # 15% chance of unexpected zombie encounter
                events.append((i, f"Surprise zombie encounter!"))
                resource_usage.needed['ammo'] += 1
                if resource_usage.allocated['ammo'] <= resource_usage.used['ammo']:
                    events.append((i, f"TEAM DIED - No ammo for surprise zombie encounter"))
                    return False, f"Ran out of ammo during surprise zombie encounter at node {node}", resource_usage, events
                resource_usage.used['ammo'] += 1
                resource_usage.effective_uses['ammo'] += 1
                events.append((i, f"Successfully handled surprise zombie encounter"))
                
            if random.random() < 0.1:  # 10% chance of radiation leak
                events.append((i, f"Unexpected radiation leak detected!"))
                resource_usage.needed['radiation_suits'] += 1
                if resource_usage.allocated['radiation_suits'] <= resource_usage.used['radiation_suits']:
                    events.append((i, f"TEAM DIED - No suits for radiation leak"))
                    return False, f"Ran out of suits during radiation leak at node {node}", resource_usage, events
                resource_usage.used['radiation_suits'] += 1
                resource_usage.effective_uses['radiation_suits'] += 1
                events.append((i, f"Successfully protected against radiation leak"))
            
            if i < len(path) - 1:
                events.append((i, f"Moving to node {path[i+1]}"))
        
        # Log successful completion
        events.append((len(path), f"Successfully reached extraction point at node {path[-1]}"))
        return True, "Successfully reached extraction point", resource_usage, events
        
    def evaluate(self, path: List[int], resources: Dict[str, int],
                city: CityGraph, true_state: Dict, max_resources:int=10000) -> SimulationResult:
        """
        Evaluate a proposed evacuation plan
        
        Args:
            path: List of node IDs in the path
            resources: Dict of resources allocated
            city: The city layout
            true_state: The true state of obstacles
            
        Returns:
            SimulationResult with metrics
        """
        result = SimulationResult()
        
        # Store true state data for resource checking
        self.radiation = true_state['radiation']
        self.zombies = true_state['zombies']
        self.blockages = true_state['blockages']
        
        # Calculate path length
        path_length = 0
        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i+1]
            path_length += city.graph[n1][n2]['weight']
            
        # Check if path reaches an extraction point
        reaches_extraction = path[-1] in city.extraction_nodes
        
        # Check resource usage
        resources_sufficient, failure_reason, resource_usage, events = self._check_resource_usage(path, resources, max_resources)
            
        # Determine success and failure reason
        success = reaches_extraction and resources_sufficient
        if not success and not failure_reason:
            failure_reason = "Path does not reach extraction point"
            events.append((len(path), "FAILED - Path does not reach extraction point"))
                
        # Calculate time taken (affected by obstacles and resource usage)
        base_time = path_length
        total_obstacles = sum(resource_usage.needed.values())  # Count total obstacles encountered
        obstacle_delay = total_obstacles * 0.5  # Each obstacle adds 50% time
        time_taken = base_time * (1 + obstacle_delay + random.uniform(0, 0.2))
        
        result.set_metrics(
            success=success,
            path_length=path_length,
            time=time_taken,
            obstacles=total_obstacles,
            resources=resource_usage,
            failure_reason=failure_reason,
            events=events
        )
        
        return result 