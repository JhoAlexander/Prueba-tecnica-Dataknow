"""Funciones de apoyo compartidas por los generadores de datos."""
from pathlib import Path
import random
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd
import yaml
from faker import Faker


def load_config(path: str = None) -> dict:
    if path is None:
        path = Path(__file__).parent / 'config.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def init_random(seed: int) -> Dict[str, Faker]:
    """Fija la semilla en random, numpy y Faker; devuelve fakers por pais."""
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)

    return {
        'CO': Faker('es_CO'),
        'MX': Faker('es_MX'),
        'CL': Faker('es_CL'),
        'PE': Faker('es_ES'),
        'EC': Faker('es_ES'),
    }


def make_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def normalize_weights(weights: Sequence[float]) -> np.ndarray:
    w = np.array(weights, dtype=float)
    total = w.sum()
    if total == 0:
        raise ValueError("Suma de pesos es 0")
    return w / total


def weighted_choice(items: Sequence, weights: Sequence[float], n: int,
                    rng: np.random.Generator) -> np.ndarray:
    p = normalize_weights(weights)
    return rng.choice(items, size=n, p=p, replace=True)


def weighted_dict_choice(d: Dict[str, dict], n: int, rng: np.random.Generator,
                         weight_key: str = 'weight') -> np.ndarray:
    keys = list(d.keys())
    weights = [d[k][weight_key] for k in keys]
    return weighted_choice(keys, weights, n, rng)


def random_dates(start: str, end: str, n: int,
                 rng: np.random.Generator) -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    days_diff = (end_ts - start_ts).days
    offsets = rng.integers(0, days_diff + 1, size=n)
    return pd.Series(pd.to_datetime(start_ts) + pd.to_timedelta(offsets, unit='D'))


def seasonal_dates(start: str, end: str, monthly_factors: Dict[int, float],
                   n: int, rng: np.random.Generator) -> pd.Series:
    """Fechas con probabilidad proporcional al factor mensual."""
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    all_days = pd.date_range(start_ts, end_ts, freq='D')

    day_weights = np.array(
        [monthly_factors.get(d.month, 1.0) for d in all_days],
        dtype=float
    )
    probs = day_weights / day_weights.sum()

    chosen = rng.choice(all_days, size=n, p=probs, replace=True)
    return pd.Series(chosen)


def peak_hours(peaks: List[int], std: float, n: int,
               rng: np.random.Generator) -> np.ndarray:
    """Horas 0-23 con picos gaussianos en los valores de peaks."""
    peak_idx = rng.integers(0, len(peaks), size=n)
    centers = np.array([peaks[i] for i in peak_idx], dtype=float)
    raw = rng.normal(centers, std)
    return np.clip(np.round(raw), 0, 23).astype(int)


def hours_to_time_strings(hours: np.ndarray,
                          rng: np.random.Generator) -> List[str]:
    minutes = rng.integers(0, 60, size=len(hours))
    seconds = rng.integers(0, 60, size=len(hours))
    return [f"{h:02d}:{m:02d}:{s:02d}"
            for h, m, s in zip(hours, minutes, seconds)]


def inject_nulls(df: pd.DataFrame, columns: List[str], rate: float,
                 rng: np.random.Generator) -> pd.DataFrame:
    """Asigna nulos con probabilidad rate en las columnas indicadas."""
    n_rows = len(df)
    for col in columns:
        if col not in df.columns:
            continue
        mask = rng.random(n_rows) < rate
        dtype_name = df[col].dtype.name
        if dtype_name in ('string', 'object', 'Int64', 'boolean'):
            df.loc[mask, col] = pd.NA
        else:
            df.loc[mask, col] = np.nan
    return df


def cast_to_schema(df: pd.DataFrame, table_def: dict) -> pd.DataFrame:
    """Convierte cada columna al tipo declarado en el schema."""
    for col_def in table_def['columns']:
        name = col_def['name']
        if name not in df.columns:
            continue
        target = col_def['pandas_type']

        if 'datetime' in target:
            df[name] = pd.to_datetime(df[name], errors='coerce')
            continue

        try:
            df[name] = df[name].astype(target)
        except (ValueError, TypeError):
            if target == 'int64' and df[name].isna().any():
                df[name] = df[name].astype('Int64')
            else:
                raise

    df = df[[c['name'] for c in table_def['columns']]]
    return df


def ensure_dir(path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_table(df: pd.DataFrame, name: str, output_dir: str,
               formats: List[str], sample_n: int = 0,
               muestras_dir: str = None) -> Dict[str, str]:
    """Escribe la tabla en los formatos indicados y una muestra opcional."""
    out = ensure_dir(output_dir)
    paths = {}

    for fmt in formats:
        path = out / f"{name}.{fmt}"
        if fmt == 'csv':
            df.to_csv(path, index=False, encoding='utf-8')
        elif fmt == 'parquet':
            df.to_parquet(path, index=False, engine='pyarrow', compression='snappy')
        elif fmt == 'json':
            df.to_json(path, orient='records', lines=True, force_ascii=False)
        else:
            raise ValueError(f"Formato no soportado: {fmt}")
        paths[fmt] = str(path)

    if sample_n > 0 and muestras_dir:
        muestras_path = ensure_dir(muestras_dir)
        muestra_path = muestras_path / f"{name}_muestra.csv"
        df.head(sample_n).to_csv(muestra_path, index=False, encoding='utf-8')
        paths['muestra'] = str(muestra_path)

    return paths


if __name__ == '__main__':
    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    items = ['A', 'B', 'C']
    weights = [0.1, 0.6, 0.3]
    sample = weighted_choice(items, weights, 10000, rng)
    dist = {x: (sample == x).sum() / 10000 for x in items}
    print(f"weighted_choice: {dist}")

    hours = peak_hours([12, 19], 2.5, 10000, rng)
    print(f"peak_hours media: {hours.mean():.1f}")

    dates = seasonal_dates(
        '2025-06-01', '2026-05-31',
        cfg['distributions']['monthly_seasonality'],
        10000, rng
    )
    print(dates.dt.month.value_counts().sort_index().to_string())
