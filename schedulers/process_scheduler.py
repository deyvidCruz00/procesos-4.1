"""
Módulo ProcessScheduler
Contiene la clase principal para manejar la planificación de procesos.
"""

from models.pcb import PCB
from schedulers.algorithms import SchedulingAlgorithms

class ProcessScheduler:
    """Simulador de planificación de procesos"""
    
    def __init__(self):
        self.processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.execution_log = []
        
    def add_process(self, pid, arrival_time, burst_time, priority=0):
        """
        Agregar un proceso al sistema
        
        Args:
            pid: ID del proceso
            arrival_time: Tiempo de llegada
            burst_time: Tiempo de ráfaga
            priority: Prioridad del proceso (opcional)
        """
        process = PCB(pid, arrival_time, burst_time, priority)
        self.processes.append(process)
        
    def clear_processes(self):
        """Limpiar todos los procesos del scheduler"""
        self.processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.execution_log = []
        
    def fcfs_scheduling(self):
        """
        Ejecutar algoritmo First Come First Served
        
        Returns:
            list: Log de ejecución del algoritmo
        """
        self.current_time = 0
        self.execution_log = []
        
        execution_log, self.current_time = SchedulingAlgorithms.fcfs_scheduling(self.processes)
        self.execution_log = execution_log
        
        return self.execution_log
    
    def sjf_scheduling(self):
        """
        Ejecutar algoritmo Shortest Job First
        
        Returns:
            list: Log de ejecución del algoritmo
        """
        self.current_time = 0
        self.execution_log = []
        
        execution_log, self.current_time = SchedulingAlgorithms.sjf_scheduling(self.processes)
        self.execution_log = execution_log
        
        return self.execution_log
    
    def round_robin_scheduling(self, quantum=2):
        """
        Ejecutar algoritmo Round Robin
        
        Args:
            quantum: Quantum de tiempo para el algoritmo
            
        Returns:
            list: Log de ejecución del algoritmo
        """
        self.current_time = 0
        self.execution_log = []
        
        execution_log, self.current_time = SchedulingAlgorithms.round_robin_scheduling(self.processes, quantum)
        self.execution_log = execution_log
        
        return self.execution_log
    
    def get_process_stats(self):
        """
        Obtener estadísticas de todos los procesos
        
        Returns:
            list: Lista de estadísticas de procesos
        """
        process_stats = []
        
        for process in self.processes:
            process_stats.append({
                'pid': process.pid,
                'arrival_time': process.arrival_time,
                'burst_time': process.burst_time,
                'completion_time': getattr(process, 'completion_time', 0),
                'turnaround_time': getattr(process, 'turnaround_time', 0),
                'waiting_time': getattr(process, 'waiting_time', 0),
                'state': process.state,
                'start_time': getattr(process, 'start_time', 0)
            })
            
        return process_stats
    
    def get_pcb_data(self):
        """
        Obtener información completa del PCB de todos los procesos
        
        Returns:
            list: Lista de datos completos del PCB
        """
        pcb_data = []
        
        for process in self.processes:
            pcb_data.append(process.to_dict())
            
        return pcb_data
    
    def get_process_count(self):
        """Obtener el número de procesos en el scheduler"""
        return len(self.processes)
    
    def get_process_by_pid(self, pid):
        """
        Obtener un proceso por su PID
        
        Args:
            pid: ID del proceso a buscar
            
        Returns:
            PCB: Proceso encontrado o None si no existe
        """
        for process in self.processes:
            if process.pid == pid:
                return process
        return None
    
    def __repr__(self):
        return f"ProcessScheduler(processes={len(self.processes)}, current_time={self.current_time})"