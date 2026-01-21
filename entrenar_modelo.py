"""
Script para entrenar el modelo de intenciones
Ejecutar: python entrenar_modelo.py
"""

from modelo_intenciones import ClasificadorIntenciones
import os

def main():
    print("=" * 60)
    print("  ENTRENAMIENTO DEL CHATBOT - LA TAZA LOCA")
    print("  Red Neuronal para Clasificación de Intenciones")
    print("=" * 60)
    print()
    
    # Verificar que existe el archivo de datos
    archivo_datos = 'datos_entrenamiento.json'
    if not os.path.exists(archivo_datos):
        print(f"ERROR: No se encontró '{archivo_datos}'")
        print("Asegúrate de tener el archivo de datos de entrenamiento.")
        return
    
    # Crear clasificador
    clasificador = ClasificadorIntenciones(archivo_datos=archivo_datos)
    
    # Entrenar
    print("Iniciando entrenamiento...\n")
    clasificador.entrenar(epochs=200, batch_size=8, verbose=1)
    
    # Guardar modelo
    clasificador.guardar_modelo('modelo_chatbot')
    
    print("\n" + "=" * 60)
    print("  ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print()
    print("Archivos generados:")
    print("  - modelo_chatbot/modelo.keras (red neuronal)")
    print("  - modelo_chatbot/datos_auxiliares.pkl (vocabulario y clases)")
    print()
    
    # Pruebas rápidas
    print("=" * 60)
    print("  PRUEBAS RÁPIDAS")
    print("=" * 60)
    print()
    
    pruebas = [
        "hola buenos dias",
        "que tienen de comer",
        "cuanto cuesta",
        "hacen envios",
        "a que hora abren",
        "quiero ordenar",
        "gracias"
    ]
    
    for texto in pruebas:
        resultado = clasificador.obtener_respuesta(texto)
        print(f"👤 Usuario: {texto}")
        print(f"🤖 Intención detectada: {resultado['intencion']} ({resultado['confianza']:.1%})")
        print(f"💬 Respuesta: {resultado['respuesta'][:80]}...")
        print("-" * 50)
    
    print("\n✅ Modelo listo para usar en app.py")

if __name__ == "__main__":
    main()
