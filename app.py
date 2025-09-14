from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

class PCB:
    """Process Control Block - Estructura para representar cada proceso"""
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.state = "NEW"  # NEW, READY, RUNNING, TERMINATED
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
            if self.current_time < process.arrival_time:
                self.current_time = process.arrival_time
                
            process.start_time = self.current_time
            process.state = "RUNNING"
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {process.pid} inicia ejecución',
                'process': process.pid,
                'state': 'RUNNING'
            })
            
            self.current_time += process.burst_time
            process.completion_time = self.current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            process.state = "TERMINATED"
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {process.pid} termina',
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
                
            next_process.start_time = self.current_time
            next_process.state = "RUNNING"
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {next_process.pid} inicia ejecución',
                'process': next_process.pid,
                'state': 'RUNNING'
            })
            
            self.current_time += next_process.burst_time
            next_process.completion_time = self.current_time
            next_process.turnaround_time = next_process.completion_time - next_process.arrival_time
            next_process.waiting_time = next_process.turnaround_time - next_process.burst_time
            next_process.state = "TERMINATED"
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {next_process.pid} termina',
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
        
        while remaining_processes or ready_queue:
            # Agregar procesos que han llegado a la cola de listos
            arrived_processes = [p for p in remaining_processes if p[1] <= self.current_time]
            for p in arrived_processes:
                ready_queue.append(p)
                remaining_processes.remove(p)
                
            if not ready_queue:
                self.current_time += 1
                continue
                
            current_process = ready_queue.pop(0)
            pid, arrival_time, burst_time, priority = current_process
            
            execution_time = min(quantum, process_remaining_time[pid])
            
            self.execution_log.append({
                'time': self.current_time,
                'action': f'Proceso {pid} ejecuta por {execution_time} unidades',
                'process': pid,
                'state': 'RUNNING'
            })
            
            self.current_time += execution_time
            process_remaining_time[pid] -= execution_time
            
            # Agregar procesos que llegaron durante la ejecución
            arrived_during_execution = [p for p in remaining_processes if p[1] <= self.current_time]
            for p in arrived_during_execution:
                ready_queue.append(p)
                remaining_processes.remove(p)
            
            if process_remaining_time[pid] > 0:
                ready_queue.append(current_process)
            else:
                self.execution_log.append({
                    'time': self.current_time,
                    'action': f'Proceso {pid} termina',
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
    
    # Crear timeline detallado para animación
    if algorithm == 'fcfs':
        current_time = 0
        sorted_processes = sorted(scheduler.processes, key=lambda p: p.arrival_time)
        
        for process in sorted_processes:
            start_time = max(current_time, process.arrival_time)
            end_time = start_time + process.burst_time
            
            for t in range(start_time, end_time):
                timeline_data.append({
                    'time': t,
                    'process': process.pid,
                    'state': 'RUNNING'
                })
            
            current_time = end_time
    
    return jsonify({
        'execution_log': execution_log,
        'process_stats': process_stats,
        'timeline_data': timeline_data
    })

if __name__ == '__main__':
    app.run(debug=True)