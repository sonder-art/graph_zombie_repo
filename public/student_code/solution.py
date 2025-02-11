import networkx as nx
from typing import Dict, List

from public.lib.interfaces import CityGraph, ProxyData, PolicyResult

class EvacuationPolicy:
    """
    Your evacuation policy implementation.
    This is the class you need to implement to solve the evacuation problem.
    """
    
    def plan_evacuation(self, city: CityGraph, proxy_data: ProxyData, 
                       max_resources: int) -> PolicyResult:
        """
        Plan the evacuation route and resource allocation.
        
        Args:
            city: The city layout with nodes and edges
                 - city.graph: NetworkX graph with the city layout
                 - city.starting_node: Your starting position
                 - city.extraction_nodes: List of possible extraction points
                 
            proxy_data: Information about the environment
                 - proxy_data.node_data[node_id]: Dict with node indicators
                 - proxy_data.edge_data[(node1,node2)]: Dict with edge indicators
                 
            max_resources: Maximum total resources you can allocate
            
        Returns:
            PolicyResult with:
            - path: List[int] - List of node IDs forming your evacuation path
            - resources: Dict[str, int] - How many of each resource to take:
                       {'explosives': x, 'ammo': y, 'radiation_suits': z}
                       where x + y + z <= max_resources
        """
        # TODO: Implement your solution here
        # This is just a placeholder that returns a simple path to the first extraction point
        target = city.extraction_nodes[0]
        
        try:
            path = nx.shortest_path(city.graph, city.starting_node, target, 
                                  weight='weight')
        except nx.NetworkXNoPath:
            path = [city.starting_node]
        
        # Placeholder resource allocation
        resources = {
            'explosives': max_resources // 3,
            'ammo': max_resources // 3,
            'radiation_suits': max_resources // 3
        }
        
        return PolicyResult(path, resources) 