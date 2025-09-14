# Simulador de Gestión de Procesos del Sistema Operativo

Esta aplicación web simula el comportamiento del sistema operativo en la gestión de procesos, implementando estructuras PCB (Process Control Block) y algoritmos de planificación clásicos.

## Características Implementadas

### ✅ Requisitos Funcionales Cumplidos

1. **Estructuras PCB (Process Control Block)**
   - Cada proceso tiene: PID, tiempo de llegada, duración, prioridad, estado, tiempos de ejecución

2. **Colas de Procesos**
   - Visualización de estados: NEW, READY, RUNNING, TERMINATED
   - Seguimiento del paso del tiempo y turno de cada proceso

3. **Algoritmos de Planificación Implementados**
   - **FCFS** (First Come First Served)
   - **SJF** (Shortest Job First) 
   - **Round Robin** con quantum configurable

4. **Sistema de Entrada**
   - Formulario para definir número de procesos
   - Configuración de parámetros: tiempo de llegada, duración, prioridad

5. **Visualización Gráfica**
   - Colas de planificación en tiempo real
   - Estados de cada proceso
   - Log del paso del tiempo y turno de procesos
   - Estadísticas completas (tiempo de espera, retorno, etc.)

## Instalación y Ejecución

### Prerrequisitos
- Python 3.7 o superior

### Pasos para ejecutar

1. **Instalar dependencias:**
   ```
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación:**
   ```
   python app.py
   ```

3. **Abrir en el navegador:**
   ```
   http://localhost:5000
   ```

## Uso de la Aplicación

### 1. Configurar Procesos
- Selecciona el algoritmo de planificación (FCFS, SJF, o Round Robin)
- Para Round Robin, configura el quantum de tiempo
- Agrega procesos con sus parámetros:
  - **PID**: Identificador único del proceso
  - **Tiempo de Llegada**: Cuándo llega el proceso al sistema
  - **Duración**: Tiempo que necesita el proceso para completarse
  - **Prioridad**: Valor numérico (actualmente usado solo para referencia)

### 2. Ejecutar Simulación
- Haz clic en "Iniciar Simulación"
- La aplicación mostrará:
  - **Log de Ejecución**: Paso a paso del tiempo y acciones
  - **Estados de Procesos**: Cambios de estado a lo largo del tiempo
  - **Estadísticas**: Tiempos de finalización, espera y retorno

### 3. Interpretar Resultados
- **Estados visualizados:**
  - 🔵 NEW: Proceso recién creado
  - 🟡 READY: Proceso listo para ejecutar
  - 🟢 RUNNING: Proceso en ejecución
  - ⚫ TERMINATED: Proceso terminado

## Ejemplo de Uso

1. Selecciona "Round Robin" con quantum = 2
2. Agrega estos procesos:
   - P1: Llegada=0, Duración=5
   - P2: Llegada=1, Duración=3
   - P3: Llegada=2, Duración=4
3. Ejecuta la simulación y observa cómo Round Robin alterna entre procesos

## Estructura del Proyecto

```
procesos 4.1/
├── app.py              # Aplicación Flask principal con lógica de simulación
├── requirements.txt    # Dependencias del proyecto
├── templates/
│   └── index.html     # Interfaz web principal
├── static/
│   └── style.css      # Estilos CSS para visualización
└── README.md          # Este archivo
```

## Notas Técnicas

- **No ejecuta procesos reales**: Solo simula el comportamiento interno del SO
- **Modelo de procesamiento**: Sistemas con planificación básica por lotes
- **Algoritmos**: Implementación fiel a los algoritmos clásicos de planificación
- **Interfaz**: Diseño responsivo que funciona en desktop y móvil

La aplicación cumple estrictamente con todos los requisitos especificados para la simulación de gestión de procesos del sistema operativo.