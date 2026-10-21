import json
import threading
import urllib.error
import urllib.request

import pytest

import api

RUTA = "/api/v1/pedidos"


@pytest.fixture
def url(tmp_path):
    servidor = api.crear_servidor(str(tmp_path / "tienda.db"), 0)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}"
    servidor.shutdown()
    servidor.server_close()


def pedir(url, metodo, ruta, cuerpo=None, crudo=None):
    datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    req = urllib.request.Request(url + ruta, data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def compra(**cambios):
    cuerpo = {"email": "ana@mail.com", "zona": "CABA",
              "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]}
    cuerpo.update(cambios)
    return cuerpo


def test_una_ruta_inexistente_devuelve_404(url):
    status, cuerpo = pedir(url, "GET", "/api/v1/otra")
    assert status == 404
    assert cuerpo["error"]["code"] == "RUTA_INEXISTENTE"


def error_con_formato(cuerpo):
    return set(cuerpo) == {"error"} and set(cuerpo["error"]) == {"code", "message"}


def test_crear_un_pedido_devuelve_201_con_los_montos_como_texto(url):
    cuerpo = compra()

    status, creado = pedir(url, "POST", RUTA, cuerpo)

    assert status == 201
    assert type(creado["id"]) is int
    assert {clave: creado[clave] for clave in ("subtotal", "descuento", "envio", "total")} == {
        "subtotal": "24999.90",
        "descuento": "0.00",
        "envio": "2500.00",
        "total": "27499.90",
    }


def test_crear_y_leer_un_pedido_con_cupon_y_fecha(url):
    cuerpo = compra(email=" Ana@Mail.com ", zona="caba",
                    carrito=[{"producto": "remera", "talle": "m", "cantidad": 1}],
                    cupon="egresados2026", fecha="2026-11-30")

    status, creado = pedir(url, "POST", RUTA, cuerpo)
    status_get, leido = pedir(url, "GET", f"{RUTA}/{creado.get('id')}")

    assert status == 201
    assert creado["total"] == "12699.57"
    assert status_get == 200
    assert leido == {
        "id": creado["id"],
        "email": "ana@mail.com",
        "zona": "CABA",
        "cupon": "EGRESADOS2026",
        "subtotal": "11999.50",
        "descuento": "1799.93",
        "envio": "2500.00",
        "total": "12699.57",
        "items": [{"producto": "remera", "talle": "M", "cantidad": 1, "precio_unitario": "11999.50"}],
    }


@pytest.mark.parametrize("cambios, code", [
    ({"carrito": [{"producto": "buzo", "talle": "XXXL", "cantidad": 1}]}, "TALLE_INVALIDO"),
    ({"carrito": []}, "CARRITO_VACIO"),
    ({"zona": "MARTE"}, "ZONA_INVALIDA"),
    ({"cupon": "EGRESADOS2026", "fecha": "2026-12-01"}, "CUPON_VENCIDO"),
])
def test_un_error_de_negocio_devuelve_422_con_su_code(url, cambios, code):
    cuerpo = compra(**cambios)

    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    assert status == 422
    assert error_con_formato(respuesta)
    assert respuesta["error"]["code"] == code


def test_un_cuerpo_que_no_es_json_devuelve_400(url):
    crudo = b"{no"

    status, respuesta = pedir(url, "POST", RUTA, crudo=crudo)

    assert status == 400
    assert error_con_formato(respuesta)
    assert respuesta["error"]["code"] == "JSON_INVALIDO"


@pytest.mark.parametrize("cuerpo", [
    {"zona": "CABA", "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]},
    {"email": "ana@mail.com", "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]},
    {"email": "ana@mail.com", "zona": "CABA"},
    compra(email=None),
    compra(zona=123),
    compra(carrito="buzo"),
])
def test_datos_faltantes_o_de_otro_tipo_devuelven_400(url, cuerpo):
    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    assert status == 400
    assert error_con_formato(respuesta)
    assert respuesta["error"]["code"] == "DATOS_INCOMPLETOS"


def test_un_pedido_que_no_existe_devuelve_404(url):
    ruta = f"{RUTA}/999"

    status, respuesta = pedir(url, "GET", ruta)

    assert status == 404
    assert error_con_formato(respuesta)
    assert respuesta["error"]["code"] == "PEDIDO_INEXISTENTE"
