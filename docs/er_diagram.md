# Diagrama Entidad-Relacion (ER) — RetailMax

> Autogenerado por `docs/gen_er_diagram.py` a partir de
> `data-generation/schemas.py`. Regenerar con `python docs/gen_er_diagram.py`.

## Vista general

```mermaid
erDiagram

    MSTR_PROVEEDORES {
        int id_proveedor "PK"
        string razon_social "PII"
        string pais_origen
        int tiempo_repo_dias
        decimal calificacion_calidad
        bool activo
    }

    MSTR_TIENDAS {
        int id_tienda "PK"
        string nom_tienda
        string tipo_tienda
        int id_ciudad
        string id_pais
        int metros_cuadrados
        bool activo
        date fec_apertura
    }

    MSTR_ARTICULOS {
        int art_id "PK"
        string cod_barra
        string desc_art
        int id_categ_n1
        int id_categ_n2
        int id_categ_n3
        int id_proveedor "FK"
        decimal precio_lista
        decimal peso_kg
        string unid_medida
        bool activo
        date fec_alta
    }

    CRM_MIEMBROS {
        int id_miembro "PK"
        date fec_registro
        int id_ciudad
        string genero "PII"
        string rango_edad "PII"
        string canal_pref
        bool activo
        date fec_ultima_compra
    }

    TRANS_VENTAS {
        int id_trans "PK"
        int id_miembro "FK"
        int id_tienda "FK"
        int art_id "FK"
        date fec_trans
        time hra_trans
        int qty_vendida
        decimal precio_unitario_venta
        decimal descuento_aplicado
        string tipo_pago
        string canal_venta
    }

    INV_STOCK_DIARIO {
        int id_snapshot "PK"
        int art_id "FK"
        int id_tienda "FK"
        date fec_snapshot
        int stock_fisico
        int stock_transito
        int stock_reservado
        int stock_minimo_config
        int stock_maximo_config
    }

    POST_DEVOLUCIONES {
        int id_devolucion "PK"
        int id_trans_origen "FK"
        int art_id "FK"
        int id_tienda "FK"
        date fec_devolucion
        int qty_devuelta
        string motivo_cod
        string canal_devolucion
        string estado_devolucion
        decimal vr_reembolso
    }

    MSTR_PROVEEDORES ||--o{ MSTR_ARTICULOS : "abastece"
    MSTR_ARTICULOS ||--o{ TRANS_VENTAS : "se vende en"
    MSTR_TIENDAS ||--o{ TRANS_VENTAS : "ocurre en"
    CRM_MIEMBROS |o--o{ TRANS_VENTAS : "realiza (opcional)"
    MSTR_ARTICULOS ||--o{ INV_STOCK_DIARIO : "tiene stock"
    MSTR_TIENDAS ||--o{ INV_STOCK_DIARIO : "almacena"
    TRANS_VENTAS ||--o{ POST_DEVOLUCIONES : "es devuelta"
    MSTR_ARTICULOS ||--o{ POST_DEVOLUCIONES : "se devuelve"
    MSTR_TIENDAS ||--o{ POST_DEVOLUCIONES : "procesa devolucion"
```

## Convenciones

| Etiqueta | Significado |
|---|---|
| `PK`  | Primary Key |
| `FK`  | Foreign Key |
| `PII` | Informacion personal identificable (se enmascara desde Silver) |
| `||--o{`  | Relacion uno a muchos (mandatoria del lado uno) |
| `|o--o{`  | Relacion uno a muchos (opcional) |

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
| `MSTR_PROVEEDORES` | 800 |
| `MSTR_TIENDAS` | 150 |
| `MSTR_ARTICULOS` | 5,000 |
| `CRM_MIEMBROS` | 50,000 |
| `TRANS_VENTAS` | 1,000,000 |
| `INV_STOCK_DIARIO` | 750,000 |
| `POST_DEVOLUCIONES` | 50,000 |

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
