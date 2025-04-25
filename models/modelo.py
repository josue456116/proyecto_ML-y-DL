from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd
import nltk
import numpy as np
import re
from nltk.corpus import stopwords

# Descargar recursos de NLTK si no están disponibles
nltk.download('stopwords')
nltk.download('punkt')

class AgrupadorDocumentos:
    def __init__(self):
        # Cargar stopwords desde CSV
        self.stop_words = self._cargar_stopwords()
        
        # Ajustar parámetros del vectorizador
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            max_df=0.95,    # 95% de los documentos como máximo
            min_df=0.05,    # Al menos 5% de los documentos
            stop_words=list(self.stop_words),
            token_pattern=r'(?u)\b\w+\b',
            ngram_range=(1, 2)
        )

    def _procesar_stopwords(self, palabras_compuestas):
        """Procesa stopwords compuestas para evitar advertencias"""
        palabras_procesadas = set()
        for palabra in palabras_compuestas:
            if ' ' in palabra:
                # Agregar cada parte de la palabra compuesta
                palabras_procesadas.update(palabra.split())
            else:
                palabras_procesadas.add(palabra)
        return list(palabras_procesadas)

    def _cargar_stopwords(self):
        """Carga las stopwords desde el archivo CSV"""
        try:
            df = pd.read_csv('data/spanish_stopwords.csv')
            stopwords = list(df['palabra'].values)
            # Procesar las stopwords para manejar palabras compuestas
            return self._procesar_stopwords(stopwords)
        except FileNotFoundError:
            print("Error: No se encontró el archivo de stopwords")
            return []

    def agrupar_documentos(self, documentos):
        if not documentos:
            return {
                "clusters": {},
                "palabras_clave": {},
                "error": "No hay documentos para procesar"
            }
            
        try:
            # Asegurar que tenemos suficientes documentos
            if len(documentos) < 2:
                return {
                    "clusters": {},
                    "palabras_clave": {},
                    "error": "Se necesitan al menos 2 documentos para agrupar"
                }

            # Vectorizar documentos
            X = self.vectorizer.fit_transform(documentos)
            
            # Ajustar min_df basado en el número de documentos
            min_docs = max(2, len(documentos) * 0.05)  # Al menos 2 documentos o 5%
            self.vectorizer.min_df = min_docs / len(documentos)
            
            # Verificar dimensiones
            if X.shape[1] == 0:
                return {
                    "clusters": {},
                    "palabras_clave": {},
                    "error": "No hay suficientes términos para analizar"
                }
            
            # Determinar número de clusters
            n_clusters = min(len(documentos), 3)
            if n_clusters < 2:
                n_clusters = 2
                
            # Aplicar K-means
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # Obtener palabras clave
            palabras_clave = self._obtener_palabras_clave(kmeans)
            
            # Organizar resultados
            resultados = {
                "clusters": {},
                "palabras_clave": palabras_clave
            }
            
            # Agrupar documentos por cluster
            for idx, cluster in enumerate(clusters):
                cluster_id = int(cluster)
                if cluster_id not in resultados["clusters"]:
                    resultados["clusters"][cluster_id] = []
                    
                resultados["clusters"][cluster_id].append({
                    "texto": documentos[idx],
                    "cluster": cluster_id
                })
            
            return resultados
            
        except Exception as e:
            return {
                "clusters": {},
                "palabras_clave": {},
                "error": str(e)
            }

    def _obtener_palabras_clave(self, kmeans, n_palabras=5):
        """Extrae las palabras más relevantes de cada cluster"""
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names_out()
        palabras_clave = {}
        
        for i in range(kmeans.n_clusters):
            cluster_terms = [terms[ind] for ind in order_centroids[i, :n_palabras]]
            palabras_clave[i] = cluster_terms
            
        return palabras_clave

class AnalizadorNoticias:
    def __init__(self):
        self.categorias = {
            'politica': ['gobierno', 'presidente', 'congreso', 'ministro', 'ley', 'política'],
            'economia': ['economía', 'mercado', 'dólar', 'bolsa', 'empresas', 'inflación'],
            'deportes': ['fútbol', 'deporte', 'partido', 'jugador', 'torneo', 'mundial'],
            'tecnologia': ['tecnología', 'internet', 'digital', 'app', 'software', 'dispositivo'],
            'salud': ['salud', 'médico', 'hospital', 'enfermedad', 'tratamiento', 'paciente'],
            'cultura': ['arte', 'música', 'cine', 'teatro', 'libro', 'festival']
        }
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=list(self._cargar_stopwords())
        )
    
    def _cargar_stopwords(self):
        """Carga las stopwords desde el archivo CSV"""
        try:
            df = pd.read_csv('data/spanish_stopwords.csv')
            return set(df['palabra'].values)
        except FileNotFoundError:
            print("Error: No se encontró el archivo de stopwords")
            return set()
    
    def analizar_texto(self, texto):
        """Analiza el texto y determina su categoría"""
        try:
            texto_procesado = self._preprocesar_texto(texto)
            
            # Calcular puntuación para cada categoría
            puntuaciones = {}
            for categoria, palabras_clave in self.categorias.items():
                puntuacion = sum(1 for palabra in palabras_clave if palabra.lower() in texto_procesado.lower())
                puntuaciones[categoria] = puntuacion
            
            # Determinar categoría principal
            categoria_principal = max(puntuaciones.items(), key=lambda x: x[1])
            
            # Extraer palabras clave
            palabras_clave = self._extraer_palabras_clave(texto)
            
            return {
                'categoria': categoria_principal[0],
                'confianza': categoria_principal[1],
                'palabras_clave': palabras_clave,
                'texto_original': texto
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _preprocesar_texto(self, texto):
        """Preprocesa el texto para análisis"""
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', '', texto)
        return texto
    
    def _extraer_palabras_clave(self, texto, n_palabras=5):
        """Extrae las palabras más relevantes del texto"""
        X = self.vectorizer.fit_transform([texto])
        feature_names = self.vectorizer.get_feature_names_out()
        scores = X.toarray()[0]
        top_indices = scores.argsort()[-n_palabras:][::-1]
        return [feature_names[i] for i in top_indices]