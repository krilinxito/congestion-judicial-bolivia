# data/raw

Acá va el PDF fuente, que **no** está versionado: son 43 MB y es una publicación
pública del Consejo de la Magistratura de Bolivia.

Los notebooks lo buscan en `data/raw/anuario_2023.pdf`:

```bash
curl -L -o data/raw/anuario_2023.pdf \
  https://magistratura.organojudicial.gob.bo/wp-content/uploads/2024/06/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf
```

Para comprobar que es la misma edición con la que se construyó el dataset:
774 páginas, 42.905.977 bytes, SHA-256
`8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.
El notebook `notebooks/01_diagnostico.ipynb` lo verifica y no escribe nada.
