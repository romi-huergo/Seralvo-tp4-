from datetime import date
from decimal import Decimal

import pytest

import pedidos
from checkout import CheckoutError, calcular_total

HOY_VIGENTE = date(2026, 10, 1)


@pytest.fixture
def ruta(tmp_path):
    return str(tmp_path / "tienda.db")


@pytest.fixture
def con(ruta):
    conexion = pedidos.conectar(ruta)
    pedidos.crear_esquema(conexion)
    yield conexion
    conexion.close()


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def contar(ruta, tabla):
    assert tabla in ("pedidos", "items")
    otra = pedidos.conectar(ruta)
    try:
        return otra.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        otra.close()


def test_un_id_inexistente_devuelve_none(con):
    assert pedidos.obtener_pedido(con, 999) is None


@pytest.mark.parametrize("carrito, zona, cupon, fecha, esperado", [
    ([item(talle="ZZ")], "CABA", None, None, "TALLE_INVALIDO"),
    ([item()], "MARTE", None, None, "ZONA_INVALIDA"),
    ([item()], "CABA", "EGRESADOS2026", date(2026, 12, 1), "CUPON_VENCIDO"),
])
def test_si_checkout_falla_no_queda_nada_guardado(con, ruta, carrito, zona, cupon, fecha, esperado):
    email = "ana@mail.com"

    with pytest.raises(CheckoutError) as error:
        pedidos.guardar_pedido(con, email, carrito, zona, cupon, fecha)

    assert error.value.code == esperado
    assert contar(ruta, "pedidos") == 0
    assert contar(ruta, "items") == 0


def test_pedido_guardado_lo_ve_completo_otra_conexion(con, ruta):
    carrito = [item("remera")]

    pedido_id = pedidos.guardar_pedido(con, "ana@mail.com", carrito, "CABA")

    otra = pedidos.conectar(ruta)
    try:
        pedido = pedidos.obtener_pedido(otra, pedido_id)
    finally:
        otra.close()
    assert pedido["total"] == Decimal("14499.50")
    assert len(pedido["items"]) == 1


def test_los_montos_guardados_son_identicos_a_los_de_checkout(con):
    carrito = [item("remera")]
    fecha = date(2026, 11, 1)
    esperado = calcular_total(carrito, "CABA", "EGRESADOS2026", fecha)

    pedido_id = pedidos.guardar_pedido(con, "ana@mail.com", carrito, "CABA", "EGRESADOS2026", fecha)
    pedido = pedidos.obtener_pedido(con, pedido_id)

    montos = {clave: pedido[clave] for clave in ("subtotal", "descuento", "envio", "total")}
    assert montos == esperado
    assert montos == {
        "subtotal": Decimal("11999.50"),
        "descuento": Decimal("1799.93"),
        "envio": Decimal("2500.00"),
        "total": Decimal("12699.57"),
    }


def test_los_montos_no_pierden_precision_al_guardarse(con):
    carrito = [item("campera")]

    pedido_id = pedidos.guardar_pedido(con, "ana@mail.com", carrito, "CABA")
    pedido = pedidos.obtener_pedido(con, pedido_id)

    assert str(pedido["subtotal"]) == "47999.99"
    assert str(pedido["total"]) == "50499.99"
    assert str(pedido["items"][0]["precio_unitario"]) == "47999.99"


def test_ningun_email_altera_la_consulta(con):
    pedidos.guardar_pedido(con, "ana@mail.com", [item()], "CABA")
    pedidos.guardar_pedido(con, "beto@mail.com", [item()], "CABA")

    encontrados = pedidos.pedidos_de(con, "x' OR '1'='1")

    assert encontrados == []


def test_un_email_con_comilla_es_un_dato_valido(con):
    pedido_id = pedidos.guardar_pedido(con, "o'brien@mail.com", [item()], "CABA")

    encontrados = pedidos.pedidos_de(con, "o'brien@mail.com")

    assert [p["id"] for p in encontrados] == [pedido_id]
