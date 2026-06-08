"""Generador de TRANS_VENTAS (depende de tiendas, articulos y miembros)."""
import numpy as np
import pandas as pd

from schemas import TRANS_VENTAS, TIPOS_PAGO
from auxiliares import (
    weighted_choice, weighted_dict_choice,
    cast_to_schema, inject_nulls,
    seasonal_dates, peak_hours, hours_to_time_strings,
)


# Rotacion relativa por categoria (alimentos rotan mucho mas que electronica)
PESOS_CATEG_VENTAS = {
    1: 0.40,
    2: 0.22,
    3: 0.18,
    4: 0.05,
    5: 0.08,
    6: 0.07,
}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator,
             tiendas: pd.DataFrame = None,
             articulos: pd.DataFrame = None,
             miembros: pd.DataFrame = None) -> pd.DataFrame:
    for name, dep in (('tiendas', tiendas), ('articulos', articulos), ('miembros', miembros)):
        if dep is None:
            raise ValueError(f"Se requiere DataFrame de {name} como dependencia")

    n = cfg['volumes']['trans_ventas']
    ids = np.arange(1, n + 1, dtype=np.int64)

    fec_trans = seasonal_dates(
        cfg['date_range']['start'],
        cfg['date_range']['end'],
        cfg['distributions']['monthly_seasonality'],
        n, rng,
    )

    horas = peak_hours(
        cfg['distributions']['hour_peaks'],
        cfg['distributions']['hour_peak_std'],
        n, rng,
    )
    hra_trans = hours_to_time_strings(horas, rng)

    tienda_ids = tiendas['id_tienda'].to_numpy()
    id_tienda = rng.choice(tienda_ids, size=n, replace=True)

    # Peso por articulo = peso de su categoria repartido entre los articulos de esa categoria
    art_active = articulos.loc[articulos['activo'] == True].copy()
    art_active['cat_weight'] = art_active['id_categ_n1'].map(PESOS_CATEG_VENTAS)
    counts_by_cat = art_active.groupby('id_categ_n1')['art_id'].transform('count')
    art_active['weight'] = art_active['cat_weight'] / counts_by_cat
    art_active['weight'] = art_active['weight'] / art_active['weight'].sum()

    art_ids = art_active['art_id'].to_numpy()
    art_weights = art_active['weight'].to_numpy()
    art_id = rng.choice(art_ids, size=n, p=art_weights, replace=True)

    # 70% con miembro, 30% anonimo (NaN -> Int64 nullable en cast_to_schema)
    miembro_ids = miembros['id_miembro'].to_numpy()
    id_miembro_raw = rng.choice(miembro_ids, size=n, replace=True)
    has_miembro = rng.random(n) < 0.70
    id_miembro = np.where(has_miembro, id_miembro_raw, np.nan)

    qty_vendida = rng.poisson(lam=1.5, size=n) + 1

    precios_map = articulos.set_index('art_id')['precio_lista']
    precio_base = pd.Series(art_id).map(precios_map).to_numpy()
    variacion = rng.uniform(0.90, 1.10, size=n)
    precio_unitario_venta = np.round(precio_base * variacion, 2)

    tiene_descuento = rng.random(n) < 0.30
    porc_descuento = rng.uniform(0.05, 0.30, size=n)
    subtotal = precio_unitario_venta * qty_vendida
    descuento_aplicado = np.where(
        tiene_descuento,
        np.round(subtotal * porc_descuento, 2),
        0.0,
    )

    tipo_pago = weighted_dict_choice(TIPOS_PAGO, n, rng)

    channels = cfg['sales_channels']
    chan_codes = [c['code'] for c in channels]
    chan_weights = [c['weight'] for c in channels]
    canal_venta = weighted_choice(chan_codes, chan_weights, n, rng)

    df = pd.DataFrame({
        'id_trans': ids,
        'id_miembro': id_miembro,
        'id_tienda': id_tienda,
        'art_id': art_id,
        'fec_trans': fec_trans,
        'hra_trans': hra_trans,
        'qty_vendida': qty_vendida,
        'precio_unitario_venta': precio_unitario_venta,
        'descuento_aplicado': descuento_aplicado,
        'tipo_pago': tipo_pago,
        'canal_venta': canal_venta,
    })

    df = inject_nulls(df, ['descuento_aplicado'], cfg['quality']['null_rate'], rng)
    return cast_to_schema(df, TRANS_VENTAS)


if __name__ == '__main__':
    import time
    from auxiliares import load_config, init_random, make_rng
    from gen_01_proveedores import generate as gen_proveedores
    from gen_02_tiendas import generate as gen_tiendas
    from gen_03_articulos import generate as gen_articulos
    from gen_04_miembros import generate as gen_miembros

    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df_prov = gen_proveedores(cfg, fakes, rng)
    df_tiendas = gen_tiendas(cfg, fakes, rng)
    df_art = gen_articulos(cfg, fakes, rng, proveedores=df_prov)
    df_miembros = gen_miembros(cfg, fakes, rng)

    t0 = time.time()
    df = generate(cfg, fakes, rng,
                  tiendas=df_tiendas, articulos=df_art, miembros=df_miembros)
    print(f"{len(df):,} ventas en {time.time()-t0:.1f}s")
    print(df['fec_trans'].dt.month.value_counts().sort_index())
    print("FK tienda:", df['id_tienda'].isin(df_tiendas['id_tienda']).all())
    print("FK articulo:", df['art_id'].isin(df_art['art_id']).all())
