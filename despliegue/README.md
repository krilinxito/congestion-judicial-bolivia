# Despliegue: la página pública

La página responde la pregunta de quien tiene un caso: **¿cuánto va a tardar?** Se elige materia, tipo de proceso y
lugar, y se ve:

- **el tiempo estimado para un caso que entra ahora**, con un rango probable: el modelo de 5 variables (notebook 22)
  con la fila que espera = pendientes al cierre de 2023, los ingresos y los juzgados de 2023;
- **lo que tardaba la fila en 2023**, medido sin modelo (pendientes ÷ resueltas × 365);
- **el ritmo de su materia** (resueltas 2020-2023) y **la historia del país 2007-2023**, con la comprobación de que el
  tiempo estimado se parece a lo que la fila de verdad tardó en vaciarse;
- el mismo trámite en otros lugares y una tabla de dónde un caso nuevo tardaría más, para quien gestiona juzgados.

Publicada en https://proyanalisis.maxi42.space/ (Dokploy). El servicio de Docker conserva el nombre `prediccion-mora`
de la primera versión para no romper esa publicación.

Esta carpeta es todo lo que hace falta para publicarla en un VPS. Es independiente del
resto del proyecto: se puede copiar sola al servidor.

```
despliegue/
  sitio/                   la página que ve el usuario
    index.html             estructura
    estilos.css            diseño (colores de la UMSA, tema claro y oscuro)
    prediccion.js          la consulta, el gráfico histórico y el modelo en JavaScript (variables, 100 árboles, log → días)
    modelo/modelo_5var.json  los árboles exportados por notebooks/22_despliegue.ipynb
    datos/procesos.json    los 1.240 procesos con nombres legibles y la serie histórica, de notebooks/23_sitio_publico.ipynb
    img/umsa.png           escudo
  nginx.conf               servidor de archivos: compresión, cabeceras de seguridad y /salud
  Dockerfile               imagen nginx sin privilegios (puerto 8080)
  docker-compose.yml       el servicio, con reinicio automático y chequeo de salud
```

**No hay Python en el servidor.** El modelo corre en el navegador de quien visita la página: nginx solo entrega
archivos y no recibe ni guarda lo que se consulta. Al abrirse, la página recalcula las 1.240 estimaciones y las
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
2. Volver a ejecutar `notebooks/23_sitio_publico.ipynb`: recalcula con ese modelo las estimaciones para un caso nuevo
   y escribe `despliegue/sitio/datos/procesos.json`.
3. Hacer `git push` (Dokploy vuelve a publicar) o, a mano, en el VPS: traer los archivos y `docker compose up -d --build`.

## Probar sin Docker

```bash
cd despliegue/sitio
python -m http.server 8000             # abrir http://localhost:8000
```

Al cargar, el sello de «Detalles técnicos» debe decir **1.240 / 1.240 coinciden**.

## Seguridad

- La imagen `nginxinc/nginx-unprivileged` corre como usuario sin privilegios.
- El contenedor es de solo lectura (`read_only`), sin capacidades de Linux (`cap_drop: ALL`) y sin escalada de privilegios.
- nginx envía una política de contenido (CSP) que solo permite los archivos propios y las fuentes de Google, y oculta
  su versión.
