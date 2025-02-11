# Guía Técnica: Sistema de Evacuación Zombie

## Primeros Pasos

### Prerequisitos
- Python 3.8 o superior
- Paquetes requeridos: networkx, numpy, matplotlib, pandas

### Instalación
1. Clona el repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Descripción General del Sistema

El sistema de evacuación consta de varios componentes:
1. Representación del entorno de la ciudad
2. Recolección de datos ambientales
3. Implementación de la política
4. Simulación y evaluación
5. Análisis de resultados y visualización

### Componentes Principales

#### CityGraph
Representa el diseño de la ciudad como un grafo:
- Nodes: Ubicaciones en la ciudad
- Edges: Rutas entre ubicaciones
- Attributes: Distancias, coordenadas

```python
class CityGraph:
    graph: networkx.Graph        # Diseño de la ciudad
    starting_node: int          # Posición inicial
    extraction_nodes: List[int] # Puntos de extracción posibles
```

#### ProxyData
Contiene lecturas de sensores ambientales:
- Node data: Condiciones en cada ubicación
- Edge data: Condiciones a lo largo de las rutas

```python
class ProxyData:
    node_data: Dict[int, Dict]  # Datos para cada nodo
    edge_data: Dict[Tuple[int, int], Dict]  # Datos para cada borde
```

#### ResourceTypes
Tipos de recursos disponibles:
- `explosives`: Despejar rutas bloqueadas
- `ammo`: Manejar encuentros hostiles
- `radiation_suits`: Proteger de la radiación

## Implementando tu Solución

### La Clase EvacuationPolicy

Tu solución debe implementarse en la clase `EvacuationPolicy` en `public/student_code/solution.py`:

```python
def plan_evacuation(self, city: CityGraph, proxy_data: ProxyData, 
                   max_resources: int) -> PolicyResult:
    """
    Planifica la ruta de evacuación y asignación de recursos.
    
    Args:
        city: Diseño de la ciudad
        proxy_data: Datos ambientales
        max_resources: Máximo total de recursos disponibles
        
    Returns:
        PolicyResult con:
        - path: List[int] - Secuencia de nodos a visitar
        - resources: Dict[str, int] - Asignación de recursos
    """
```

### Indicadores Ambientales

#### Indicadores de Nodo
- `radiation_readings`: Niveles de radiación (0-1)
- `thermal_readings`: Firmas de calor (0-1)
- `seismic_activity`: Inestabilidad estructural (0-1)
- `signal_strength`: Calidad de comunicaciones (0-1)
- `population_density`: Niveles de actividad (0-1)
- `emergency_calls`: Señales de socorro (0-1)
- `structural_integrity`: Condición del edificio (0-1)

#### Indicadores de Borde
- `structural_damage`: Bloqueo de ruta (0-1)
- `signal_interference`: Interrupción de comunicaciones (0-1)
- `movement_sightings`: Detección de actividad (0-1)
- `debris_density`: Niveles de obstáculos (0-1)
- `hazard_gradient`: Cambios ambientales (0-1)

## Probando tu Solución

### Prueba Individual
Prueba tu política en un escenario único:
```bash
python3 run_simulation.py
```

### Pruebas Masivas
Prueba en múltiples escenarios:
```bash
python3 run_bulk_simulations.py
```

Agrega el flag `--skip-city-analysis` para omitir el análisis detallado por ciudad:
```bash
python3 run_bulk_simulations.py --skip-city-analysis
```

## Entendiendo los Resultados

### Resultados de Misión
Cada intento de evacuación produce:
- Estado de éxito/fracaso
- Ruta tomada
- Recursos utilizados
- Tiempo tomado
- Registro detallado de eventos

### Análisis Masivo
Múltiples ejecuciones generan:
- Tasas de éxito por tamaño de ciudad
- Patrones de uso de recursos
- Correlaciones ambientales
- Visualizaciones de rendimiento

## Visualizaciones

### Diseño de Ciudad
- Colores de nodo indican estado
- Grosor de borde muestra ruta tomada
- Íconos muestran uso de recursos
- Registro de eventos muestra progreso de misión

### Gráficos de Análisis
- Tasa de éxito por tamaño de ciudad
- Eficiencia de recursos
- Correlaciones ambientales
- Relaciones tiempo-distancia
- Análisis de impacto de recursos

## Consejos para Desarrollo

1. Comienza Simple
   - Prueba primero la búsqueda de rutas básica
   - Agrega gestión de recursos gradualmente
   - Valida en escenarios individuales antes de pruebas masivas

2. Usa las Herramientas Disponibles
   - NetworkX para operaciones de grafo
   - Matplotlib para visualizaciones personalizadas
   - Pandas para análisis de datos

3. Depura Efectivamente
   - Revisa registros de eventos para puntos de fallo
   - Analiza patrones de uso de recursos
   - Prueba casos límite con diferentes tamaños de ciudad 