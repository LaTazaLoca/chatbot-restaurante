"""
Sistema de Pedidos - Fonda Doña Magui
Gestiona carritos de compra y envío por WhatsApp
"""

import json
import uuid
from datetime import datetime
from urllib.parse import quote

class GestorPedidos:
    def __init__(self):
        # Almacenamiento en memoria de pedidos activos
        self.pedidos = {}
        self.numero_whatsapp = "5216645631675"  # Formato internacional
    
    def crear_pedido(self, usuario_id=None):
        """Crea un nuevo pedido vacío"""
        if usuario_id is None:
            usuario_id = str(uuid.uuid4())
        
        self.pedidos[usuario_id] = {
            'id': usuario_id,
            'items': [],
            'total': 0,
            'fecha_creacion': datetime.now().isoformat(),
            'estado': 'en_proceso',
            'datos_cliente': {}
        }
        
        return usuario_id
    
    def agregar_item(self, usuario_id, platillo, cantidad=1):
        """Agrega un platillo al pedido"""
        if usuario_id not in self.pedidos:
            self.crear_pedido(usuario_id)
        
        pedido = self.pedidos[usuario_id]
        
        # Buscar si el platillo ya existe en el carrito
        item_existente = None
        for item in pedido['items']:
            if item['id'] == platillo['id']:
                item_existente = item
                break
        
        if item_existente:
            # Incrementar cantidad
            item_existente['cantidad'] += cantidad
            item_existente['subtotal'] = item_existente['cantidad'] * platillo['precio']
        else:
            # Agregar nuevo item
            pedido['items'].append({
                'id': platillo['id'],
                'nombre': platillo['nombre'],
                'precio': platillo['precio'],
                'cantidad': cantidad,
                'subtotal': platillo['precio'] * cantidad
            })
        
        # Recalcular total
        self._calcular_total(usuario_id)
        
        return pedido
    
    def quitar_item(self, usuario_id, platillo_id):
        """Quita un platillo del pedido"""
        if usuario_id not in self.pedidos:
            return None
        
        pedido = self.pedidos[usuario_id]
        pedido['items'] = [item for item in pedido['items'] if item['id'] != platillo_id]
        
        self._calcular_total(usuario_id)
        
        return pedido
    
    def actualizar_cantidad(self, usuario_id, platillo_id, cantidad):
        """Actualiza la cantidad de un platillo"""
        if usuario_id not in self.pedidos:
            return None
        
        pedido = self.pedidos[usuario_id]
        
        for item in pedido['items']:
            if item['id'] == platillo_id:
                if cantidad <= 0:
                    # Si la cantidad es 0 o negativa, quitar el item
                    return self.quitar_item(usuario_id, platillo_id)
                else:
                    item['cantidad'] = cantidad
                    item['subtotal'] = item['precio'] * cantidad
                    break
        
        self._calcular_total(usuario_id)
        
        return pedido
    
    def vaciar_pedido(self, usuario_id):
        """Vacía todo el carrito"""
        if usuario_id in self.pedidos:
            self.pedidos[usuario_id]['items'] = []
            self.pedidos[usuario_id]['total'] = 0
        
        return self.pedidos.get(usuario_id)
    
    def obtener_pedido(self, usuario_id):
        """Obtiene el pedido actual"""
        return self.pedidos.get(usuario_id)
    
    def agregar_datos_cliente(self, usuario_id, nombre, telefono, direccion, tipo_entrega="domicilio", notas=""):
        """Agrega los datos del cliente al pedido"""
        if usuario_id not in self.pedidos:
            return None
        
        self.pedidos[usuario_id]['datos_cliente'] = {
            'nombre': nombre,
            'telefono': telefono,
            'direccion': direccion,
            'tipo_entrega': tipo_entrega,  # "domicilio" o "recoger"
            'notas': notas
        }
        
        return self.pedidos[usuario_id]
    
    def _calcular_total(self, usuario_id):
        """Calcula el total del pedido"""
        if usuario_id not in self.pedidos:
            return 0
        
        pedido = self.pedidos[usuario_id]
        total = sum(item['subtotal'] for item in pedido['items'])
        pedido['total'] = total
        
        return total
    
    def formatear_pedido_texto(self, usuario_id):
        """Formatea el pedido para enviar por WhatsApp"""
        pedido = self.pedidos.get(usuario_id)
        
        if not pedido or not pedido['items']:
            return None
        
        # Encabezado
        mensaje = "🍽️ *NUEVO PEDIDO - FONDA DOÑA MAGUI*\n"
        mensaje += "=" * 40 + "\n\n"
        
        # Datos del cliente
        cliente = pedido['datos_cliente']
        if cliente:
            mensaje += f"👤 *Cliente:* {cliente.get('nombre', 'Sin nombre')}\n"
            mensaje += f"📱 *Teléfono:* {cliente.get('telefono', 'Sin teléfono')}\n"
            
            if cliente.get('tipo_entrega') == 'domicilio':
                mensaje += f"🏠 *Dirección:* {cliente.get('direccion', 'Sin dirección')}\n"
                mensaje += "🚚 *Tipo:* Entrega a domicilio\n"
            else:
                mensaje += "🏪 *Tipo:* Recoger en local\n"
            
            if cliente.get('notas'):
                mensaje += f"📝 *Notas:* {cliente.get('notas')}\n"
            
            mensaje += "\n"
        
        # Items del pedido
        mensaje += "📋 *PEDIDO:*\n"
        mensaje += "-" * 40 + "\n"
        
        for i, item in enumerate(pedido['items'], 1):
            mensaje += f"{i}. *{item['nombre']}*\n"
            mensaje += f"   Cantidad: {item['cantidad']}\n"
            mensaje += f"   Precio unitario: ${item['precio']}\n"
            mensaje += f"   Subtotal: ${item['subtotal']}\n\n"
        
        # Total
        mensaje += "=" * 40 + "\n"
        mensaje += f"💰 *TOTAL: ${pedido['total']} MXN*\n"
        mensaje += "=" * 40 + "\n\n"
        
        # Pie de página
        mensaje += f"⏰ Hora del pedido: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        mensaje += "\n¡Gracias por tu preferencia! 😊🌮"
        
        return mensaje
    
    def generar_link_whatsapp(self, usuario_id):
        """Genera el link de WhatsApp con el pedido formateado"""
        mensaje = self.formatear_pedido_texto(usuario_id)
        
        if not mensaje:
            return None
        
        # Codificar el mensaje para URL
        mensaje_codificado = quote(mensaje)
        
        # Generar link de WhatsApp
        link = f"https://wa.me/{self.numero_whatsapp}?text={mensaje_codificado}"
        
        return link
    
    def finalizar_pedido(self, usuario_id):
        """Marca el pedido como finalizado y retorna el link de WhatsApp"""
        if usuario_id not in self.pedidos:
            return None
        
        pedido = self.pedidos[usuario_id]
        
        # Validar que el pedido tenga items y datos del cliente
        if not pedido['items']:
            return {
                'error': 'El pedido está vacío',
                'codigo': 'PEDIDO_VACIO'
            }
        
        if not pedido['datos_cliente'].get('nombre'):
            return {
                'error': 'Faltan datos del cliente',
                'codigo': 'DATOS_INCOMPLETOS'
            }
        
        # Generar link de WhatsApp
        link_whatsapp = self.generar_link_whatsapp(usuario_id)
        
        # Marcar como finalizado
        pedido['estado'] = 'finalizado'
        pedido['fecha_finalizacion'] = datetime.now().isoformat()
        
        return {
            'link_whatsapp': link_whatsapp,
            'mensaje': self.formatear_pedido_texto(usuario_id),
            'pedido': pedido,
            'codigo': 'SUCCESS'
        }
    
    def resumen_pedido(self, usuario_id):
        """Genera un resumen legible del pedido actual"""
        pedido = self.pedidos.get(usuario_id)
        
        if not pedido or not pedido['items']:
            return "🛒 Tu carrito está vacío"
        
        resumen = "🛒 *TU PEDIDO ACTUAL:*\n\n"
        
        for item in pedido['items']:
            resumen += f"• {item['cantidad']}x {item['nombre']} - ${item['subtotal']}\n"
        
        resumen += f"\n💰 *Total: ${pedido['total']} MXN*"
        
        return resumen


# Instancia global
gestor_pedidos = GestorPedidos()
