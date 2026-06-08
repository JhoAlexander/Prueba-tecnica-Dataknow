"""Generador de INV_STOCK_DIARIO (depende de articulos y tiendas).

Construye 25.000 pares (articulo, tienda) y los proyecta sobre los
ultimos 30 dias para obtener snapshots diarios.
"""
import numpy as np
import pandas as pd

from schemas import INV_STOCK_DIARIO
from auxiliares import cast_to_schema, inject_nulls


STOCK_MIN_POR_CATEG = {
    1: 10,
    2: 8,
    3: 10,
    4: 3,
    5: 5,
    6: 8,
}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator,
             articulos: pd.DataFrame = None,
             tiendas: pd.DataFrame = None) -> pd.DataFrame:
    for name, dep in (('articulos', articulos), ('tiendas', tiendas)):
        if dep is None:
            raise ValueError(f"Se requiere DataFrame de {name} como dependencia")

    n_objetivo = cfg['volumes']['inv_stock_diario']
    n_dias = 30
    n_pares = n_objetivo // n_dias

    art_active = articulos.loc[articulos['activo'] == True, ['art_id', 'id_categ_n1']].copy()
    tienda_ids = tiendas.loc[tiendas['activo'] == True, 'id_tienda'].to_numpy()

    sampled_arts = rng.choice(art_active['art_id'].to_numpy(), size=n_pares, replace=True)
    sampled_tiendas = rng.choice(tienda_ids, size=n_pares, replace=True)
    pares = pd.DataFrame({
        'art_id': sampled_arts,
        'id_tienda': sampled_tiendas,
    }).drop_duplicates().reset_index(drop=True)

    while len(pares) < n_pares:
        falta = n_pares - len(pares)
        extra_arts = rng.choice(art_active['art_id'].to_numpy(), size=falta, replace=True)
        extra_tiendas = rng.choice(tienda_ids, size=falta, replace=True)
        extra = pd.DataFrame({'art_id': extra_arts, 'id_tienda': extra_tiendas})
        pares = pd.concat([pares, extra], ignore_index=True).drop_duplicates().reset_index(drop=True)

    pares = pares.head(n_pares)

    cat_map = art_active.set_index('art_id')['id_categ_n1']
    pares['id_categ_n1'] = pares['art_id'].map(cat_map)

    fec_fin = pd.Timestamp(cfg['date_range']['end'])
    fechas = pd.date_range(end=fec_fin, periods=n_dias, freq='D')

    df = pares.merge(pd.DataFrame({'fec_snapshot': fechas}), how='cross')
    n = len(df)

    df['id_snapshot'] = np.arange(1, n + 1, dtype=np.int64)
    df['stock_minimo_config'] = df['id_categ_n1'].map(STOCK_MIN_POR_CATEG).astype(int)
    df['stock_maximo_config'] = df['stock_minimo_config'] * 3
    df['stock_fisico'] = rng.poisson(lam=15, size=n).astype(int)

    has_transito = rng.random(n) < 0.30
    df['stock_transito'] = np.where(has_transito, rng.poisson(lam=10, size=n), 0).astype(int)

    has_reservado = rng.random(n) < 0.20
    df['stock_reservado'] = np.where(has_reservado, rng.poisson(lam=5, size=n), 0).astype(int)

    df = df.drop(columns=['id_categ_n1'])

    df = inject_nulls(df, ['stock_transito', 'stock_reservado'],
                      cfg['quality']['null_rate'], rng)
    return cast_to_schema(df, INV_STOCK_DIARIO)


if __name__ == '__main__':
    import time
    from auxiliares import load_config, init_random, make_rng
    from gen_01_proveedores import generate as gen_proveedores
    from gen_02_tiendas import generate as gen_tiendas
    from gen_03_articulos import generate as gen_articulos

    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df_prov = gen_proveedores(cfg, fakes, rng)
    df_tiendas = gen_tiendas(cfg, fakes, rng)
    df_art = gen_articulos(cfg, fakes, rng, proveedores=df_prov)

    t0 = time.time()
    df = generate(cfg, fakes, rng, articulos=df_art, tiendas=df_tiendas)
    print(f"{len(df):,} snapshots en {time.time()-t0:.1f}s")
    print(df['stock_fisico'].describe().round(1))
    print("FK articulo:", df['art_id'].isin(df_art['art_id']).all())
    print("FK tienda:", df['id_tienda'].isin(df_tiendas['id_tienda']).all())
