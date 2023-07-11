#Importo pandas para poder traer el archivo csv ya con las catacterícticas del cliente
import pandas as pd

# Cargar el archivo CSV en un DataFrame
combined_df = pd.read_csv('combined_movies.csv')

#importo la librerías de la APIs
from fastapi import FastAPI,  APIRouter

app = FastAPI()
#Creo una función para encontrar el idioma original de la película y año de estreno

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a nuestra api de recomendacion de películas!"}


@app.get("/peliculas_idioma")
def peliculas_idioma(idioma: str, año: int):
    total = 0
    for df in [combined_df]:
        mask = (df['original_language'] == idioma) & (df['release_year'] == año)
        total += len(df[mask])
    
    return {"total_peliculas": total}

#Se genera una función que retorne en base al nombre de la película indique duración y fecha de lanzamiento
@app.get("/peliculas_duracion")
def peliculas_duracion(pelicula: str):
    for df in [combined_df]:
        mask = df['original_title'] == pelicula
        pelicula_df = df[mask]
        if not pelicula_df.empty:
            duracion = pelicula_df['runtime'].values[0]
            año = pelicula_df['release_year'].values[0]
            return {"Duración": duracion, "Año": año}
    
    return {"message": "Película no encontrada"}

#Genero una función que en base a la franquicia perteneciente indique la cantidad de películas, ganancias totales
#y promedio

@app.get("/franquicia")
def franquicia(Franquicia: str):
    for df in [combined_df]:
        mask = df['belongs_to_collection'].str.contains(Franquicia, na=False)
        franquicia_df = df[mask]
        if not franquicia_df.empty:
            cantidad_peliculas = len(franquicia_df)
            ganancia_total = franquicia_df['revenue'].sum()
            ganancia_promedio = franquicia_df['revenue'].mean()
            return {
                "Franquicia": Franquicia,
                "Cantidad de películas": cantidad_peliculas,
                "Ganancia total": ganancia_total,
                "Ganancia promedio": ganancia_promedio
            }
    
    return {"message": "Franquicia no encontrada"}

#Se realiza una función que según país indique la cantidad de peliculas producidas en el mismo.

@app.get("/peliculas_pais")
def peliculas_pais(Pais: str):
    for df in [combined_df]:
        mask = df['production_countries'].str.contains(Pais, na=False)
        peliculas_pais_df = df[mask]
        if not peliculas_pais_df.empty:
            cantidad_peliculas = len(peliculas_pais_df)
            return {
                "País": Pais,
                "Cantidad de películas": cantidad_peliculas
            }
    
    return {"message": "País no encontrado"}

#Se ingresa el productor e indica  el revunue total y la cantidad de peliculas que realizo.
@app.get("/productoras_exitosas")
def productoras_exitosas(Productora: str):
    for df in [combined_df]:
        mask = df['production_companies'].str.contains(Productora, na=False)
        productora_df = df[mask]
        if not productora_df.empty:
            cantidad_peliculas = len(productora_df)
            revenue_total = productora_df['revenue'].sum()
            return {
                "Productora": Productora,
                "Revenue total": revenue_total,
                "Cantidad de películas": cantidad_peliculas
            }
    
    return {"message": "Productora no encontrada"}

#Se genera una función en el cual se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo 
# devolver el éxito del mismo medido a través del retorno. 
# Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, retorno individual, 
# costo y ganancia de la misma, en formato lista.

@app.get("/get_director")
def get_director(nombre_director: str):
    director_movies = []
    for df in [combined_df]:
        mask = df['crew'].str.contains(nombre_director, na=False)
        director_df = df[mask]
        if not director_df.empty:
            movies = director_df[['original_title', 'release_date', 'revenue', 'budget']]
            movies = movies.rename(columns={'original_title': 'Título', 'release_date': 'Fecha de lanzamiento', 'revenue': 'Retorno', 'budget': 'Costo'})
            movies['Ganancia'] = movies['Retorno'] - movies['Costo']
            director_movies.append(movies)
    
    if director_movies:
        return {
            "Director": nombre_director,
            "Películas": director_movies
        }
    
    return {"message": "Director no encontrado"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#Genero el modelo de recomendacion de peliculas en la Api

import nltk

nltk.download('punkt')

# Obtener los títulos de las películas como una lista de conjuntos de palabras clave
titles = [set(title.split()) for title in combined_df['title'].astype(str).tolist()]

# Función para calcular la similitud de Jaccard entre dos conjuntos de palabras clave
def calculate_jaccard_similarity(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

# Función para obtener recomendaciones basadas en un título específico
def get_recommendations_based_on_title(title, titles, n_recommendations=5):
    # Encontrar el conjunto de palabras clave del título de referencia
    reference_set = set(title.split())

    # Calcular la similitud de Jaccard entre el título de referencia y todos los demás títulos
    similarity_scores = [calculate_jaccard_similarity(reference_set, title_set) for title_set in titles]

    # Obtener los índices de los títulos más similares
    top_indices = sorted(range(len(similarity_scores)), key=lambda i: similarity_scores[i], reverse=True)[1:n_recommendations+1]

    # Obtener los títulos recomendados
    recommended_titles = [combined_df['title'].iloc[index] for index in top_indices]

    return recommended_titles

# Ejemplo de uso: obtener recomendaciones para un título específico
title = "The Dark Knight"
recommended_titles = get_recommendations_based_on_title(title, titles)
print(recommended_titles)