from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

class PCB:
    """Process Control Block - Estructura para representar cada proceso"""
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        # Información básica del proceso
        self.pid = pid  # PID: Unique Process Identifier
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        
        # PCB Components
        self.state = "CREATED"  # State: Current execution state (CREATED, READY, EXECUTING, WAITING, TERMINATED)
        self.cpu = {  # CPU: CPU context (register values, program counter)
            "program_counter": 0,
            "registers": {
                "AX": 0, "BX": 0, "CX": 0, "DX": 0,
                "SP": 1024, "BP": 1024
            },
            "instruction_pointer": 0
        }
        self.memo = {  # Memo: Memory management information
            "base_register": pid * 1000,  # Base address for process
            "limit_register": 1000,       # Memory limit
            "page_table": f"PT_{pid}",    # Page table reference
            "allocated_memory": burst_time * 100  # Memory allocated based on burst time
        }
        self.io = {  # IO: I/O status and devices allocated
            "status": "NONE",  # NONE, PENDING, BLOCKED
            "allocated_devices": [],
            "pending_requests": [],
            "io_operations": 0
        }
        self.files = {  # Files: List of open file descriptors
            "open_files": [],
            "file_descriptors": [],
            "current_directory": f"/proc/{pid}"
        }
        self.security = {  # Security: User credentials, privileges, and access rights
            "user_id": 1000 + int(pid) if str(pid).isdigit() else 1000,
            "group_id": 100,
            "privileges": ["READ", "WRITE"],
            "access_rights": "USER",
            "security_level": "NORMAL"
        }
        
        # Timing information
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

class ProcessScheduler:
    """Simulador de planificación de procesos"""
    def __init__(self):
        self.processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.execution_log = []
        
    def add_process(self, pid, arrival_time, burst_time, priority=0):
        """Agregar un proceso al sistema"""
        process = PCB(pid, arrival_time, burst_time, priority)
        self.processes.append(process)
        
    def fcfs_scheduling(self):
        """First Come First Served"""
        self.current_time = 0
        self.execution_log = []
        
        # Ordenar por tiempo de llegada
        processes = sorted(self.processes, key=lambda p: p.arrival_time)
        
        for process in processes:
            # Cambiar estado a READY cuando el proceso llega
            if self.current_time < process.arrival_time:
                self.current_time = process.arrival_time
            
            process.state = "READY"
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {process.pid} está listo (READY)',
                'process': process.pid,
                'state': 'READY'
            })
                
            process.start_time = self.current_time
            process.state = "EXECUTING"
            
            # Actualizar contexto de CPU
            process.cpu["program_counter"] = 0
            process.cpu["instruction_pointer"] = process.start_time
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {process.pid} inicia ejecución (EXECUTING)',
                'process': process.pid,
                'state': 'EXECUTING'
            })
            
            self.current_time += process.burst_time
            process.completion_time = self.current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            process.state = "TERMINATED"
            
            # Actualizar contexto final
            process.cpu["program_counter"] = process.burst_time
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {process.pid} termina (TERMINATED)',
                'process': process.pid,
                'state': 'TERMINATED'
            })
            
        return self.execution_log
    
    def sjf_scheduling(self):
        """Shortest Job First"""
        self.current_time = 0
        self.execution_log = []
        completed_processes = []
        remaining_processes = self.processes.copy()
        
        while remaining_processes:
            # Procesos que han llegado
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            
            if not available_processes:
                self.current_time += 1
                continue
                
            # Seleccionar el de menor duración
            next_process = min(available_processes, key=lambda p: p.burst_time)
            remaining_processes.remove(next_process)
            
            if self.current_time < next_process.arrival_time:
                self.current_time = next_process.arrival_time
            
            # Cambiar a READY
            next_process.state = "READY"
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {next_process.pid} está listo (READY)',
                'process': next_process.pid,
                'state': 'READY'
            })
                
            next_process.start_time = self.current_time
            next_process.state = "EXECUTING"
            
            # Actualizar contexto de CPU
            next_process.cpu["program_counter"] = 0
            next_process.cpu["instruction_pointer"] = next_process.start_time
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {next_process.pid} inicia ejecución (EXECUTING)',
                'process': next_process.pid,
                'state': 'EXECUTING'
            })
            
            self.current_time += next_process.burst_time
            next_process.completion_time = self.current_time
            next_process.turnaround_time = next_process.completion_time - next_process.arrival_time
            next_process.waiting_time = next_process.turnaround_time - next_process.burst_time
            next_process.state = "TERMINATED"
            
            # Actualizar contexto final
            next_process.cpu["program_counter"] = next_process.burst_time
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {next_process.pid} termina (TERMINATED)',
                'process': next_process.pid,
                'state': 'TERMINATED'
            })
            
        return self.execution_log
    
    def round_robin_scheduling(self, quantum=2):
        """Round Robin con quantum de tiempo"""
        self.current_time = 0
        self.execution_log = []
        ready_queue = []
        remaining_processes = [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        process_remaining_time = {p.pid: p.burst_time for p in self.processes}
        process_objects = {p.pid: p for p in self.processes}
        
        while remaining_processes or ready_queue:
            # Agregar procesos que han llegado a la cola de listos
            arrived_processes = [p for p in remaining_processes if p[1] <= self.current_time]
            for p in arrived_processes:
                ready_queue.append(p)
                remaining_processes.remove(p)
                # Cambiar estado a READY
                process_obj = process_objects[p[0]]
                process_obj.state = "READY"
                
                self.execution_log.append({
                    'time': self.current_time,
                    'action': f'Proceso {p[0]} está listo (READY)',
                    'process': p[0],
                    'state': 'READY'
                })
                
            if not ready_queue:
                self.current_time += 1
                continue
                
            current_process = ready_queue.pop(0)
            pid, arrival_time, burst_time, priority = current_process
            process_obj = process_objects[pid]
            
            execution_time = min(quantum, process_remaining_time[pid])
            
            # Cambiar a EXECUTING
            process_obj.state = "EXECUTING"
            process_obj.cpu["program_counter"] += execution_time
            process_obj.cpu["instruction_pointer"] = self.current_time
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {pid} ejecuta por {execution_time} unidades (EXECUTING)',
                'process': pid,
                'state': 'EXECUTING'
            })
            
            self.current_time += execution_time
            process_remaining_time[pid] -= execution_time
            
            # Agregar procesos que llegaron durante la ejecución
            arrived_during_execution = [p for p in remaining_processes if p[1] <= self.current_time]
            for p in arrived_during_execution:
                ready_queue.append(p)
                remaining_processes.remove(p)
                # Cambiar estado a READY
                process_obj_new = process_objects[p[0]]
                process_obj_new.state = "READY"
                
                self.execution_log.append({
                    'time': self.current_time,
                    'action': f'Proceso {p[0]} está listo (READY)',
                    'process': p[0],
                    'state': 'READY'
                })
            
            if process_remaining_time[pid] > 0:
                # Proceso no terminado - va a WAITING (simulando espera por quantum)
                process_obj.state = "WAITING"
                self.execution_log.append({
                    'time': self.current_time,
                    'action': f'Proceso {pid} espera su turno (WAITING)',
                    'process': pid,
                    'state': 'WAITING'
                })
                ready_queue.append(current_process)
            else:
                # Proceso terminado
                process_obj.state = "TERMINATED"
                process_obj.completion_time = self.current_time
                process_obj.turnaround_time = self.current_time - arrival_time
                process_obj.waiting_time = process_obj.turnaround_time - burst_time
                
                self.execution_log.append({
                    'time': self.current_time,
                    'action': f'Proceso {pid} termina (TERMINATED)',
                    'process': pid,
                    'state': 'TERMINATED'
                })
                
        return self.execution_log

scheduler = ProcessScheduler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    processes = data['processes']
    algorithm = data['algorithm']
    quantum = data.get('quantum', 2)
    
    # Limpiar scheduler anterior
    scheduler.processes = []
    
    # Agregar procesos
    for process in processes:
        scheduler.add_process(
            process['pid'],
            process['arrival_time'],
            process['burst_time'],
            process.get('priority', 0)
        )
    
    # Ejecutar algoritmo seleccionado
    if algorithm == 'fcfs':
        execution_log = scheduler.fcfs_scheduling()
    elif algorithm == 'sjf':
        execution_log = scheduler.sjf_scheduling()
    elif algorithm == 'rr':
        execution_log = scheduler.round_robin_scheduling(quantum)
    
    # Calcular estadísticas
    process_stats = []
    timeline_data = []
    pcb_data = []
    
    for process in scheduler.processes:
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
        
        # Información completa del PCB
        pcb_data.append({
            'pid': process.pid,
            'state': process.state,
            'cpu': process.cpu,
            'memo': process.memo,
            'io': process.io,
            'files': process.files,
            'security': process.security,
            'timing': {
                'arrival_time': process.arrival_time,
                'burst_time': process.burst_time,
                'start_time': getattr(process, 'start_time', None),
                'completion_time': getattr(process, 'completion_time', None),
                'waiting_time': process.waiting_time,
                'turnaround_time': process.turnaround_time
            }
        })
    
    # Crear timeline detallado para animación
    timeline_data = generate_execution_timeline(scheduler.processes, algorithm, quantum if algorithm == 'rr' else None)
    
    return jsonify({
        'execution_log': execution_log,
        'process_stats': process_stats,
        'timeline_data': timeline_data,
        'pcb_data': pcb_data
    })

def generate_execution_timeline(processes, algorithm, quantum=None):
    """Genera timeline detallado de ejecución para animación"""
    timeline_data = []
    
    if algorithm == 'fcfs':
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
            
    elif algorithm == 'sjf':
        current_time = 0
        remaining_processes = [(p.pid, p.arrival_time, p.burst_time) for p in processes]
        completed = []
        
        while remaining_processes:
            # Procesos disponibles en el tiempo actual
            available = [p for p in remaining_processes if p[1] <= current_time]
            
            if not available:
                current_time += 1
                continue
            
            # Seleccionar proceso con menor burst time
            next_process = min(available, key=lambda p: p[2])
            remaining_processes.remove(next_process)
            
            pid, arrival_time, burst_time = next_process
            start_time = current_time
            end_time = start_time + burst_time
            
            for t in range(start_time, end_time):
                timeline_data.append({
                    'time': t,
                    'process': pid,
                    'state': 'EXECUTING'
                })
            
            current_time = end_time
            
    elif algorithm == 'rr':
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

if __name__ == '__main__':
    app.run(debug=True)