from flask import Flask, request, jsonify
from datetime import datetime
from collections import deque

app = Flask(__name__)

# Almacenar últimos 50 registros en memoria
registros = deque(maxlen=50)

@app.route('/recibir', methods=['POST'])
def recibir_datos():
    """
    Endpoint para recibir datos por POST
    Acepta JSON en el body de la petición
    """
    # Obtener datos del body (JSON)
    datos = request.get_json() or {}
    
    # Registrar el timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear registro
    registro = {
        'timestamp': timestamp,
        'datos': datos,
        'ip': request.remote_addr
    }
    
    # Guardar en memoria
    registros.append(registro)
    
    # Imprimir en consola
    print(f"\n[{timestamp}] Datos recibidos:")
    print(f"IP: {request.remote_addr}")
    for key, value in datos.items():
        print(f"  {key}: {value}")
    
    # Responder confirmación
    return jsonify({
        'status': 'ok',
        'mensaje': 'Datos recibidos correctamente',
        'datos_recibidos': datos,
        'timestamp': timestamp
    }), 200

@app.route('/ver-datos', methods=['GET'])
def ver_datos():
    """
    Endpoint para ver todos los datos recibidos
    Acceder: http://localhost:5000/ver-datos
    """
    return jsonify({
        'total_registros': len(registros),
        'registros': list(registros)
    }), 200

@app.route('/', methods=['GET'])
def inicio():
    """
    Página de inicio con información
    """
    return f"""
    <html>
    <head>
        <title>API Monitor</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f0f0f0; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
            .count {{ font-size: 24px; color: #4CAF50; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 API Monitor - Activa</h1>
            <div class="info">
                <p><strong>Registros almacenados:</strong> <span class="count">{len(registros)}</span></p>
            </div>
            
            <h2>📡 Endpoints disponibles:</h2>
            
            <h3>1. Recibir datos (GET):</h3>
            <p><code>http://localhost:5000/recibir?param1=valor1&param2=valor2</code></p>
            <p>Ejemplo: <code>http://localhost:5000/recibir?temperatura=25&humedad=60</code></p>
            
            <h3>2. Ver todos los datos recibidos:</h3>
            <p><code>http://localhost:5000/ver-datos</code></p>
            <p><a href="/ver-datos">👉 Ver datos ahora</a></p>
            
            <h2>💡 Uso:</h2>
            <ul>
                <li>Tu programa debe hacer peticiones GET a <code>/recibir</code></li>
                <li>Los datos se mostrarán en la consola en tiempo real</li>
                <li>Se almacenan los últimos 50 registros</li>
                <li>Accede a <code>/ver-datos</code> para ver el historial completo</li>
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 API Monitor iniciada")
    print("=" * 50)
    print("\n📍 Accede a: http://localhost:5000")
    print("📡 Endpoint de recepción: http://localhost:5000/recibir")
    print("👀 Ver datos: http://localhost:5000/ver-datos")
    print("\n⏳ Esperando datos...\n")
    
    # Iniciar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)