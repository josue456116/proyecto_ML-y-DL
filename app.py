from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import unicodedata
from models.modelo import AgrupadorDocumentos, AnalizadorNoticias
import requests
from bs4 import BeautifulSoup
import os

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Definimos stop_words en español
stop_words = set(stopwords.words('spanish'))
# Agregamos palabras adicionales comunes en noticias
stop_words.update(['si', 'así', 'vez', 'dice', 'dijo', 'además', 'según', 'ser', 'puede', 'están'])

# Inicializamos la app de Flask
app = Flask(__name__)
agrupador = AgrupadorDocumentos()
analizador = AnalizadorNoticias()

def preprocess_text(text):
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar caracteres especiales y números
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Normalizar caracteres unicode
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Tokenización y lematización
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def get_optimal_clusters(X, max_clusters=10):
    silhouette_scores = []
    K = range(2, min(max_clusters, X.shape[0]))
    
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        score = silhouette_score(X, kmeans.labels_)
        silhouette_scores.append(score)
    
    return K[silhouette_scores.index(max(silhouette_scores))]

def get_cluster_keywords(vectorizer, kmeans, n_terms=5):
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    keywords = {}
    
    for i in range(kmeans.n_clusters):
        cluster_terms = [terms[ind] for ind in order_centroids[i, :n_terms]]
        keywords[i] = cluster_terms
    
    return keywords

def extraer_texto_url(url):
    """Extrae el texto principal de una URL de noticia"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminar scripts, estilos y elementos no deseados
        for elemento in soup(['script', 'style', 'nav', 'header', 'footer']):
            elemento.decompose()
        
        # Obtener párrafos con contenido significativo
        parrafos = []
        for p in soup.find_all('p'):
            texto = p.get_text().strip()
            # Filtrar párrafos muy cortos o que parecen ser navegación
            if len(texto) > 50 and not any(palabra in texto.lower() for palabra in ['cookie', 'copyright', 'todos los derechos']):
                parrafos.append(texto)
        
        return '\n'.join(parrafos)
    except Exception as e:
        print(f"Error al procesar URL: {str(e)}")
        return None

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Página de resultados del agrupamiento
@app.route('/cluster', methods=['POST'])
def cluster():
    if request.method == 'POST':
        documents = request.form.getlist('documents')
        
        if len(documents) < 2:
            return "Por favor, ingrese al menos dos documentos."
            
        # Preprocesamiento de documentos
        processed_docs = [preprocess_text(doc) for doc in documents]
        
        # Vectorización
        vectorizer = TfidfVectorizer(
            stop_words=stop_words,
            min_df=2,
            max_df=0.95
        )
        X = vectorizer.fit_transform(processed_docs)
        
        # Determinar número óptimo de clusters
        num_clusters = get_optimal_clusters(X)
        
        # Aplicar KMeans
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(X)
        
        # Obtener keywords por cluster
        cluster_keywords = get_cluster_keywords(vectorizer, kmeans)
        
        # Agrupar documentos
        clustered_documents = {}
        for i, label in enumerate(kmeans.labels_):
            if label not in clustered_documents:
                clustered_documents[label] = []
            clustered_documents[label].append({
                'text': documents[i],
                'processed': processed_docs[i]
            })
            
        return render_template(
            'result.html', 
            clusters=clustered_documents,
            keywords=cluster_keywords
        )

@app.route('/procesar_archivos', methods=['POST'])
def procesar_archivos():
    if 'files' not in request.files:
        return render_template('resultados.html', resultados={
            'error': 'No se subieron archivos',
            'clusters': {},
            'palabras_clave': {}
        })
    
    files = request.files.getlist('files')
    documentos = []
    
    for file in files:
        if file.filename.endswith('.txt'):
            contenido = file.read().decode('utf-8')
            documentos.append(contenido)
    
    if not documentos:
        return render_template('resultados.html', resultados={
            'error': 'No se encontraron archivos válidos',
            'clusters': {},
            'palabras_clave': {}
        })
    
    resultados = agrupador.agrupar_documentos(documentos)
    return render_template('resultados.html', resultados=resultados)

@app.route('/procesar_urls', methods=['POST'])
def procesar_urls():
    urls = request.form.getlist('urls[]')
    if not urls:
        return render_template('resultados.html', resultados={
            'error': 'No se proporcionaron URLs',
            'clusters': {},
            'palabras_clave': {}
        })
    
    documentos = []
    for url in urls:
        texto = extraer_texto_url(url)
        if texto:
            # Dividir el texto en párrafos si solo hay una URL
            if len(urls) == 1:
                parrafos = [p.strip() for p in texto.split('\n') if len(p.strip()) > 50]
                documentos.extend(parrafos[:5])  # Tomar los primeros 5 párrafos
            else:
                documentos.append(texto)
    
    if len(documentos) < 2:
        return render_template('resultados.html', resultados={
            'error': 'No se pudo extraer suficiente texto. Por favor, proporcione más URLs o una URL con más contenido.',
            'clusters': {},
            'palabras_clave': {}
        })
    
    resultados = agrupador.agrupar_documentos(documentos)
    return render_template('resultados.html', resultados=resultados)

@app.route('/analizar_texto', methods=['POST'])
def analizar_texto():
    texto = request.form.get('texto_noticia', '')
    if not texto:
        return render_template('resultados.html', resultados={
            'error': 'No se proporcionó texto para analizar'
        })
    
    resultados = analizador.analizar_texto(texto)
    return render_template('resultados.html', resultados=resultados)

@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'error': str(error),
        'message': 'Ha ocurrido un error en el procesamiento'
    }), 500

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
