"""Generador de MSTR_TIENDAS."""
import numpy as np
import pandas as pd

from schemas import MSTR_TIENDAS
from auxiliares import (
    weighted_choice, cast_to_schema, inject_nulls, random_dates,
)


def generate(cfg: dict, fakes: dict, rng: np.random.Generator) -> pd.DataFrame:
    n = cfg['volumes']['mstr_tiendas']
    ids = np.arange(1, n + 1)

    countries = cfg['countries']
    country_codes = [c['code'] for c in countries]
    country_weights = [c['weight'] for c in countries]
    pais_assign = weighted_choice(country_codes, country_weights, n, rng)

    store_types = cfg['store_types']
    type_codes = [s['code'] for s in store_types]
    type_weights = [s['weight'] for s in store_types]
    avg_sqm_by_type = {s['code']: s['avg_sqm'] for s in store_types}
    tipo_assign = weighted_choice(type_codes, type_weights, n, rng)

    sqm = np.zeros(n, dtype=int)
    for i, tipo in enumerate(tipo_assign):
        avg = avg_sqm_by_type[tipo]
        val = rng.normal(loc=avg, scale=avg * 0.20)
        sqm[i] = int(np.clip(round(val), 50, avg * 3))

    nombres = []
    for p in pais_assign:
        ciudad = fakes[p].city().replace(',', '')
        nombres.append(f"RetailMax {ciudad}")

    id_ciudad = rng.integers(1, 51, size=n)
    fec_apertura = random_dates('1998-01-01', '2025-12-31', n, rng)
    activo = rng.random(n) < 0.95

    df = pd.DataFrame({
        'id_tienda': ids,
        'nom_tienda': nombres,
        'tipo_tienda': tipo_assign,
        'id_ciudad': id_ciudad,
        'id_pais': pais_assign,
        'metros_cuadrados': sqm,
        'activo': activo,
        'fec_apertura': fec_apertura,
    })

    df = inject_nulls(df, ['metros_cuadrados'], cfg['quality']['null_rate'], rng)
    return cast_to_schema(df, MSTR_TIENDAS)


if __name__ == '__main__':
    from auxiliares import load_config, init_random, make_rng
    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df = generate(cfg, fakes, rng)
    print(f"{len(df)} tiendas")
    print(df['id_pais'].value_counts(normalize=True).round(3))
    print(df['tipo_tienda'].value_counts(normalize=True).round(3))
