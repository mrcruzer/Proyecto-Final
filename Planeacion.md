# Google / Yelp

La idea de este documento es ser el borrador para la definición de la estructura del proyecto grupal.

<br>

## Contexto:

La industria restaurantera ha tenido un crecimiento interesante en los Estados Unidos, principalmente la que se refiere a la comida asiática, que ha tenido mayor popularidad debido al uso de especias y picantes, así como al creciente numero de inmigrantes y el espíritu aventurero del paladar norteamericano. En este sentido,  fuimos contratados por el grupo restaurantero de comida japonesa, que desea un análisis detallado de la opinión de los usuarios, utilizando análisis de sentimientos, conveniencia de lugares para nuevos locales, sistemas de recomendación para el usuario basados en experiencias previas.

Yelp - es una plataforma de reseñas y la información que tenemos disponible a través de cinco archivos es:
* busines.pkl (información del comercio):
    * Id del negocio.
    * Nombre del negocio.
    * Ubicación del negocio (cols con dirección, estado, C.P., coordenadas).
    * Rating en estrellas (decimal .5).
    * Número de reseñas.
    * Si está cerrado.
    * Diccionario atributos del negocio(p.ej. estacionamiento, valet, calle.)
    * Lista catergorías del negocio (tipo de comida).
    * Horarios.

* review.json (contiene las reseñas completas):
    * Id de reseña.
    * Id usuario.
    * Id del negocio.
    * Puntaje en estrellas (entero).
    * Fecha (texto).
    * Reseña completa.
    * Numero de votos por tipo de reseña (cols util, graciosa, cool).

* user.parquet (información del usuario):
    * Id de usuario.
    * Nombre del usuario.
    * Número de reseñas.
    * Fecha de creación del usuario.
    * Id de usuarios amigos.
    * Numero de votos por tipo (cols util, graciosa, cool) por el usuario.
    * Número de fans que tiene el usuario.
    * Lista de años en los que el usuario fue miembro elite.
    * Promedio del valor de las reseñas.
    * Total de cumplidos recibidos por el usuario (cols "hot", varios, por el perfil, "cute", listas, notas, planos, cool, graciosos, escritos, en foto).

* checkin.json (Registros en el negocio):
    * Id del negocio.
    * Lista de fechas separadas por coma.

* tip.json (Consejos escritos por el usuario):
    * Texto del tip.
    * Fecha en que se escribió.
    * Total de cumplidos.
    * Id del negocio.
    * Id del usuario.

Google Maps - contiene información de los negocios a partir de los sigientes archivos:
* Metadata_sitios. 11 archivos con:
    * Nombre del negocio.
    * Dirección del negocio.
    * Id de mapa.
    * Descripción.
    * Latitud.
    * Longitud.
    * Categoría.
    * Promedio de calificación.
    * Número de reseñas.
    * Precio.
    * Horarios.
    * Diccionario atributos del negocio.
    * Estado de actividad (p.ej. cierra en 30 minutos).
    * Resultados aproximados (podría ser otro id de reseña similar, requiere exploración).
    * Url.

* Review-estados. contiene la información de las reseñas de los 51 estados:
    * Id usuario.
    * Nombre de Usario.
    * Fecha (verificar el formato).
    * Texto de la reseña.
    * Imágenes.
    * Diccionario Respuesta. con fecha y texto de la respuesta.
    * Id de mapa.


Con esta información podemos decir que se tienen bastantes elementos para analizar y sacar correlación entre los mismos datasets.

<br>

## Lineas investigación, objetivos y actividades.

* Disponibilización de la información.
    * Obtener los datasets a trabajar:
        * Crear bases de datos.
        * Extraer data estática y cargarla en la base de datos.
        * Mediante webscrapping completar datos faltantes necesarios del dataset.
    * Limpiar y transformar los datasets:
        * Eliminar columnas repetidas.
        * Eliminar filas repetidas.
        * Eliminar registros que no se vayan a utilizar (negocios o reviews que no sean de/a restaurants)
        * Normalizar los campos a utilizar
        * Cruzar los dataset de negocios de Google y yelp y juntarlos en una sola tabla (si hay coincidencia normalizar)
        * En caso de ser posible (por la reducción de la información) juntar todas las reviews en una sola tabla.
        * Crear tabla con información relevante de los usuarios (id, estado y condado)
        * Tratar valores nulos.
        * Tratar outliers.
        * Noramlizar valores.
        
        <br>

* Análisis de sentimientos. Correlación entre los tipos de comentarios con las calificaciones de los locales.
    * Identificar las palabras o frases más comunes utilizadas en las reseñas positivas y negativas, y analizar su impacto en la percepción general del negocio o servicio (correlación con la calificación).
        * Preprocesamiento de datos para eliminar ruido, caracteres extraños palabras irrelevantes y errores ortográficos.
        * Identificar las palabras más utilizadas para cada una de las calificaciones.
        * A partir de las palabras identificar los temas más relevantes, p.ej. calidad de servicio, comida, ubicación, entre otros que se mencionen más en las distintas calificaciones.
    * Elaborar un reporte con las áreas de oportunidad que la gente considera más relevantes para el sector restaurantero en general.
        * Visualizar los resultados, a partir de gráficas o mapas, que muestren los temas más recurrentes cuando las califiaciones son buenas así como cuando las calificaciones son malas.

    <br>

* Analisis de atributos. Correlación entre atributos y puntuaciones.
    * Identificar los atributos que mayor impacto tienen en la calificación del usuario.
        * Armar tabla con los atributos como campos, las valoraciones (1 a 5) como registros y cantidad de veces que aparecen como los valores.
        * Armar distintas métricas que nos indiquen porcentualmente cuanto aparecen los atributos en base a cada puntuación.

    * Elaborar un reporte de recomendación sobre las características más elogiadas de los restaurantes contra las negativas que tiene el grupo restaurantero.
        * Visualizar mediante streamlit y/o PowerBI los resultados obtenidos.
<br>

*  Sistema de recomendación al cliente basado en experiencias previas.
    * Diseñar un modelo de aprendizaje supervisado que se ajuste a las preferencias a partir del ID del usuario.
        * EDA
        * Optimización de parámetros.
        * Probar algoritmos - cross validation.
        * Intanciar modelo elegido.
        * Entrenar modelo.
        * Testear modelo.
        * Evaluar métricas.
    * Elaborar una aplicación (deploy) que permita al usuario ingresar su id y le sugiera algún restaurante a partir de lo que calificó. Complementar con buscador que informe los restaurants mejor puntuados al buscar un tipo de restaurant.
        * Diseñar la aplicación.
        * Cargar el modelo en la aplicación.
        * Crear programa que identifique el texto ingresado para recomendar.
        * Hacer pruebas.
