# 

## R1 — Catálogo y precios

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Producto del catálogo: buzo | — | calcular\_subtotal(\[item(producto="buzo")\]) | 24999.90 | unitario |
| Producto del catálogo: remera | — | calcular\_subtotal(\[item(producto="remera")\]) | 11999.50 | unitario |
| Producto del catálogo: campera | — | calcular\_subtotal(\[item(producto="campera")\]) | 47999.99 | unitario |
| Varios productos distintos | — | calcular\_subtotal(\[item("buzo"), item("remera", cantidad=2), item("campera")\]) | 96998.89 | unitario |
| El ítem trae un precio propio | precio menor y mayor | calcular\_subtotal(\[item(precio=1)\]) | 24999.90 | unitario |
|  |  | calcular\_subtotal(\[item(precio=99999)\]) | 24999.90 | unitario |
| Claves extra en el ítem | — | calcular\_subtotal(\[item(color="rojo")\]) | 24999.90 | unitario |
| Producto que no existe | — | validar\_item(item(producto="gorra")) | → PRODUCTO\_INEXISTENTE | unitario |
| Nombre con mayúsculas | "buzo" OK / "Buzo" no | validar\_item(item(producto="Buzo")) | → PRODUCTO\_INEXISTENTE | unitario |
| Nombre con espacios | — | validar\_item(item(producto=" buzo ")) | → PRODUCTO\_INEXISTENTE | unitario |
| Producto vacío | — | validar\_item(item(producto="")) | → PRODUCTO\_INEXISTENTE | unitario |
| Producto que no es texto | — | validar\_item(item(producto=None)) | → PRODUCTO\_INEXISTENTE | unitario |
| Producto inexistente dentro de un carrito | — | calcular\_total(\[item(producto="gorra")\], "CABA") | → PRODUCTO\_INEXISTENTE | unitario |

## R2 — Talles

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Talle válido en mayúscula | los 6 talles | validar\_item(item(talle=t)) con t en XS, S, M, L, XL, XXL | OK | unitario |
| Talle válido en minúscula | — | validar\_item(item(talle="m")) | OK | unitario |
|  |  | validar\_item(item(talle="xxl")) | OK | unitario |
| Mayúsculas y minúsculas mezcladas | — | validar\_item(item(talle="Xl")) | OK | unitario |
| Espacios al principio y al final | — | validar\_item(item(talle="  M ")) | OK | unitario |
| Espacios y minúscula juntos | — | validar\_item(item(talle=" xs ")) | OK | unitario |
| Talle fuera de la lista, por arriba | XXL OK / XXXL no | validar\_item(item(talle="XXXL")) | → TALLE\_INVALIDO | unitario |
| Talle fuera de la lista, por abajo | XS OK / XXS no | validar\_item(item(talle="XXS")) | → TALLE\_INVALIDO | unitario |
| Talle inventado | — | validar\_item(item(talle="ZZ")) | → TALLE\_INVALIDO | unitario |
| Espacio en el medio | — | validar\_item(item(talle="X L")) | → TALLE\_INVALIDO | unitario |
| Texto vacío | — | validar\_item(item(talle="")) | → TALLE\_INVALIDO | unitario |
| Solo espacios | — | validar\_item(item(talle="   ")) | → TALLE\_INVALIDO | unitario |
| Talle que no es texto | — | validar\_item(item(talle=None)) | → TALLE\_INVALIDO | unitario |
|  |  | validar\_item(item(talle=42)) | → TALLE\_INVALIDO | unitario |

## R3 — Cantidad

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Menor al mínimo | 0 | validar\_item(item(cantidad=0)) | → CANTIDAD\_INVALIDA | unitario |
| Negativa | \-1 | validar\_item(item(cantidad=-1)) | → CANTIDAD\_INVALIDA | unitario |
| Mínimo válido | 1 | validar\_item(item(cantidad=1)) | OK | unitario |
| Justo arriba del mínimo | 2 | validar\_item(item(cantidad=2)) | OK | unitario |
| Justo abajo del máximo | 9 | validar\_item(item(cantidad=9)) | OK | unitario |
| Máximo válido | 10 | validar\_item(item(cantidad=10)) | OK | unitario |
| Máximo dentro del cálculo | 10 | calcular\_subtotal(\[item(cantidad=10)\]) | 249999.00 | unitario |
| Mayor al máximo | 11 | validar\_item(item(cantidad=11)) | → CANTIDAD\_INVALIDA | unitario |
| Número no entero | — | validar\_item(item(cantidad=2.5)) | → CANTIDAD\_INVALIDA | unitario |
| Float con valor entero | — | validar\_item(item(cantidad=3.0)) | → CANTIDAD\_INVALIDA | unitario |
| Texto con un número | — | validar\_item(item(cantidad="3")) | → CANTIDAD\_INVALIDA | unitario |
| Booleano | — | validar\_item(item(cantidad=True)) | → CANTIDAD\_INVALIDA | unitario |
| Sin valor | — | validar\_item(item(cantidad=None)) | → CANTIDAD\_INVALIDA | unitario |

## R4 — Carrito

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Carrito vacío | 0 ítems | calcular\_total(\[\], "CABA") | → CARRITO\_VACIO | unitario |
|  |  | calcular\_subtotal(\[\]) | → CARRITO\_VACIO | unitario |
| Carrito con un ítem | 1 ítem | calcular\_total(\[item()\], "CABA") | OK, subtotal 24999.90 | unitario |
| validar\_item no modifica el ítem | — | it \= item(talle=" m "); validar\_item(it) | it queda igual a una copia hecha antes (" m ") | unitario |
| calcular\_subtotal no modifica el carrito | — | c \= \[item(talle="m", precio=1)\]; calcular\_subtotal(c) | c queda igual a su copy.deepcopy previo | unitario |
| calcular\_total no modifica el carrito | — | c \= \[item(talle=" m ", cantidad=5)\]; calcular\_total(c, " caba ", " egresados2026 ", HOY) | c queda igual a su copy.deepcopy previo | unitario |
| No se modifica aunque haya error | — | c \= \[item(talle=" m "), item(producto="gorra")\]; calcular\_total(c, "CABA") | → PRODUCTO\_INEXISTENTE y c igual a su copia | unitario |

## R5 — Descuento por cantidad

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Menos de 5 prendas → sin descuento | 4 | calcular\_descuento(Decimal("100000.00"), 4, None, HOY) | 0.00 | unitario |
| Una sola prenda | 1 | calcular\_descuento(Decimal("100000.00"), 1, None, HOY) | 0.00 | unitario |
| 5 o más prendas → 10% | 5 (borde) | calcular\_descuento(Decimal("100000.00"), 5, None, HOY) | 10000.00 | unitario |
|  | 6 | calcular\_descuento(Decimal("100000.00"), 6, None, HOY) | 10000.00 | unitario |
|  | 10 | calcular\_descuento(Decimal("100000.00"), 10, None, HOY) | 10000.00 | unitario |
| Las prendas se suman entre ítems | 2 \+ 3 \= 5 | calcular\_total(\[item("buzo", cantidad=2), item("remera", cantidad=3)\], "CABA") | descuento 8599.83 | unitario |
| Varios ítems que suman 4 | 2 \+ 2 \= 4 | calcular\_total(\[item("buzo", cantidad=2), item("remera", cantidad=2)\], "CABA") | descuento 0.00 | unitario |

## R6 — Cupones

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| EGRESADOS2026 vigente → 15% | — | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", HOY) | 15000.00 | unitario |
| EGRESADOS2026 el día antes del vencimiento | 29/11/2026 | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 11, 29)) | 15000.00 | unitario |
| EGRESADOS2026 el último día | 30/11/2026 | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 11, 30)) | 15000.00 | unitario |
| EGRESADOS2026 vencido | 01/12/2026 | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 12, 1)) | → CUPON\_VENCIDO | unitario |
| BIENVENIDA con el mínimo justo | 20000.00 | calcular\_descuento(Decimal("20000.00"), 1, "BIENVENIDA", HOY) | 3000.00 | unitario |
| BIENVENIDA arriba del mínimo | 20000.01 | calcular\_descuento(Decimal("20000.01"), 1, "BIENVENIDA", HOY) | 3000.00 | unitario |
| BIENVENIDA abajo del mínimo | 19999.99 | calcular\_descuento(Decimal("19999.99"), 1, "BIENVENIDA", HOY) | → CUPON\_MINIMO\_NO\_ALCANZADO | unitario |
| BIENVENIDA no depende de la fecha | — | calcular\_descuento(Decimal("50000.00"), 1, "BIENVENIDA", date(2030, 1, 1)) | 3000.00 | unitario |
| Cupón en minúscula | — | calcular\_descuento(Decimal("100000.00"), 1, "egresados2026", HOY) | 15000.00 | unitario |
| Cupón con espacios alrededor y mezcla de mayúsculas | — | calcular\_descuento(Decimal("50000.00"), 1, "  Bienvenida ", HOY) | 3000.00 | unitario |
| Sin cupón: None | — | calcular\_descuento(Decimal("100000.00"), 1, None, HOY) | 0.00, sin error | unitario |
| Sin cupón: texto vacío | — | calcular\_descuento(Decimal("100000.00"), 1, "", HOY) | 0.00, sin error | unitario |
| Sin cupón: solo espacios | — | calcular\_descuento(Decimal("100000.00"), 1, "   ", HOY) | 0.00, sin error | unitario |
| Código que no existe | — | calcular\_descuento(Decimal("100000.00"), 1, "PROMO10", HOY) | → CUPON\_INVALIDO | unitario |
| Código parecido a uno real | — | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2025", HOY) | → CUPON\_INVALIDO | unitario |
| Cupón que no es texto | — | calcular\_descuento(Decimal("100000.00"), 1, 123, HOY) | → CUPON\_INVALIDO | unitario |
| No se acumula: gana el cupón | 15% \> 10% | calcular\_descuento(Decimal("100000.00"), 6, "EGRESADOS2026", HOY) | 15000.00 | unitario |
| No se acumula: gana la cantidad | 10000 \> 3000 | calcular\_descuento(Decimal("100000.00"), 5, "BIENVENIDA", HOY) | 10000.00 | unitario |
| No se acumula: gana el cupón fijo | 3000 \> 2500 | calcular\_descuento(Decimal("25000.00"), 5, "BIENVENIDA", HOY) | 3000.00 | unitario |
| Empate entre los dos descuentos | 3000 \= 3000 | calcular\_descuento(Decimal("30000.00"), 5, "BIENVENIDA", HOY) | 3000.00 | unitario |
| Cupón inválido aunque haya 5 prendas → igual es error | — | calcular\_descuento(Decimal("100000.00"), 5, "PROMO10", HOY) | → CUPON\_INVALIDO | unitario |
| Cupón vencido aunque haya 5 prendas | — | calcular\_descuento(Decimal("100000.00"), 5, "EGRESADOS2026", date(2026, 12, 1)) | → CUPON\_VENCIDO | unitario |
| El descuento nunca supera el subtotal | descuento ≤ subtotal | calcular\_descuento(Decimal("20000.00"), 10, "BIENVENIDA", HOY) | 3000.00 | unitario |
| Sin fecha → se usa la del día de la llamada (hoy \= vencido) | hoy 01/12/2026 | Simular que hoy es date(2026, 12, 1\) con monkeypatch; calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026") | → CUPON\_VENCIDO | unitario |
| Sin fecha → se usa la del día de la llamada (hoy \= vigente) | hoy 30/11/2026 | Simular que hoy es date(2026, 11, 30); calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026") | 15000.00 | unitario |
| Sin fecha también en calcular\_total | hoy 01/12/2026 | Simular hoy date(2026, 12, 1); calcular\_total(\[item()\], "CABA", "EGRESADOS2026") | → CUPON\_VENCIDO | unitario |

## R7 — Dinero y redondeo

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| El subtotal es Decimal | — | calcular\_subtotal(\[item(cantidad=2)\]) | Decimal("49999.80") y type(...) is Decimal | unitario |
| Todos los importes de calcular\_total son Decimal | — | calcular\_total(\[item(cantidad=2)\], "CABA") | los cuatro valores son Decimal | unitario |
| El descuento y el envío son Decimal aunque valgan 0 | — | calcular\_total(\[item(producto="campera", cantidad=2)\], "CABA") | descuento \== Decimal("0.00"), envio \== Decimal("0.00"), ambos Decimal | unitario |
| Porcentaje con medio centavo → redondea hacia arriba (cupón) | ,925 → ,93 | calcular\_descuento(Decimal("11999.50"), 1, "EGRESADOS2026", HOY) | 1799.93 | unitario |
| Porcentaje con medio centavo → redondea hacia arriba (cantidad) | ,005 → ,01 | calcular\_descuento(Decimal("100.05"), 5, None, HOY) | 10.01 | unitario |
| Porcentaje por debajo del medio centavo → redondea hacia abajo | ,0015 → ,00 | calcular\_descuento(Decimal("100.01"), 1, "EGRESADOS2026", HOY) | 15.00 | unitario |
| Porcentaje exacto, sin redondeo | — | calcular\_descuento(Decimal("100000.00"), 5, None, HOY) | 10000.00 | unitario |
| Montos con centavos que en float no son exactos | — | calcular\_subtotal(\[item("remera", cantidad=3)\]) | 35998.50 | unitario |

## R8 — Envío

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| CABA | — | calcular\_envio(Decimal("1000.00"), "CABA") | 2500.00 | unitario |
| GBA | — | calcular\_envio(Decimal("1000.00"), "GBA") | 4000.00 | unitario |
| INTERIOR | — | calcular\_envio(Decimal("1000.00"), "INTERIOR") | 6500.00 | unitario |
| RETIRO | — | calcular\_envio(Decimal("1000.00"), "RETIRO") | 0.00 | unitario |
| Zona en minúscula | — | calcular\_envio(Decimal("1000.00"), "gba") | 4000.00 | unitario |
| Zona con espacios y mezcla de mayúsculas | — | calcular\_envio(Decimal("1000.00"), "  Interior ") | 6500.00 | unitario |
| Envío pago: base menor a 60.000 | 59999.99 | calcular\_envio(Decimal("59999.99"), "CABA") | 2500.00 | unitario |
| Envío gratis: base igual a 60.000 | 60000.00 | calcular\_envio(Decimal("60000.00"), "CABA") | 0.00 | unitario |
| Envío gratis: base mayor a 60.000 | 60000.01 | calcular\_envio(Decimal("60000.01"), "INTERIOR") | 0.00 | unitario |
| El límite se mira con el descuento ya aplicado | 61999.30 − 3000 \= 58999.30 | calcular\_total(\[item("buzo", cantidad=2), item("remera")\], "CABA", "BIENVENIDA", HOY) | envío 2500.00 | unitario |
| Base con descuento que sigue arriba de 60.000 | 85998.30 − 8599.83 \= 77398.47 | calcular\_total(\[item("buzo", cantidad=2), item("remera", cantidad=3)\], "CABA") | envío 0.00 | unitario |
| Zona que no existe | — | calcular\_envio(Decimal("1000.00"), "MARTE") | → ZONA\_INVALIDA | unitario |
| Zona vacía | — | calcular\_envio(Decimal("1000.00"), "") | → ZONA\_INVALIDA | unitario |
| Zona que no es texto | — | calcular\_envio(Decimal("1000.00"), None) | → ZONA\_INVALIDA | unitario |
| Zona inválida aunque el envío sea gratis | — | calcular\_envio(Decimal("70000.00"), "MARTE") | → ZONA\_INVALIDA | unitario |

## R9 — Total

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Ejemplo de la spec: sin descuento, con envío | — | calcular\_total(\[item(cantidad=2)\], "CABA") | {"subtotal": 49999.80, "descuento": 0.00, "envio": 2500.00, "total": 52499.80} | unitario |
| Con descuento y con envío | — | calcular\_total(\[item("remera")\], "CABA", "EGRESADOS2026", HOY) | {"subtotal": 11999.50, "descuento": 1799.93, "envio": 2500.00, "total": 12699.57} | unitario |
| Con descuento por cantidad y envío gratis | — | calcular\_total(\[item("buzo", cantidad=2), item("remera", cantidad=3)\], "CABA") | {"subtotal": 85998.30, "descuento": 8599.83, "envio": 0.00, "total": 77398.47} | unitario |
| Con cupón fijo y envío pago | — | calcular\_total(\[item("buzo", cantidad=2), item("remera")\], "CABA", "BIENVENIDA", HOY) | {"subtotal": 61999.30, "descuento": 3000.00, "envio": 2500.00, "total": 61499.30} | unitario |
| Sin descuento y envío gratis | — | calcular\_total(\[item("campera", cantidad=2)\], "CABA") | {"subtotal": 95999.98, "descuento": 0.00, "envio": 0.00, "total": 95999.98} | unitario |
| Retiro en el colegio | — | calcular\_total(\[item()\], "RETIRO") | total \== 24999.90 | unitario |
| Envío a GBA | — | calcular\_total(\[item("campera")\], "GBA") | total \== 51999.99 | unitario |

## Orden de validación de calcular\_total

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Carrito vacío antes que la zona y el cupón | — | calcular\_total(\[\], "MARTE", "PROMO10", HOY) | → CARRITO\_VACIO | unitario |
| Producto antes que talle y cantidad | — | calcular\_total(\[item(producto="gorra", talle="ZZ", cantidad=0)\], "CABA") | → PRODUCTO\_INEXISTENTE | unitario |
| Talle antes que cantidad | — | calcular\_total(\[item(talle="ZZ", cantidad=0)\], "CABA") | → TALLE\_INVALIDO | unitario |
| Los ítems se revisan en orden | — | calcular\_total(\[item(cantidad=0), item(producto="gorra")\], "CABA") | → CANTIDAD\_INVALIDA | unitario |
| Ítems antes que el cupón | — | calcular\_total(\[item(talle="ZZ")\], "CABA", "PROMO10", HOY) | → TALLE\_INVALIDO | unitario |
| Cupón antes que la zona | — | calcular\_total(\[item()\], "MARTE", "PROMO10", HOY) | → CUPON\_INVALIDO | unitario |
| Solo la zona está mal | — | calcular\_total(\[item()\], "MARTE") | → ZONA\_INVALIDA | unitario |
| Nunca otra excepción: falta una clave | — | calcular\_total(\[{"producto": "buzo", "cantidad": 1}\], "CABA") | → TALLE\_INVALIDO | unitario |

---

## R10 — Persistencia (pedidos.py)

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Error de checkout en un ítem → no se guarda nada | — | guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item(talle="ZZ")\], "CABA") | → TALLE\_INVALIDO, y desde otra conexión: 0 filas en pedidos y 0 en items | integración |
| Error de checkout en la zona → no se guarda nada | — | guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item()\], "MARTE") | → ZONA\_INVALIDA, 0 pedidos y 0 ítems | integración |
| Error de checkout en el cupón → no se guarda nada | — | guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item()\], "CABA", "EGRESADOS2026", date(2026, 12, 1)) | → CUPON\_VENCIDO, 0 pedidos y 0 ítems | integración |
| Un error no borra los pedidos anteriores | — | Guardar un pedido válido y después uno con talle="ZZ" | queda 1 pedido y 1 ítem | integración |
| Pedido terminado → otra conexión lo ve completo | — | pid \= guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item("remera")\], "CABA"); obtener\_pedido(otra, pid) | total \== Decimal("14499.50") y 1 ítem | integración |
| Pedido con varios ítems → otra conexión ve todos | 2 ítems | guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item("buzo"), item("remera", cantidad=2)\], "GBA") y leer desde otra conexión | 2 ítems, en el mismo orden | integración |
| Montos idénticos a los de checkout | 1799.925 → 1799.93 | guardar\_pedido(con, "[ana@mail.com](mailto:ana@mail.com)", \[item("remera")\], "CABA", "EGRESADOS2026", date(2026, 11, 1)) y leer | subtotal 11999.50, descuento 1799.93, envio 2500.00, total 12699.57, todos Decimal e iguales a calcular\_total(...) con los mismos datos | integración |
| Montos que en float pierden precisión | — | Guardar \[item("campera")\] a "CABA" y leer | subtotal \== Decimal("47999.99"), total \== Decimal("50499.99") y str(subtotal) \== "47999.99" | integración |
| precio\_unitario sale del catálogo | — | Guardar \[item(precio=1)\] y leer | items\[0\]\["precio\_unitario"\] \== Decimal("24999.90") | integración |
| El precio del cliente tampoco cambia los totales | — | Guardar \[item(precio=1)\] a "CABA" y leer | subtotal \== Decimal("24999.90") | integración |
| Email normalizado | — | guardar\_pedido(con, "  [Ana@Mail.COM](mailto:Ana@Mail.COM) ", \[item()\], "CABA") y leer | email \== "[ana@mail.com](mailto:ana@mail.com)" | integración |
| Zona normalizada | — | Guardar con zona " caba " y leer | zona \== "CABA" | integración |
| Talle normalizado | — | Guardar \[item(talle=" m ")\] y leer | items\[0\]\["talle"\] \== "M" | integración |
| Cupón normalizado | — | Guardar con cupón " egresados2026 " y fecha=date(2026, 11, 1\) y leer | cupon \== "EGRESADOS2026" | integración |
| Cupón vacío → None | "", "   ", None | Guardar con cada uno y leer | cupon is None | integración |
| Id inexistente → None | base vacía | obtener\_pedido(con, 999\) | None | integración |
| Id inexistente con otros pedidos guardados | id siguiente al último | Guardar 1 pedido (pid); obtener\_pedido(con, pid \+ 1\) | None | integración |
| pedidos\_de ordena del más reciente al más antiguo | 3 pedidos | Guardar 3 pedidos de [ana@mail.com](mailto:ana@mail.com); pedidos\_de(con, "[ana@mail.com](mailto:ana@mail.com)") | 3 pedidos, con los ids en orden descendente | integración |
| pedidos\_de no distingue mayúsculas ni espacios | — | Guardar como [ana@mail.com](mailto:ana@mail.com); pedidos\_de(con, "  [ANA@Mail.com](mailto:ANA@Mail.com) ") | encuentra el pedido | integración |
| pedidos\_de solo trae los del email pedido | 2 personas | Guardar de [ana@mail.com](mailto:ana@mail.com) y de [beto@mail.com](mailto:beto@mail.com); pedidos\_de(con, "[beto@mail.com](mailto:beto@mail.com)") | solo el de beto | integración |
| pedidos\_de de un email sin pedidos | — | pedidos\_de(con, "[nadie@mail.com](mailto:nadie@mail.com)") | \[\] | integración |
| Ningún email altera la consulta (inyección SQL) | — | Guardar pedidos de 2 personas; pedidos\_de(con, "x' OR '1'='1") | \[\] | integración |
| Un email con comilla es un dato válido | — | Guardar de o'[brien@mail.com](mailto:brien@mail.com); pedidos\_de(con, "o'[brien@mail.com](mailto:brien@mail.com)") | devuelve ese pedido, sin error | integración |

---

## R11 — API HTTP (api.py)

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| POST válido sin cupón ni fecha | — | POST /api/v1/pedidos con {"email": "[ana@mail.com](mailto:ana@mail.com)", "zona": "CABA", "carrito": \[buzo M 1\]} | 201, {"id": , "subtotal": "24999.90", "descuento": "0.00", "envio": "2500.00", "total": "27499.90"} | E2E |
| POST válido con cupón y fecha (último día) | 2026-11-30 | POST con remera M 1, "cupon": "EGRESADOS2026", "fecha": "2026-11-30" | 201, "descuento": "1799.93", "total": "12699.57" | E2E |
| Los montos viajan como texto, nunca como número | — | Cualquier POST válido | subtotal, descuento, envio y total son str en el JSON | E2E |
| Crear y leer: el GET devuelve el pedido completo | — | POST del caso anterior y GET /api/v1/pedidos/{id} | 200, mismos montos como texto, email, zona, cupon, e items\[0\]\["precio\_unitario"\] \== "11999.50" | E2E |
| GET de un pedido con datos sin normalizar | — | POST con email " [Ana@Mail.com](mailto:Ana@Mail.com) " y zona "caba", después GET | "email": "[ana@mail.com](mailto:ana@mail.com)", "zona": "CABA" | E2E |
| Error de negocio → 422 con el code del checkout | — | POST con talle "XXXL" | 422, {"error": {"code": "TALLE\_INVALIDO", "message": ...}} | E2E |
|  |  | POST con "carrito": \[\] | 422, CARRITO\_VACIO | E2E |
|  |  | POST con "zona": "MARTE" | 422, ZONA\_INVALIDA | E2E |
| Cupón vencido por la fecha que manda el cliente | 2026-12-01 | POST con "cupon": "EGRESADOS2026", "fecha": "2026-12-01" | 422, CUPON\_VENCIDO | E2E |
| Cuerpo que no es JSON | — | POST con el cuerpo crudo b"{no" | 400, JSON\_INVALIDO | E2E |
| Falta un dato obligatorio | email, zona, carrito | POST sin "email" (y lo mismo sin "zona" y sin "carrito") | 400, DATOS\_INCOMPLETOS | E2E |
| Dato obligatorio con otro tipo | — | POST con "zona": 123 | 400, DATOS\_INCOMPLETOS | E2E |
|  |  | POST con "carrito": "buzo" | 400, DATOS\_INCOMPLETOS | E2E |
|  |  | POST con "email": null | 400, DATOS\_INCOMPLETOS | E2E |
| JSON válido que no es un objeto | — | POST con el cuerpo \[\] | 400, DATOS\_INCOMPLETOS | E2E |
| Fecha con otro formato | — | POST con "fecha": "30/11/2026" | 400, FECHA\_INVALIDA | E2E |
| Fecha con formato correcto pero imposible | mes 13 | POST con "fecha": "2026-13-01" | 400, FECHA\_INVALIDA | E2E |
| Pedido que no existe | — | GET /api/v1/pedidos/999 | 404, PEDIDO\_INEXISTENTE | E2E |
| Ruta que no existe (GET) | — | GET /api/v1/otra | 404, RUTA\_INEXISTENTE | E2E |
| Ruta que no existe (POST) | — | POST /api/v1/otra | 404, RUTA\_INEXISTENTE | E2E |
| Un error nunca devuelve 500 | — | Todos los casos de error de esta tabla | ninguno responde 500 y todos tienen el formato {"error": {"code", "message"}} | E2E |
| Un error no deja nada guardado | — | POST con talle "XXXL" y después GET /api/v1/pedidos/1 | 404, PEDIDO\_INEXISTENTE | E2E |

