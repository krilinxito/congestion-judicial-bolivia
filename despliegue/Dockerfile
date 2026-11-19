# Página pública «¿Cuánto tardará mi caso?» (despliegue del modelo de 5 variables).
# El modelo corre en el navegador (modelo/modelo_5var.json): el servidor solo entrega archivos estáticos.
# nginx-unprivileged corre como usuario sin privilegios y escucha en el puerto 8080.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY sitio/ /usr/share/nginx/html/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/salud || exit 1
