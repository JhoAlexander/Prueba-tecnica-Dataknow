"""Configuracion compartida del pipeline Medallion.

Rutas OneLake (abfss), catalogo de tablas con sus llaves y relaciones,
y parametros de ejecucion. Centralizar esto evita repetir IDs en cada capa.
"""

# Identificadores de workspaces y lakehouses (OneLake)
WORKSPACE_PROD = "ef3f34e4-d275-4635-923d-151c027f3261"
WORKSPACE_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"

LH_FUENTE = "551056c6-6b7c-49d5-963c-f009cda2a170"  # lakehouse_retailmax_fuente (prod)
LH_BRONZE = "5d469c7d-d1b6-4166-89df-3caa8b8e6dc1"
LH_SILVER = "cca20c1b-8219-4641-88e0-16fc9cf3be56"
LH_GOLD   = "07875980-48ed-4203-95cc-c992a1e7e37a"

_ONELAKE = "onelake.dfs.fabric.microsoft.com"


def abfss(workspace_id: str, lakehouse_id: str, table: str) -> str:
    """Construye la ruta abfss a una tabla Delta dentro de un lakehouse."""
    return f"abfss://{workspace_id}@{_ONELAKE}/{lakehouse_id}/Tables/{table}"


def fuente_path(table: str) -> str:
    # La fuente tiene schemas habilitados (tablas bajo el schema dbo).
    return abfss(WORKSPACE_PROD, LH_FUENTE, f"dbo/{table}")


def bronze_path(table: str) -> str:
    return abfss(WORKSPACE_DEV, LH_BRONZE, table)


def silver_path(table: str) -> str:
    return abfss(WORKSPACE_DEV, LH_SILVER, table)


def gold_path(table: str) -> str:
    return abfss(WORKSPACE_DEV, LH_GOLD, table)


# Catalogo de tablas fuente: llave primaria y columna de fecha para incremental.
TABLAS = {
    "mstr_proveedores":  {"pk": "id_proveedor",  "fecha": None},
    "mstr_tiendas":      {"pk": "id_tienda",     "fecha": "fec_apertura"},
    "mstr_articulos":    {"pk": "art_id",        "fecha": "fec_alta"},
    "crm_miembros":      {"pk": "id_miembro",    "fecha": "fec_registro"},
    "trans_ventas":      {"pk": "id_trans",      "fecha": "fec_trans"},
    "inv_stock_diario":  {"pk": "id_snapshot",   "fecha": "fec_snapshot"},
    "post_devoluciones": {"pk": "id_devolucion", "fecha": "fec_devolucion"},
}

# Relaciones para validar integridad referencial en Silver.
# (tabla_hecho, columna_fk) -> (tabla_dim, columna_pk)
FOREIGN_KEYS = [
    ("mstr_articulos",    "id_proveedor",    "mstr_proveedores", "id_proveedor"),
    ("trans_ventas",      "id_tienda",       "mstr_tiendas",     "id_tienda"),
    ("trans_ventas",      "art_id",          "mstr_articulos",   "art_id"),
    ("inv_stock_diario",  "art_id",          "mstr_articulos",   "art_id"),
    ("inv_stock_diario",  "id_tienda",       "mstr_tiendas",     "id_tienda"),
    ("post_devoluciones", "id_trans_origen", "trans_ventas",     "id_trans"),
    ("post_devoluciones", "art_id",          "mstr_articulos",   "art_id"),
    ("post_devoluciones", "id_tienda",       "mstr_tiendas",     "id_tienda"),
]

# Columnas con informacion identificable a enmascarar en Silver (hash).
# El escenario no contiene nombres de persona, documentos ni contacto;
# razon_social es el unico identificador directo. genero y rango_edad se
# conservan como datos demograficos para segmentacion.
PII_COLUMNS = {
    "mstr_proveedores": ["razon_social"],
}

SISTEMA_FUENTE = "lakehouse_retailmax_fuente"
