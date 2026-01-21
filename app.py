"""
API del Chatbot - La Taza Loca
Con Red Neuronal para Clasificación de Intenciones
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import os
import random
from difflib import SequenceMatcher

# Importar el clasificador de intenciones
from modelo_intenciones import ClasificadorIntenciones

app = Flask(__name__)
CORS(app)

class ChatbotRestaurante:
    def __init__(self, archivo_menu='menu.json'):
        self.archivo_menu = archivo_menu
        self.menu = self.cargar_menu()
        
        # Cargar el modelo de red neuronal
        self.clasificador = None
        self.usar_neural = False
        self.cargar_modelo_neural()
        
    def cargar_modelo_neural(self):
        """Intenta cargar el modelo de red neuronal"""
        try:
            ruta_modelo = 'modelo_chatbot'
            if os.path.exists(ruta_modelo):
                self.clasificador = ClasificadorIntenciones()
                self.clasificador.cargar_modelo(ruta_modelo)
                self.usar_neural = True
                print("✅ Modelo de red neuronal cargado correctamente")
            else:
                print("⚠️ Modelo no encontrado. Ejecuta 'python entrenar_modelo.py' primero.")
                print("   Usando modo de respaldo con patrones.")
        except Exception as e:
            print(f"⚠️ Error cargando modelo neural: {e}")
            print("   Usando modo de respaldo con patrones.")
            self.usar_neural = False
    
    def cargar_menu(self):
        """Carga el menú desde el archivo JSON"""
        if os.path.exists(self.archivo_menu):
            with open(self.archivo_menu, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza el texto del usuario"""
        texto = texto.lower()
        texto = re.sub(r'[¿?¡!.,;]', '', texto)
        return texto.strip()
    
    def similitud_texto(self, texto1, texto2):
        """Calcula la similitud entre dos textos"""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def buscar_platillo(self, nombre_platillo):
        """Busca un platillo en el menú por nombre"""
        nombre_limpio = self.limpiar_texto(nombre_platillo)
        mejores_coincidencias = []
        
        for platillo in self.menu:
            nombre_plat = self.limpiar_texto(platillo['nombre'])
            similitud = self.similitud_texto(nombre_limpio, nombre_plat)
            
            if similitud > 0.6:
                mejores_coincidencias.append((platillo, similitud))
        
        mejores_coincidencias.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in mejores_coincidencias[:3]]
    
    def formatear_platillo(self, platillo):
        """Formatea la información de un platillo"""
        disponible = "✓ Disponible" if platillo['disponible'] else "✗ No disponible"
        precio_final = platillo['precio']
        
        info = f"\n🍽️ **{platillo['nombre']}**\n"
        info += f"{platillo['descripcion']}\n"
        info += f"💰 Precio: ${precio_final} pesos\n"
        info += f"📦 Estado: {disponible}"
        
        if platillo.get('oferta'):
            info += f"\n🎉 ¡EN OFERTA! Descuento: {platillo['descuento']}%"
        
        if platillo.get('mas_vendido'):
            info += "\n⭐ ¡Más vendido!"
        
        if platillo.get('popular'):
            info += "\n🔥 ¡Popular!"
        
        return info
    
    def responder(self, mensaje_usuario):
        """Genera una respuesta al mensaje del usuario"""
        
        # Primero intentar buscar platillos específicos mencionados
        platillos_encontrados = self.buscar_platillo(mensaje_usuario)
        if platillos_encontrados and len(platillos_encontrados) > 0:
            # Si la similitud es muy alta, probablemente está preguntando por ese platillo
            nombre_limpio = self.limpiar_texto(mensaje_usuario)
            for platillo in self.menu:
                if self.similitud_texto(nombre_limpio, self.limpiar_texto(platillo['nombre'])) > 0.8:
                    return self.formatear_platillo(platillo)
        
        # Usar red neuronal si está disponible
        if self.usar_neural and self.clasificador:
            resultado = self.clasificador.obtener_respuesta(mensaje_usuario)
            
            # Si la confianza es buena, usar la respuesta de la red neuronal
            if resultado['confianza'] > 0.3:
                respuesta = resultado['respuesta']
                
                # Log para debugging (opcional, puedes quitar esto en producción)
                print(f"[Neural] Intención: {resultado['intencion']} ({resultado['confianza']:.1%})")
                
                return respuesta
        
        # Respaldo: buscar platillos si no se encontró intención clara
        if platillos_encontrados:
            respuesta = "Encontré estos platillos:\n"
            for platillo in platillos_encontrados:
                respuesta += self.formatear_platillo(platillo) + "\n"
            return respuesta
        
        # Respuesta por defecto
        return ("Lo siento, no entendí bien 😅\n"
                "Puedes preguntarme sobre:\n"
                "• **Menú** - Ver platillos\n"
                "• **Precios** - Costos\n"
                "• **Horario** - Cuándo abrimos\n"
                "• **Entrega** - Servicio a domicilio\n"
                "• **Ordenar** - Hacer pedido\n\n"
                "📲 WhatsApp: **664-563-16-75**")


# Instancia global del chatbot
bot = ChatbotRestaurante()

# ===== RUTAS DE LA API =====

@app.route('/')
def home():
    """Página de inicio de la API"""
    return jsonify({
        "mensaje": "API del Chatbot La Taza Loca",
        "version": "2.0 - Con Red Neuronal",
        "status": "running",
        "modelo_neural": bot.usar_neural,
        "endpoints": {
            "/chat": "POST - Enviar mensaje al chatbot",
            "/menu": "GET - Obtener menú completo",
            "/menu/disponibles": "GET - Obtener solo platillos disponibles",
            "/platillo/<id>": "GET - Información de un platillo",
            "/buscar": "POST - Buscar platillos",
            "/estadisticas": "GET - Estadísticas del menú",
            "/health": "GET - Estado del servicio"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal para chatear con el bot"""
    try:
        data = request.get_json()
        mensaje = data.get('mensaje', '')
        
        if not mensaje:
            return jsonify({
                "error": "El mensaje no puede estar vacío"
            }), 400
        
        respuesta = bot.responder(mensaje)
        
        return jsonify({
            "respuesta": respuesta,
            "status": "success",
            "modelo": "neural" if bot.usar_neural else "patrones"
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/menu', methods=['GET'])
def obtener_menu():
    """Obtiene el menú completo"""
    return jsonify({
        "menu": bot.menu,
        "total": len(bot.menu),
        "status": "success"
    })

@app.route('/menu/disponibles', methods=['GET'])
def obtener_disponibles():
    """Obtiene solo los platillos disponibles"""
    disponibles = [p for p in bot.menu if p['disponible']]
    return jsonify({
        "platillos": disponibles,
        "total": len(disponibles),
        "status": "success"
    })

@app.route('/platillo/<int:platillo_id>', methods=['GET'])
def obtener_platillo(platillo_id):
    """Obtiene información de un platillo específico"""
    platillo = next((p for p in bot.menu if p['id'] == platillo_id), None)
    
    if platillo:
        return jsonify({
            "platillo": platillo,
            "status": "success"
        })
    else:
        return jsonify({
            "error": "Platillo no encontrado",
            "status": "error"
        }), 404

@app.route('/buscar', methods=['POST'])
def buscar_platillo_endpoint():
    """Busca platillos por nombre"""
    try:
        data = request.get_json()
        termino = data.get('termino', '')
        
        if not termino:
            return jsonify({
                "error": "El término de búsqueda no puede estar vacío"
            }), 400
        
        resultados = bot.buscar_platillo(termino)
        
        return jsonify({
            "resultados": resultados,
            "total": len(resultados),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    """Obtiene estadísticas del menú"""
    total = len(bot.menu)
    disponibles = len([p for p in bot.menu if p['disponible']])
    mas_vendidos = [p for p in bot.menu if p.get('mas_vendido')]
    populares = [p for p in bot.menu if p.get('popular')]
    
    return jsonify({
        "total_platillos": total,
        "disponibles": disponibles,
        "no_disponibles": total - disponibles,
        "mas_vendidos": mas_vendidos,
        "populares": populares,
        "modelo_neural_activo": bot.usar_neural,
        "status": "success"
    })

@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({
        "status": "healthy",
        "modelo_neural": bot.usar_neural
    }), 200

@app.route('/reentrenar', methods=['POST'])
def reentrenar():
    """Endpoint para reentrenar el modelo (uso administrativo)"""
    try:
        from modelo_intenciones import ClasificadorIntenciones
        
        clasificador = ClasificadorIntenciones(archivo_datos='datos_entrenamiento.json')
        clasificador.entrenar(epochs=200, verbose=0)
        clasificador.guardar_modelo('modelo_chatbot')
        
        # Recargar el modelo en el bot
        bot.cargar_modelo_neural()
        
        return jsonify({
            "mensaje": "Modelo reentrenado exitosamente",
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
