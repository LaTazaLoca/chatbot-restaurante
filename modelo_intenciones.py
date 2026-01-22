"""
Modelo de Red Neuronal para Clasificación de Intenciones
La Taza Loca - Chatbot Inteligente
Versión PyTorch
"""

import numpy as np
import json
import pickle
import os
import re
import random

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


class RedNeuronalIntenciones(nn.Module):
    """Red neuronal para clasificar intenciones"""
    
    def __init__(self, input_size, hidden_size, output_size):
        super(RedNeuronalIntenciones, self).__init__()
        
        self.red = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(32, output_size)
        )
    
    def forward(self, x):
        return self.red(x)


class DatasetIntenciones(Dataset):
    """Dataset para entrenar el modelo"""
    
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class ProcesadorTexto:
    """Procesa y tokeniza texto en español"""
    
    def __init__(self):
        self.vocabulario = {}
        self.idx_a_palabra = {}
        self.vocab_size = 0
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza el texto"""
        texto = texto.lower()
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ü': 'u', 'ñ': 'n'
        }
        for acento, sin_acento in reemplazos.items():
            texto = texto.replace(acento, sin_acento)
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        return texto.strip()
    
    def tokenizar(self, texto):
        """Divide el texto en tokens (palabras)"""
        texto_limpio = self.limpiar_texto(texto)
        tokens = texto_limpio.split()
        return tokens
    
    def construir_vocabulario(self, textos):
        """Construye el vocabulario a partir de una lista de textos"""
        todas_palabras = set()
        for texto in textos:
            tokens = self.tokenizar(texto)
            todas_palabras.update(tokens)
        
        self.vocabulario = {palabra: idx for idx, palabra in enumerate(sorted(todas_palabras))}
        self.idx_a_palabra = {idx: palabra for palabra, idx in self.vocabulario.items()}
        self.vocab_size = len(self.vocabulario)
        
        print(f"Vocabulario construido: {self.vocab_size} palabras")
        return self.vocabulario
    
    def texto_a_bow(self, texto):
        """Convierte texto a Bag of Words (vector de características)"""
        tokens = self.tokenizar(texto)
        bow = np.zeros(self.vocab_size)
        
        for token in tokens:
            if token in self.vocabulario:
                bow[self.vocabulario[token]] = 1
        
        return bow


class ClasificadorIntenciones:
    """Red neuronal para clasificar intenciones del usuario"""
    
    def __init__(self, archivo_datos='datos_entrenamiento.json'):
        self.archivo_datos = archivo_datos
        self.procesador = ProcesadorTexto()
        self.modelo = None
        self.intenciones = []
        self.respuestas = {}
        self.clases = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def cargar_datos(self):
        """Carga los datos de entrenamiento"""
        if not os.path.exists(self.archivo_datos):
            raise FileNotFoundError(f"No se encontró el archivo: {self.archivo_datos}")
        
        with open(self.archivo_datos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        self.intenciones = datos['intenciones']
        self.clases = [intent['tag'] for intent in self.intenciones]
        self.respuestas = {intent['tag']: intent['respuestas'] for intent in self.intenciones}
        
        print(f"Cargadas {len(self.intenciones)} intenciones")
        return datos
    
    def preparar_datos_entrenamiento(self):
        """Prepara los datos para entrenar el modelo"""
        documentos = []
        etiquetas = []
        todos_patrones = []
        
        for intent in self.intenciones:
            tag = intent['tag']
            for patron in intent['patrones']:
                todos_patrones.append(patron)
                documentos.append(patron)
                etiquetas.append(tag)
        
        self.procesador.construir_vocabulario(todos_patrones)
        
        X = []
        y = []
        
        for i, doc in enumerate(documentos):
            bow = self.procesador.texto_a_bow(doc)
            X.append(bow)
            y.append(self.clases.index(etiquetas[i]))
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"Datos preparados: {len(X)} ejemplos, {self.procesador.vocab_size} características")
        return X, y
    
    def entrenar(self, epochs=200, batch_size=8, learning_rate=0.001, verbose=1):
        """Entrena el modelo"""
        print("Cargando datos...")
        self.cargar_datos()
        
        print("Preparando datos de entrenamiento...")
        X, y = self.preparar_datos_entrenamiento()
        
        # Crear dataset y dataloader
        dataset = DatasetIntenciones(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Crear modelo
        print("Construyendo modelo...")
        self.modelo = RedNeuronalIntenciones(
            input_size=self.procesador.vocab_size,
            hidden_size=128,
            output_size=len(self.clases)
        ).to(self.device)
        
        # Configurar entrenamiento
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.modelo.parameters(), lr=learning_rate)
        
        print(f"\nEntrenando modelo ({epochs} épocas)...")
        
        for epoch in range(epochs):
            self.modelo.train()
            total_loss = 0
            correct = 0
            total = 0
            
            for batch_X, batch_y in dataloader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # Forward
                outputs = self.modelo(batch_X)
                loss = criterion(outputs, batch_y)
                
                # Backward
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                # Calcular precisión
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
            
            accuracy = correct / total
            
            if verbose and (epoch + 1) % 20 == 0:
                print(f"Época {epoch+1}/{epochs} - Loss: {total_loss/len(dataloader):.4f} - Precisión: {accuracy:.2%}")
        
        print(f"\nEntrenamiento completado!")
        print(f"Precisión final: {accuracy:.2%}")
        
        return accuracy
    
    def guardar_modelo(self, ruta='modelo_chatbot'):
        """Guarda el modelo y los datos necesarios"""
        os.makedirs(ruta, exist_ok=True)
        
        # Guardar modelo PyTorch
        torch.save(self.modelo.state_dict(), os.path.join(ruta, 'modelo.pth'))
        
        # Guardar datos auxiliares
        datos_auxiliares = {
            'vocabulario': self.procesador.vocabulario,
            'idx_a_palabra': self.procesador.idx_a_palabra,
            'vocab_size': self.procesador.vocab_size,
            'clases': self.clases,
            'respuestas': self.respuestas
        }
        
        with open(os.path.join(ruta, 'datos_auxiliares.pkl'), 'wb') as f:
            pickle.dump(datos_auxiliares, f)
        
        print(f"Modelo guardado en: {ruta}/")
    
    def cargar_modelo(self, ruta='modelo_chatbot'):
        """Carga un modelo previamente entrenado"""
        # Cargar datos auxiliares primero
        with open(os.path.join(ruta, 'datos_auxiliares.pkl'), 'rb') as f:
            datos = pickle.load(f)
        
        self.procesador.vocabulario = datos['vocabulario']
        self.procesador.idx_a_palabra = datos['idx_a_palabra']
        self.procesador.vocab_size = datos['vocab_size']
        self.clases = datos['clases']
        self.respuestas = datos['respuestas']
        
        # Crear y cargar modelo
        self.modelo = RedNeuronalIntenciones(
            input_size=self.procesador.vocab_size,
            hidden_size=128,
            output_size=len(self.clases)
        ).to(self.device)
        
        self.modelo.load_state_dict(torch.load(os.path.join(ruta, 'modelo.pth'), map_location=self.device))
        self.modelo.eval()
        
        print(f"Modelo cargado desde: {ruta}/")
    
    def predecir_intencion(self, texto, umbral_confianza=0.10):
        """Predice la intención de un texto"""
        if self.modelo is None:
            raise ValueError("El modelo no está cargado. Entrena o carga un modelo primero.")
        
        self.modelo.eval()
        
        # Convertir texto a vector
        bow = self.procesador.texto_a_bow(texto)
        bow_tensor = torch.FloatTensor([bow]).to(self.device)
        
        # Hacer predicción
        with torch.no_grad():
            outputs = self.modelo(bow_tensor)
            probabilidades = torch.softmax(outputs, dim=1)[0]
        
        # Obtener la intención con mayor probabilidad
        confianza, idx_max = torch.max(probabilidades, 0)
        confianza = confianza.item()
        intencion = self.clases[idx_max.item()]
        
        if confianza < umbral_confianza:
            return None, confianza
        
        return intencion, confianza
    
    def obtener_respuesta(self, texto):
        """Obtiene una respuesta para el texto del usuario"""
        intencion, confianza = self.predecir_intencion(texto)
        
        if intencion is None:
            return {
                'respuesta': "Lo siento, no entendí bien. ¿Quieres ver el **menú**, **precios** o **hacer un pedido**? 😄",
                'intencion': 'desconocida',
                'confianza': float(confianza)
            }
        
        respuesta = random.choice(self.respuestas[intencion])
        
        return {
            'respuesta': respuesta,
            'intencion': intencion,
            'confianza': float(confianza)
        }


if __name__ == "__main__":
    print("=== Probando el Clasificador de Intenciones (PyTorch) ===\n")
    
    clasificador = ClasificadorIntenciones()
    clasificador.entrenar(epochs=200, verbose=1)
    clasificador.guardar_modelo()
    
    print("\n=== Probando predicciones ===\n")
    
    pruebas = [
        "hola que tal",
        "cuanto cuestan los chilaquiles",
        "tienen servicio a domicilio",
        "a que hora cierran",
        "quiero pedir unos huevos rancheros",
        "que me recomiendas"
    ]
    
    for texto in pruebas:
        resultado = clasificador.obtener_respuesta(texto)
        print(f"Usuario: {texto}")
        print(f"Intención: {resultado['intencion']} ({resultado['confianza']:.2%})")
        print(f"Bot: {resultado['respuesta'][:100]}...")
        print("-" * 50)
