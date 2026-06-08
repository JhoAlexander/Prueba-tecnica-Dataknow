"""Orquestador de generacion de datos sinteticos.

Genera las 7 tablas en orden de dependencias, inyecta anomalias,
exporta a CSV/Parquet y produce un reporte de ejecucion.

Uso:
    python generador.py
    python generador.py --config otra_config.yaml
    python generador.py --skip-anomalies
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from anomalias import apply_all_anomalies
from gen_01_proveedores import generate as gen_proveedores
from gen_02_tiendas import generate as gen_tiendas
from gen_03_articulos import generate as gen_articulos
from gen_04_miembros import generate as gen_miembros
from gen_05_ventas import generate as gen_ventas
from gen_06_inventario import generate as gen_inventario
from gen_07_devoluciones import generate as gen_devoluciones
from auxiliares import init_random, load_config, make_rng, save_table


TABLE_FILE_NAMES = {
    'MSTR_PROVEEDORES':  'mstr_proveedores',
    'MSTR_TIENDAS':      'mstr_tiendas',
    'MSTR_ARTICULOS':    'mstr_articulos',
    'CRM_MIEMBROS':      'crm_miembros',
    'TRANS_VENTAS':      'trans_ventas',
    'INV_STOCK_DIARIO':  'inv_stock_diario',
    'POST_DEVOLUCIONES': 'post_devoluciones',
}


def main():
    parser = argparse.ArgumentParser(description='Generador de datos sinteticos RetailMax')
    parser.add_argument('--config', default=None)
    parser.add_argument('--skip-anomalies', action='store_true')
    args = parser.parse_args()

    t_start = time.time()
    cfg = load_config(args.config)
    print(f"Config: seed={cfg['random_seed']} "
          f"rango={cfg['date_range']['start']} a {cfg['date_range']['end']}\n")

    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])
    base_dir = Path(__file__).parent
    output_dir = base_dir / cfg['output']['base_path']
    muestras_dir = base_dir / 'muestras'

    dfs = {}
    timings = {}

    def _step(name: str, func, *args, **kwargs):
        t0 = time.time()
        df = func(cfg, fakes, rng, *args, **kwargs)
        elapsed = time.time() - t0
        timings[name] = round(elapsed, 2)
        print(f"  [{elapsed:6.2f}s] {name:22s} -> {len(df):>9,} filas")
        return df

    print("--- Generando tablas ---")
    dfs['MSTR_PROVEEDORES']  = _step('MSTR_PROVEEDORES',  gen_proveedores)
    dfs['MSTR_TIENDAS']      = _step('MSTR_TIENDAS',      gen_tiendas)
    dfs['MSTR_ARTICULOS']    = _step('MSTR_ARTICULOS',    gen_articulos,    proveedores=dfs['MSTR_PROVEEDORES'])
    dfs['CRM_MIEMBROS']      = _step('CRM_MIEMBROS',      gen_miembros)
    dfs['TRANS_VENTAS']      = _step('TRANS_VENTAS',      gen_ventas,
                                     tiendas=dfs['MSTR_TIENDAS'],
                                     articulos=dfs['MSTR_ARTICULOS'],
                                     miembros=dfs['CRM_MIEMBROS'])
    dfs['INV_STOCK_DIARIO']  = _step('INV_STOCK_DIARIO',  gen_inventario,
                                     articulos=dfs['MSTR_ARTICULOS'],
                                     tiendas=dfs['MSTR_TIENDAS'])
    dfs['POST_DEVOLUCIONES'] = _step('POST_DEVOLUCIONES', gen_devoluciones,
                                     ventas=dfs['TRANS_VENTAS'],
                                     articulos=dfs['MSTR_ARTICULOS'],
                                     tiendas=dfs['MSTR_TIENDAS'])

    anomaly_log = None
    if not args.skip_anomalies:
        print("\n--- Inyectando anomalias ---")
        t0 = time.time()
        dfs, anomaly_log = apply_all_anomalies(dfs, cfg, rng, output_dir=output_dir)
        timings['anomalies'] = round(time.time() - t0, 2)
        print(f"  {anomaly_log['summary']['filas_anomalas_total']} anomalias inyectadas")

    print("\n--- Exportando archivos ---")
    formats = cfg['output']['formats']
    sample_n = cfg['output']['sample_rows_per_table']
    file_paths = {}

    for table_name, df in dfs.items():
        fname = TABLE_FILE_NAMES[table_name]
        t0 = time.time()
        paths = save_table(
            df, fname,
            output_dir=str(output_dir),
            formats=formats,
            sample_n=sample_n,
            muestras_dir=str(muestras_dir),
        )
        print(f"  [{time.time()-t0:6.2f}s] {table_name:22s} -> {', '.join(formats)} + muestra")
        file_paths[table_name] = paths

    total_filas = sum(len(df) for df in dfs.values())
    total_elapsed = time.time() - t_start

    reporte = {
        'fecha_ejecucion': datetime.now().isoformat(),
        'seed': cfg['random_seed'],
        'rango_temporal': cfg['date_range'],
        'volumenes_solicitados': cfg['volumes'],
        'volumenes_generados': {name: len(df) for name, df in dfs.items()},
        'total_filas': total_filas,
        'tiempos_segundos': timings,
        'tiempo_total_segundos': round(total_elapsed, 2),
        'formatos_exportados': formats,
        'rutas_archivos': file_paths,
        'anomalias': anomaly_log,
    }
    reporte_path = output_dir / 'reporte_generacion.json'
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, default=str, ensure_ascii=False)

    print(f"\nTotal: {total_filas:,} filas en {total_elapsed:.1f}s "
          f"({total_filas/total_elapsed:,.0f} filas/seg)")
    print(f"Reporte: {reporte_path}")


if __name__ == '__main__':
    main()
