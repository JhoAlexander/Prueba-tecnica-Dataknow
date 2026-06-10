# Catalogo de datos

Catalogo de las capas Silver y Gold: cada campo con su tipo, origen y si
contiene informacion sensible. Autogenerado por `docs/gen_catalogo.py`.

## Capa Silver

Datos limpios y validados. `razon_social` se almacena como hash desde Silver.

### `mstr_proveedores`

Maestro de proveedores de articulos. Incluye pais de origen y tiempo de reposicion.

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_proveedor` | INT | mstr_proveedores | No | ID unico del proveedor (PK) |
| `razon_social` | VARCHAR(150) | mstr_proveedores | Si (hash SHA-256) | Razon social legal del proveedor |
| `pais_origen` | VARCHAR(2) | mstr_proveedores | No | Codigo ISO de pais (CO, MX, US, CN, etc.) |
| `tiempo_repo_dias` | INT | mstr_proveedores | No | Tiempo promedio de reposicion en dias (lead time) |
| `calificacion_calidad` | DECIMAL(3,2) | mstr_proveedores | No | Calificacion de calidad del proveedor (0.00 a 5.00) |
| `activo` | BIT | mstr_proveedores | No | Indicador de proveedor activo (1) o inactivo (0) |

### `mstr_tiendas`

Maestro de tiendas fisicas y centros de venta en 5 paises LATAM.

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_tienda` | INT | mstr_tiendas | No | ID unico de la tienda (PK) |
| `nom_tienda` | VARCHAR(120) | mstr_tiendas | No | Nombre comercial de la tienda |
| `tipo_tienda` | VARCHAR(20) | mstr_tiendas | No | Tipo: HIPER, SUPER o CONVE |
| `id_ciudad` | INT | mstr_tiendas | No | ID de ciudad donde opera (catalogo interno) |
| `id_pais` | VARCHAR(2) | mstr_tiendas | No | Codigo ISO de pais (CO, MX, CL, PE, EC) |
| `metros_cuadrados` | INT | mstr_tiendas | No | Area de la tienda en m2 |
| `activo` | BIT | mstr_tiendas | No | Indicador de tienda operativa |
| `fec_apertura` | DATE | mstr_tiendas | No | Fecha de apertura al publico |

### `mstr_articulos`

Catalogo de articulos (SKUs) con jerarquia de 3 niveles de categoria y proveedor asociado.

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `art_id` | INT | mstr_articulos | No | ID unico del articulo / SKU (PK) |
| `cod_barra` | VARCHAR(13) | mstr_articulos | No | Codigo EAN-13 del articulo |
| `desc_art` | VARCHAR(200) | mstr_articulos | No | Descripcion comercial del articulo |
| `id_categ_n1` | INT | mstr_articulos | No | Categoria nivel 1 (macro categoria, 1-6) |
| `id_categ_n2` | INT | mstr_articulos | No | Categoria nivel 2 (subcategoria) |
| `id_categ_n3` | INT | mstr_articulos | No | Categoria nivel 3 (subsubcategoria - opcional) |
| `id_proveedor` | INT | mstr_articulos | No | FK al proveedor (MSTR_PROVEEDORES) |
| `precio_lista` | DECIMAL(12,2) | mstr_articulos | No | Precio de lista en moneda local del pais primario |
| `peso_kg` | DECIMAL(8,3) | mstr_articulos | No | Peso del articulo en kg (logistica) |
| `unid_medida` | VARCHAR(10) | mstr_articulos | No | Unidad de medida: UN, KG, LT, MT |
| `activo` | BIT | mstr_articulos | No | Articulo activo en catalogo |
| `fec_alta` | DATE | mstr_articulos | No | Fecha de alta del articulo en el catalogo |

### `crm_miembros`

Miembros del programa de fidelizacion de RetailMax.

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_miembro` | INT | crm_miembros | No | ID unico del miembro (PK) |
| `fec_registro` | DATE | crm_miembros | No | Fecha de afiliacion al programa |
| `id_ciudad` | INT | crm_miembros | No | Ciudad de residencia del miembro |
| `genero` | VARCHAR(1) | crm_miembros | Si (hash SHA-256) | Genero: M, F u otro |
| `rango_edad` | VARCHAR(10) | crm_miembros | Si (hash SHA-256) | Rango de edad: 18-25, 26-35, etc. |
| `canal_pref` | VARCHAR(20) | crm_miembros | No | Canal preferido: TIENDA, WEB, MKT, APP |
| `activo` | BIT | crm_miembros | No | Miembro activo en programa |
| `fec_ultima_compra` | DATE | crm_miembros | No | Fecha de ultima transaccion del miembro |

### `trans_ventas`

Hechos de transacciones de venta. Grain: una fila por linea de venta (articulo en un ticket).

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_trans` | BIGINT | trans_ventas | No | ID unico de la transaccion (PK) |
| `id_miembro` | INT | trans_ventas | No | FK al miembro (NULL si es cliente anonimo) |
| `id_tienda` | INT | trans_ventas | No | FK a la tienda donde ocurrio la venta |
| `art_id` | INT | trans_ventas | No | FK al articulo vendido |
| `fec_trans` | DATE | trans_ventas | No | Fecha de la transaccion |
| `hra_trans` | TIME | trans_ventas | No | Hora HH:MM:SS de la transaccion |
| `qty_vendida` | INT | trans_ventas | No | Cantidad de unidades vendidas |
| `precio_unitario_venta` | DECIMAL(12,2) | trans_ventas | No | Precio unitario aplicado en la venta |
| `descuento_aplicado` | DECIMAL(12,2) | trans_ventas | No | Monto de descuento aplicado en moneda local |
| `tipo_pago` | VARCHAR(20) | trans_ventas | No | Medio de pago: EFECTIVO, TARJETA, PSE, NEQUI, etc. |
| `canal_venta` | VARCHAR(20) | trans_ventas | No | Canal: TIENDA, WEB, MKT o APP |

### `inv_stock_diario`

Snapshot diario de inventario por articulo y tienda. Grain: una fila por (articulo, tienda, fecha).

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_snapshot` | BIGINT | inv_stock_diario | No | ID unico del snapshot (PK) |
| `art_id` | INT | inv_stock_diario | No | FK al articulo |
| `id_tienda` | INT | inv_stock_diario | No | FK a la tienda |
| `fec_snapshot` | DATE | inv_stock_diario | No | Fecha del snapshot diario |
| `stock_fisico` | INT | inv_stock_diario | No | Unidades fisicas disponibles en piso/bodega |
| `stock_transito` | INT | inv_stock_diario | No | Unidades en transito desde CD |
| `stock_reservado` | INT | inv_stock_diario | No | Unidades reservadas (ecommerce, click and collect) |
| `stock_minimo_config` | INT | inv_stock_diario | No | Stock minimo configurado para alerta |
| `stock_maximo_config` | INT | inv_stock_diario | No | Stock maximo configurado (sobrestock) |

### `post_devoluciones`

Hechos de devoluciones post-venta. Grain: una fila por linea devuelta de una venta original.

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_devolucion` | BIGINT | post_devoluciones | No | ID unico de la devolucion (PK) |
| `id_trans_origen` | BIGINT | post_devoluciones | No | FK a la transaccion original |
| `art_id` | INT | post_devoluciones | No | FK al articulo devuelto |
| `id_tienda` | INT | post_devoluciones | No | FK a la tienda donde se procesa la devolucion |
| `fec_devolucion` | DATE | post_devoluciones | No | Fecha de la devolucion |
| `qty_devuelta` | INT | post_devoluciones | No | Cantidad de unidades devueltas |
| `motivo_cod` | VARCHAR(20) | post_devoluciones | No | Codigo del motivo de devolucion |
| `canal_devolucion` | VARCHAR(20) | post_devoluciones | No | Canal por donde se procesa la devolucion |
| `estado_devolucion` | VARCHAR(20) | post_devoluciones | No | Estado: PROCESADA, APROBADA, RECHAZADA, REEMBOLSADA |
| `vr_reembolso` | DECIMAL(12,2) | post_devoluciones | No | Monto del reembolso en moneda local |

## Capa Gold

Modelo dimensional y agregados para consumo analitico.

### `dim_productos`

Dimension de productos (MSTR_ARTICULOS + MSTR_PROVEEDORES)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `art_id` | INT | MSTR_ARTICULOS | No | ID del articulo (PK) |
| `desc_art` | VARCHAR | MSTR_ARTICULOS | No | Descripcion comercial |
| `id_categ_n1` | INT | MSTR_ARTICULOS | No | Categoria nivel 1 |
| `categoria_n1` | VARCHAR | calculado | No | Etiqueta legible de categoria |
| `id_categ_n2` | INT | MSTR_ARTICULOS | No | Categoria nivel 2 |
| `id_categ_n3` | INT | MSTR_ARTICULOS | No | Categoria nivel 3 |
| `id_proveedor` | INT | MSTR_ARTICULOS | No | FK al proveedor |
| `proveedor_pais` | VARCHAR | MSTR_PROVEEDORES | No | Pais del proveedor |
| `proveedor_calificacion` | DECIMAL | MSTR_PROVEEDORES | No | Calificacion del proveedor |
| `precio_lista` | DECIMAL | MSTR_ARTICULOS | No | Precio de lista |
| `margen_estimado_pct` | DECIMAL | calculado | No | Margen estimado por categoria |
| `precio_con_margen` | DECIMAL | calculado | No | Precio con margen aplicado |
| `unid_medida` | VARCHAR | MSTR_ARTICULOS | No | Unidad de medida |
| `activo` | BIT | MSTR_ARTICULOS | No | Articulo activo |

### `dim_tiendas`

Dimension de tiendas (MSTR_TIENDAS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_tienda` | INT | MSTR_TIENDAS | No | ID de la tienda (PK) |
| `nom_tienda` | VARCHAR | MSTR_TIENDAS | No | Nombre comercial |
| `tipo_tienda` | VARCHAR | MSTR_TIENDAS | No | Tipo (codigo) |
| `tipo_tienda_desc` | VARCHAR | calculado | No | Tipo estandarizado |
| `id_ciudad` | INT | MSTR_TIENDAS | No | Ciudad |
| `id_pais` | VARCHAR | MSTR_TIENDAS | No | Pais |
| `zona_distribucion` | VARCHAR | calculado | No | Centro de distribucion asignado |
| `metros_cuadrados` | INT | MSTR_TIENDAS | No | Area en m2 |
| `activo` | BIT | MSTR_TIENDAS | No | Tienda operativa |

### `dim_clientes`

Dimension de clientes (CRM_MIEMBROS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_miembro` | INT | CRM_MIEMBROS | No | ID del miembro (PK) |
| `fec_registro` | DATE | CRM_MIEMBROS | No | Fecha de afiliacion |
| `antiguedad_dias` | INT | calculado | No | Dias desde el registro |
| `id_ciudad` | INT | CRM_MIEMBROS | No | Ciudad de residencia |
| `genero_std` | VARCHAR | calculado | Si (demografico) | Genero estandarizado M/F/No informado |
| `rango_edad` | VARCHAR | CRM_MIEMBROS | Si (demografico) | Rango de edad (imputado si faltaba) |
| `canal_pref` | VARCHAR | CRM_MIEMBROS | No | Canal preferido |
| `activo` | BIT | CRM_MIEMBROS | No | Miembro activo |
| `fec_ultima_compra` | DATE | CRM_MIEMBROS | No | Ultima compra |

### `fact_ventas`

Hechos de ventas (TRANS_VENTAS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_trans` | BIGINT | TRANS_VENTAS | No | ID de la transaccion (PK) |
| `id_cliente` | VARCHAR | calculado | No | ID de miembro o ANONIMO |
| `id_miembro` | INT | TRANS_VENTAS | No | FK al miembro (nulo si anonimo) |
| `id_tienda` | INT | TRANS_VENTAS | No | FK a la tienda |
| `art_id` | INT | TRANS_VENTAS | No | FK al articulo |
| `fec_trans` | DATE | TRANS_VENTAS | No | Fecha de la venta |
| `hra_trans` | TIME | TRANS_VENTAS | No | Hora de la venta |
| `qty_vendida` | INT | TRANS_VENTAS | No | Cantidad vendida |
| `precio_unitario_venta` | DECIMAL | TRANS_VENTAS | No | Precio unitario |
| `descuento_aplicado` | DECIMAL | TRANS_VENTAS | No | Descuento (0 si no aplica) |
| `vr_venta_bruto` | DECIMAL | calculado | No | qty x precio |
| `vr_venta_neto` | DECIMAL | calculado | No | Bruto menos descuento |
| `ind_descuento` | BIT | calculado | No | Indicador de venta con descuento |
| `tipo_pago` | VARCHAR | TRANS_VENTAS | No | Medio de pago |
| `canal_venta` | VARCHAR | TRANS_VENTAS | No | Canal de venta |

### `fact_inventario`

Hechos de inventario (INV_STOCK_DIARIO + TRANS_VENTAS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_snapshot` | BIGINT | INV_STOCK_DIARIO | No | ID del snapshot (PK) |
| `art_id` | INT | INV_STOCK_DIARIO | No | FK al articulo |
| `id_tienda` | INT | INV_STOCK_DIARIO | No | FK a la tienda |
| `fec_snapshot` | DATE | INV_STOCK_DIARIO | No | Fecha del snapshot |
| `stock_fisico` | INT | INV_STOCK_DIARIO | No | Unidades en piso/bodega |
| `stock_minimo_config` | INT | INV_STOCK_DIARIO | No | Stock minimo configurado |
| `dif_stock_minimo` | INT | calculado | No | Diferencia vs stock minimo |
| `consumo_14d` | INT | calculado | No | Unidades vendidas del articulo en 14 dias |
| `consumo_diario` | DECIMAL | calculado | No | Consumo diario promedio |
| `cobertura_dias` | DECIMAL | calculado | No | Dias de cobertura del stock |
| `alerta_quiebre` | BIT | calculado | No | Alerta de riesgo de quiebre |

### `fact_devoluciones`

Hechos de devoluciones (POST_DEVOLUCIONES + TRANS_VENTAS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_devolucion` | BIGINT | POST_DEVOLUCIONES | No | ID de la devolucion (PK) |
| `id_trans_origen` | BIGINT | POST_DEVOLUCIONES | No | FK a la venta original |
| `art_id` | INT | POST_DEVOLUCIONES | No | FK al articulo |
| `id_tienda` | INT | POST_DEVOLUCIONES | No | FK a la tienda |
| `fec_devolucion` | DATE | POST_DEVOLUCIONES | No | Fecha de la devolucion |
| `qty_devuelta` | INT | POST_DEVOLUCIONES | No | Cantidad devuelta |
| `motivo_cod` | VARCHAR | POST_DEVOLUCIONES | No | Codigo de motivo |
| `motivo_desc` | VARCHAR | calculado | No | Motivo legible |
| `canal_devolucion` | VARCHAR | POST_DEVOLUCIONES | No | Canal de devolucion |
| `estado_devolucion` | VARCHAR | POST_DEVOLUCIONES | No | Estado |
| `vr_reembolso` | DECIMAL | POST_DEVOLUCIONES | No | Monto reembolsado |
| `precio_venta_original` | DECIMAL | calculado | No | Precio de la venta origen |

### `fact_rfm_clientes`

Hechos RFM (TRANS_VENTAS + CRM_MIEMBROS)

| Campo | Tipo | Origen | Sensible | Descripcion |
|---|---|---|---|---|
| `id_miembro` | INT | CRM_MIEMBROS | No | ID del miembro (PK) |
| `recencia_dias` | INT | calculado | No | Dias desde la ultima compra |
| `frecuencia` | INT | calculado | No | Numero de compras en 90 dias |
| `monetario` | DECIMAL | calculado | No | Gasto en 90 dias |
| `R` | INT | calculado | No | Quintil de recencia (1-5) |
| `F` | INT | calculado | No | Quintil de frecuencia (1-5) |
| `M` | INT | calculado | No | Quintil monetario (1-5) |
| `segmento_rfm` | VARCHAR | calculado | No | Segmento concatenado (ej. R5-F4-M5) |
| `etiqueta` | VARCHAR | calculado | No | Etiqueta de negocio (Champions, Leales...) |

### Agregados y KPIs

| Tabla | Descripcion |
|---|---|
| `agg_ventas_diarias` | Ventas agregadas por fecha, pais, tienda, canal y categoria. |
| `agg_tasa_devolucion` | Tasa de devolucion por categoria y canal. |
| `agg_segmentos_rfm` | Distribucion de clientes por etiqueta RFM. |
| `kpi_ventas_pais_canal` | KPI de ventas, ticket y % descuento por pais y canal. |
| `kpi_top_productos` | Top 10 productos por categoria. |
| `kpi_ventas_semanales` | Ventas por semana con comparativo vs la anterior. |

## Tablas de control

| Tabla | Capa | Descripcion |
|---|---|---|
| `_log_ingesta` | Bronze | Registros procesados por ejecucion |
| `_errores` | Silver | Registros rechazados con su motivo |
| `_reporte_calidad` | Silver | Metricas de calidad por tabla |
| `_resultados_dq` | Gold | Resultado de las verificaciones de calidad |
