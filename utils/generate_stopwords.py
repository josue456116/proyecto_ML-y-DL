import pandas as pd
import nltk
from nltk.corpus import stopwords

def generar_stopwords_csv():
    # Descargar stopwords en español
    nltk.download('stopwords')
    
    # Obtener stopwords base
    stop_words = set(stopwords.words('spanish'))
    
    # Agregar palabras específicas para noticias
    palabras_noticias = {
        # Verbos comunes en noticias
        'dice', 'dijo', 'afirmó', 'señaló', 'explicó', 'informó', 'aseguró',
        'comentó', 'manifestó', 'declaró', 'añadió', 'indicó',
        
        # Expresiones temporales
        'ayer', 'hoy', 'mañana', 'ahora', 'mientras', 'durante',
        'año', 'mes', 'semana', 'día',
        
        # Conectores comunes
        'además', 'sin embargo', 'no obstante', 'por otro lado',
        'asimismo', 'también', 'inclusive',
        
        # Palabras de contexto noticioso
        'según', 'fuente', 'fuentes', 'comunicado', 'informe',
        'estudio', 'análisis', 'investigación',
        
        # Lugares comunes
        'país', 'ciudad', 'región', 'zona', 'área', 'sector',
        
        # Cifras y medidas
        'aproximadamente', 'cerca', 'más', 'menos', 'varios',
        'algunos', 'millones', 'miles'
    }
    
    # Unir todas las stopwords
    stop_words.update(palabras_noticias)
    
    # Agregar palabras compuestas correctamente
    palabras_compuestas = {
        'sin embargo',
        'por otro lado',
        'no obstante',
        # Separar en palabras individuales
        'sin', 'embargo', 'por', 'otro', 'lado', 'no', 'obstante'
    }
    
    stop_words.update(palabras_compuestas)
    
    # Crear DataFrame
    df_stopwords = pd.DataFrame(sorted(list(stop_words)), columns=['palabra'])
    
    # Guardar CSV
    output_path = 'data/spanish_stopwords.csv'
    df_stopwords.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Archivo CSV creado exitosamente en: {output_path}")
    print(f"Total de stopwords: {len(df_stopwords)}")

if __name__ == "__main__":
    generar_stopwords_csv()