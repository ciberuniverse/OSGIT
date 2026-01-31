# **OSGIT**

Este README busca ofrecer una documentación sencilla pero clara sobre **OSGIT**, una herramienta que nació a partir de la necesidad de recolectar información de forma pasiva desde páginas o servicios web.  

La idea es obtener datos sin interacción directa —como corresponde al espíritu del **OSINT**— pero, personalmente, me demoraba bastante usando *GitHub dorks*. De hecho, pocos saben siquiera que existen.  

Este script combina **GitHub dorks**, iteración de resultados y un sistema de **probabilidad** para determinar qué repositorios podrían estar relacionados con el backend de un sitio web.

![Imagen](https://repository-images.githubusercontent.com/1146420863/3d12de9b-93cf-4ed2-a365-64f63ea30425)

---

## ¿Como funciona el script?

Imagina que tienes 100 puertas y sabes que detrás de una de ellas alguien pidió un paquete. Si tú tienes 3 paquetes, los entregas a las 3 puertas donde encuentras coincidencias y así identificas a los solicitantes. Creo que no fue muy buen ejemplo
que digamos pero, en términos más simples:

- El programa genera combinaciones de búsqueda basadas en **huellas del código fuente** de una web:
  - Comentarios
  - Nombres de variables
  - Archivos
  - Otros elementos identificables

- Luego realiza búsquedas únicas en GitHub.
- Cuenta cuántas veces aparecen esas coincidencias a lo largo de las iteraciones.
- Finalmente clasifica los resultados en:

### [ HIGH ]  
Altamente probable que el repositorio esté relacionado con el backend del sitio analizado.

### [ MEDIUM ]  
Puede ser una versión antigua, un fragmento del proyecto o código subido por un colaborador en algún momento.

### [ NO PROBABLE  ]
Poco probable que tenga relación. Serán la mayoría, pero si obtienes pocos resultados, vale la pena revisarlos.

> **Nota:** pueden existir **muchos falsos positivos**.

---

## Parámetros de uso

A continuación copiare y pegare el menú de ayuda de la herramienta:

```
Uso:
    python osgit.py --URL <http://sitio.com> [opciones]

Opciones:
    -A              Activa búsqueda combinada (huellas + archivos)
    -f              Busca únicamente por nombres de archivos
    -h              Busca únicamente por huellas en comentarios
    -I <N>          Número de coincidencias por búsqueda (AND)
    -l <N>          Límite de consultas a la API
    -g <tipo>       Tipo de generación de combinaciones:
                        "normal" | "itertools"
    -lP <N>         Límite de búsquedas por página en búsquedas profundas
    --filter X      Lista de extensiones a filtrar (ej: .js,.php,.html)
    --no-end        No finaliza automáticamente al encontrar los repos
                    más probables
    --deep          Itera sobre todos los resultados de GitHub (Lento)

    --api-key       Tu api key de GitHub Api. Puedes conseguirla en:

                    https://github.com/settings/personal-access-tokens

                    Ahi deberas crear y configurar un token unicamente de lectura para
                    luego usarlo con el parametro --api-key.

Ejemplos:
    python osgit.py --api-key TU_TOKEN --URL http://example.com -A -I 2
    python osgit.py --api-key TU_TOKEN --URL http://example.com -f --filter .js,.css
    python osgit.py --api-key TU_TOKEN --URL http://example.com -h -l 10 -g itertools
```

---

## Explicación de un caso práctico

Ejemplo:

```
python osgit.py --api-key TU_TOKEN --URL http://example.com -f --filter .js,.css
```

Esto indica al programa que:

- Este usando la api key creada en [GitHub Profile](https://github.com/settings/personal-access-tokens)
- Escanee el código fuente de `example.com`.
- Considere únicamente **archivos** (`-f`).
- Tome en cuenta solo las extensiones **.js** y **.css** (`--filter`).

---

## Estado actual del proyecto

La herramienta es mas que nada una **prueba de concepto** y la modularidad puede mejorar, pero el código está ampliamente comentado y es fácil de seguir.  

Planeo mejorar las búsquedas en el futuro y estoy abierto a sugerencias o aportes.
