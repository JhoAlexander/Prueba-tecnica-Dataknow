# Evidencias — Gobierno y seguridad

| Archivo | Descripcion |
|---|---|
| `compartir_gold.png` | Permisos de `lh_gold`: el Analista con acceso de solo lectura, sin acceso a Bronze ni Silver (minimo privilegio) |

## Roles implementados

- **Administrador**: cuenta propietaria del workspace (control total).
- **Ingeniero de Datos**: Member del workspace (R/W en las tres capas).
- **Analista**: usuario invitado con acceso compartido **solo a `lh_gold`** (lectura).

La definicion completa y el mecanismo de acceso por capa estan en `docs/roles.md`.

## Alerta de anomalia de volumen

El codigo de la tercera alerta (anomalia de volumen, desviacion > 30% vs el
promedio de las ultimas 7 ejecuciones) esta en
`pipelines/data_quality/alerta_anomalia_volumen.py`. Las alertas de fallo y de
reporte diario tienen su evidencia en `docs/evidencias/fase4/`.

## Catalogo de datos

El catalogo de las capas Silver y Gold (campos, tipos, origen y sensibilidad)
esta en `docs/catalogo.md`, autogenerado por `docs/gen_catalogo.py`.
