from sys import argv
import requests, bs4, time, json
from urllib.parse import urlparse
from itertools import combinations_with_replacement

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"

# Configuramos la session para mantener el keep alive
session_find = requests.session()

# Configuramos nuestras variables para empezar a buscar
api_endpoint = "https://api.github.com/search/code"

def response_json(code: int, data: str, log: bool = False) -> dict | None:
    """Se usa como log usando el parametro log en true"""

    if log:

        if code == 200:
            indic = f"{BOLD}{GREEN}PASS"

        elif code == 500:
            indic = f"{BOLD}{RED}ERROR"
        
        elif code == 0:
            indic = "INFO"

        else:
            indic = f"{BOLD}{YELLOW}WARNING"

        print(f"[ {indic} ] {data}{RESET}")
    
    return {"status": code, "data": data}

def formatear_url(url: str) -> str:

    if "://" in url:
        url = urlparse(url).path

    if "?" in url:
        url = url.split("?")[0]

    url = url.split("/")
    return url[len(url) - 1]

def banner():

    print(f"""{CYAN}{BOLD}
            .      .            .     .            
           . .-.  .-           -.   -...           
           ..  -+. ..--++++--.....--  .            
            .    -- .-+++++++-..-+.   -            
            .  .-+++-++-++-+++++-+-.  .            
             ..+--+++++++--+-+++---+..             
              --     -++--+++-.    +-              
              +. .++-.   .   .-++  --     I C4N S33 Y0U         
             .--  -++-  -+-  -++-  -+.             
             .-+-.   .--   --.   .++-.             
              .--+-.-----.-+---..--..              
               .++-  . .   ...  ---      -.        
                  -+-.      ..---     .++-         
                      ------.        . --.         
                  .-.         --.      -           
                  --+--     --++.      -.          
                . --.+-+-.-+++.+. .     -          
               ++-.+ --+.-.++-.+.--+    +          
               +-. . -++   -+- . .--   --          
                -    .+-   ++.    .  .-+           
                      -+   ++.       .             
               .--. .---. .+--. --.-               
{RESET}
            {MAGENTA}------------------------------{RESET}
            {RED}{BOLD}OSGIT => THE CAT THAT (ALMOST){RESET}
                     {RED}{BOLD}SEES EVERYTHING{RESET}
            {MAGENTA}------------------------------{RESET}
                {RESET}{BLUE}{BOLD}DEVELOPER = Ciberuniverse
                {RESET}{BOLD}         </>
        """)

def ayuda():
    banner()

    filename = max(argv[0].split("/"))

    print(f"""{YELLOW}{BOLD}Uso:{RESET}
    python {filename} --URL <http://sitio.com> [opciones]

{YELLOW}{BOLD}Opciones:{RESET}
    {GREEN}-A{RESET}          Activa búsqueda combinada (huellas + archivos)
    {GREEN}-f{RESET}          Busca únicamente por nombres de archivos
    {GREEN}-h{RESET}          Busca únicamente por huellas en comentarios
    {GREEN}-I <N>{RESET}      Número de coincidencias por búsqueda (AND)
    {GREEN}-l <N>{RESET}      Límite de consultas a la API
    {GREEN}-g <tipo>{RESET}   Tipo de generación de combinaciones:
                "normal" | "itertools"
    {GREEN}-lP <N>{RESET}     Limite de busquedas por paginas en busquedas profundas.
    {GREEN}--filter X{RESET}  Lista de extensiones a filtrar (ej: .js,.php,.html)
    {GREEN}--no-end {RESET}   No finaliza automaticamente cuando encuentra los repos
                mas probables.
    {GREEN}--deep {RESET}     Itera sobre todos los resultados de GitHub (Lento)

    {RED}{BOLD}--api-key {RESET}  Tu api key de GitHub Api. Puedes conseguirla en:
    
                {BLUE}https://github.com/settings/personal-access-tokens{RESET}

                Ahi deberas crear y configurar un token unicamente de lectura para
                luego usarlo con el parametro --api-key.

{YELLOW}{BOLD}Ejemplos:{RESET}
    python {filename} --api-key TU_TOKEN --URL http://example.com -A -I 2
    python {filename} --api-key TU_TOKEN --URL http://example.com -f --filter .js,.css
    python {filename} --api-key TU_TOKEN --URL http://example.com -h -l 10 -g itertools

{MAGENTA}------------------------------{RESET}
""")
    exit(0)

def verificar_argumentos():

    # Funcion que obtiene el valor que estipulo el usuario en un parametro
    def obtener_valor(parametro: str) -> str:
        return argv[argv.index(parametro) + 1]

    # Parametros utilizados en la TOOL
    parametros = ["-A", "-f", "-h", "-I", "-l", "-g", "-lP", "--filter", "--no-end", "--deep"]
    """
        -A: Busca tanto huellas de comentarios como filtrado por archivos.
        -f: Busca unicamente por nombres de archivos.
        -h: Busca unicamente por huella de comentarios.
        -I: Cantidad de coincidencias por busqueda (AND's).
        -l: Cantidad de consultas que usara la api.
        -g: Tipo de generacion de combinaciones "normal" | "itertools".
        -lP: Limite de busquedas por paginas en busquedas profundas.
        --filter: Archivos a filtrar.
        --no-end: No finaliza el programa cuando se encuentra la coincidencia maxima.
        --deep: Itera sobre todos los resultados de GitHub (Lento).
    """

    configuracion = {
        "human": False,
        "files": False,
        "integraciones": 2,
        "limite": 0,
        "filtro": ["."],
        "gen_type": "normal",
        "end": True,
        "deep": False,
        "limite_paginas": 10
    }
    
    if "--api-key" not in argv:
        return response_json(400, "No estas enviando ninguna api key.")

    # Si la url no existe se retorna error
    if "--URL" not in argv:
        return response_json(400, "El parametro --URL no existe")
    
    url = obtener_valor("--URL")
    if any(x not in url for x in ["://", "http"]):
        return response_json(400, "La url no cumple con el formato esperado.")

    configuracion["url"] = url

    # Si es que no se estipulo ningun argumento retorna error
    if all(p not in argv for p in parametros):
        return response_json(400, "Menu")
    
    # Si existe cantidad de limite se configura
    if "-I" in argv:
        try:
            configuracion["integraciones"] = int(obtener_valor("-I"))

        except Exception as err:
            return response_json(500, f"Menu {err}")

    # Si existe limite de consultas a api, se especifica
    if "-l" in argv:
        try:
            configuracion["limite"] = int(obtener_valor("-l"))

        except Exception as err:
            return response_json(500, f"Menu {err}")

    if "--filter" in argv:
        configuracion["filtro"] = obtener_valor("--filter").split(",")

    if "--no-end" in argv:
        configuracion["end"] = False
    
    if "--deep" in argv:
        configuracion["deep"] = True

    if "--api-key" in argv:
        session_find.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {obtener_valor('--api-key')}"
        })

    if "-g" in argv:
        configuracion["gen_type"] = obtener_valor("-g")

    # Se configuran las formas de escanear
    if "-f" in argv:
        configuracion["files"] = True

    if "-h" in argv:
        configuracion["human"] = True

    if "-A" in argv:
        configuracion["files"] = True
        configuracion["human"] = True

    if "-lP" in argv:
        try:
            configuracion["limite_paginas"] = int(obtener_valor("-lP"))

        except Exception as err:
            return response_json(500, f"Menu {err}")

    # Retorna la configuracion estipulada
    return response_json(200, configuracion)

def busqueda_humana(html_source: str) -> set:

    lines_html = html_source.split("\n")
    results_ = set()

    search_line_term = ["//", "<!--"]

    for line in lines_html:

        if "://" in line:
            continue

        if all(x not in line for x in search_line_term):
            continue

        if not line:
            continue
        
        results_.add(line.strip())
    
    return results_

def buscar_posibles_enlaces(html_source: str, filtro: list = ["."]) -> set:

    web_parse = bs4.BeautifulSoup(html_source, "html.parser")

    search_terminos = {
        "img": "src",
        "script": "src",
        "link": "href",
        "iframe": "src",
    }

    results_ = set()
    for etiqueta, atributo in search_terminos.items():

        for tag_line in web_parse.find_all(etiqueta):

            path = tag_line.get(atributo)
            if not path:
                continue
            
            if "://" in path and len(path.split("/")) <= 4:
                continue
            
            if all(ext not in path for ext in filtro):
                continue

            path = formatear_url(path)

            results_.add(path)

    return results_

def buscar_por_nombres(html_source: str) -> set:

    # Se parsean las lineas de html 
    web_parse = bs4.BeautifulSoup(html_source, "html.parser")

    # Se especifican los terminos de tags a buscar
    search_terminos = {
        "input": "name",
        "img": "alt"
    }

    results_ = set()
    results_.add(web_parse.find("title").get_text(strip=True))

    # Por cada elemento a buscar se obtiene la informacion y se guarda en la variable
    # result_ para retornar
    for etiqueta, atributo in search_terminos.items():

        for tag_line in web_parse.find_all(etiqueta):
            results_.add(tag_line.get(atributo))
    
    # Se retornan los datos en un iterable set
    return results_

def generar_combinaciones(list_terms: set, configuracion_iter: str = "normal", iter: int = 2) -> list[str]:

    # Se generan todas las combinaciones posibles para probar (no recomendable)
    if configuracion_iter == "itertools":
        
        combinations = list(combinations_with_replacement(list_terms, iter))
        return [ " AND ".join(x) for x in combinations ]

    
    #### Si el tipo de configuracion es una combinacion simple se usa, en esta 
    # se iteran combinando el archivo o comentario + 1 por la cantidad de iteraciones
    if configuracion_iter == "normal":

        # Se configura la maxima iteracion por rango (el tamaño de la lista de huellas)        
        max_iter = len(list_terms)
        
        # Se define la variable de retorno que contiene las consultas
        return_querys = []

        # Se generan las consultas mediante el metodo simple, asignandola la pareja que
        # sigue dependiendo de el numero de iteracion correspondiente
        for x in range(0, max_iter):
            
            # Se intenta crear la query, en caso de error se muestra en pantalla y termina el bucle
            try:

                querys: list = []
                for i in range(0, iter):
                    try:
                        querys.append(list_terms[x + i])
                    except:
                        querys.append(list_terms[0])

                return_querys.append(" AND ".join(querys))

            except Exception as err:
                print(err)
                return return_querys
        
        # Retorna el resultado de las querys generadas
        return return_querys

def __obtener_repositorios__(response_json: dict) -> set:
    # Funcion encargada de iterar los resultados de las respuestas de github y retornar
    # los repositorios encontrados

    result_git = set()

    for repo in response_json["items"]:
        result_git.add(repo["repository"]["html_url"])
    
    return result_git

def __get2_github__(params: dict) -> dict:

    try:
        # Se realiza la solicitud get con los parametros personalizados a github
        result = session_find.get(api_endpoint, params=params)
        return result.json()
    
    # Aun no se como se comporta esto en caso de error (referente al comportamiento en si del programa)
    except Exception as err:
        response_json(500, err, True)

def __check_aviable_gh__(params) -> dict:
    """
    Funcion encargada de verificar si es que, la solicitud llego con lo esperado.
    de no ser asi, se crea un time sleep de 60 segundos en donde se
    vuelve a intentar la solicitud 5 veces antes de salir y mostrar el problema.

    En caso de funcionar, retorna los valores normales.
    """

    # Se envia la solicitud a nuestro servidor
    result = __get2_github__(params)

    # Se verifica con un limite de 5 intentos fallidos en conexion con la api para 
    # salir de el programa indicando que algo esta mal
    cont_timeout = 1
    while True:

        # Si el contador de time out llego al limite se indica que algo esta mal
        # y termina la ejecucion del programa
        if cont_timeout >= 5:
            print(f"Algo esta pasando en el servidor: {result}")
            exit(0)

        # Si la respuesta no contiene lo que deberia de responder en una respuesta exitosa
        # se ejecuta un time out para luego ejecutar la misma solicitud
        if "total_count" not in result:

            response_json(400, "TIME SLEEP DE 60 SEGUNDOS EN CURSO", True)

            try:
                time.sleep(60)
            except:
                return result

            result = __get2_github__(params)

        # En caso de no, se sale del bucle para retornar los valores
        else:
            break

        cont_timeout += 1

    return result

def dorking_github(dork_query: str, escaneo_profundo: bool = False, limit_page: int = 0) -> dict:

    response_json(0, F"QUERY => {dork_query}", True)

    parametros = dict()
    parametros["q"] = dork_query
    parametros["per_page"] = 100
    
    result = __check_aviable_gh__(parametros)

    if "items" not in result or not result["items"]:
        return

    result_git = __obtener_repositorios__(
        response_json = result
    )

    # Si la configuracion de escaneo profundo esta activa
    if escaneo_profundo:

        # Se calcula el total de repositorios dividiendo la cantidad por pagina
        total_pages = round(result["total_count"] / 100)

        # En caso de solo ser una pagina se retorna el resultado actual, ya que este
        # es la primera pagina
        if total_pages <= 1:
            return result_git
        
        # Se itera por la cantidad de paginas disponibles a iterar
        for page_num in range(2, total_pages + 1):

            # Se especifica el numero de pagina y se envia la solicitud a github
            parametros["page"] = page_num
            response_json(0,f"DEEP_QUERY => {parametros['q']}", True)

            result = __check_aviable_gh__(parametros)

            # Si la consulta no contiene resultados se salta a la siguiente iteracion
            if "items" not in result or not result["items"]:
                continue
            
            # Se obtienen los repositorios que coincidieron con la busqueda y se actualiza la variable del resultado
            result_git_tmp = __obtener_repositorios__(result)
            result_git.update(result_git_tmp)

            # Si se supera el limite de sub busquedas especificadas por el usuario se retornan los resultados
            if limit_page and page_num > limit_page:
                return result_git
            
    return result_git

def iterar_github(
        dorks_github: list[str],
        rate_limit_gh_api: int = 0,
        terminar_encontrado: bool = True,
        escaneo_profundo: bool = False,
        limite_paginas: int = 0
    ) -> dict:

    resultados_con_coincidencias: dict[int] = dict()

    idx_rate_limit = 1

    # Se ejecuta el codigo y cuando hay un error se devuelve lo que hay en la variable
    try:

        # Por cada dork generado se realizara una solicitud a github buscando coincidencias
        for x in dorks_github:

            # Se buscan y obtienen los resultados para agregar un diccionario de urls obtenidas            
            results_git = dorking_github(
                dork_query = x,
                escaneo_profundo = escaneo_profundo,
                limit_page = limite_paginas
            )

            # Si el usuario agrego un limite de intentos se le suma uno al contador
            if rate_limit_gh_api:
                idx_rate_limit += 1 

            # Si el contador llego al limite estipulado por el usuario se retornan los resultados
            if rate_limit_gh_api and idx_rate_limit >= rate_limit_gh_api:
                return resultados_con_coincidencias

            # Si no hay resultados se continua
            if not results_git:
                continue
            
            # Por cada repositorio encontrado en github se registran en el diccionario de retorno
            # el cual tiene un formato de cuantas veces aparece en busquedas:
            """
                {
                    "https://www.github.com/ciberuniverse/osgit": 10,
                    "https://www.github.com/akakiller/mikaware": 4,
                    ...
                }
            """
            for git_ in results_git:
                
                if git_ not in resultados_con_coincidencias:
                    resultados_con_coincidencias[git_] = 1
                    continue
                
                resultados_con_coincidencias[git_] += 1
                if resultados_con_coincidencias[git_] >= 3:
                    
                    if terminar_encontrado:
                        return resultados_con_coincidencias
        
    except Exception as err:
        return resultados_con_coincidencias

    return resultados_con_coincidencias