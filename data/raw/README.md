# data/raw

Acá va el PDF fuente, que **no** está versionado: son 41 MB y es una publicación
pública que se baja del sitio del Consejo de la Magistratura de Bolivia.

El pipeline lo busca en `data/raw/anuario_2023.pdf`. Poné el archivo con ese
nombre, o dejá un enlace simbólico:

```bash
ln -s /ruta/al/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf data/raw/anuario_2023.pdf
```

Para comprobar que es la misma edición con la que se construyó este dataset:
774 páginas, generado con PDF24 sobre Ghostscript 9.56.1, con capa de texto.
`python3 src/01_diagnostico.py` lo verifica y no escribe nada.
