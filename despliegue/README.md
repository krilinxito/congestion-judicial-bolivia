# Despliegue: la página pública

La página responde la pregunta de quien tiene un caso: elige materia, tipo de proceso y lugar, y ve **cuánto tarda
hoy la fila** de causas pendientes (pendientes ÷ resueltas × 365, datos del Anuario 2023) y **si es probable que crezca
el año siguiente** (el modelo de 5 variables con stock heredado = pendientes al cierre de 2023 y los ingresos de 2023).
Tiene además una tabla de prioridades para quien gestiona juzgados.

Esta carpeta es todo lo que hace falta para publicarla en un VPS. Es independiente del
resto del proyecto: se puede copiar sola al servidor.

```
despliegue/
  sitio/                   la página que ve el usuario
    index.html             estructura
    estilos.css            diseño (colores de la UMSA, tema claro y oscuro)
    prediccion.js          la consulta y el modelo en JavaScript (variables, one-hot, 200 árboles, curva S)
    modelo/modelo_5var.json  los árboles exportados por notebooks/22_despliegue.ipynb
    datos/procesos.json    los 1.240 procesos con nombres legibles, de notebooks/23_sitio_publico.ipynb
    img/umsa.png           escudo
  nginx.conf               servidor de archivos: compresión, cabeceras de seguridad y /salud
  Dockerfile               imagen nginx sin privilegios (puerto 8080)
  docker-compose.yml       el servicio, con reinicio automático y chequeo de salud
```

**No hay Python en el servidor.** El modelo corre en el navegador de quien visita la página: nginx solo entrega
archivos y no recibe ni guarda lo que se consulta. Al abrirse, la página recalcula las 1.240 probabilidades y las
compara con las de Python (sello «1.240 / 1.240 coinciden» en «Detalles técnicos»).

## Publicar en el VPS

Requisitos en el VPS: Docker con el complemento Compose (`docker compose version`).

```bash
# 1. Llevar la carpeta al VPS (o clonar el repositorio y entrar a despliegue/)
scp -r despliegue usuario@IP-DEL-VPS:~/prediccion-mora
ssh usuario@IP-DEL-VPS
cd ~/prediccion-mora

# 2. Construir y levantar
docker compose up -d --build

# 3. Comprobar
docker compose ps                      # el estado debe decir "healthy"
curl http://localhost:8080/salud       # responde: ok
```

La página queda en `http://IP-DEL-VPS:8080`. Para usar otro puerto: `PUERTO=80 docker compose up -d --build`
(o un archivo `.env` con `PUERTO=80`). Si el puerto no responde desde afuera, abrirlo en el firewall
(por ejemplo, `sudo ufw allow 8080/tcp`).

### Con dominio y HTTPS

Si el VPS ya tiene un proxy inverso (Caddy, Traefik o nginx), dejar el contenedor en el puerto 8080 y apuntar el
dominio a `http://127.0.0.1:8080`. Con Caddy basta:

```
prediccion.midominio.com {
    reverse_proxy 127.0.0.1:8080
}
```

## Actualizar el modelo

1. Volver a ejecutar `notebooks/22_despliegue.ipynb`: escribe el JSON en `web/modelo/` y la misma copia en
   `despliegue/sitio/modelo/`, y verifica que sean idénticas.
2. Volver a ejecutar `notebooks/23_sitio_publico.ipynb`: recalcula con ese modelo las probabilidades del año siguiente
   y escribe `despliegue/sitio/datos/procesos.json`.
3. Hacer `git push` (Dokploy vuelve a publicar) o, a mano, en el VPS: traer los archivos y `docker compose up -d --build`.

## Probar sin Docker

```bash
cd despliegue/sitio
python -m http.server 8000             # abrir http://localhost:8000
```

Al cargar, la sección «Autoverificación contra Python» debe decir **20 / 20 coinciden**.

## Seguridad

- La imagen `nginxinc/nginx-unprivileged` corre como usuario sin privilegios.
- El contenedor es de solo lectura (`read_only`), sin capacidades de Linux (`cap_drop: ALL`) y sin escalada de privilegios.
- nginx envía una política de contenido (CSP) que solo permite los archivos propios y las fuentes de Google, y oculta
  su versión.
