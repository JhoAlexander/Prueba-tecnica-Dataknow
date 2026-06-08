"""Generador de CRM_MIEMBROS."""
import numpy as np
import pandas as pd

from schemas import CRM_MIEMBROS, RANGOS_EDAD
from auxiliares import (
    weighted_choice, cast_to_schema, inject_nulls, random_dates,
)


# Orden: '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
PESOS_RANGO_EDAD = [0.22, 0.28, 0.22, 0.15, 0.08, 0.05]
GENERO_DIST = {'M': 0.48, 'F': 0.48, 'X': 0.04}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator) -> pd.DataFrame:
    n = cfg['volumes']['crm_miembros']
    ids = np.arange(1, n + 1)

    fec_registro = random_dates('2021-01-01', '2026-05-31', n, rng)
    id_ciudad = rng.integers(1, 101, size=n)

    genero = weighted_choice(
        list(GENERO_DIST.keys()), list(GENERO_DIST.values()), n, rng)
    rango_edad = weighted_choice(RANGOS_EDAD, PESOS_RANGO_EDAD, n, rng)

    channels = cfg['sales_channels']
    chan_codes = [c['code'] for c in channels]
    chan_weights = [c['weight'] for c in channels]
    canal_pref = weighted_choice(chan_codes, chan_weights, n, rng)

    activo = rng.random(n) < 0.90
    fec_ultima = random_dates('2024-01-01', '2026-05-31', n, rng)

    df = pd.DataFrame({
        'id_miembro': ids,
        'fec_registro': fec_registro,
        'id_ciudad': id_ciudad,
        'genero': genero,
        'rango_edad': rango_edad,
        'canal_pref': canal_pref,
        'activo': activo,
        'fec_ultima_compra': fec_ultima,
    })

    df = inject_nulls(
        df, ['genero', 'rango_edad', 'id_ciudad', 'canal_pref'],
        cfg['quality']['null_rate'], rng)
    # 15% nunca compraron
    df = inject_nulls(df, ['fec_ultima_compra'], 0.15, rng)
    return cast_to_schema(df, CRM_MIEMBROS)


if __name__ == '__main__':
    from auxiliares import load_config, init_random, make_rng
    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df = generate(cfg, fakes, rng)
    print(f"{len(df)} miembros")
    print(df['genero'].value_counts(normalize=True, dropna=False).round(3))
    print(df.isna().sum())
