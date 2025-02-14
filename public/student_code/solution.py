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
        # print(f'City graph: {city.graph} \n')
        # print(f'City starting_node: {city.starting_node}\n')
        # print(f'City extraction_nodes: {city.extraction_nodes}\n')
        # print(f'Proxy node_data: {proxy_data.node_data} \n \n')
        # print(f'Proxy edge_data: {proxy_data.edge_data} \n \n')
        # print(f'Max Resources: {max_resources} \n \n')
        
        # TODO: Implement your solution here
        # This is just a placeholder that returns a simple path to the first extraction point
        target = city.extraction_nodes[0]
        
        try:
            path = nx.shortest_path(city.graph, city.starting_node, target, 
                                  weight='weight')
        except nx.NetworkXNoPath:
            path = [city.starting_node]
        print(f'Path {path} \n')
        max_resources = 10000
        # Placeholder resource allocation
        resources = {
            'explosives': max_resources // 3,
            'ammo': max_resources // 3,
            'radiation_suits': max_resources // 3
        }
        
        return PolicyResult(path, resources) 