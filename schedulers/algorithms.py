"""
Algoritmos de Planificación de Procesos
========================================
Implementa tres algoritmos básicos de sistemas operativos:
- FCFS (First Come First Served)
- SJF (Shortest Job First) 
- Round Robin
"""

class SchedulingAlgorithms:
    """Algoritmos de planificación de procesos para el sistema operativo"""
    
    @staticmethod
    def _agregar_evento(historial, tiempo, accion, proceso_id, estado):
        """Función auxiliar para agregar eventos al historial de manera consistente"""
        historial.append({
            'time': tiempo,
            'action': accion,
            'process': proceso_id,
            'state': estado
        })
    
    @staticmethod
    def _ejecutar_proceso_completo(proceso, tiempo_inicio, historial):
        """
        Función auxiliar que ejecuta un proceso completamente.
        Útil para FCFS y SJF que no tienen interrupciones.
        """
        # Marcar como listo
        proceso.state = "READY"
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_inicio, f'Proceso {proceso.pid} → LISTO', proceso.pid, 'READY'
        )
        
        # Comenzar ejecución
        proceso.start_time = tiempo_inicio
        proceso.state = "EXECUTING"
        proceso.update_cpu_context(program_counter=0, instruction_pointer=tiempo_inicio)
        
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_inicio, f'Proceso {proceso.pid} → EJECUTANDO', proceso.pid, 'EXECUTING'
        )
        
        # Calcular tiempo de finalización
        tiempo_fin = tiempo_inicio + proceso.burst_time
        
        # Marcar como terminado
        proceso.completion_time = tiempo_fin
        proceso.calculate_times()
        proceso.state = "TERMINATED"
        proceso.update_cpu_context(program_counter=proceso.burst_time)
        
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_fin, f'Proceso {proceso.pid} → TERMINADO', proceso.pid, 'TERMINATED'
        )
        
        return tiempo_fin
    
    @staticmethod
    def fcfs_scheduling(processes):
        """
        FCFS: Primer Llegado, Primer Servido
        
        Regla simple: Los procesos se ejecutan en orden de llegada.
        No hay interrupciones hasta que el proceso termine.
        
        Args:
            processes: Lista de objetos PCB (Process Control Block)
        Returns:
            tuple: (historial_ejecución, tiempo_total)
        """
        tiempo_actual = 0
        historial = []
        
        # PASO 1: Ordenar procesos por tiempo de llegada
        procesos_ordenados = sorted(processes, key=lambda p: p.arrival_time)
        
        # PASO 2: Ejecutar cada proceso completamente
        for proceso in procesos_ordenados:
            # Esperar hasta que el proceso llegue (si es necesario)
            if tiempo_actual < proceso.arrival_time:
                tiempo_actual = proceso.arrival_time
            
            # Ejecutar proceso completamente usando función auxiliar
            tiempo_actual = SchedulingAlgorithms._ejecutar_proceso_completo(
                proceso, tiempo_actual, historial
            )
            
        return historial, tiempo_actual
    
    @staticmethod
    def sjf_scheduling(processes):
        """
        SJF: Trabajo Más Corto Primero
        
        Regla: Ejecutar primero el proceso con menor tiempo de ráfaga.
        Sistema batch: conoce todos los procesos desde el inicio.
        
        Args:
            processes: Lista de objetos PCB
        Returns:
            tuple: (historial_ejecución, tiempo_total)
        """
        tiempo_actual = 0
        historial = []
        
        # PASO 1: Mostrar información del sistema batch
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, 'SJF: Cargando todos los procesos...', 'SISTEMA', 'INFO'
        )
        
        info_procesos = [f"P{p.pid}(llegada:{p.arrival_time}, ráfaga:{p.burst_time})" for p in processes]
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, f'Procesos: {", ".join(info_procesos)}', 'SISTEMA', 'INFO'
        )
        
        # PASO 2: Ordenar SOLO por tiempo de ráfaga (burst_time)
        procesos_ordenados = sorted(processes, key=lambda p: p.burst_time)
        
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, 'Ordenando por tiempo de ráfaga...', 'SISTEMA', 'INFO'
        )
        
        orden_rafaga = [f"P{p.pid}(ráfaga:{p.burst_time})" for p in procesos_ordenados]
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, f'Orden final: {" → ".join(orden_rafaga)}', 'SISTEMA', 'INFO'
        )
        
        # PASO 3: Ejecutar en orden de ráfaga
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, 'Iniciando ejecución SJF...', 'SISTEMA', 'INFO'
        )
        
        for posicion, proceso in enumerate(procesos_ordenados, 1):
            SchedulingAlgorithms._agregar_evento(
                historial, tiempo_actual, 
                f'Seleccionado: P{proceso.pid} (ráfaga: {proceso.burst_time}) - Posición {posicion}',
                proceso.pid, 'SELECTED'
            )
            
            # Esperar hasta que llegue el proceso (si es necesario)
            if tiempo_actual < proceso.arrival_time:
                SchedulingAlgorithms._agregar_evento(
                    historial, tiempo_actual, 
                    f'Esperando llegada de P{proceso.pid} (t={proceso.arrival_time})',
                    proceso.pid, 'WAITING'
                )
                tiempo_actual = proceso.arrival_time
            
            # Ejecutar proceso usando función auxiliar
            tiempo_actual = SchedulingAlgorithms._ejecutar_proceso_completo(
                proceso, tiempo_actual, historial
            )
            
        # Resumen final
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, 'Resumen SJF completado', 'SISTEMA', 'INFO'
        )
        
        orden_final = [f"P{p.pid}(ráfaga:{p.burst_time})" for p in procesos_ordenados]
        SchedulingAlgorithms._agregar_evento(
            historial, tiempo_actual, f'Orden ejecutado: {" → ".join(orden_final)}', 'SISTEMA', 'INFO'
        )
            
        return historial, tiempo_actual
    
    @staticmethod
    def round_robin_scheduling(processes, quantum=2):
        """
        Round Robin: Planificación Circular con Quantum
        
        Regla: Cada proceso ejecuta máximo 'quantum' unidades de tiempo,
        luego pasa el turno al siguiente proceso en la cola.
        
        Args:
            processes: Lista de objetos PCB
            quantum: Tiempo máximo que puede ejecutar cada proceso por turno
        Returns:
            tuple: (historial_ejecución, tiempo_total)
        """
        tiempo_actual = 0
        historial = []
        cola_listos = []  # Procesos esperando su turno
        
        # Configuración 
        procesos_pendientes = [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
        tiempo_restante = {p.pid: p.burst_time for p in processes}
        objetos_proceso = {p.pid: p for p in processes}
        
        def agregar_procesos_llegados():
            """Función auxiliar: agrega procesos que han llegado a la cola"""
            llegaron = [p for p in procesos_pendientes if p[1] <= tiempo_actual]
            for proceso in llegaron:
                cola_listos.append(proceso)
                procesos_pendientes.remove(proceso)
                
                obj_proceso = objetos_proceso[proceso[0]]
                obj_proceso.state = "READY"
                SchedulingAlgorithms._agregar_evento(
                    historial, tiempo_actual, 
                    f'Proceso {proceso[0]} → LISTO (llegó a la cola)', 
                    proceso[0], 'READY'
                )
        
        # Bucle principal: mientras haya procesos pendientes o en cola
        while procesos_pendientes or cola_listos:
            
            # PASO 1: Agregar procesos que han llegado
            agregar_procesos_llegados()
                
            # PASO 2: Si no hay procesos listos, avanzar tiempo
            if not cola_listos:
                tiempo_actual += 1
                continue
                
            # PASO 3: Tomar el primer proceso de la cola (FIFO)
            proceso_actual = cola_listos.pop(0)
            pid, arrival_time, burst_time, priority = proceso_actual
            obj_proceso = objetos_proceso[pid]
            
            # PASO 4: Calcular tiempo de ejecución para este turno
            tiempo_a_ejecutar = min(quantum, tiempo_restante[pid])
            
            # PASO 5: Ejecutar el proceso
            obj_proceso.state = "EXECUTING"
            obj_proceso.cpu["program_counter"] += tiempo_a_ejecutar
            obj_proceso.cpu["instruction_pointer"] = tiempo_actual
            
            SchedulingAlgorithms._agregar_evento(
                historial, tiempo_actual,
                f'Proceso {pid} → EJECUTANDO por {tiempo_a_ejecutar} unidades (quantum={quantum})',
                pid, 'EXECUTING'
            )
            
            # Avanzar tiempo y reducir tiempo restante
            tiempo_actual += tiempo_a_ejecutar
            tiempo_restante[pid] -= tiempo_a_ejecutar
            
            # PASO 6: Agregar procesos que llegaron DURANTE la ejecución
            agregar_procesos_llegados()
            
            # PASO 7: Decidir qué hacer con el proceso actual
            if tiempo_restante[pid] > 0:
                # NO terminó: vuelve a la cola
                obj_proceso.state = "WAITING"
                SchedulingAlgorithms._agregar_evento(
                    historial, tiempo_actual,
                    f'Proceso {pid} → ESPERANDO (le quedan {tiempo_restante[pid]} unidades)',
                    pid, 'WAITING'
                )
                cola_listos.append(proceso_actual)  # Al final de la cola
            else:
                # SÍ terminó: marcar como terminado
                obj_proceso.state = "TERMINATED"
                obj_proceso.completion_time = tiempo_actual
                obj_proceso.turnaround_time = tiempo_actual - arrival_time
                obj_proceso.waiting_time = obj_proceso.turnaround_time - burst_time
                
                SchedulingAlgorithms._agregar_evento(
                    historial, tiempo_actual, f'Proceso {pid} → TERMINADO', pid, 'TERMINATED'
                )
                
        return historial, tiempo_actual