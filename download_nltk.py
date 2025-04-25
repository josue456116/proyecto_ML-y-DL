import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_resources():
    """Descarga todos los recursos necesarios de NLTK"""
    recursos = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger'
    ]
    
    for recurso in recursos:
        print(f"Descargando {recurso}...")
        try:
            nltk.download(recurso, quiet=True)
            print(f"✓ {recurso} descargado correctamente")
        except Exception as e:
            print(f"✗ Error descargando {recurso}: {str(e)}")

if __name__ == "__main__":
    print("Iniciando descarga de recursos NLTK...")
    download_nltk_resources()
    print("Proceso completado")