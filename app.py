
from flask import Flask, render_template, request, jsonify
from schedulers import ProcessScheduler
from utils import generate_execution_timeline

app = Flask(__name__)

# Instancia global del scheduler
scheduler = ProcessScheduler()

@app.route('/')
def index():
    """Página principal de la aplicación"""
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    """Endpoint para ejecutar la simulación de planificación de procesos"""
    try:
        data = request.get_json()
        processes = data['processes']
        algorithm = data['algorithm']
        quantum = data.get('quantum', 2)
        
        # Limpiar scheduler anterior
        scheduler.clear_processes()
        
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
        else:
            return jsonify({'error': f'Algoritmo no soportado: {algorithm}'}), 400
        
        # Obtener estadísticas y datos
        process_stats = scheduler.get_process_stats()
        pcb_data = scheduler.get_pcb_data()
        
        # Crear timeline detallado para animación
        timeline_data = generate_execution_timeline(
            scheduler.processes, 
            algorithm, 
            quantum if algorithm == 'rr' else None
        )
        
        return jsonify({
            'execution_log': execution_log,
            'process_stats': process_stats,
            'timeline_data': timeline_data,
            'pcb_data': pcb_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en la simulación: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)