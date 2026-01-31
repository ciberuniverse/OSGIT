
from modules.modules import verificar_argumentos, buscar_por_nombres
from modules.modules import buscar_posibles_enlaces, generar_combinaciones
from modules.modules import busqueda_humana, ayuda, iterar_github, banner, response_json
from modules.modules import GREEN, YELLOW, BOLD, RESET
import requests

    
configuracion_valida = verificar_argumentos()
if configuracion_valida["status"] != 200:
    ayuda()

configuracion_valida = configuracion_valida["data"]

try:
    escaneo_web = requests.get(configuracion_valida["url"], timeout=30, allow_redirects=False)

except Exception as err:
    print(f"ERROR: {err}")
    exit(0)

######################################

# Se crea una lista con huellas encontradas en el sitio
# para luego agregarle las busquedas dependiendo si se estipulo eso o no
# en la entrega de parametros
huellas_ = []
if configuracion_valida["human"]:
    huellas_.extend(busqueda_humana(escaneo_web.text))

if configuracion_valida["files"]:
    huellas_.extend(buscar_posibles_enlaces(escaneo_web.text, configuracion_valida["filtro"]))

huellas_.extend(buscar_por_nombres(escaneo_web.text))

##################################

# Se generan las combinaciones para realizar las consultas
querys_list_github = generar_combinaciones(
    list_terms = huellas_,
    configuracion_iter = configuracion_valida["gen_type"],
    iter = configuracion_valida["integraciones"]
)

banner()
# Se itera por cada resultado para obtener los repositorios a traves de las combinaciones
resultados_coincidencias = iterar_github(
    dorks_github = querys_list_github,
    rate_limit_gh_api = configuracion_valida["limite"] or 0,
    terminar_encontrado = configuracion_valida["end"],
    escaneo_profundo = configuracion_valida["deep"],
    limite_paginas = configuracion_valida["limite_paginas"]
)

def return_color(indice_coincidencia: int) -> str:

    if indice_coincidencia == 1:
        return "[ NO PROBABLE ]"
    
    elif indice_coincidencia == 2:
        return f"{BOLD}{YELLOW}[ MEDIUM ]"
    
    return f"{BOLD}{GREEN}[ HIGH ]"


# Si existen resultados se ordenan de mayor probabilidad a menor
# con colores que distinguen la probabilidad de que sea ese repo
# que corre en el backend
if resultados_coincidencias:
    
    print(f"{BOLD}===================[ RESULTADOS ]===================")
    mayor_2_menor = sorted(resultados_coincidencias, key=lambda x: resultados_coincidencias[x], reverse=True)
    for result in mayor_2_menor:

        coincidencia_numero = resultados_coincidencias[result]
        print(f"{return_color(coincidencia_numero)} = {resultados_coincidencias[result]} =>> URL {result}{RESET}")

else:
    response_json(500, "No se logro encontrar ningun resultado asociado a la URL", True)