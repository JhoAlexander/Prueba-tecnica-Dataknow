"""Generador de MSTR_ARTICULOS (depende de MSTR_PROVEEDORES)."""
import numpy as np
import pandas as pd

from schemas import MSTR_ARTICULOS, UNIDADES_MEDIDA
from auxiliares import (
    weighted_choice, cast_to_schema, inject_nulls, random_dates,
)


PRODUCTOS_POR_CATEG = {
    1: [
        'Arroz', 'Pasta', 'Aceite Vegetal', 'Azucar', 'Leche', 'Cafe',
        'Atun en Lata', 'Frijoles', 'Harina', 'Sal', 'Te', 'Agua Mineral',
        'Jugo de Naranja', 'Gaseosa', 'Cerveza', 'Vino Tinto', 'Galletas',
        'Chocolate', 'Cereal', 'Mermelada',
    ],
    2: [
        'Shampoo', 'Acondicionador', 'Jabon de Bano', 'Pasta Dental',
        'Cepillo Dental', 'Desodorante', 'Crema Corporal', 'Gel de Bano',
        'Papel Higienico', 'Toallas Humedas', 'Maquinilla', 'Talco',
        'Enjuague Bucal', 'Hilo Dental', 'Crema de Afeitar',
    ],
    3: [
        'Detergente', 'Suavizante', 'Blanqueador', 'Limpia Pisos',
        'Limpia Vidrios', 'Escoba', 'Trapero', 'Bolsas de Basura',
        'Papel Cocina', 'Lavavajillas', 'Esponja', 'Insecticida',
        'Ambientador', 'Cepillo Bano',
    ],
    4: [
        'Smart TV 32', 'Smart TV 50', 'Smart TV 65', 'Parlante Bluetooth',
        'Audifonos Inalambricos', 'Mouse Optico', 'Teclado USB',
        'Cargador USB-C', 'Cable HDMI', 'Memoria USB 64GB',
        'Camara Web HD', 'Power Bank 10000mAh', 'Bocina Portatil',
    ],
    5: [
        'Camiseta Basica', 'Pantalon Jean', 'Vestido Casual',
        'Tenis Deportivos', 'Sandalias', 'Calcetines Pack 3',
        'Ropa Interior Pack 3', 'Pijama', 'Chaqueta Liviana',
        'Bermuda', 'Falda Midi', 'Saco de Lana',
    ],
    6: [
        'Panales Etapa 1', 'Panales Etapa 2', 'Panales Etapa 3',
        'Leche en Polvo Etapa 1', 'Biberon', 'Chupo', 'Cereal Infantil',
        'Ropita Bebe 0-3m', 'Ropita Bebe 3-6m', 'Cobija para Bebe',
        'Manzanilla en Crema', 'Pomada para Panalitis',
    ],
}

ADJETIVOS = [
    'Premium', 'Clasico', 'Economico', 'Familiar', 'Original',
    'Gold', 'Plus', 'Extra', 'Light', 'Tradicional', 'Selecto',
]

VARIANTES_POR_CATEG = {
    1: ['250g', '500g', '1kg', '5kg', '500ml', '1L', '2L', 'Pack x6'],
    2: ['200ml', '400ml', '750ml', '100g', 'Pack x4', 'Pack x10'],
    3: ['1kg', '2kg', '1L', '5L', 'Pack x12', 'Rollo x500'],
    4: [''],
    5: ['Talla S', 'Talla M', 'Talla L', 'Talla XL', ''],
    6: ['Talla P', 'Talla M', 'Talla G', 'Pack x30', 'Pack x60'],
}

PRECIO_BASE_POR_CATEG = {
    1: 8000,
    2: 12000,
    3: 15000,
    4: 250000,
    5: 50000,
    6: 30000,
}

UNID_POR_CATEG = {
    1: ['UN', 'KG', 'LT', 'CC'],
    2: ['UN', 'CC'],
    3: ['UN', 'KG', 'LT'],
    4: ['UN'],
    5: ['UN'],
    6: ['UN'],
}


def generate(cfg: dict, fakes: dict, rng: np.random.Generator,
             proveedores: pd.DataFrame = None) -> pd.DataFrame:
    if proveedores is None:
        raise ValueError("Se requiere DataFrame de proveedores como dependencia")

    n = cfg['volumes']['mstr_articulos']
    ids = np.arange(1, n + 1)

    cats = cfg['categories_n1']
    cat_ids = [c['id'] for c in cats]
    cat_weights = [c['weight'] for c in cats]
    categ_n1 = weighted_choice(cat_ids, cat_weights, n, rng)

    # Jerarquia: n2 = n1*10 + sub, n3 = n2*10 + sub
    sub_n2 = rng.integers(1, 6, size=n)
    categ_n2 = categ_n1 * 10 + sub_n2
    sub_n3 = rng.integers(1, 10, size=n)
    categ_n3 = categ_n2 * 10 + sub_n3

    prov_activos = proveedores.loc[proveedores['activo'] == True, 'id_proveedor'].to_numpy()
    id_proveedor = rng.choice(prov_activos, size=n, replace=True)

    descripciones = []
    for c1 in categ_n1:
        producto = rng.choice(PRODUCTOS_POR_CATEG[int(c1)])
        adj = rng.choice(ADJETIVOS)
        var = rng.choice(VARIANTES_POR_CATEG[int(c1)])
        partes = [str(producto), str(adj)]
        if var:
            partes.append(str(var))
        descripciones.append(' '.join(partes))

    # EAN-13 con prefijo 770 (Colombia)
    raw_codes = rng.integers(0, 10**10, size=n)
    cod_barra = [f"770{c:010d}" for c in raw_codes]

    precio_lista = np.zeros(n)
    for i, c1 in enumerate(categ_n1):
        base = PRECIO_BASE_POR_CATEG[int(c1)]
        precio_lista[i] = round(rng.lognormal(mean=np.log(base), sigma=0.6), 2)

    peso_kg = np.zeros(n)
    for i, c1 in enumerate(categ_n1):
        c1_int = int(c1)
        if c1_int == 1:
            peso_kg[i] = round(rng.uniform(0.1, 5.0), 3)
        elif c1_int == 4:
            peso_kg[i] = round(rng.uniform(0.2, 15.0), 3)
        elif c1_int == 5:
            peso_kg[i] = round(rng.uniform(0.1, 2.0), 3)
        else:
            peso_kg[i] = round(rng.uniform(0.05, 2.0), 3)

    unid_medida = [rng.choice(UNID_POR_CATEG[int(c1)]) for c1 in categ_n1]
    activo = rng.random(n) < 0.95
    fec_alta = random_dates('2020-01-01', '2026-05-31', n, rng)

    df = pd.DataFrame({
        'art_id': ids,
        'cod_barra': cod_barra,
        'desc_art': descripciones,
        'id_categ_n1': categ_n1,
        'id_categ_n2': categ_n2,
        'id_categ_n3': categ_n3,
        'id_proveedor': id_proveedor,
        'precio_lista': precio_lista,
        'peso_kg': peso_kg,
        'unid_medida': unid_medida,
        'activo': activo,
        'fec_alta': fec_alta,
    })

    df = inject_nulls(df, ['cod_barra', 'peso_kg'], cfg['quality']['null_rate'], rng)
    df = inject_nulls(df, ['id_categ_n3'], 0.20, rng)
    return cast_to_schema(df, MSTR_ARTICULOS)


if __name__ == '__main__':
    from auxiliares import load_config, init_random, make_rng
    from gen_01_proveedores import generate as gen_proveedores

    cfg = load_config()
    fakes = init_random(cfg['random_seed'])
    rng = make_rng(cfg['random_seed'])

    df_prov = gen_proveedores(cfg, fakes, rng)
    df = generate(cfg, fakes, rng, proveedores=df_prov)
    print(f"{len(df)} articulos")
    print(df['id_categ_n1'].value_counts(normalize=True).sort_index().round(3))
    print("FK valida:", df['id_proveedor'].isin(df_prov['id_proveedor']).all())
