import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def descargar_recursos_nltk():
    """Descarga todos los recursos necesarios de NLTK"""
    recursos = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'punkt_tab'
    ]
    
    for recurso in recursos:
        print(f"Descargando {recurso}...")
        try:
            nltk.download(recurso)
            print(f"✓ {recurso} descargado correctamente")
        except Exception as e:
            print(f"✗ Error descargando {recurso}: {e}")

if __name__ == "__main__":
    print("Iniciando descarga de recursos NLTK...")
    descargar_recursos_nltk()
    print("Proceso completado")