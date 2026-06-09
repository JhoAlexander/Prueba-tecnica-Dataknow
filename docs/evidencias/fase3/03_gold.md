# Evidencia — Capa Gold

## Dimensiones y hechos

```
Fecha de referencia: 2026-05-31
  dim_productos: 5,000
  dim_tiendas: 150
  dim_clientes: 50,000
  fact_ventas: 999,901
  fact_inventario: 25,000 (alertas quiebre: 4,616)
  fact_devoluciones: 49,998
  fact_rfm_clientes: 49,930
```

## Agregados y KPIs

```
  agg_ventas_diarias: 531,911 filas
  agg_tasa_devolucion: 24 filas
  agg_segmentos_rfm: 5 filas
  kpi_ventas_pais_canal: 20 filas
  kpi_top_productos: 60 filas
  kpi_ventas_semanales: 270 filas
```

## Tablas de la capa Gold

| Tabla | Tipo | Reglas de negocio |
|---|---|---|
| `dim_productos` | Dimension | Join con proveedores, jerarquia de categorias, margen por categoria |
| `dim_tiendas` | Dimension | Tipo estandarizado, zona de distribucion |
| `dim_clientes` | Dimension | Antiguedad, imputacion de rango_edad, genero estandarizado |
| `fact_ventas` | Hecho | vr_venta_neto, cliente anonimo, indicador de descuento |
| `fact_inventario` | Hecho | cobertura_dias, alerta_quiebre (cobertura<7 y consumo>0) |
| `fact_devoluciones` | Hecho | Join con venta origen, motivo legible |
| `fact_rfm_clientes` | Hecho | RFM 90 dias, quintiles 1-5, segmento, etiqueta |
| `agg_ventas_diarias` | Agregado | Ventas por fecha, pais, tienda, canal y categoria |
| `agg_tasa_devolucion` | Agregado | Unidades devueltas / vendidas por categoria y canal |
| `agg_segmentos_rfm` | Agregado | Distribucion de clientes por etiqueta RFM |
| `kpi_ventas_pais_canal` | KPI | Ventas netas, ticket y % descuento por pais y canal |
| `kpi_top_productos` | KPI | Top 10 productos por categoria |
| `kpi_ventas_semanales` | KPI | Ventas por semana con comparativo vs semana anterior |
