from models.modelo import AgrupadorDocumentos

def test_agrupamiento():
    agrupador = AgrupadorDocumentos()
    
    documentos = [
        "El precio del petróleo sube por tensiones globales",
        "Nueva vacuna muestra resultados prometedores",
        "Mercados financieros responden a crisis petrolera",
        "Investigadores anuncian avances en vacunación"
    ]
    
    resultados = agrupador.agrupar_documentos(documentos)
    
    # Verificar estructura de resultados
    print("\nEstructura de resultados:", resultados.keys())
    
    if "error" in resultados and resultados["error"]:
        print(f"\nError: {resultados['error']}")
    else:
        print("\nResultados del agrupamiento:")
        for cluster_id, docs in resultados["clusters"].items():
            print(f"\nCluster {cluster_id}:")
            if cluster_id in resultados["palabras_clave"]:
                print("Palabras clave:", ", ".join(resultados["palabras_clave"][cluster_id]))
            for doc in docs:
                print(f"- {doc['texto']}")

if __name__ == "__main__":
    test_agrupamiento()