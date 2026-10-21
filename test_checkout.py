import copy
from datetime import date
from decimal import Decimal

import pytest

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
