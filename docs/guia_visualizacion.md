
# Guía de Visualización y Métricas

Esta guía explica cómo interpretar las diferentes visualizaciones y métricas generadas a partir de las simulaciones masivas. Cada visualización proporciona diferentes perspectivas sobre el rendimiento de las misiones y las interacciones con el entorno.

## Métricas de Rendimiento Principales

Las siguientes métricas son rastreadas y visualizadas a lo largo del análisis:

1. **Tasa de Éxito**
   - Porcentaje de misiones completadas exitosamente
   - Medida a través de diferentes tamaños de ciudad
   - Promedio general de éxito

2. **Eficiencia de Recursos**
   - Proporción de recursos utilizados vs. asignados
   - Seguimiento por tipo de recurso (explosivos, municiones, trajes de radiación)
   - Eficiencia = (Recursos Utilizados / Recursos Asignados) × 100%

3. **Tiempo de Misión**
   - Duración requerida para completar misiones
   - Correlacionada con longitud de ruta y tamaño de ciudad
   - Medida en unidades de tiempo de simulación

## Interpretación de Visualizaciones

### 1. Tabla Resumen de Métricas
- Vista rápida de indicadores clave de rendimiento
- Muestra:
  - Tasa general de éxito
  - Tiempo promedio de misión
  - Estadísticas de longitud de ruta
  - Eficiencia de recursos por tipo

### 2. Análisis de Tasa de Éxito
- Gráfico de barras mostrando tasas de éxito por tamaño de ciudad
- Línea roja punteada indica el promedio general
- Ayuda a identificar:
  - Escalas operativas óptimas
  - Umbrales de rendimiento
  - Impacto del tamaño de la ciudad

### 3. Análisis de Uso de Recursos
- Gráfico de barras apiladas comparando recursos asignados vs. utilizados
- Muestra:
  - Patrones de utilización de recursos
  - Eficiencia de asignación
  - Distribución de uso por tipo de recurso

### 4. Relación Tiempo-Distancia
- Gráfico de dispersión de tiempo de misión vs. longitud de ruta
- Codificado por color según tamaño de ciudad
- Revela:
  - Patrones de duración de misión
  - Eficiencia de ruta
  - Impactos relacionados con el tamaño

### 5. Patrones de Riesgo Ambiental
- Gráfico de barras múltiples mostrando métricas de riesgo por tamaño de ciudad
- Rastrea:
  - Riesgo estructural
  - Dificultad de ruta
  - Demanda de recursos
- Muestra cómo escalan los desafíos ambientales con el tamaño de la ciudad

### 6. Correlaciones de Métricas
- Mapa de calor mostrando relaciones entre:
  - Métricas principales de rendimiento
  - Indicadores ambientales
  - Patrones de uso de recursos
- Intensidad de correlación indicada por color

## Métricas Clave para Análisis

Las siguientes métricas pueden utilizarse para evaluar el rendimiento de la misión:

1. **Eficiencia Operativa**
   - Tasa de éxito
   - Utilización de recursos
   - Tiempo de finalización

2. **Gestión de Recursos**
   - Ratios de eficiencia de recursos
   - Precisión de asignación
   - Patrones de uso

3. **Impacto Ambiental**
   - Manejo de riesgos
   - Optimización de ruta
   - Escalabilidad por tamaño

4. **Fiabilidad de Misión**
   - Consistencia de éxito
   - Predictibilidad de recursos
   - Confiabilidad temporal

## Estructura de Datos

Los resultados están organizados jerárquicamente:
```json
{
    "total_runs": int,
    "tasa_exito": float,
    "tiempo_promedio": float,
    "longitud_ruta_promedio": float,
    "por_tamano": {
        "tamano_n": {
            "tasa_exito": float,
            "tiempo_promedio": float,
            "metricas_recursos": {...}
        }
    },
    "metricas_recursos": {
        "tipo_recurso": {
            "promedio_asignado": float,
            "promedio_usado": float,
            "promedio_restante": float
        }
    }
}
```

## Uso de las Visualizaciones

1. Comenzar con la Tabla Resumen de Métricas para una vista general rápida
2. Utilizar el Análisis de Tasa de Éxito para entender impactos de escala
3. Examinar patrones de Uso de Recursos para perspectivas de eficiencia
4. Revisar Patrones de Riesgo Ambiental para evaluación de desafíos
5. Usar Correlaciones de Métricas para entender relaciones entre factores

Estas visualizaciones y métricas proporcionan una vista integral del rendimiento de las misiones a través de diferentes dimensiones, permitiendo un análisis basado en datos de la efectividad operacional.

