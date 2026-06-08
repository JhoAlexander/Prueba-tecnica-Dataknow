"""Definicion de las tablas fuente: columnas, tipos, PII y relaciones.

Fuente unica de verdad consumida por los generadores, el diagrama ER
y el catalogo de datos.
"""
from typing import TypedDict, List, Dict, Optional


class ColumnDef(TypedDict):
    name: str
    sql_type: str
    pandas_type: str
    nullable: bool
    pii: bool
    description: str


class ForeignKey(TypedDict):
    column: str
    references: str


class TableDef(TypedDict):
    description: str
    pk: str
    fks: List[ForeignKey]
    columns: List[ColumnDef]


MSTR_PROVEEDORES: TableDef = {
    'description': 'Maestro de proveedores de articulos. Incluye pais de origen y tiempo de reposicion.',
    'pk': 'id_proveedor',
    'fks': [],
    'columns': [
        {'name': 'id_proveedor',         'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico del proveedor (PK)'},
        {'name': 'razon_social',         'sql_type': 'VARCHAR(150)',   'pandas_type': 'string', 'nullable': False, 'pii': True,  'description': 'Razon social legal del proveedor'},
        {'name': 'pais_origen',          'sql_type': 'VARCHAR(2)',     'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Codigo ISO de pais (CO, MX, US, CN, etc.)'},
        {'name': 'tiempo_repo_dias',     'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'Tiempo promedio de reposicion en dias (lead time)'},
        {'name': 'calificacion_calidad', 'sql_type': 'DECIMAL(3,2)',   'pandas_type': 'float64','nullable': True,  'pii': False, 'description': 'Calificacion de calidad del proveedor (0.00 a 5.00)'},
        {'name': 'activo',               'sql_type': 'BIT',            'pandas_type': 'boolean','nullable': False, 'pii': False, 'description': 'Indicador de proveedor activo (1) o inactivo (0)'},
    ],
}

MSTR_TIENDAS: TableDef = {
    'description': 'Maestro de tiendas fisicas y centros de venta en 5 paises LATAM.',
    'pk': 'id_tienda',
    'fks': [],
    'columns': [
        {'name': 'id_tienda',         'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico de la tienda (PK)'},
        {'name': 'nom_tienda',        'sql_type': 'VARCHAR(120)',   'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Nombre comercial de la tienda'},
        {'name': 'tipo_tienda',       'sql_type': 'VARCHAR(20)',    'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Tipo: HIPER, SUPER o CONVE'},
        {'name': 'id_ciudad',         'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID de ciudad donde opera (catalogo interno)'},
        {'name': 'id_pais',           'sql_type': 'VARCHAR(2)',     'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Codigo ISO de pais (CO, MX, CL, PE, EC)'},
        {'name': 'metros_cuadrados',  'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': True,  'pii': False, 'description': 'Area de la tienda en m2'},
        {'name': 'activo',            'sql_type': 'BIT',            'pandas_type': 'boolean','nullable': False, 'pii': False, 'description': 'Indicador de tienda operativa'},
        {'name': 'fec_apertura',      'sql_type': 'DATE',           'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha de apertura al publico'},
    ],
}

MSTR_ARTICULOS: TableDef = {
    'description': 'Catalogo de articulos (SKUs) con jerarquia de 3 niveles de categoria y proveedor asociado.',
    'pk': 'art_id',
    'fks': [
        {'column': 'id_proveedor', 'references': 'MSTR_PROVEEDORES.id_proveedor'},
    ],
    'columns': [
        {'name': 'art_id',          'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico del articulo / SKU (PK)'},
        {'name': 'cod_barra',       'sql_type': 'VARCHAR(13)',    'pandas_type': 'string', 'nullable': True,  'pii': False, 'description': 'Codigo EAN-13 del articulo'},
        {'name': 'desc_art',        'sql_type': 'VARCHAR(200)',   'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Descripcion comercial del articulo'},
        {'name': 'id_categ_n1',     'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'Categoria nivel 1 (macro categoria, 1-6)'},
        {'name': 'id_categ_n2',     'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'Categoria nivel 2 (subcategoria)'},
        {'name': 'id_categ_n3',     'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': True,  'pii': False, 'description': 'Categoria nivel 3 (subsubcategoria - opcional)'},
        {'name': 'id_proveedor',    'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK al proveedor (MSTR_PROVEEDORES)'},
        {'name': 'precio_lista',    'sql_type': 'DECIMAL(12,2)',  'pandas_type': 'float64','nullable': False, 'pii': False, 'description': 'Precio de lista en moneda local del pais primario'},
        {'name': 'peso_kg',         'sql_type': 'DECIMAL(8,3)',   'pandas_type': 'float64','nullable': True,  'pii': False, 'description': 'Peso del articulo en kg (logistica)'},
        {'name': 'unid_medida',     'sql_type': 'VARCHAR(10)',    'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Unidad de medida: UN, KG, LT, MT'},
        {'name': 'activo',          'sql_type': 'BIT',            'pandas_type': 'boolean','nullable': False, 'pii': False, 'description': 'Articulo activo en catalogo'},
        {'name': 'fec_alta',        'sql_type': 'DATE',           'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha de alta del articulo en el catalogo'},
    ],
}

CRM_MIEMBROS: TableDef = {
    'description': 'Miembros del programa de fidelizacion de RetailMax.',
    'pk': 'id_miembro',
    'fks': [],
    'columns': [
        {'name': 'id_miembro',         'sql_type': 'INT',         'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico del miembro (PK)'},
        {'name': 'fec_registro',       'sql_type': 'DATE',        'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha de afiliacion al programa'},
        {'name': 'id_ciudad',          'sql_type': 'INT',         'pandas_type': 'int64',  'nullable': True,  'pii': False, 'description': 'Ciudad de residencia del miembro'},
        {'name': 'genero',             'sql_type': 'VARCHAR(1)',  'pandas_type': 'string', 'nullable': True,  'pii': True,  'description': 'Genero: M, F u otro'},
        {'name': 'rango_edad',         'sql_type': 'VARCHAR(10)', 'pandas_type': 'string', 'nullable': True,  'pii': True,  'description': 'Rango de edad: 18-25, 26-35, etc.'},
        {'name': 'canal_pref',         'sql_type': 'VARCHAR(20)', 'pandas_type': 'string', 'nullable': True,  'pii': False, 'description': 'Canal preferido: TIENDA, WEB, MKT, APP'},
        {'name': 'activo',             'sql_type': 'BIT',         'pandas_type': 'boolean','nullable': False, 'pii': False, 'description': 'Miembro activo en programa'},
        {'name': 'fec_ultima_compra',  'sql_type': 'DATE',        'pandas_type': 'datetime64[ns]', 'nullable': True,  'pii': False, 'description': 'Fecha de ultima transaccion del miembro'},
    ],
}

TRANS_VENTAS: TableDef = {
    'description': 'Hechos de transacciones de venta. Grain: una fila por linea de venta (articulo en un ticket).',
    'pk': 'id_trans',
    'fks': [
        {'column': 'id_miembro', 'references': 'CRM_MIEMBROS.id_miembro'},
        {'column': 'id_tienda',  'references': 'MSTR_TIENDAS.id_tienda'},
        {'column': 'art_id',     'references': 'MSTR_ARTICULOS.art_id'},
    ],
    'columns': [
        {'name': 'id_trans',              'sql_type': 'BIGINT',         'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico de la transaccion (PK)'},
        {'name': 'id_miembro',            'sql_type': 'INT',            'pandas_type': 'Int64',  'nullable': True,  'pii': False, 'description': 'FK al miembro (NULL si es cliente anonimo)'},
        {'name': 'id_tienda',             'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK a la tienda donde ocurrio la venta'},
        {'name': 'art_id',                'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK al articulo vendido'},
        {'name': 'fec_trans',             'sql_type': 'DATE',           'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha de la transaccion'},
        {'name': 'hra_trans',             'sql_type': 'TIME',           'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Hora HH:MM:SS de la transaccion'},
        {'name': 'qty_vendida',           'sql_type': 'INT',            'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'Cantidad de unidades vendidas'},
        {'name': 'precio_unitario_venta', 'sql_type': 'DECIMAL(12,2)',  'pandas_type': 'float64','nullable': False, 'pii': False, 'description': 'Precio unitario aplicado en la venta'},
        {'name': 'descuento_aplicado',    'sql_type': 'DECIMAL(12,2)',  'pandas_type': 'float64','nullable': True,  'pii': False, 'description': 'Monto de descuento aplicado en moneda local'},
        {'name': 'tipo_pago',             'sql_type': 'VARCHAR(20)',    'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Medio de pago: EFECTIVO, TARJETA, PSE, NEQUI, etc.'},
        {'name': 'canal_venta',           'sql_type': 'VARCHAR(20)',    'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Canal: TIENDA, WEB, MKT o APP'},
    ],
}

INV_STOCK_DIARIO: TableDef = {
    'description': 'Snapshot diario de inventario por articulo y tienda. Grain: una fila por (articulo, tienda, fecha).',
    'pk': 'id_snapshot',
    'fks': [
        {'column': 'art_id',    'references': 'MSTR_ARTICULOS.art_id'},
        {'column': 'id_tienda', 'references': 'MSTR_TIENDAS.id_tienda'},
    ],
    'columns': [
        {'name': 'id_snapshot',          'sql_type': 'BIGINT', 'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'ID unico del snapshot (PK)'},
        {'name': 'art_id',               'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'FK al articulo'},
        {'name': 'id_tienda',            'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'FK a la tienda'},
        {'name': 'fec_snapshot',         'sql_type': 'DATE',   'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha del snapshot diario'},
        {'name': 'stock_fisico',         'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'Unidades fisicas disponibles en piso/bodega'},
        {'name': 'stock_transito',       'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': True,  'pii': False, 'description': 'Unidades en transito desde CD'},
        {'name': 'stock_reservado',      'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': True,  'pii': False, 'description': 'Unidades reservadas (ecommerce, click and collect)'},
        {'name': 'stock_minimo_config',  'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'Stock minimo configurado para alerta'},
        {'name': 'stock_maximo_config',  'sql_type': 'INT',    'pandas_type': 'int64', 'nullable': False, 'pii': False, 'description': 'Stock maximo configurado (sobrestock)'},
    ],
}

POST_DEVOLUCIONES: TableDef = {
    'description': 'Hechos de devoluciones post-venta. Grain: una fila por linea devuelta de una venta original.',
    'pk': 'id_devolucion',
    'fks': [
        {'column': 'id_trans_origen', 'references': 'TRANS_VENTAS.id_trans'},
        {'column': 'art_id',          'references': 'MSTR_ARTICULOS.art_id'},
        {'column': 'id_tienda',       'references': 'MSTR_TIENDAS.id_tienda'},
    ],
    'columns': [
        {'name': 'id_devolucion',     'sql_type': 'BIGINT',        'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'ID unico de la devolucion (PK)'},
        {'name': 'id_trans_origen',   'sql_type': 'BIGINT',        'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK a la transaccion original'},
        {'name': 'art_id',            'sql_type': 'INT',           'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK al articulo devuelto'},
        {'name': 'id_tienda',         'sql_type': 'INT',           'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'FK a la tienda donde se procesa la devolucion'},
        {'name': 'fec_devolucion',    'sql_type': 'DATE',          'pandas_type': 'datetime64[ns]', 'nullable': False, 'pii': False, 'description': 'Fecha de la devolucion'},
        {'name': 'qty_devuelta',      'sql_type': 'INT',           'pandas_type': 'int64',  'nullable': False, 'pii': False, 'description': 'Cantidad de unidades devueltas'},
        {'name': 'motivo_cod',        'sql_type': 'VARCHAR(20)',   'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Codigo del motivo de devolucion'},
        {'name': 'canal_devolucion',  'sql_type': 'VARCHAR(20)',   'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Canal por donde se procesa la devolucion'},
        {'name': 'estado_devolucion', 'sql_type': 'VARCHAR(20)',   'pandas_type': 'string', 'nullable': False, 'pii': False, 'description': 'Estado: PROCESADA, APROBADA, RECHAZADA, REEMBOLSADA'},
        {'name': 'vr_reembolso',      'sql_type': 'DECIMAL(12,2)', 'pandas_type': 'float64','nullable': True,  'pii': False, 'description': 'Monto del reembolso en moneda local'},
    ],
}


# Orden de declaracion = orden de generacion (respeta dependencias de FKs)
TABLES: Dict[str, TableDef] = {
    'MSTR_PROVEEDORES':   MSTR_PROVEEDORES,
    'MSTR_TIENDAS':       MSTR_TIENDAS,
    'MSTR_ARTICULOS':     MSTR_ARTICULOS,
    'CRM_MIEMBROS':       CRM_MIEMBROS,
    'TRANS_VENTAS':       TRANS_VENTAS,
    'INV_STOCK_DIARIO':   INV_STOCK_DIARIO,
    'POST_DEVOLUCIONES':  POST_DEVOLUCIONES,
}


# Catalogos controlados
MOTIVOS_DEVOLUCION = {
    'DEFECTUOSO':     {'weight': 0.30, 'desc': 'Articulo defectuoso o danado'},
    'NO_DESEADO':     {'weight': 0.22, 'desc': 'Cliente cambio de opinion'},
    'TALLA':          {'weight': 0.18, 'desc': 'Talla incorrecta (ropa/calzado)'},
    'INCOMPLETO':     {'weight': 0.10, 'desc': 'Paquete incompleto / faltantes'},
    'NO_CORRESPONDE': {'weight': 0.10, 'desc': 'No corresponde a lo solicitado'},
    'VENCIDO':        {'weight': 0.07, 'desc': 'Producto vencido o proximo a vencer'},
    'OTRO':           {'weight': 0.03, 'desc': 'Otro motivo no clasificado'},
}

ESTADOS_DEVOLUCION = {
    'PROCESADA':   {'weight': 0.40},
    'APROBADA':    {'weight': 0.25},
    'REEMBOLSADA': {'weight': 0.25},
    'RECHAZADA':   {'weight': 0.10},
}

TIPOS_PAGO = {
    'EFECTIVO':  {'weight': 0.25},
    'TARJETA':   {'weight': 0.42},
    'PSE':       {'weight': 0.10},
    'NEQUI':     {'weight': 0.08},
    'DAVIPLATA': {'weight': 0.05},
    'TRANSFER':  {'weight': 0.05},
    'CREDITO':   {'weight': 0.05},
}

UNIDADES_MEDIDA = ['UN', 'KG', 'LT', 'MT', 'CC']

RANGOS_EDAD = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']


def get_table_columns(table_name: str) -> List[str]:
    return [c['name'] for c in TABLES[table_name]['columns']]


def get_pii_columns(table_name: str) -> List[str]:
    return [c['name'] for c in TABLES[table_name]['columns'] if c['pii']]


def get_create_table_sql(table_name: str, schema: str = 'dbo') -> str:
    """Genera el CREATE TABLE en T-SQL para una tabla."""
    table = TABLES[table_name]
    cols_sql = []
    for c in table['columns']:
        null_part = 'NULL' if c['nullable'] else 'NOT NULL'
        cols_sql.append(f"    [{c['name']}] {c['sql_type']} {null_part}")
    body = ",\n".join(cols_sql)
    return (
        f"-- {table['description']}\n"
        f"-- PK: {table['pk']}\n"
        + (f"-- FKs: " + "; ".join(f"{fk['column']} -> {fk['references']}" for fk in table['fks']) + "\n" if table['fks'] else "")
        + f"CREATE TABLE [{schema}].[{table_name}] (\n{body}\n);"
    )


if __name__ == '__main__':
    for name, t in TABLES.items():
        n_cols = len(t['columns'])
        n_pii = len(get_pii_columns(name))
        n_fks = len(t['fks'])
        print(f"  {name:22s}  cols={n_cols:2d}  pii={n_pii}  fks={n_fks}  pk={t['pk']}")
    print(f"Total tablas: {len(TABLES)}")
