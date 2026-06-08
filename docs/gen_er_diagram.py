"""Genera el diagrama ER en Mermaid a partir de schemas.py.

Produce docs/er_diagram.md, renderizable directamente en GitHub/GitLab.

Uso:
    python docs/gen_er_diagram.py
"""
import sys
from pathlib import Path

DOC_DIR = Path(__file__).parent
ROOT = DOC_DIR.parent
sys.path.insert(0, str(ROOT / 'data-generation'))

from schemas import TABLES  # noqa: E402


RELACIONES_NEGOCIO = {
    ('MSTR_PROVEEDORES',  'MSTR_ARTICULOS'):    ('||--o{', 'abastece'),
    ('MSTR_ARTICULOS',    'TRANS_VENTAS'):      ('||--o{', 'se vende en'),
    ('MSTR_TIENDAS',      'TRANS_VENTAS'):      ('||--o{', 'ocurre en'),
    ('CRM_MIEMBROS',      'TRANS_VENTAS'):      ('|o--o{', 'realiza (opcional)'),
    ('MSTR_ARTICULOS',    'INV_STOCK_DIARIO'):  ('||--o{', 'tiene stock'),
    ('MSTR_TIENDAS',      'INV_STOCK_DIARIO'):  ('||--o{', 'almacena'),
    ('TRANS_VENTAS',      'POST_DEVOLUCIONES'): ('||--o{', 'es devuelta'),
    ('MSTR_ARTICULOS',    'POST_DEVOLUCIONES'): ('||--o{', 'se devuelve'),
    ('MSTR_TIENDAS',      'POST_DEVOLUCIONES'): ('||--o{', 'procesa devolucion'),
}


def mermaid_type(sql_type: str) -> str:
    s = sql_type.upper()
    if s.startswith('INT') or s.startswith('BIGINT'):
        return 'int'
    if s.startswith('DECIMAL') or s.startswith('FLOAT'):
        return 'decimal'
    if s.startswith('VARCHAR') or s.startswith('CHAR'):
        return 'string'
    if s.startswith('DATE') or s.startswith('TIME'):
        return s.lower()
    if s.startswith('BIT'):
        return 'bool'
    return s.lower()


def build_mermaid_block() -> str:
    lines = ['erDiagram', '']

    for table_name, table in TABLES.items():
        lines.append(f"    {table_name} {{")
        for col in table['columns']:
            mtype = mermaid_type(col['sql_type'])
            mname = col['name']
            tags = []
            if col['name'] == table['pk']:
                tags.append('PK')
            for fk in table['fks']:
                if fk['column'] == col['name']:
                    tags.append('FK')
            if col['pii']:
                tags.append('PII')
            tag_str = (' "' + ', '.join(tags) + '"') if tags else ''
            lines.append(f"        {mtype} {mname}{tag_str}")
        lines.append("    }")
        lines.append("")

    for (src, dst), (card, label) in RELACIONES_NEGOCIO.items():
        lines.append(f'    {src} {card} {dst} : "{label}"')

    return '\n'.join(lines)


def build_markdown() -> str:
    mermaid = build_mermaid_block()

    md = f'''# Diagrama Entidad-Relacion (ER) — RetailMax

> Autogenerado por `docs/gen_er_diagram.py` a partir de
> `data-generation/schemas.py`. Regenerar con `python docs/gen_er_diagram.py`.

## Vista general

```mermaid
{mermaid}
```

## Convenciones

| Etiqueta | Significado |
|---|---|
| `PK`  | Primary Key |
| `FK`  | Foreign Key |
| `PII` | Informacion personal identificable (se enmascara desde Silver) |
| `||--o{{`  | Relacion uno a muchos (mandatoria del lado uno) |
| `|o--o{{`  | Relacion uno a muchos (opcional) |

## Clasificacion de tablas

### Dimensiones
1. **MSTR_PROVEEDORES** — Proveedores de articulos
2. **MSTR_TIENDAS** — Red de tiendas fisicas
3. **MSTR_ARTICULOS** — Catalogo de SKUs con jerarquia de categorias
4. **CRM_MIEMBROS** — Miembros del programa de fidelizacion

### Hechos
5. **TRANS_VENTAS** — Lineas de venta (grain: una linea por articulo en un ticket)
6. **INV_STOCK_DIARIO** — Snapshots diarios de inventario por (articulo, tienda)
7. **POST_DEVOLUCIONES** — Devoluciones post-venta

## Volumenes

| Tabla | Filas |
|---|---:|
'''
    sys.path.insert(0, str(ROOT / 'data-generation'))
    from auxiliares import load_config
    cfg = load_config(str(ROOT / 'data-generation' / 'config.yaml'))
    vol_key_map = {
        'MSTR_PROVEEDORES':  'mstr_proveedores',
        'MSTR_TIENDAS':      'mstr_tiendas',
        'MSTR_ARTICULOS':    'mstr_articulos',
        'CRM_MIEMBROS':      'crm_miembros',
        'TRANS_VENTAS':      'trans_ventas',
        'INV_STOCK_DIARIO':  'inv_stock_diario',
        'POST_DEVOLUCIONES': 'post_devoluciones',
    }
    for table_name in TABLES:
        vol = cfg['volumes'][vol_key_map[table_name]]
        md += f"| `{table_name}` | {vol:,} |\n"

    md += '''
## Relaciones

| Origen | Destino | Cardinalidad | Significado |
|---|---|---|---|
| `MSTR_PROVEEDORES` | `MSTR_ARTICULOS` | 1 : N | Un proveedor abastece muchos articulos |
| `MSTR_ARTICULOS` | `TRANS_VENTAS` | 1 : N | Un articulo se vende en muchas transacciones |
| `MSTR_TIENDAS` | `TRANS_VENTAS` | 1 : N | Una tienda registra muchas ventas |
| `CRM_MIEMBROS` | `TRANS_VENTAS` | 0..1 : N | 30% de las ventas son anonimas (id_miembro NULL) |
| `MSTR_ARTICULOS` | `INV_STOCK_DIARIO` | 1 : N | Un articulo tiene un snapshot por (tienda, dia) |
| `MSTR_TIENDAS` | `INV_STOCK_DIARIO` | 1 : N | Una tienda mantiene snapshot de su catalogo cada dia |
| `TRANS_VENTAS` | `POST_DEVOLUCIONES` | 1 : 0..N | Una venta puede generar 0 o mas devoluciones |
| `MSTR_ARTICULOS` | `POST_DEVOLUCIONES` | 1 : N | El articulo devuelto se valida contra el catalogo |
| `MSTR_TIENDAS` | `POST_DEVOLUCIONES` | 1 : N | La tienda que procesa la devolucion |
'''
    return md


def main():
    md = build_markdown()
    out_path = DOC_DIR / 'er_diagram.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Diagrama ER generado: {out_path}")
    print(f"  {len(TABLES)} tablas, {len(RELACIONES_NEGOCIO)} relaciones")


if __name__ == '__main__':
    main()
