# Evidencia — Verificaciones de calidad (capa Gold)

Resultado: **8/8 verificaciones PASS**

| check | estado | valor_obtenido |
|---|---|---|
| pk_unica_dim_productos | PASS | 5000 filas / 5000 art_id distintos |
| pk_unica_dim_tiendas | PASS | 150 filas / 150 id_tienda distintos |
| pk_unica_dim_clientes | PASS | 50000 filas / 50000 id_miembro distintos |
| no_nulos_fact_ventas | PASS | 0 nulos |
| ri_ventas_productos | PASS | 0 huerfanos |
| rango_vr_venta_neto | PASS | 0 no positivos |
| rango_scores_rfm | PASS | 0 fuera de rango |
| rango_cobertura | PASS | 0 negativas |

Las verificaciones cubren: unicidad de llaves primarias, ausencia de nulos en
campos criticos, integridad referencial Gold, rangos validos de montos y
scores RFM, y consistencia de la cobertura de inventario. Los resultados se
persisten en la tabla `_resultados_dq`.
