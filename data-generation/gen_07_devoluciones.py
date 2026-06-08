"""Generador de POST_DEVOLUCIONES (depende de ventas, articulos y tiendas)."""
import numpy as np
import pandas as pd

from schemas import POST_DEVOLUCIONES, MOTIVOS_DEVOLUCION, ESTADOS_DEVOLUCION
from auxiliares import (
    weighted_dict_choice, weighted_choice,
    cast_to_schema, inject_nulls,
)


FACTOR_REEMBOLSO = {
    'REEMBOLSADA': 1.00,
    'APROBADA':    0.95,
    'PROCESADA':   0.90,
    'RECHAZADA':   0.00,
}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator,
             ventas: pd.DataFrame = None,
             articulos: pd.DataFrame = None,
             tiendas: pd.DataFrame = None) -> pd.DataFrame:
    for name, dep in (('ventas', ventas), ('articulos', articulos), ('tiendas', tiendas)):
        if dep is None:
            raise ValueError(f"Se requiere DataFrame de {name} como dependencia")

    n = cfg['volumes']['post_devoluciones']

    # Cada transaccion se devuelve una sola vez (sin reemplazo)
    ventas_sample_idx = rng.choice(len(ventas), size=n, replace=False)
    ventas_origen = ventas.iloc[ventas_sample_idx].reset_index(drop=True)

    ids = np.arange(1, n + 1, dtype=np.int64)
    id_trans_origen = ventas_origen['id_trans'].to_numpy()
    art_id = ventas_origen['art_id'].to_numpy()
    id_tienda = ventas_origen['id_tienda'].to_numpy()

    dias_offset = np.clip(rng.poisson(lam=7, size=n), 1, 30)
    fec_devolucion = pd.to_datetime(ventas_origen['fec_trans']) + pd.to_timedelta(dias_offset, unit='D')

    qty_vendida_orig = ventas_origen['qty_vendida'].to_numpy()
    qty_devuelta = np.where(
        rng.random(n) < 0.80,
        1,
        rng.integers(1, qty_vendida_orig + 1)
    ).astype(int)
    qty_devuelta = np.minimum(qty_devuelta, qty_vendida_orig)

    motivo_cod = weighted_dict_choice(MOTIVOS_DEVOLUCION, n, rng)
    estado_devolucion = weighted_dict_choice(ESTADOS_DEVOLUCION, n, rng)

    # 80% se devuelve por el mismo canal de la compra
    canal_venta_orig = ventas_origen['canal_venta'].to_numpy()
    channels = cfg['sales_channels']
    chan_codes = [c['code'] for c in channels]
    chan_weights = [c['weight'] for c in channels]
    canal_otros = weighted_choice(chan_codes, chan_weights, n, rng)
    same_channel = rng.random(n) < 0.80
    canal_devolucion = np.where(same_channel, canal_venta_orig, canal_otros)

    precio_unitario_orig = ventas_origen['precio_unitario_venta'].to_numpy()
    factor = np.array([FACTOR_REEMBOLSO[e] for e in estado_devolucion])
    vr_reembolso = np.round(precio_unitario_orig * qty_devuelta * factor, 2)

    df = pd.DataFrame({
        'id_devolucion': ids,
        'id_trans_origen': id_trans_origen,
        'art_id': art_id,
        'id_tienda': id_tienda,
        'fec_devolucion': fec_devolucion,
        'qty_devuelta': qty_devuelta,
        'motivo_cod': motivo_cod,
        'canal_devolucion': canal_devolucion,
        'estado_devolucion': estado_devolucion,
        'vr_reembolso': vr_reembolso,
    })

    df = inject_nulls(df, ['vr_reembolso'], cfg['quality']['null_rate'], rng)
    return cast_to_schema(df, POST_DEVOLUCIONES)


if __name__ == '__main__':
    import time
    from auxiliares import load_config, init_random, make_rng
    from gen_01_proveedores import generate as gen_proveedores
    from gen_02_tiendas import generate as gen_tiendas
    from gen_03_articulos import generate as gen_articulos
    from gen_04_miembros import generate as gen_miembros
    from gen_05_ventas import generate as gen_ventas

    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df_prov = gen_proveedores(cfg, fakes, rng)
    df_tiendas = gen_tiendas(cfg, fakes, rng)
    df_art = gen_articulos(cfg, fakes, rng, proveedores=df_prov)
    df_miembros = gen_miembros(cfg, fakes, rng)
    df_ventas = gen_ventas(cfg, fakes, rng,
                           tiendas=df_tiendas, articulos=df_art, miembros=df_miembros)

    t0 = time.time()
    df = generate(cfg, fakes, rng, ventas=df_ventas, articulos=df_art, tiendas=df_tiendas)
    print(f"{len(df):,} devoluciones en {time.time()-t0:.2f}s")
    print(f"Tasa devolucion: {len(df) / len(df_ventas):.1%}")
    print("FK venta:", df['id_trans_origen'].isin(df_ventas['id_trans']).all())
