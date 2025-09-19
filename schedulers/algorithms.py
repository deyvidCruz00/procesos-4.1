"""
Módulo de Algoritmos de Planificación
Contiene la implementación de los diferentes algoritmos de planificación de procesos.
"""

class SchedulingAlgorithms:
    """Clase que contiene los algoritmos de planificación de procesos"""
    
    @staticmethod
    def fcfs_scheduling(processes):
        """
        First Come First Served
        Args:
            processes: Lista de procesos PCB
        Returns:
            tuple: (execution_log, current_time)
        """
        current_time = 0
        execution_log = []
        
        # Ordenar por tiempo de llegada
        sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
        
        for process in sorted_processes:
            # Cambiar estado a READY cuando el proceso llega
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            process.state = "READY"
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} está listo (READY)',
                'process': process.pid,
                'state': 'READY'
            })
                
            process.start_time = current_time
            process.state = "EXECUTING"
            
            # Actualizar contexto de CPU
            process.update_cpu_context(program_counter=0, instruction_pointer=process.start_time)
            
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} inicia ejecución (EXECUTING)',
                'process': process.pid,
                'state': 'EXECUTING'
            })
            
            current_time += process.burst_time
            process.completion_time = current_time
            process.calculate_times()
            process.state = "TERMINATED"
            
            # Actualizar contexto final
            process.update_cpu_context(program_counter=process.burst_time)
            
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} termina (TERMINATED)',
                'process': process.pid,
                'state': 'TERMINATED'
            })
            
        return execution_log, current_time
    
    @staticmethod
    def sjf_scheduling(processes):
        """
        Shortest Job First - Carga todos los procesos por lote y ordena por ráfaga
        Args:
            processes: Lista de procesos PCB
        Returns:
            tuple: (execution_log, current_time)
        """
        current_time = 0
        execution_log = []
        
        # PASO 1: Cargar todos los procesos por lote para conocer sus ráfagas
        execution_log.append({
            'time': current_time,
            'action': '=== SJF: CARGA POR LOTES ===',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        # Mostrar información de todos los procesos cargados
        process_info = []
        for process in processes:
            process_info.append(f"P{process.pid} (Llegada: {process.arrival_time}, Ráfaga: {process.burst_time})")
        
        execution_log.append({
            'time': current_time,
            'action': f'Procesos cargados: {", ".join(process_info)}',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        # PASO 2: ORDENAR TODOS LOS PROCESOS ÚNICAMENTE POR BURST_TIME (RÁFAGA)
        processes_sorted_by_burst = sorted(processes, key=lambda p: p.burst_time)
        
        execution_log.append({
            'time': current_time,
            'action': '=== ORDENAMIENTO POR RÁFAGA (BURST TIME) ===',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        burst_order = []
        for p in processes_sorted_by_burst:
            burst_order.append(f"P{p.pid} (ráfaga: {p.burst_time})")
        
        execution_log.append({
            'time': current_time,
            'action': f'Orden final por ráfaga: {" → ".join(burst_order)}',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        # PASO 3: Ejecutar procesos EN EXACTAMENTE EL ORDEN DE RÁFAGA
        execution_log.append({
            'time': current_time,
            'action': '=== INICIO DE EJECUCIÓN SJF ===',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        # Ejecutar cada proceso en el orden establecido
        for i, process in enumerate(processes_sorted_by_burst):
            execution_log.append({
                'time': current_time,
                'action': f'SELECCIONADO: P{process.pid} (ráfaga: {process.burst_time}) - Posición {i+1} en orden de ráfaga',
                'process': process.pid,
                'state': 'SELECTED'
            })
            
            # Esperar hasta que el proceso llegue si es necesario
            if current_time < process.arrival_time:
                execution_log.append({
                    'time': current_time,
                    'action': f'Esperando llegada de P{process.pid} (llegará en t={process.arrival_time})',
                    'process': process.pid,
                    'state': 'WAITING'
                })
                current_time = process.arrival_time
            
            # Cambiar a READY
            process.state = "READY"
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} está listo (READY)',
                'process': process.pid,
                'state': 'READY'
            })
                
            # Iniciar ejecución
            process.start_time = current_time
            process.state = "EXECUTING"
            
            # Actualizar contexto de CPU
            process.update_cpu_context(program_counter=0, instruction_pointer=process.start_time)
            
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} inicia ejecución (EXECUTING) - Ráfaga: {process.burst_time}',
                'process': process.pid,
                'state': 'EXECUTING'
            })
            
            # Ejecutar por completo (no preemptivo)
            current_time += process.burst_time
            process.completion_time = current_time
            process.calculate_times()
            process.state = "TERMINATED"
            
            # Actualizar contexto final
            process.update_cpu_context(program_counter=process.burst_time)
            
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {process.pid} termina (TERMINATED) - Tiempo total: {process.burst_time}',
                'process': process.pid,
                'state': 'TERMINATED'
            })
            
        # Mostrar resumen final
        execution_log.append({
            'time': current_time,
            'action': '=== RESUMEN DE EJECUCIÓN SJF ===',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
        
        execution_order = [f"P{p.pid} (ráfaga: {p.burst_time})" for p in processes_sorted_by_burst]
        execution_log.append({
            'time': current_time,
            'action': f'Orden de ejecución final: {" → ".join(execution_order)}',
            'process': 'SYSTEM',
            'state': 'INFO'
        })
            
        return execution_log, current_time
    
    @staticmethod
    def round_robin_scheduling(processes, quantum=2):
        """
        Round Robin con quantum de tiempo
        Args:
            processes: Lista de procesos PCB
            quantum: Quantum de tiempo para el algoritmo
        Returns:
            tuple: (execution_log, current_time)
        """
        current_time = 0
        execution_log = []
        ready_queue = []
        remaining_processes = [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
        process_remaining_time = {p.pid: p.burst_time for p in processes}
        process_objects = {p.pid: p for p in processes}
        
        while remaining_processes or ready_queue:
            # Agregar procesos que han llegado a la cola de listos
            arrived_processes = [p for p in remaining_processes if p[1] <= current_time]
            for p in arrived_processes:
                ready_queue.append(p)
                remaining_processes.remove(p)
                # Cambiar estado a READY
                process_obj = process_objects[p[0]]
                process_obj.state = "READY"
                
                execution_log.append({
                    'time': current_time,
                    'action': f'Proceso {p[0]} está listo (READY)',
                    'process': p[0],
                    'state': 'READY'
                })
                
            if not ready_queue:
                current_time += 1
                continue
                
            current_process = ready_queue.pop(0)
            pid, arrival_time, burst_time, priority = current_process
            process_obj = process_objects[pid]
            
            execution_time = min(quantum, process_remaining_time[pid])
            
            # Cambiar a EXECUTING
            process_obj.state = "EXECUTING"
            process_obj.cpu["program_counter"] += execution_time
            process_obj.cpu["instruction_pointer"] = current_time
            
            execution_log.append({
                'time': current_time,
                'action': f'Proceso {pid} ejecuta por {execution_time} unidades (EXECUTING)',
                'process': pid,
                'state': 'EXECUTING'
            })
            
            current_time += execution_time
            process_remaining_time[pid] -= execution_time
            
            # Agregar procesos que llegaron durante la ejecución
            arrived_during_execution = [p for p in remaining_processes if p[1] <= current_time]
            for p in arrived_during_execution:
                ready_queue.append(p)
                remaining_processes.remove(p)
                # Cambiar estado a READY
                process_obj_new = process_objects[p[0]]
                process_obj_new.state = "READY"
                
                execution_log.append({
                    'time': current_time,
                    'action': f'Proceso {p[0]} está listo (READY)',
                    'process': p[0],
                    'state': 'READY'
                })
            
            if process_remaining_time[pid] > 0:
                # Proceso no terminado - va a WAITING (simulando espera por quantum)
                process_obj.state = "WAITING"
                execution_log.append({
                    'time': current_time,
                    'action': f'Proceso {pid} espera su turno (WAITING)',
                    'process': pid,
                    'state': 'WAITING'
                })
                ready_queue.append(current_process)
            else:
                # Proceso terminado
                process_obj.state = "TERMINATED"
                process_obj.completion_time = current_time
                process_obj.turnaround_time = current_time - arrival_time
                process_obj.waiting_time = process_obj.turnaround_time - burst_time
                
                execution_log.append({
                    'time': current_time,
                    'action': f'Proceso {pid} termina (TERMINATED)',
                    'process': pid,
                    'state': 'TERMINATED'
                })
                
        return execution_log, current_time