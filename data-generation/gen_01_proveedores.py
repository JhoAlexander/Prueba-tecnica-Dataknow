"""Generador de MSTR_PROVEEDORES."""
import numpy as np
import pandas as pd

from schemas import MSTR_PROVEEDORES
from auxiliares import cast_to_schema, inject_nulls


PAISES_PROVEEDOR = {
    'CO': 0.30,
    'MX': 0.15,
    'US': 0.15,
    'CN': 0.15,
    'ES': 0.10,
    'BR': 0.08,
    'AR': 0.07,
}

SUFIJOS_PAIS = {
    'CO': ['S.A.S.', 'Ltda.', 'S.A.', '& Cia.'],
    'MX': ['S.A. de C.V.', 'S.C.', 'S.A.'],
    'US': ['Inc.', 'LLC', 'Corp.'],
    'CN': ['Co. Ltd.', 'Trading Co.', 'Group'],
    'ES': ['S.A.', 'S.L.', 'S.L.U.'],
    'BR': ['Ltda.', 'S.A.'],
    'AR': ['S.A.', 'S.R.L.'],
}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator) -> pd.DataFrame:
    n = cfg['volumes']['mstr_proveedores']
    ids = np.arange(1, n + 1)

    paises = list(PAISES_PROVEEDOR.keys())
    pesos = list(PAISES_PROVEEDOR.values())
    pais_origen = rng.choice(paises, size=n, p=pesos)

    fake_co = fakes['CO']
    razones = []
    for p in pais_origen:
        base = fake_co.company().replace(',', '')
        suf = rng.choice(SUFIJOS_PAIS[p])
        razones.append(f"{base} {suf}")

    # Lead time lognormal: mediana ~7 dias, cola larga para importados
    raw_lead = rng.lognormal(mean=2.0, sigma=0.6, size=n)
    tiempo_repo = np.clip(np.round(raw_lead), 1, 60).astype(int)

    raw_cal = rng.normal(loc=3.8, scale=0.6, size=n)
    calificacion = np.round(np.clip(raw_cal, 1.0, 5.0), 2)

    activo = rng.random(n) < 0.95

    df = pd.DataFrame({
        'id_proveedor': ids,
        'razon_social': razones,
        'pais_origen': pais_origen,
        'tiempo_repo_dias': tiempo_repo,
        'calificacion_calidad': calificacion,
        'activo': activo,
    })

    df = inject_nulls(df, ['calificacion_calidad'], cfg['quality']['null_rate'], rng)
    return cast_to_schema(df, MSTR_PROVEEDORES)


if __name__ == '__main__':
    from auxiliares import load_config, init_random, make_rng
    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df = generate(cfg, fakes, rng)
    print(f"{len(df)} proveedores")
    print(df['pais_origen'].value_counts(normalize=True).round(3))
    print(df.isna().sum())
