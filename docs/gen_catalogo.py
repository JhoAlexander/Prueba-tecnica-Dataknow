"""Genera el catalogo de datos (docs/catalogo.md) de las capas Silver y Gold.

Silver se deriva de schemas.py. Gold se define aqui (columnas calculadas por las
reglas de negocio). Marca el origen y si cada campo contiene informacion sensible.

Uso:
    python docs/gen_catalogo.py
"""
import sys
from pathlib import Path

DOC_DIR = Path(__file__).parent
ROOT = DOC_DIR.parent
sys.path.insert(0, str(ROOT / 'data-generation'))

from schemas import TABLES  # noqa: E402


# Columnas de la capa Silver: igual que la fuente, sin auditoria, con PII hasheada.
def silver_rows(table_name):
    t = TABLES[table_name.upper()]
    rows = []
    for c in t['columns']:
        sensible = "Si (hash SHA-256)" if c['pii'] else "No"
        rows.append((c['name'], c['sql_type'], table_name, sensible, c['description']))
    return rows


# Definicion de la capa Gold: (columna, tipo, origen, sensible, descripcion).
GOLD = {
    "dim_productos": ("Dimension de productos (MSTR_ARTICULOS + MSTR_PROVEEDORES)", [
        ("art_id", "INT", "MSTR_ARTICULOS", "No", "ID del articulo (PK)"),
        ("desc_art", "VARCHAR", "MSTR_ARTICULOS", "No", "Descripcion comercial"),
        ("id_categ_n1", "INT", "MSTR_ARTICULOS", "No", "Categoria nivel 1"),
        ("categoria_n1", "VARCHAR", "calculado", "No", "Etiqueta legible de categoria"),
        ("id_categ_n2", "INT", "MSTR_ARTICULOS", "No", "Categoria nivel 2"),
        ("id_categ_n3", "INT", "MSTR_ARTICULOS", "No", "Categoria nivel 3"),
        ("id_proveedor", "INT", "MSTR_ARTICULOS", "No", "FK al proveedor"),
        ("proveedor_pais", "VARCHAR", "MSTR_PROVEEDORES", "No", "Pais del proveedor"),
        ("proveedor_calificacion", "DECIMAL", "MSTR_PROVEEDORES", "No", "Calificacion del proveedor"),
        ("precio_lista", "DECIMAL", "MSTR_ARTICULOS", "No", "Precio de lista"),
        ("margen_estimado_pct", "DECIMAL", "calculado", "No", "Margen estimado por categoria"),
        ("precio_con_margen", "DECIMAL", "calculado", "No", "Precio con margen aplicado"),
        ("unid_medida", "VARCHAR", "MSTR_ARTICULOS", "No", "Unidad de medida"),
        ("activo", "BIT", "MSTR_ARTICULOS", "No", "Articulo activo"),
    ]),
    "dim_tiendas": ("Dimension de tiendas (MSTR_TIENDAS)", [
        ("id_tienda", "INT", "MSTR_TIENDAS", "No", "ID de la tienda (PK)"),
        ("nom_tienda", "VARCHAR", "MSTR_TIENDAS", "No", "Nombre comercial"),
        ("tipo_tienda", "VARCHAR", "MSTR_TIENDAS", "No", "Tipo (codigo)"),
        ("tipo_tienda_desc", "VARCHAR", "calculado", "No", "Tipo estandarizado"),
        ("id_ciudad", "INT", "MSTR_TIENDAS", "No", "Ciudad"),
        ("id_pais", "VARCHAR", "MSTR_TIENDAS", "No", "Pais"),
        ("zona_distribucion", "VARCHAR", "calculado", "No", "Centro de distribucion asignado"),
        ("metros_cuadrados", "INT", "MSTR_TIENDAS", "No", "Area en m2"),
        ("activo", "BIT", "MSTR_TIENDAS", "No", "Tienda operativa"),
    ]),
    "dim_clientes": ("Dimension de clientes (CRM_MIEMBROS)", [
        ("id_miembro", "INT", "CRM_MIEMBROS", "No", "ID del miembro (PK)"),
        ("fec_registro", "DATE", "CRM_MIEMBROS", "No", "Fecha de afiliacion"),
        ("antiguedad_dias", "INT", "calculado", "No", "Dias desde el registro"),
        ("id_ciudad", "INT", "CRM_MIEMBROS", "No", "Ciudad de residencia"),
        ("genero_std", "VARCHAR", "calculado", "Si (demografico)", "Genero estandarizado M/F/No informado"),
        ("rango_edad", "VARCHAR", "CRM_MIEMBROS", "Si (demografico)", "Rango de edad (imputado si faltaba)"),
        ("canal_pref", "VARCHAR", "CRM_MIEMBROS", "No", "Canal preferido"),
        ("activo", "BIT", "CRM_MIEMBROS", "No", "Miembro activo"),
        ("fec_ultima_compra", "DATE", "CRM_MIEMBROS", "No", "Ultima compra"),
    ]),
    "fact_ventas": ("Hechos de ventas (TRANS_VENTAS)", [
        ("id_trans", "BIGINT", "TRANS_VENTAS", "No", "ID de la transaccion (PK)"),
        ("id_cliente", "VARCHAR", "calculado", "No", "ID de miembro o ANONIMO"),
        ("id_miembro", "INT", "TRANS_VENTAS", "No", "FK al miembro (nulo si anonimo)"),
        ("id_tienda", "INT", "TRANS_VENTAS", "No", "FK a la tienda"),
        ("art_id", "INT", "TRANS_VENTAS", "No", "FK al articulo"),
        ("fec_trans", "DATE", "TRANS_VENTAS", "No", "Fecha de la venta"),
        ("hra_trans", "TIME", "TRANS_VENTAS", "No", "Hora de la venta"),
        ("qty_vendida", "INT", "TRANS_VENTAS", "No", "Cantidad vendida"),
        ("precio_unitario_venta", "DECIMAL", "TRANS_VENTAS", "No", "Precio unitario"),
        ("descuento_aplicado", "DECIMAL", "TRANS_VENTAS", "No", "Descuento (0 si no aplica)"),
        ("vr_venta_bruto", "DECIMAL", "calculado", "No", "qty x precio"),
        ("vr_venta_neto", "DECIMAL", "calculado", "No", "Bruto menos descuento"),
        ("ind_descuento", "BIT", "calculado", "No", "Indicador de venta con descuento"),
        ("tipo_pago", "VARCHAR", "TRANS_VENTAS", "No", "Medio de pago"),
        ("canal_venta", "VARCHAR", "TRANS_VENTAS", "No", "Canal de venta"),
    ]),
    "fact_inventario": ("Hechos de inventario (INV_STOCK_DIARIO + TRANS_VENTAS)", [
        ("id_snapshot", "BIGINT", "INV_STOCK_DIARIO", "No", "ID del snapshot (PK)"),
        ("art_id", "INT", "INV_STOCK_DIARIO", "No", "FK al articulo"),
        ("id_tienda", "INT", "INV_STOCK_DIARIO", "No", "FK a la tienda"),
        ("fec_snapshot", "DATE", "INV_STOCK_DIARIO", "No", "Fecha del snapshot"),
        ("stock_fisico", "INT", "INV_STOCK_DIARIO", "No", "Unidades en piso/bodega"),
        ("stock_minimo_config", "INT", "INV_STOCK_DIARIO", "No", "Stock minimo configurado"),
        ("dif_stock_minimo", "INT", "calculado", "No", "Diferencia vs stock minimo"),
        ("consumo_14d", "INT", "calculado", "No", "Unidades vendidas del articulo en 14 dias"),
        ("consumo_diario", "DECIMAL", "calculado", "No", "Consumo diario promedio"),
        ("cobertura_dias", "DECIMAL", "calculado", "No", "Dias de cobertura del stock"),
        ("alerta_quiebre", "BIT", "calculado", "No", "Alerta de riesgo de quiebre"),
    ]),
    "fact_devoluciones": ("Hechos de devoluciones (POST_DEVOLUCIONES + TRANS_VENTAS)", [
        ("id_devolucion", "BIGINT", "POST_DEVOLUCIONES", "No", "ID de la devolucion (PK)"),
        ("id_trans_origen", "BIGINT", "POST_DEVOLUCIONES", "No", "FK a la venta original"),
        ("art_id", "INT", "POST_DEVOLUCIONES", "No", "FK al articulo"),
        ("id_tienda", "INT", "POST_DEVOLUCIONES", "No", "FK a la tienda"),
        ("fec_devolucion", "DATE", "POST_DEVOLUCIONES", "No", "Fecha de la devolucion"),
        ("qty_devuelta", "INT", "POST_DEVOLUCIONES", "No", "Cantidad devuelta"),
        ("motivo_cod", "VARCHAR", "POST_DEVOLUCIONES", "No", "Codigo de motivo"),
        ("motivo_desc", "VARCHAR", "calculado", "No", "Motivo legible"),
        ("canal_devolucion", "VARCHAR", "POST_DEVOLUCIONES", "No", "Canal de devolucion"),
        ("estado_devolucion", "VARCHAR", "POST_DEVOLUCIONES", "No", "Estado"),
        ("vr_reembolso", "DECIMAL", "POST_DEVOLUCIONES", "No", "Monto reembolsado"),
        ("precio_venta_original", "DECIMAL", "calculado", "No", "Precio de la venta origen"),
    ]),
    "fact_rfm_clientes": ("Hechos RFM (TRANS_VENTAS + CRM_MIEMBROS)", [
        ("id_miembro", "INT", "CRM_MIEMBROS", "No", "ID del miembro (PK)"),
        ("recencia_dias", "INT", "calculado", "No", "Dias desde la ultima compra"),
        ("frecuencia", "INT", "calculado", "No", "Numero de compras en 90 dias"),
        ("monetario", "DECIMAL", "calculado", "No", "Gasto en 90 dias"),
        ("R", "INT", "calculado", "No", "Quintil de recencia (1-5)"),
        ("F", "INT", "calculado", "No", "Quintil de frecuencia (1-5)"),
        ("M", "INT", "calculado", "No", "Quintil monetario (1-5)"),
        ("segmento_rfm", "VARCHAR", "calculado", "No", "Segmento concatenado (ej. R5-F4-M5)"),
        ("etiqueta", "VARCHAR", "calculado", "No", "Etiqueta de negocio (Champions, Leales...)"),
    ]),
}

AGG_KPI = {
    "agg_ventas_diarias": "Ventas agregadas por fecha, pais, tienda, canal y categoria.",
    "agg_tasa_devolucion": "Tasa de devolucion por categoria y canal.",
    "agg_segmentos_rfm": "Distribucion de clientes por etiqueta RFM.",
    "kpi_ventas_pais_canal": "KPI de ventas, ticket y % descuento por pais y canal.",
    "kpi_top_productos": "Top 10 productos por categoria.",
    "kpi_ventas_semanales": "Ventas por semana con comparativo vs la anterior.",
}


def tabla_md(rows):
    out = "| Campo | Tipo | Origen | Sensible | Descripcion |\n"
    out += "|---|---|---|---|---|\n"
    for (campo, tipo, origen, sensible, desc) in rows:
        out += f"| `{campo}` | {tipo} | {origen} | {sensible} | {desc} |\n"
    return out


def main():
    md = "# Catalogo de datos\n\n"
    md += "Catalogo de las capas Silver y Gold: cada campo con su tipo, origen y si\n"
    md += "contiene informacion sensible. Autogenerado por `docs/gen_catalogo.py`.\n\n"

    md += "## Capa Silver\n\n"
    md += "Datos limpios y validados. `razon_social` se almacena como hash desde Silver.\n\n"
    silver_order = ["mstr_proveedores", "mstr_tiendas", "mstr_articulos", "crm_miembros",
                    "trans_ventas", "inv_stock_diario", "post_devoluciones"]
    for t in silver_order:
        md += f"### `{t}`\n\n{TABLES[t.upper()]['description']}\n\n"
        md += tabla_md(silver_rows(t)) + "\n"

    md += "## Capa Gold\n\n"
    md += "Modelo dimensional y agregados para consumo analitico.\n\n"
    for t, (desc, rows) in GOLD.items():
        md += f"### `{t}`\n\n{desc}\n\n"
        md += tabla_md(rows) + "\n"

    md += "### Agregados y KPIs\n\n"
    md += "| Tabla | Descripcion |\n|---|---|\n"
    for t, desc in AGG_KPI.items():
        md += f"| `{t}` | {desc} |\n"

    md += "\n## Tablas de control\n\n"
    md += "| Tabla | Capa | Descripcion |\n|---|---|---|\n"
    md += "| `_log_ingesta` | Bronze | Registros procesados por ejecucion |\n"
    md += "| `_errores` | Silver | Registros rechazados con su motivo |\n"
    md += "| `_reporte_calidad` | Silver | Metricas de calidad por tabla |\n"
    md += "| `_resultados_dq` | Gold | Resultado de las verificaciones de calidad |\n"

    out_path = DOC_DIR / 'catalogo.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md)
    n_silver = sum(len(silver_rows(t)) for t in silver_order)
    n_gold = sum(len(rows) for _, rows in GOLD.values())
    print(f"Catalogo generado: {out_path}")
    print(f"  Silver: {len(silver_order)} tablas, {n_silver} campos")
    print(f"  Gold: {len(GOLD)} tablas dim/fact ({n_gold} campos) + {len(AGG_KPI)} agg/kpi")


if __name__ == '__main__':
    main()
