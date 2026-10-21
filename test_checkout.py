import copy
from datetime import date
from decimal import Decimal

import pytest

import checkout
from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)

HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"


def test_subtotal_de_dos_buzos_es_decimal_exacto():
    carrito = [item(cantidad=2)]

    subtotal = calcular_subtotal(carrito)

    assert type(subtotal) is Decimal
    assert subtotal == Decimal("49999.80")


def test_quince_por_ciento_con_medio_centavo_redondea_hacia_arriba():
    subtotal = Decimal("11999.50")

    descuento = calcular_descuento(subtotal, 1, "EGRESADOS2026", HOY_VIGENTE)

    assert descuento == Decimal("1799.93")


def test_el_precio_que_trae_el_item_se_ignora():
    carrito = [item(precio=1)]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal("24999.90")


@pytest.mark.parametrize("producto", ["gorra", "Buzo", " buzo ", "", None])
def test_producto_fuera_del_catalogo_es_inexistente(producto):
    item_invalido = item(producto=producto)

    codigo = codigo_de_error(validar_item, item_invalido)

    assert codigo == "PRODUCTO_INEXISTENTE"


@pytest.mark.parametrize("talle", ["XS", "S", "M", "L", "XL", "XXL", "m", "xxl", "Xl", "  M ", " xs "])
def test_talle_valido_sin_importar_mayusculas_ni_espacios(talle):
    carrito = [item(talle=talle)]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal("24999.90")


@pytest.mark.parametrize("talle", ["XXXL", "XXS", "ZZ", "X L", "", "   ", None, 42])
def test_talle_fuera_de_la_lista_es_invalido(talle):
    item_invalido = item(talle=talle)

    codigo = codigo_de_error(validar_item, item_invalido)

    assert codigo == "TALLE_INVALIDO"


@pytest.mark.parametrize("cantidad, esperado", [
    (1, "24999.90"),
    (2, "49999.80"),
    (9, "224999.10"),
    (10, "249999.00"),
])
def test_cantidad_entre_uno_y_diez_es_valida(cantidad, esperado):
    carrito = [item(cantidad=cantidad)]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal(esperado)


@pytest.mark.parametrize("cantidad", [11, -1, 2.5, 3.0, "3", True, None])
def test_cantidad_fuera_de_rango_o_no_entera_es_invalida(cantidad):
    item_invalido = item(cantidad=cantidad)

    codigo = codigo_de_error(validar_item, item_invalido)

    assert codigo == "CANTIDAD_INVALIDA"


def test_carrito_vacio_da_error_en_el_total():
    carrito = []

    codigo = codigo_de_error(calcular_total, carrito, "CABA")

    assert codigo == "CARRITO_VACIO"


def test_carrito_vacio_da_error_en_el_subtotal():
    carrito = []

    codigo = codigo_de_error(calcular_subtotal, carrito)

    assert codigo == "CARRITO_VACIO"


def test_validar_item_no_modifica_el_item():
    item_original = item(talle=" m ")
    copia = copy.deepcopy(item_original)

    validar_item(item_original)

    assert item_original == copia


def test_calcular_total_no_modifica_el_carrito():
    carrito = [item(talle=" m ", cantidad=5), item("remera", talle="xl")]
    copia = copy.deepcopy(carrito)

    calcular_total(carrito, "CABA", "EGRESADOS2026", HOY_VIGENTE)

    assert carrito == copia


def test_no_se_modifica_el_carrito_aunque_haya_error():
    carrito = [item(talle=" m "), item(producto="gorra")]
    copia = copy.deepcopy(carrito)

    codigo = codigo_de_error(calcular_total, carrito, "CABA")

    assert codigo == "PRODUCTO_INEXISTENTE"
    assert carrito == copia


@pytest.mark.parametrize("producto, esperado", [
    ("buzo", "24999.90"),
    ("remera", "11999.50"),
    ("campera", "47999.99"),
])
def test_precio_de_cada_producto_del_catalogo(producto, esperado):
    carrito = [item(producto=producto)]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal(esperado)


def test_subtotal_suma_varios_productos():
    carrito = [item("buzo"), item("remera", cantidad=2), item("campera")]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal("96998.89")


def test_las_claves_extra_del_item_se_ignoran():
    carrito = [item(color="rojo", precio=99999)]

    subtotal = calcular_subtotal(carrito)

    assert subtotal == Decimal("24999.90")


@pytest.mark.parametrize("prendas, esperado", [
    (1, "0.00"),
    (4, "0.00"),
    (5, "10000.00"),
    (6, "10000.00"),
    (10, "10000.00"),
])
def test_descuento_por_cantidad_desde_cinco_prendas(prendas, esperado):
    subtotal = Decimal("100000.00")

    descuento = calcular_descuento(subtotal, prendas, None, HOY_VIGENTE)

    assert descuento == Decimal(esperado)


def test_las_prendas_se_suman_entre_items():
    carrito = [item("buzo", cantidad=2), item("remera", cantidad=3)]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("8599.83")


def test_cuatro_prendas_repartidas_no_tienen_descuento():
    carrito = [item("buzo", cantidad=2), item("remera", cantidad=2)]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("0.00")


@pytest.mark.parametrize("fecha", [date(2026, 10, 1), date(2026, 11, 29), date(2026, 11, 30)])
def test_egresados2026_vigente_hasta_el_30_de_noviembre_inclusive(fecha):
    subtotal = Decimal("100000.00")

    descuento = calcular_descuento(subtotal, 1, "EGRESADOS2026", fecha)

    assert descuento == Decimal("15000.00")


def test_egresados2026_vencido_el_primero_de_diciembre():
    subtotal = Decimal("100000.00")

    codigo = codigo_de_error(calcular_descuento, subtotal, 1, "EGRESADOS2026", date(2026, 12, 1))

    assert codigo == "CUPON_VENCIDO"


@pytest.mark.parametrize("subtotal", ["20000.00", "20000.01", "50000.00"])
def test_bienvenida_descuenta_tres_mil_desde_veinte_mil(subtotal):
    monto = Decimal(subtotal)

    descuento = calcular_descuento(monto, 1, "BIENVENIDA", date(2030, 1, 1))

    assert descuento == Decimal("3000.00")


def test_bienvenida_por_debajo_del_minimo():
    subtotal = Decimal("19999.99")

    codigo = codigo_de_error(calcular_descuento, subtotal, 1, "BIENVENIDA", HOY_VIGENTE)

    assert codigo == "CUPON_MINIMO_NO_ALCANZADO"


@pytest.mark.parametrize("cupon, subtotal, esperado", [
    ("egresados2026", "100000.00", "15000.00"),
    ("  Bienvenida ", "50000.00", "3000.00"),
])
def test_cupon_sin_importar_mayusculas_ni_espacios(cupon, subtotal, esperado):
    monto = Decimal(subtotal)

    descuento = calcular_descuento(monto, 1, cupon, HOY_VIGENTE)

    assert descuento == Decimal(esperado)


@pytest.mark.parametrize("cupon", [None, "", "   "])
def test_cupon_vacio_equivale_a_no_usar_cupon(cupon):
    subtotal = Decimal("100000.00")

    descuento = calcular_descuento(subtotal, 1, cupon, HOY_VIGENTE)

    assert descuento == Decimal("0.00")


@pytest.mark.parametrize("cupon", ["PROMO10", "EGRESADOS2025", "DEBUG100", 123])
def test_cupon_que_no_existe_es_invalido(cupon):
    subtotal = Decimal("100000.00")

    codigo = codigo_de_error(calcular_descuento, subtotal, 1, cupon, HOY_VIGENTE)

    assert codigo == "CUPON_INVALIDO"


@pytest.mark.parametrize("subtotal, prendas, cupon, esperado", [
    ("100000.00", 6, "EGRESADOS2026", "15000.00"),
    ("100000.00", 5, "BIENVENIDA", "10000.00"),
    ("25000.00", 5, "BIENVENIDA", "3000.00"),
    ("30000.00", 5, "BIENVENIDA", "3000.00"),
    ("20000.00", 10, "BIENVENIDA", "3000.00"),
])
def test_cupon_y_cantidad_no_se_acumulan_gana_el_mayor(subtotal, prendas, cupon, esperado):
    monto = Decimal(subtotal)

    descuento = calcular_descuento(monto, prendas, cupon, HOY_VIGENTE)

    assert descuento == Decimal(esperado)


@pytest.mark.parametrize("cupon, fecha, esperado", [
    ("PROMO10", HOY_VIGENTE, "CUPON_INVALIDO"),
    ("EGRESADOS2026", date(2026, 12, 1), "CUPON_VENCIDO"),
])
def test_cupon_con_error_aunque_haya_cinco_prendas(cupon, fecha, esperado):
    subtotal = Decimal("100000.00")

    codigo = codigo_de_error(calcular_descuento, subtotal, 5, cupon, fecha)

    assert codigo == esperado


def fijar_hoy(monkeypatch, hoy):
    class FechaFalsa(date):
        @classmethod
        def today(cls):
            return hoy

    monkeypatch.setattr(checkout, "date", FechaFalsa)


def test_sin_fecha_usa_la_del_dia_de_la_llamada_vencido(monkeypatch):
    fijar_hoy(monkeypatch, date(2026, 12, 1))

    codigo = codigo_de_error(calcular_descuento, Decimal("100000.00"), 1, "EGRESADOS2026")

    assert codigo == "CUPON_VENCIDO"


def test_sin_fecha_usa_la_del_dia_de_la_llamada_vigente(monkeypatch):
    fijar_hoy(monkeypatch, date(2026, 11, 30))

    descuento = calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026")

    assert descuento == Decimal("15000.00")


def test_sin_fecha_en_calcular_total_usa_la_del_dia(monkeypatch):
    fijar_hoy(monkeypatch, date(2026, 12, 1))

    codigo = codigo_de_error(calcular_total, [item()], "CABA", "EGRESADOS2026")

    assert codigo == "CUPON_VENCIDO"


@pytest.mark.parametrize("subtotal, prendas, cupon, esperado", [
    ("100.05", 5, None, "10.01"),
    ("100.01", 1, "EGRESADOS2026", "15.00"),
])
def test_redondeo_al_centavo(subtotal, prendas, cupon, esperado):
    monto = Decimal(subtotal)

    descuento = calcular_descuento(monto, prendas, cupon, HOY_VIGENTE)

    assert descuento == Decimal(esperado)


def test_todos_los_importes_del_total_son_decimal():
    carrito = [item("campera", cantidad=2)]

    resultado = calcular_total(carrito, "CABA")

    assert all(type(valor) is Decimal for valor in resultado.values())
    assert resultado["descuento"] == Decimal("0.00")
    assert resultado["envio"] == Decimal("0.00")


@pytest.mark.parametrize("zona, esperado", [
    ("CABA", "2500.00"),
    ("GBA", "4000.00"),
    ("INTERIOR", "6500.00"),
    ("RETIRO", "0.00"),
    ("gba", "4000.00"),
    ("  Interior ", "6500.00"),
])
def test_costo_de_envio_por_zona(zona, esperado):
    base = Decimal("1000.00")

    envio = calcular_envio(base, zona)

    assert envio == Decimal(esperado)


@pytest.mark.parametrize("base, zona, esperado", [
    ("59999.99", "CABA", "2500.00"),
    ("60000.00", "CABA", "0.00"),
    ("60000.01", "INTERIOR", "0.00"),
])
def test_envio_gratis_desde_sesenta_mil(base, zona, esperado):
    monto = Decimal(base)

    envio = calcular_envio(monto, zona)

    assert envio == Decimal(esperado)


@pytest.mark.parametrize("zona, base", [
    ("MARTE", "1000.00"),
    ("", "1000.00"),
    (None, "1000.00"),
    ("MARTE", "70000.00"),
])
def test_zona_que_no_existe_es_invalida(zona, base):
    monto = Decimal(base)

    codigo = codigo_de_error(calcular_envio, monto, zona)

    assert codigo == "ZONA_INVALIDA"


def test_envio_se_calcula_con_el_descuento_aplicado():
    carrito = [item("buzo", cantidad=2), item("remera")]

    resultado = calcular_total(carrito, "CABA", "BIENVENIDA", HOY_VIGENTE)

    assert resultado["envio"] == Decimal("2500.00")


@pytest.mark.parametrize("carrito, zona, cupon, esperado", [
    ([item(cantidad=2)], "CABA", None, ("49999.80", "0.00", "2500.00", "52499.80")),
    ([item("remera")], "CABA", "EGRESADOS2026", ("11999.50", "1799.93", "2500.00", "12699.57")),
    ([item("buzo", cantidad=2), item("remera", cantidad=3)], "CABA", None,
     ("85998.30", "8599.83", "0.00", "77398.47")),
    ([item("buzo", cantidad=2), item("remera")], "CABA", "BIENVENIDA",
     ("61999.30", "3000.00", "2500.00", "61499.30")),
    ([item("campera", cantidad=2)], "CABA", None, ("95999.98", "0.00", "0.00", "95999.98")),
    ([item()], "RETIRO", None, ("24999.90", "0.00", "0.00", "24999.90")),
    ([item("campera")], "GBA", None, ("47999.99", "0.00", "4000.00", "51999.99")),
])
def test_total_es_subtotal_menos_descuento_mas_envio(carrito, zona, cupon, esperado):
    claves = ("subtotal", "descuento", "envio", "total")

    resultado = calcular_total(carrito, zona, cupon, HOY_VIGENTE)

    assert resultado == {clave: Decimal(valor) for clave, valor in zip(claves, esperado, strict=True)}


@pytest.mark.parametrize("carrito, zona, cupon, esperado", [
    ([], "MARTE", "PROMO10", "CARRITO_VACIO"),
    ([item(producto="gorra", talle="ZZ", cantidad=0)], "CABA", None, "PRODUCTO_INEXISTENTE"),
    ([item(talle="ZZ", cantidad=0)], "CABA", None, "TALLE_INVALIDO"),
    ([item(cantidad=0), item(producto="gorra")], "CABA", None, "CANTIDAD_INVALIDA"),
    ([item(talle="ZZ")], "CABA", "PROMO10", "TALLE_INVALIDO"),
    ([item()], "MARTE", "PROMO10", "CUPON_INVALIDO"),
    ([item()], "MARTE", None, "ZONA_INVALIDA"),
    ([{"producto": "buzo", "cantidad": 1}], "CABA", None, "TALLE_INVALIDO"),
])
def test_orden_de_validacion_informa_el_primer_error(carrito, zona, cupon, esperado):
    fecha = HOY_VIGENTE

    codigo = codigo_de_error(calcular_total, carrito, zona, cupon, fecha)

    assert codigo == esperado
