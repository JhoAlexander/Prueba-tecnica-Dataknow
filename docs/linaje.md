# Linaje de datos — Campos calculados en la capa Gold

Trazabilidad de tres campos calculados, desde la fuente hasta su uso de negocio.

## 1. `fact_ventas.vr_venta_neto`

| Etapa | Detalle |
|---|---|
| Origen | `TRANS_VENTAS` (`qty_vendida`, `precio_unitario_venta`, `descuento_aplicado`) |
| Bronze | Copia cruda con auditoria |
| Silver | Dedup, validacion de monto positivo y fecha valida, integridad referencial |
| Gold | `vr_venta_bruto = qty_vendida * precio_unitario_venta`; `vr_venta_neto = vr_venta_bruto - descuento_aplicado` (descuento nulo -> 0) |
| Proposito | Ingreso neto real por linea de venta; base de todos los KPIs de ventas |

## 2. `fact_inventario.alerta_quiebre`

| Etapa | Detalle |
|---|---|
| Origen | `INV_STOCK_DIARIO` (`stock_fisico`) + `TRANS_VENTAS` (`qty_vendida`) |
| Bronze | Copia cruda de ambas fuentes |
| Silver | Limpieza y validacion de integridad |
| Gold | `consumo_14d` = unidades vendidas del articulo en los ultimos 14 dias; `consumo_diario = consumo_14d / 14`; `cobertura_dias = stock_fisico / consumo_diario`; `alerta_quiebre = (cobertura_dias < 7) AND (consumo_diario > 0)` |
| Proposito | Identificar referencias en riesgo de quiebre de stock para Supply Chain |

## 3. `fact_rfm_clientes.segmento_rfm`

| Etapa | Detalle |
|---|---|
| Origen | `TRANS_VENTAS` (`id_miembro`, `fec_trans`, `vr_venta_neto`) |
| Bronze | Copia cruda |
| Silver | Dedup y validacion |
| Gold | Sobre los ultimos 90 dias y clientes activos (compra en 180 dias): `recencia` = dias desde la ultima compra; `frecuencia` = numero de transacciones; `monetario` = suma de `vr_venta_neto`. Cada dimension se divide en quintiles (1-5) y se concatena en `segmento_rfm` (ej. R5-F4-M5) |
| Proposito | Segmentar clientes del programa de fidelizacion para campanas de marketing |
