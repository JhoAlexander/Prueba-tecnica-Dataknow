"""Capa Gold (1/2) — Dimensiones y hechos.

Se construye el modelo dimensional aplicando las reglas de negocio del sector:
dim_productos, dim_tiendas, dim_clientes, fact_ventas, fact_inventario,
fact_devoluciones y fact_rfm_clientes.

"""
from pyspark.sql import functions as F
from pyspark.sql import Window

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_SILVER = "cca20c1b-8219-4641-88e0-16fc9cf3be56"
LH_GOLD   = "07875980-48ed-4203-95cc-c992a1e7e37a"

def _silver(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_SILVER}/Tables/{t}"
def _gold(t):   return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_GOLD}/Tables/{t}"
def leer(t):    return spark.read.format("delta").load(_silver(t))
def escribir(df, t):
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(_gold(t))

# Catalogos de negocio
CATEG_N1 = {1: "Alimentos y bebidas", 2: "Cuidado personal e higiene",
            3: "Hogar y limpieza", 4: "Electronica y tecnologia",
            5: "Ropa y calzado basico", 6: "Bebes y maternidad"}
MARGEN = {1: 0.18, 2: 0.30, 3: 0.28, 4: 0.22, 5: 0.45, 6: 0.35}
TIPO_TIENDA = {"HIPER": "Hipermercado", "SUPER": "Supermercado de barrio",
               "CONVE": "Tienda de conveniencia"}
ZONA_DIST = {"CO": "CD Bogota", "MX": "CD Ciudad de Mexico",
             "CL": "CD Santiago", "PE": "CD Santiago", "EC": "CD Santiago"}
MOTIVO = {"DEFECTUOSO": "Articulo defectuoso o danado", "NO_DESEADO": "Cliente cambio de opinion",
          "TALLA": "Talla incorrecta", "INCOMPLETO": "Paquete incompleto",
          "NO_CORRESPONDE": "No corresponde a lo solicitado", "VENCIDO": "Producto vencido",
          "OTRO": "Otro motivo"}

def map_col(col, d, default=None):
    """Convierte un dict Python en una expresion CASE WHEN de Spark."""
    expr = F.lit(default)
    for k, v in d.items():
        expr = F.when(F.col(col) == F.lit(k), F.lit(v)).otherwise(expr)
    return expr
# ==================================================

# Fecha de referencia = ultima fecha de venta (los datos terminan en mayo 2026).
FECHA_REF = leer("trans_ventas").agg(F.max("fec_trans")).collect()[0][0]
print(f"Fecha de referencia: {FECHA_REF}")

# ---------- dim_productos ----------
art = leer("mstr_articulos")
prov = leer("mstr_proveedores").select(
    "id_proveedor", F.col("razon_social").alias("proveedor_hash"),
    F.col("pais_origen").alias("proveedor_pais"),
    F.col("calificacion_calidad").alias("proveedor_calificacion"))
dim_productos = (art.join(prov, "id_proveedor", "left")
    .withColumn("categoria_n1", map_col("id_categ_n1", CATEG_N1, "Sin categoria"))
    .withColumn("margen_estimado_pct", map_col("id_categ_n1", MARGEN, 0.20))
    .withColumn("precio_con_margen", F.round(F.col("precio_lista") * (1 + F.col("margen_estimado_pct")), 2))
    .select("art_id", "desc_art", "id_categ_n1", "categoria_n1", "id_categ_n2", "id_categ_n3",
            "id_proveedor", "proveedor_pais", "proveedor_calificacion",
            "precio_lista", "margen_estimado_pct", "precio_con_margen",
            "unid_medida", "activo"))
escribir(dim_productos, "dim_productos")
print(f"  dim_productos: {dim_productos.count():,}")

# ---------- dim_tiendas ----------
dim_tiendas = (leer("mstr_tiendas")
    .withColumn("tipo_tienda_desc", map_col("tipo_tienda", TIPO_TIENDA, "Otro"))
    .withColumn("zona_distribucion", map_col("id_pais", ZONA_DIST, "Sin asignar"))
    .select("id_tienda", "nom_tienda", "tipo_tienda", "tipo_tienda_desc",
            "id_ciudad", "id_pais", "zona_distribucion", "metros_cuadrados", "activo"))
escribir(dim_tiendas, "dim_tiendas")
print(f"  dim_tiendas: {dim_tiendas.count():,}")

# ---------- dim_clientes ----------
cli = leer("crm_miembros")
# Imputar rango_edad nulo con la moda (valor mas frecuente) del canal preferido.
modas = (cli.filter(F.col("rango_edad").isNotNull())
    .groupBy("canal_pref", "rango_edad").count()
    .withColumn("rn", F.row_number().over(
        Window.partitionBy("canal_pref").orderBy(F.desc("count"))))
    .filter(F.col("rn") == 1).select("canal_pref",
        F.col("rango_edad").alias("rango_edad_moda")))
dim_clientes = (cli.join(modas, "canal_pref", "left")
    .withColumn("rango_edad", F.coalesce("rango_edad", "rango_edad_moda", F.lit("26-35")))
    .withColumn("genero_std", F.when(F.col("genero") == "M", "M")
                               .when(F.col("genero") == "F", "F")
                               .otherwise("No informado"))
    .withColumn("antiguedad_dias", F.datediff(F.lit(FECHA_REF), F.col("fec_registro")))
    .select("id_miembro", "fec_registro", "antiguedad_dias", "id_ciudad",
            "genero_std", "rango_edad", "canal_pref", "activo", "fec_ultima_compra"))
escribir(dim_clientes, "dim_clientes")
print(f"  dim_clientes: {dim_clientes.count():,}")

# ---------- fact_ventas ----------
fact_ventas = (leer("trans_ventas")
    .withColumn("descuento_aplicado", F.coalesce("descuento_aplicado", F.lit(0.0)))
    .withColumn("vr_venta_bruto", F.round(F.col("qty_vendida") * F.col("precio_unitario_venta"), 2))
    .withColumn("vr_venta_neto", F.round(F.col("vr_venta_bruto") - F.col("descuento_aplicado"), 2))
    .withColumn("ind_descuento", F.col("descuento_aplicado") > 0)
    .withColumn("id_cliente", F.coalesce(F.col("id_miembro").cast("string"), F.lit("ANONIMO")))
    .select("id_trans", "id_cliente", "id_miembro", "id_tienda", "art_id",
            "fec_trans", "hra_trans", "qty_vendida", "precio_unitario_venta",
            "descuento_aplicado", "vr_venta_bruto", "vr_venta_neto",
            "ind_descuento", "tipo_pago", "canal_venta"))
escribir(fact_ventas, "fact_ventas")
print(f"  fact_ventas: {fact_ventas.count():,}")

# ---------- fact_inventario ----------
# Consumo de los ultimos 14 dias por articulo a nivel cadena (todas las tiendas).
# Se mide por referencia porque las ventas por par (articulo, tienda) son
# demasiado dispersas para estimar el consumo en una ventana de 14 dias.
ini_14 = F.date_sub(F.lit(FECHA_REF), 14)
consumo = (fact_ventas.filter(F.col("fec_trans") > ini_14)
    .groupBy("art_id")
    .agg(F.sum("qty_vendida").alias("consumo_14d")))
# Ultimo snapshot por (articulo, tienda).
inv = leer("inv_stock_diario")
ult = inv.withColumn("rn", F.row_number().over(
        Window.partitionBy("art_id", "id_tienda").orderBy(F.desc("fec_snapshot")))) \
    .filter(F.col("rn") == 1).drop("rn")
fact_inventario = (ult.join(consumo, "art_id", "left")
    .withColumn("consumo_14d", F.coalesce("consumo_14d", F.lit(0)))
    .withColumn("consumo_diario", F.col("consumo_14d") / 14.0)
    .withColumn("cobertura_dias", F.when(F.col("consumo_diario") > 0,
        F.round(F.col("stock_fisico") / F.col("consumo_diario"), 1)).otherwise(None))
    .withColumn("alerta_quiebre",
        (F.col("cobertura_dias") < 7) & (F.col("consumo_diario") > 0))
    .withColumn("dif_stock_minimo", F.col("stock_fisico") - F.col("stock_minimo_config"))
    .select("id_snapshot", "art_id", "id_tienda", "fec_snapshot", "stock_fisico",
            "stock_minimo_config", "dif_stock_minimo", "consumo_14d", "consumo_diario",
            "cobertura_dias", "alerta_quiebre"))
escribir(fact_inventario, "fact_inventario")
n_alerta = fact_inventario.filter("alerta_quiebre").count()
print(f"  fact_inventario: {fact_inventario.count():,} (alertas quiebre: {n_alerta:,})")

# ---------- fact_devoluciones ----------
ventas_origen = fact_ventas.select(
    F.col("id_trans").alias("id_trans_origen"),
    F.col("precio_unitario_venta").alias("precio_venta_original"),
    F.col("canal_venta").alias("canal_venta_original"))
fact_devoluciones = (leer("post_devoluciones")
    .join(ventas_origen, "id_trans_origen", "left")
    .withColumn("motivo_desc", map_col("motivo_cod", MOTIVO, "Sin clasificar"))
    .withColumn("vr_reembolso", F.coalesce("vr_reembolso", F.lit(0.0)))
    .select("id_devolucion", "id_trans_origen", "art_id", "id_tienda", "fec_devolucion",
            "qty_devuelta", "motivo_cod", "motivo_desc", "canal_devolucion",
            "estado_devolucion", "vr_reembolso", "precio_venta_original"))
escribir(fact_devoluciones, "fact_devoluciones")
print(f"  fact_devoluciones: {fact_devoluciones.count():,}")

# ---------- fact_rfm_clientes ----------
# RFM sobre 90 dias; quintiles 1-5 sobre clientes activos (compra en 180 dias).
ini_90 = F.date_sub(F.lit(FECHA_REF), 90)
ini_180 = F.date_sub(F.lit(FECHA_REF), 180)
ventas_cli = fact_ventas.filter(F.col("id_miembro").isNotNull())

activos = ventas_cli.filter(F.col("fec_trans") > ini_180) \
    .select("id_miembro").distinct()
v90 = ventas_cli.filter(F.col("fec_trans") > ini_90)
rfm_base = (activos
    .join(ventas_cli.groupBy("id_miembro").agg(
        F.max("fec_trans").alias("ultima_compra")), "id_miembro", "left")
    .join(v90.groupBy("id_miembro").agg(
        F.count("*").alias("frecuencia"),
        F.sum("vr_venta_neto").alias("monetario")), "id_miembro", "left")
    .fillna({"frecuencia": 0, "monetario": 0.0})
    .withColumn("recencia_dias", F.datediff(F.lit(FECHA_REF), F.col("ultima_compra"))))

# Quintiles: recencia invertida (menos dias = mejor), frecuencia y monetario directos.
wR = Window.orderBy(F.asc("recencia_dias"))
wF = Window.orderBy(F.asc("frecuencia"))
wM = Window.orderBy(F.asc("monetario"))
fact_rfm = (rfm_base
    .withColumn("R", F.ntile(5).over(Window.orderBy(F.desc("recencia_dias"))))
    .withColumn("F", F.ntile(5).over(wF))
    .withColumn("M", F.ntile(5).over(wM))
    .withColumn("segmento_rfm", F.concat_ws("-",
        F.concat(F.lit("R"), F.col("R")),
        F.concat(F.lit("F"), F.col("F")),
        F.concat(F.lit("M"), F.col("M"))))
    .withColumn("etiqueta",
        F.when((F.col("R") >= 4) & (F.col("F") >= 4) & (F.col("M") >= 4), "Champions")
         .when((F.col("R") >= 3) & (F.col("F") >= 3), "Leales")
         .when(F.col("R") >= 4, "Recientes")
         .when(F.col("R") <= 2, "En riesgo")
         .otherwise("Ocasionales"))
    .select("id_miembro", "recencia_dias", "frecuencia", "monetario",
            "R", "F", "M", "segmento_rfm", "etiqueta"))
escribir(fact_rfm, "fact_rfm_clientes")
print(f"  fact_rfm_clientes: {fact_rfm.count():,}")

print("\nGold (dimensiones y hechos) completado.")
