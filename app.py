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
"meta": {
    "patrones": [
        "la taza loca", "taza loca", "tu nombre", "como se llaman", "cómo se llaman",
        "info", "informacion", "información", "datos", "contacto", "contactar",
        "whatsapp", "wsp", "wasap", "telefono", "teléfono", "numero", "número",
        "horario", "abren", "cierran", "a que hora", "a qué hora",
        "entrega", "domicilio", "delivery", "envio", "envío",
        "ubicacion", "ubicación", "direccion", "dirección", "donde estan", "dónde están"
    ],
    "respuestas": [
        "☕🌮 **La Taza Loca**\n📲 WhatsApp: **664-563-16-75**\n🕒 Horario: **9:00 am a 4:00 pm**\n🚚 Entrega a domicilio **GRATIS** en lugares cercanos (sujeto a zona).\n📍 Tijuana, Baja California.\n\n¿Quieres ver el **menú** o hacer un **pedido**? 😄",
        "¡Claro! 😄\n📲 WhatsApp: **664-563-16-75**\n🕒 **9:00 am a 4:00 pm**\n🚚 Entrega **GRATIS** en cercanos (sujeto a zona)\n📍 Tijuana\n\nDime si buscas **menú**, **precios** o **recomendación** 🌮🔥"
    ],

    "nombre_negocio": "La Taza Loca",
    "whatsapp": "664-563-16-75",
    "whatsapp_link": "https://wa.me/526645631675",
    "horario": "De 9:00 am a 4:00 pm",
    "zona": "Tijuana, Baja California",
    "entrega_texto": "🚚 Entrega a domicilio GRATIS en lugares cercanos (sujeto a zona).",
    "nota": "Si necesitas dirección exacta, pide la ubicación al personal o comparte tu colonia para confirmar entrega."
},

    "saludos": {
        "patrones": ["hola", "buenos dias", "buen día", "buenas tardes", "buenas noches", "hey", "que tal", "qué tal", "holi", "buenas"],
        "respuestas": [
            "¡Hola! 👋 Bienvenido a **La Taza Loca** ☕🌮 ¿Qué se te antoja hoy: **desayuno**, **antojitos** o **comida**?",
            "¡Qué onda! 😄 Soy el asistente de **La Taza Loca**. ¿Quieres que te pase el **menú** o te recomiendo algo 🔥?"
        ]
    },

    "despedidas": {
        "patrones": ["adios", "adiós", "hasta luego", "chao", "nos vemos", "bye", "gracias", "sale", "va", "ok gracias", "muchas gracias"],
        "respuestas": [
            "¡Con gusto! 😄🌮 Cuando gustes te atendemos. ¡Bonito día!",
            "¡Gracias por tu preferencia! ☕✨ Si quieres ordenar, mándanos WhatsApp: **664-563-16-75** 📲"
        ]
    },

    "menu_completo": {
        "patrones": ["menu", "menú", "que venden", "platillos", "comida", "opciones", "que hay", "qué hay", "lista"],
        "respuestas": [
            "Aquí va el **menú de La Taza Loca** 🌮🔥\n\n**DESAYUNOS** 🍳\n• Huevos Rancheros\n• Huevos a la Mexicana\n• Huevos con Jamón\n• Huevos Divorciados\n• Omelette de Queso\n\n**ANTOJITOS** 🌮\n• Flautas de Pollo\n• Chilaquiles Verdes con Huevo\n• Chilaquiles Rojos con Huevo\n• Enmoladas de Pollo\n• Enchiladas de Pollo\n• Chiles Rellenos de Queso\n\n**COMIDAS** 🍛\n• Pechuga en Chipotle\n• Mole de Pollo\n• Puerco en Salsa Verde\n\n📲 Ordena por WhatsApp: **664-563-16-75**\n🕒 Horario: **9:00 am a 4:00 pm**\n🚚 Entrega GRATIS en lugares cercanos (sujeto a zona).",
            "¿Qué te interesa ver primero? 😄\n1) **Desayunos** 🍳\n2) **Antojitos** 🌮\n3) **Comidas** 🍛\nDime el número y te lo paso."
        ]
    },

    "menu_desayunos": {
        "patrones": ["desayunos", "huevos", "omelette", "omelet", "desayuno"],
        "respuestas": [
            "**DESAYUNOS 🍳**\n• Huevos Rancheros\n• Huevos a la Mexicana\n• Huevos con Jamón\n• Huevos Divorciados\n• Omelette de Queso\n\n¿Te antoja algo en especial? 😋",
            "En desayunos tenemos huevos de varios estilos y omelette 🧀 ¿Quieres algo más picosito 🌶️ o más tranqui?"
        ]
    },

    "menu_antojitos": {
        "patrones": ["antojitos", "chilaquiles", "enmoladas", "enchiladas", "flautas", "chiles rellenos", "chile relleno"],
        "respuestas": [
            "**ANTOJITOS 🌮🔥**\n• Flautas de Pollo\n• Chilaquiles Verdes con Huevo\n• Chilaquiles Rojos con Huevo\n• Enmoladas de Pollo\n• Enchiladas de Pollo\n• Chiles Rellenos de Queso\n\n¿Los quieres **rojos o verdes**? 😄",
            "Ufff antojitos tenemos de los buenos 😋 ¿Te recomiendo **chilaquiles rojos** o **enmoladas**?"
        ]
    },

    "menu_comidas": {
        "patrones": ["comidas", "mole", "chipotle", "puerco", "salsa verde", "comida corrida", "platillo fuerte"],
        "respuestas": [
            "**COMIDAS 🍛**\n• Pechuga en Chipotle\n• Mole de Pollo\n• Puerco en Salsa Verde\n\n¿Te late más algo cremosito (chipotle) o algo tradicional (mole)? 🔥",
            "Para comida te recomiendo el **mole de pollo** si quieres algo tradicional 😋 o la **pechuga en chipotle** si quieres cremita 🌶️"
        ]
    },

    "precios": {
        "patrones": ["precio", "costo", "cuanto cuesta", "cuánto cuesta", "cuanto vale", "cuánto vale", "precios", "en cuanto", "en cuánto"],
        "respuestas": [
            "La mayoría de nuestros platillos están en **$120 pesos** 😄🌮 ¿Cuál platillo te interesa para confirmarte?",
            "Normalmente andan en **$120** 💛 ¿Quieres desayunos, antojitos o comidas?"
        ]
    },

    "recomendaciones": {
        "patrones": ["recomienda", "recomendacion", "recomendación", "que me recomiendas", "qué me recomiendas", "sugieres", "popular", "mas vendido", "más vendido", "top"],
        "respuestas": [
            "🔥 Recomendación de la casa: **Chilaquiles rojos con huevo** 😋\nTambién rifan las **Enmoladas de Pollo**.\n¿Prefieres **rojo** o **verde**?",
            "Si quieres irte a la segura 😄: **Huevos Rancheros** o **Chilaquiles**.\nSi quieres algo bien tradicional: **Mole de Pollo** ✨"
        ]
    },

    "disponibilidad": {
        "patrones": ["disponible", "esta disponible", "está disponible", "hay disponible", "tienen", "hay", "si hay", "si tienen"],
        "respuestas": [
            "Dime el platillo que buscas 😄 y te confirmo disponibilidad. ¿Cuál se te antojó?",
            "¡Va! 👌 ¿Qué platillo quieres? (Ej: *chilaquiles rojos*, *mole de pollo*)"
        ]
    },

    "horarios": {
        "patrones": ["horario", "cuando abren", "cuándo abren", "hora", "abierto", "cierran", "a que hora", "a qué hora"],
        "respuestas": [
            "🕒 Nuestro horario es **de 9:00 am a 4:00 pm** todos los días 😄",
            "Estamos atendiendo **de 9:00 am a 4:00 pm** ⏰ ¿Quieres ordenar por WhatsApp?"
        ]
    },

    "entrega": {
        "patrones": ["entrega", "domicilio", "envio", "envío", "llevan", "delivery", "reparto", "mandan", "mandas", "me lo traen"],
        "respuestas": [
            "🚚 Sí hacemos entrega a domicilio, y en lugares cercanos es **GRATIS** 😄\nDime tu **colonia** para confirmar cobertura.",
            "¡Claro! 📦 ¿En qué **colonia** estás? Así te digo si entra en entrega **GRATIS**."
        ]
    },

    "pagos": {
        "patrones": ["como pago", "cómo pago", "pagar", "metodos de pago", "métodos de pago", "tarjeta", "efectivo", "transferencia"],
        "respuestas": [
            "Aceptamos **efectivo, transferencia y tarjeta** 💳✨ ¿Vas a recoger o quieres entrega a domicilio?",
            "Puedes pagar en **efectivo**, **transferencia** o **tarjeta** 😄"
        ]
    },

    "ubicacion": {
        "patrones": ["donde estan", "dónde están", "ubicacion", "ubicación", "direccion", "dirección", "como llego", "cómo llego", "maps", "google"],
        "respuestas": [
            "Estamos en **Tijuana, Baja California** 📍\nSi me dices tu zona/colonia te doy referencia y confirmo si te queda cerca 😄",
            "Pásame tu colonia y te digo qué tan cerca estás 📍😄"
        ]
    },

    "wifi": {
        "patrones": ["wifi", "internet", "contraseña", "clave", "password", "wi-fi"],
        "respuestas": [
            "Sí tenemos **WiFi** para clientes 😄📶 La clave te la comparten en caja o el personal, ¡nomás pídela!",
            "Claro 📶 Pídele la clave del WiFi al personal y te la pasan en corto 😄"
        ]
    },

    "telefono": {
        "patrones": ["telefono", "teléfono", "numero", "número", "llamar", "contacto", "whatsapp", "wasap", "wsp"],
        "respuestas": [
            "📲 Nuestro WhatsApp es **664-563-16-75** 😄\nSi quieres, dime qué vas a pedir y te ayudo a armar tu orden.",
            "¡Claro! Escríbenos por WhatsApp: **664-563-16-75** 📲✨"
        ]
    },

    "ordenar": {
        "patrones": ["quiero pedir", "quiero ordenar", "hacer pedido", "hacer un pedido", "ordenar", "pedido", "para llevar", "pickup", "recoger"],
        "respuestas": [
            "¡Va! 😄 Para armar tu pedido dime:\n1) Platillo(s)\n2) ¿Entrega o para recoger?\n3) Tu colonia (si es entrega)\n📲 WhatsApp: **664-563-16-75**",
            "Perfecto 🔥 ¿Qué vas a pedir y cuántos? (Ej: *2 chilaquiles rojos con huevo*)"
        ]
    },

    "fallback": {
        "patrones": [],
        "respuestas": [
            "Perdón 😅 no caché bien. ¿Quieres ver el **menú**, **horarios**, **entrega** o **hacer un pedido**?",
            "Dime si buscas **menú**, **precios**, **entrega** o **recomendación** 😄🌮"
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
                if nombre_plat in mensaje_limpio or self.similitud_texto(nombre_plat, mensaje_limpio) > 0.7:
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
