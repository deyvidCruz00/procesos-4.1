"""
Módulo Timeline
Contiene funciones para generar timeline de ejecución para la animación.
"""

def generate_execution_timeline(processes, algorithm, quantum=None):
    """
    Genera timeline detallado de ejecución para animación
    
    Args:
        processes: Lista de procesos PCB
        algorithm: Algoritmo utilizado ('fcfs', 'sjf', 'rr')
        quantum: Quantum para Round Robin (opcional)
        
    Returns:
        list: Timeline de datos para animación
    """
    timeline_data = []
    
    if algorithm == 'fcfs':
        timeline_data = _generate_fcfs_timeline(processes)
    elif algorithm == 'sjf':
        timeline_data = _generate_sjf_timeline(processes)
    elif algorithm == 'rr':
        timeline_data = _generate_rr_timeline(processes, quantum)
    
    return timeline_data

def _generate_fcfs_timeline(processes):
    """Generar timeline para FCFS"""
    timeline_data = []
    current_time = 0
    sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
    
    for process in sorted_processes:
        start_time = max(current_time, process.arrival_time)
        end_time = start_time + process.burst_time
        
        for t in range(start_time, end_time):
            timeline_data.append({
                'time': t,
                'process': process.pid,
                'state': 'EXECUTING'
            })
        
        current_time = end_time
    
    return timeline_data

def _generate_sjf_timeline(processes):
    """Generar timeline para SJF"""
    timeline_data = []
    current_time = 0
    
    # Ordenar todos los procesos ÚNICAMENTE por burst_time (sin considerar arrival_time)
    processes_sorted_by_burst = sorted(
        [(p.pid, p.arrival_time, p.burst_time) for p in processes], 
        key=lambda p: p[2]  # Solo burst_time
    )
    
    # Ejecutar en el orden de ráfaga establecido
    for pid, arrival_time, burst_time in processes_sorted_by_burst:
        # Esperar hasta que el proceso llegue si es necesario
        start_time = max(current_time, arrival_time)
        end_time = start_time + burst_time
        
        # Generar timeline para este proceso
        for t in range(start_time, end_time):
            timeline_data.append({
                'time': t,
                'process': pid,
                'state': 'EXECUTING'
            })
        
        current_time = end_time
    
    return timeline_data

def _generate_rr_timeline(processes, quantum):
    """Generar timeline para Round Robin"""
    timeline_data = []
    current_time = 0
    ready_queue = []
    remaining_processes = [(p.pid, p.arrival_time, p.burst_time) for p in processes]
    process_remaining_time = {p.pid: p.burst_time for p in processes}
    
    while remaining_processes or ready_queue:
        # Agregar procesos que han llegado
        arrived_processes = [p for p in remaining_processes if p[1] <= current_time]
        for p in arrived_processes:
            ready_queue.append(p)
            remaining_processes.remove(p)
            
        if not ready_queue:
            current_time += 1
            continue
            
        current_process = ready_queue.pop(0)
        pid, arrival_time, burst_time = current_process
        
        execution_time = min(quantum, process_remaining_time[pid])
        
        # Generar timeline para este quantum
        for t in range(current_time, current_time + execution_time):
            timeline_data.append({
                'time': t,
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
        
        # Si el proceso no ha terminado, volver a la cola
        if process_remaining_time[pid] > 0:
            ready_queue.append((pid, arrival_time, burst_time))
    
    return timeline_data