from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
from difflib import SequenceMatcher
import os

app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier origen

class ChatbotRestaurante:
    def __init__(self, archivo_conocimiento='conocimiento_bot.json', archivo_menu='menu.json'):
        self.archivo_conocimiento = archivo_conocimiento
        self.archivo_menu = archivo_menu
        self.conocimiento = self.cargar_conocimiento()
        self.menu = self.cargar_menu()
        
    def cargar_menu(self):
        """Carga el menú desde el archivo JSON"""
        if os.path.exists(self.archivo_menu):
            with open(self.archivo_menu, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def cargar_conocimiento(self):
        """Carga el conocimiento desde un archivo JSON"""
        if os.path.exists(self.archivo_conocimiento):
            with open(self.archivo_conocimiento, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            conocimiento_inicial = {
                "saludos": {
                    "patrones": ["hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "que tal", "que onda"],
                    "respuestas": [
                        "¡Hola! Bienvenido a nuestro restaurante. ¿En qué puedo ayudarte?",
                        "¡Buen día! ¿Quieres conocer nuestro menú o tienes alguna pregunta?",
                        "¡Hola! Estoy aquí para ayudarte con tu pedido o resolver tus dudas."
                    ]
                },
                "despedidas": {
                    "patrones": ["adios", "hasta luego", "chao", "nos vemos", "bye", "gracias", "eso es todo"],
                    "respuestas": [
                        "¡Hasta pronto! Que disfrutes tu comida.",
                        "¡Que tengas un excelente día! Vuelve cuando quieras.",
                        "¡Gracias por tu preferencia! Nos vemos pronto."
                    ]
                },
                "menu_completo": {
                    "patrones": ["menu", "que venden", "que tienen", "platillos", "comida", "que hay", "opciones"],
                    "respuestas": [
                        "Tenemos deliciosos platillos mexicanos. ¿Te gustaría ver desayunos o algún platillo en particular?",
                        "Nuestro menú incluye desayunos tradicionales mexicanos. ¿Quieres que te recomiende algo?"
                    ]
                },
                "precios": {
                    "patrones": ["precio", "costo", "cuanto cuesta", "cuanto vale", "precios"],
                    "respuestas": [
                        "La mayoría de nuestros platillos tienen un precio de $120 pesos. ¿Te gustaría saber el precio de algún platillo en específico?",
                        "Nuestros desayunos cuestan $120 pesos. ¿Quieres información sobre algún platillo?"
                    ]
                },
                "recomendaciones": {
                    "patrones": ["recomienda", "recomendacion", "que me recomiendas", "sugieres", "que pido", "popular", "favorito"],
                    "respuestas": [
                        "Te recomiendo nuestros Chilaquiles Rojos con Huevo, son los más vendidos. También las Enmoladas de Pollo son muy populares.",
                        "¡Nuestros platillos estrella son los Chilaquiles Rojos y las Enmoladas de Pollo! Son deliciosos."
                    ]
                },
                "disponibilidad": {
                    "patrones": ["disponible", "tienen", "hay", "esta disponible", "tienen disponible"],
                    "respuestas": [
                        "Déjame verificar la disponibilidad. ¿Qué platillo te interesa?",
                        "La mayoría de nuestros platillos están disponibles. ¿Cuál te gustaría ordenar?"
                    ]
                },
                "horarios": {
                    "patrones": ["horario", "horarios", "cuando abren", "hora", "abierto", "que hora cierran"],
                    "respuestas": [
                        "Estamos abiertos de Lunes a Domingo de 8:00 AM a 4:00 PM.",
                        "Nuestro horario es de 8:00 AM a 4:00 PM todos los días."
                    ]
                },
                "entrega": {
                    "patrones": ["entrega", "domicilio", "envio", "llevan", "delivery"],
                    "respuestas": [
                        "Sí, hacemos entregas a domicilio en Tijuana. El costo de envío depende de tu ubicación.",
                        "Realizamos entregas en Tijuana. ¿En qué colonia te encuentras?"
                    ]
                },
                "pagos": {
                    "patrones": ["como pago", "pagar", "metodos de pago", "formas de pago", "efectivo", "tarjeta"],
                    "respuestas": [
                        "Aceptamos efectivo, transferencia y tarjeta de crédito/débito.",
                        "Puedes pagar en efectivo, transferencia bancaria o con tarjeta."
                    ]
                },
                "ubicacion": {
                    "patrones": ["donde estan", "ubicacion", "direccion", "donde", "como llego"],
                    "respuestas": [
                        "Estamos ubicados en Tijuana, Baja California. ¿Quieres que te enviemos la dirección exacta?",
                        "Nos encontramos en Tijuana. Puedo darte más detalles de la ubicación si gustas."
                    ]
                }
            }
            self.guardar_conocimiento(conocimiento_inicial)
            return conocimiento_inicial
    
    def guardar_conocimiento(self, conocimiento=None):
        """Guarda el conocimiento en un archivo JSON"""
        if conocimiento is None:
            conocimiento = self.conocimiento
        with open(self.archivo_conocimiento, 'w', encoding='utf-8') as f:
            json.dump(conocimiento, f, ensure_ascii=False, indent=4)
    
    def similitud_texto(self, texto1, texto2):
        """Calcula la similitud entre dos textos"""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza el texto del usuario"""
        texto = texto.lower()
        texto = re.sub(r'[¿?¡!.,;]', '', texto)
        return texto.strip()
    
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
    
    def listar_platillos_disponibles(self):
        """Lista todos los platillos disponibles"""
        disponibles = [p for p in self.menu if p['disponible']]
        
        if not disponibles:
            return "Lo siento, no tenemos platillos disponibles en este momento."
        
        respuesta = "\n📋 **MENÚ DISPONIBLE**\n\n"
        for platillo in disponibles:
            precio = platillo['precio']
            respuesta += f"• {platillo['nombre']} - ${precio}"
            if platillo.get('mas_vendido'):
                respuesta += " ⭐"
            if platillo.get('popular'):
                respuesta += " 🔥"
            respuesta += "\n"
        
        respuesta += "\n💬 ¿Quieres información detallada de algún platillo?"
        return respuesta
    
    def encontrar_mejor_respuesta(self, mensaje_usuario):
        """Encuentra la mejor respuesta basada en patrones"""
        mensaje_limpio = self.limpiar_texto(mensaje_usuario)
        
        # Verificar si está preguntando por un platillo específico
        if any(palabra in mensaje_limpio for palabra in ['info', 'informacion', 'detalles', 'dame', 'quiero']):
            for platillo in self.menu:
                nombre_plat = self.limpiar_texto(platillo['nombre'])
                if nombre_plat en mensaje_limpio or self.similitud_texto(nombre_plat, mensaje_limpio) > 0.7:
                    return self.formatear_platillo(platillo)
        
        mejor_coincidencia = None
        mejor_puntuacion = 0
        
        for categoria, datos in self.conocimiento.items():
            for patron in datos['patrones']:
                if patron in mensaje_limpio:
                    puntuacion = 1.0
                else:
                    puntuacion = self.similitud_texto(patron, mensaje_limpio)
                
                if puntuacion > mejor_puntuacion and puntuacion > 0.6:
                    mejor_puntuacion = puntuacion
                    mejor_coincidencia = categoria
        
        if mejor_coincidencia:
            import random
            respuesta = random.choice(self.conocimiento[mejor_coincidencia]['respuestas'])
            
            if mejor_coincidencia == 'menu_completo':
                respuesta += self.listar_platillos_disponibles()
            
            return respuesta
        
        return None
    
    def responder(self, mensaje_usuario):
        """Genera una respuesta al mensaje del usuario"""
        respuesta = self.encontrar_mejor_respuesta(mensaje_usuario)
        
        if respuesta:
            return respuesta
        else:
            platillos_encontrados = self.buscar_platillo(mensaje_usuario)
            if platillos_encontrados:
                respuesta = "Encontré estos platillos:\n"
                for platillo in platillos_encontrados:
                    respuesta += self.formatear_platillo(platillo) + "\n"
                return respuesta
            
            return ("Lo siento, no entendí bien. Puedes preguntarme sobre nuestro menú, "
                   "precios, horarios, entregas o algún platillo específico.")

# Instancia global del chatbot
bot = ChatbotRestaurante()

# ===== RUTAS DE LA API =====

@app.route('/')
def home():
    """Página de inicio de la API"""
    return jsonify({
        "mensaje": "API del Chatbot Restaurante",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/chat": "POST - Enviar mensaje al chatbot",
            "/menu": "GET - Obtener menú completo",
            "/menu/disponibles": "GET - Obtener solo platillos disponibles",
            "/platillo/<id>": "GET - Obtener información de un platillo específico",
            "/buscar": "POST - Buscar platillos",
            "/estadisticas": "GET - Estadísticas del menú"
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
            "status": "success"
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
def buscar_platillo():
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
        "status": "success"
    })

# Endpoint de salud para Render
@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Render asigna el puerto automáticamente
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
