"""
Módulo PCB (Process Control Block)
Contiene la definición de la estructura de datos del PCB para representar procesos.
"""

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
    
    def update_cpu_context(self, program_counter=None, instruction_pointer=None):
        """Actualizar el contexto de CPU del proceso"""
        if program_counter is not None:
            self.cpu["program_counter"] = program_counter
        if instruction_pointer is not None:
            self.cpu["instruction_pointer"] = instruction_pointer
    
    def calculate_times(self):
        """Calcular tiempos de turnaround y espera"""
        if self.completion_time is not None:
            self.turnaround_time = self.completion_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
    
    def to_dict(self):
        """Convertir PCB a diccionario para serialización JSON"""
        return {
            'pid': self.pid,
            'state': self.state,
            'cpu': self.cpu,
            'memo': self.memo,
            'io': self.io,
            'files': self.files,
            'security': self.security,
            'timing': {
                'arrival_time': self.arrival_time,
                'burst_time': self.burst_time,
                'start_time': self.start_time,
                'completion_time': self.completion_time,
                'waiting_time': self.waiting_time,
                'turnaround_time': self.turnaround_time
            }
        }
    
    def __repr__(self):
        return f"PCB(pid={self.pid}, state={self.state}, arrival={self.arrival_time}, burst={self.burst_time})"