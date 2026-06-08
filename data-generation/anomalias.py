"""Inyeccion de anomalias controladas en los datos sinteticos.

Patrones: duplicados naturales, fechas fuera de rango, montos negativos
y referencias huerfanas. Cada patron registra los IDs afectados para su
posterior validacion en la capa Silver.
"""
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


ART_ID_HUERFANO = 99999


def inject_duplicates(df_ventas: pd.DataFrame, ratio: float,
                      rng: np.random.Generator) -> tuple:
    """Duplica filas con id_trans nuevo pero misma clave de negocio."""
    n_dup = int(len(df_ventas) * ratio)
    if n_dup == 0:
        return df_ventas, []

    idx_to_dup = rng.choice(len(df_ventas), size=n_dup, replace=False)
    dups = df_ventas.iloc[idx_to_dup].copy()

    max_id = int(df_ventas['id_trans'].max())
    new_ids = np.arange(max_id + 1, max_id + 1 + n_dup, dtype=np.int64)
    dups['id_trans'] = new_ids

    df_modificado = pd.concat([df_ventas, dups], ignore_index=True)

    info = {
        'cantidad': n_dup,
        'ids_originales': df_ventas.iloc[idx_to_dup]['id_trans'].tolist()[:20],
        'ids_nuevos': new_ids.tolist()[:20],
        'total_filas_despues': len(df_modificado),
    }
    return df_modificado, info


def inject_future_dates(df_ventas: pd.DataFrame, count: int,
                        rng: np.random.Generator) -> tuple:
    """Asigna fechas de 2027 a N registros."""
    if count == 0:
        return df_ventas, {}

    idx = rng.choice(len(df_ventas), size=count, replace=False)
    offsets = rng.integers(0, 365, size=count)
    fechas_futuras = pd.Timestamp('2027-01-01') + pd.to_timedelta(offsets, unit='D')
    df_ventas.iloc[idx, df_ventas.columns.get_loc('fec_trans')] = fechas_futuras

    info = {
        'cantidad': count,
        'ids_afectados': df_ventas.iloc[idx]['id_trans'].tolist(),
        'rango_fechas': ['2027-01-01', '2027-12-31'],
    }
    return df_ventas, info


def inject_negative_amounts(df_ventas: pd.DataFrame, count: int,
                            rng: np.random.Generator) -> tuple:
    """Invierte el signo de precio_unitario_venta en N registros."""
    if count == 0:
        return df_ventas, {}

    idx = rng.choice(len(df_ventas), size=count, replace=False)
    col_loc = df_ventas.columns.get_loc('precio_unitario_venta')
    df_ventas.iloc[idx, col_loc] = df_ventas.iloc[idx, col_loc] * -1

    info = {
        'cantidad': count,
        'ids_afectados': df_ventas.iloc[idx]['id_trans'].tolist(),
    }
    return df_ventas, info


def inject_orphan_refs(df_ventas: pd.DataFrame, count: int,
                       rng: np.random.Generator) -> tuple:
    """Asigna un art_id inexistente a N registros."""
    if count == 0:
        return df_ventas, {}

    idx = rng.choice(len(df_ventas), size=count, replace=False)
    col_loc = df_ventas.columns.get_loc('art_id')
    df_ventas.iloc[idx, col_loc] = ART_ID_HUERFANO

    info = {
        'cantidad': count,
        'ids_afectados': df_ventas.iloc[idx]['id_trans'].tolist(),
        'art_id_huerfano_usado': ART_ID_HUERFANO,
    }
    return df_ventas, info


def apply_all_anomalies(dataframes: Dict[str, pd.DataFrame], cfg: dict,
                        rng: np.random.Generator,
                        output_dir: str = None) -> tuple:
    """Aplica los cuatro patrones de anomalias a TRANS_VENTAS."""
    anomalies_cfg = cfg['quality']['anomalies']
    log = {}

    df_ventas = dataframes['TRANS_VENTAS'].copy()
    n_inicial = len(df_ventas)

    df_ventas, info1 = inject_duplicates(
        df_ventas, anomalies_cfg['duplicates_ratio'], rng
    )
    log['duplicates'] = info1

    df_ventas, info2 = inject_future_dates(
        df_ventas, anomalies_cfg['future_dates_count'], rng
    )
    log['future_dates'] = info2

    df_ventas, info3 = inject_negative_amounts(
        df_ventas, anomalies_cfg['negative_amounts_count'], rng
    )
    log['negative_amounts'] = info3

    df_ventas, info4 = inject_orphan_refs(
        df_ventas, anomalies_cfg['orphan_refs_count'], rng
    )
    log['orphan_refs'] = info4

    log['summary'] = {
        'filas_iniciales': n_inicial,
        'filas_finales': len(df_ventas),
        'filas_anomalas_total': (
            info1.get('cantidad', 0)
            + info2.get('cantidad', 0)
            + info3.get('cantidad', 0)
            + info4.get('cantidad', 0)
        ),
    }

    dataframes['TRANS_VENTAS'] = df_ventas

    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        log_path = out / 'anomalias_inyectadas.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, default=str, ensure_ascii=False)
        print(f"Log de anomalias guardado en: {log_path}")

    return dataframes, log
