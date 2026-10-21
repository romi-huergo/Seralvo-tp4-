# Auditoría

## Sección 1: los tests de la IA

### Clasificación

| Test | Clasificación | Por qué |
| :---- | :---- | :---- |
| test\_subtotal | Tautológico | El esperado se calcula como CATALOGO\["buzo"\] \* 2, igual que el código: si el precio del catálogo está mal o es float, el test también. |
| test\_total\_funciona | Inútil | Solo verifica que el resultado no sea None, y calcular\_total siempre devuelve un diccionario: no puede detectar ningún monto mal calculado. |
| test\_total\_positivo | Débil | total \> 0 acepta cualquier número positivo, así que pasa aunque el descuento, el envío o el redondeo estén mal. |
| test\_cupon\_egresados | Tautológico | Compara contra 100000 \* 0.15 en float, la misma cuenta que hace el código, y usa una fecha lejos del vencimiento: no ve el 30/11 ni el redondeo. |
| test\_envio\_caba | Útil | Compara contra 2500, un valor fijo que sale de la spec, aunque prueba una sola zona y lejos del límite de 60.000. |
| test\_descuento\_por\_cantidad | Débil | Usa 6 prendas, donde \> 5 y \>= 5 dan lo mismo, así que no detecta que con 5 prendas no hay descuento. |
| test\_talle\_valido | Débil | No tiene assert y prueba solo el caso más común ("M"): no ve que "m " o " M" fallen ni que se modifique el ítem. |
| test\_no\_explota\_con\_varios\_productos | Inútil | El try/except: pass hace que pase siempre, aunque calcular\_total tire cualquier error o devuelva cualquier cosa. |

### Mutación

Comando: python mutar.py \--tests test\_checkout\_ia.py

Resultado: 29 mutantes generados, 17 muertos, 12 sobrevivientes. Puntaje de mutación: 58,6%.

### Por qué casi 80% de cobertura no detectó ninguna falla

No importa cuanto cubre. Porque los tests de la IA pasan por casi todo el código, pero sus asserts son débiles (\> 0, is not None), tautológicos (repiten la misma cuenta en float que el código) o directamente no existen. Además usan siempre valores del medio del rango (6 prendas, una fecha de octubre, una base de 10.000) y nunca los bordes (5 prendas, el 30/11, 60.000), que es donde están los errores. Y como el código y los tests los escribió la misma IA, comparten el mismo malentendido de la spec: si la IA creyó que el descuento era con más de 5 prendas, el test también lo cree. Por eso la línea con el error se ejecuta,y por mas que este mal, el test sigue en verde.

SECCION 2 HALLAZGOS

# Hallazgos

## checkout.py

### F-01 · Los montos se manejan como float

- Archivo y línea: checkout.py, líneas 13-15, 21-22, 27-30, 45 y 58 (y el envío devuelve int en 97 y 99\)  
- Categoría: numéricos  
- Regla: R7 (todos los importes como Decimal, nunca float)  
- Qué pasa: calcular\_subtotal devuelve float y calcular\_envio devuelve int; ningún importe es Decimal.  
- Cómo la encontré: caso de CASOS.md (R7, tipo del subtotal) y lectura del catálogo  
- Severidad: alta

### F-02 · El redondeo no es comercial

- Archivo y línea: checkout.py, líneas 54, 84 y 117  
- Categoría: numéricos  
- Regla: R7 (el medio centavo redondea hacia arriba)  
- Qué pasa: el 15% de 11.999,50 da 1.799,92 en vez de 1.799,93, porque round() sobre un float redondea al par y además el float no guarda exacto el ,925.  
- Cómo la encontré: ejemplo de la spec en R7, probado con calcular\_descuento  
- Severidad: alta

### F-03 · Usa el precio que manda el cliente

- Archivo y línea: checkout.py, línea 49  
- Categoría: seguridad  
- Regla: R1 (el precio sale siempre del catálogo)  
- Qué pasa: item.get("precio", ...) usa el precio del ítem si viene; una campera con "precio": 1 cuesta \$1  
- Cómo la encontré: lectura del código y caso de CASOS.md (R1, precio propio)  
- Severidad: alta

### F-04 · Los productos inexistentes se saltean sin error

- Archivo y línea: checkout.py, líneas 48-51  
- Categoría: manejo de errores  
- Regla: R1 (producto que no está en el catálogo  PRODUCTO\_INEXISTENTE)  
- Qué pasa: el except vacío atrapa el KeyError y hace continue; una "gorra" suma \$0 y nunca se lanza PRODUCTO\_INEXISTENTE.  
- Cómo la encontré: ruff (E722) y caso de CASOS.md (R1, "gorra")  
- Severidad: alta

### F-05 · validar\_item no valida el producto y valida el talle primero

- Archivo y línea: checkout.py, líneas 34-41  
- Categoría: lógica y límites  
- Regla: R1 y sección 3 (orden: producto, talle, cantidad)  
- Qué pasa: validar\_item({"producto": "gorra", "talle": "ZZ"}) informa TALLE\_INVALIDO en vez de PRODUCTO\_INEXISTENTE.  
- Cómo la encontré: caso de CASOS.md (orden de validación)  
- Severidad: media

### F-06 · El talle con espacios es rechazado

- Archivo y línea: checkout.py, línea 35  
- Categoría: strings  
- Regla: R2 (se ignoran los espacios al principio y al final)  
- Qué pasa: "  M " da TALLE\_INVALIDO porque solo se hace upper(), sin strip().  
- Cómo la encontré: caso de CASOS.md (R2)  
- Severidad: media

### F-07 · validar\_item modifica el ítem que recibe

- Archivo y línea: checkout.py, línea 35  
- Categoría: efectos laterales  
- Regla: R4 (ninguna función modifica el carrito que recibe)  
- Qué pasa: item\["talle"\] \= item\["talle"\].upper() pisa el talle del carrito del frontend: "m" pasa a ser "M".  
- Cómo la encontré: lectura del código y caso de CASOS.md (R4, copia del carrito)  
- Severidad: media

### F-08 · Un talle que no es texto rompe con AttributeError

- Archivo y línea: checkout.py, línea 35  
- Categoría: tipos  
- Regla: R2 y sección 1 (ante un dato inválido, siempre CheckoutError)  
- Qué pasa: talle None tira AttributeError en vez de TALLE\_INVALIDO.  
- Cómo la encontré: caso de CASOS.md (R2, talle None)  
- Severidad: baja

### F-09 · La cantidad 10 es rechazada

- Archivo y línea: checkout.py, línea 40  
- Categoría: lógica y límites  
- Regla: R3 (entre 1 y 10, ambos inclusive)  
- Qué pasa: el código usa \< 10 en vez de \<= 10, así que no se pueden comprar 10 unidades.  
- Cómo la encontré: valor límite de CASOS.md (R3, 10\)  
- Severidad: alta

### F-10 · Acepta cantidades que no son enteras

- Archivo y línea: checkout.py, línea 40  
- Categoría: tipos  
- Regla: R3 (los no enteros → CANTIDAD\_INVALIDA)  
- Qué pasa: 2.5 y True pasan la validación; "3" tira TypeError en vez de CANTIDAD\_INVALIDA.  
- Cómo la encontré: casos de CASOS.md (R3, no enteros)  
- Severidad: media

### F-11 · El carrito vacío no da error

- Archivo y línea: checkout.py, líneas 44-54 y 102-103  
- Categoría: lógica y límites  
- Regla: R4 (al menos un ítem, si no CARRITO\_VACIO)  
- Qué pasa: calcular\_total(\[\], "CABA") devuelve un total de 2500 en vez de CARRITO\_VACIO.  
- Cómo la encontré: caso de CASOS.md (R4, 0 ítems)  
- Severidad: media

### F-12 · Con 5 prendas no hay descuento

- Archivo y línea: checkout.py, línea 60  
- Categoría: lógica y límites  
- Regla: R5 (5 o más prendas → 10%)  
- Qué pasa: el código usa \> 5, así que con exactamente 5 prendas el descuento es 0\.  
- Cómo la encontré: valor límite de CASOS.md (R5, 5\) y mutante sobreviviente de la línea 60  
- Severidad: alta

### F-13 · El cupón se acumula con el descuento por cantidad

- Archivo y línea: checkout.py, líneas 60-82  
- Categoría: lógica y límites  
- Regla: R6 (no se acumulan: se aplica el mayor)  
- Qué pasa: 6 prendas con EGRESADOS2026 sobre 100.000 dan 25.000 de descuento en vez de 15.000.  
- Cómo la encontré: caso de CASOS.md (R6, no se acumula)  
- Severidad: alta

### F-14 · Existe un cupón oculto de 100%

- Archivo y línea: checkout.py, línea 23  
- Categoría: seguridad  
- Regla: R6 (EGRESADOS2026 y BIENVENIDA son los únicos cupones)  
- Qué pasa: DEBUG100 regala el 100% de la compra hasta 2099 a cualquiera que lo conozca.  
- Cómo la encontré: lectura del diccionario CUPONES  
- Severidad: alta

### F-15 · El descuento puede superar el subtotal

- Archivo y línea: checkout.py, líneas 58-84  
- Categoría: lógica y límites  
- Regla: R6 (el descuento nunca puede superar el subtotal)  
- Qué pasa: 6 buzos con DEBUG100 a RETIRO dan un descuento de 164.999,34 sobre 149.999,40 y un total negativo de \-14.999,94.  
- Cómo la encontré: probando la combinación de F-13 y F-14  
- Severidad: media

### F-16 · El cupón distingue mayúsculas

- Archivo y línea: checkout.py, línea 64  
- Categoría: strings  
- Regla: R6 (no se distingue mayúscula de minúscula)  
- Qué pasa: "egresados2026" da CUPON\_INVALIDO porque se hace strip() pero no upper().  
- Cómo la encontré: caso de CASOS.md (R6, minúscula)  
- Severidad: media

### F-17 · El cupón vacío da error

- Archivo y línea: checkout.py, líneas 63-67  
- Categoría: strings  
- Regla: R6 ("" o solo espacios equivalen a no usar cupón)  
- Qué pasa: "" y "   " dan CUPON\_INVALIDO en vez de descuento 0 sin error.  
- Cómo la encontré: caso de CASOS.md (R6, cupón vacío)  
- Severidad: media

### F-18 · EGRESADOS2026 vence un día antes

- Archivo y línea: checkout.py, línea 72  
- Categoría: fechas  
- Regla: R6 (válido hasta el 30/11/2026 inclusive)  
- Qué pasa: not fecha \< vence rechaza el mismo 30/11 con CUPON\_VENCIDO.  
- Cómo la encontré: valor límite de CASOS.md (R6, 30/11) y mutante sobreviviente de la línea 72  
- Severidad: alta

### F-19 · La fecha por defecto se calcula al importar el módulo

- Archivo y línea: checkout.py, líneas 57 y 102  
- Categoría: fechas  
- Regla: R6 (sin fecha, se usa la del día en que se hace la llamada)  
- Qué pasa: fecha=date.today() se evalúa una sola vez, cuando arranca el programa; si el servidor queda prendido del 30/11 al 1/12, el cupón sigue valiendo.  
- Cómo la encontré: ruff (B008) y caso de CASOS.md (R6, sin fecha)  
- Severidad: media

### F-20 · fecha=None explícita rompe el cupón

- Archivo y línea: checkout.py, líneas 57 y 72  
- Categoría: fechas  
- Regla: R6 y contrato (fecha: date | None)  
- Qué pasa: calcular\_descuento(..., "EGRESADOS2026", None) tira TypeError. pedidos.py siempre pasa fecha=None si no la recibe, así que guardar cualquier pedido con cupón y sin fecha explota.  
- Cómo la encontré: probando guardar\_pedido con cupón y sin fecha  
- Severidad: alta

### F-21 · Un cupón que no es texto rompe con AttributeError

- Archivo y línea: checkout.py, línea 64  
- Categoría: tipos  
- Regla: sección 1 (ante un dato inválido, siempre CheckoutError)  
- Qué pasa: un cupón 123 tira AttributeError en vez de CUPON\_INVALIDO.  
- Cómo la encontré: caso de CASOS.md (R6, cupón que no es texto)  
- Severidad: baja

### F-22 · El mensaje de zona inválida usa un método que no existe

- Archivo y línea: checkout.py, línea 93  
- Categoría: alucinación  
- Regla: R8 (zona que no existe → ZONA\_INVALIDA)  
- Qué pasa: ENVIOS.keys().join(", ") no existe en Python; en vez de ZONA\_INVALIDA sale un AttributeError.  
- Cómo la encontré: caso de CASOS.md (R8, "MARTE")  
- Severidad: alta

### F-23 · El envío gratis se calcula sin el descuento

- Archivo y línea: checkout.py, línea 110  
- Categoría: lógica y límites  
- Regla: R8 (gratis si el subtotal ya con el descuento es de 60.000 o más)  
- Qué pasa: 2 buzos y una remera con BIENVENIDA (61.999,30 − 3.000 \= 58.999,30) tienen envío gratis cuando deberían pagar 2.500.  
- Cómo la encontré: caso de CASOS.md (R8, límite con descuento)  
- Severidad: media

### F-24 · Una zona que no es texto rompe con AttributeError

- Archivo y línea: checkout.py, línea 88  
- Categoría: tipos  
- Regla: sección 1 (ante un dato inválido, siempre CheckoutError)  
- Qué pasa: zona None tira AttributeError en vez de ZONA\_INVALIDA.  
- Cómo la encontré: caso de CASOS.md (R8, zona que no es texto)  
- Severidad: baja

### F-25 · Un ítem sin alguna clave rompe con KeyError

- Archivo y línea: checkout.py, líneas 35, 40, 49 y 107  
- Categoría: manejo de errores  
- Regla: sección 1 (ante un dato inválido, siempre CheckoutError)  
- Qué pasa: un ítem sin "talle" tira KeyError en vez de TALLE\_INVALIDO.  
- Cómo la encontré: caso de CASOS.md (orden de validación, falta una clave)  
- Severidad: baja

### F-26 · Import sin usar

- Archivo y línea: checkout.py, línea 1  
- Categoría: code smell  
- Regla: —  
- Qué pasa: se importa json y nunca se usa.  
- Cómo la encontré: ruff (F401)  
- Severidad: baja

### F-27 · Comparación con None usando \!=

- Archivo y línea: checkout.py, línea 63  
- Categoría: code smell  
- Regla: —  
- Qué pasa: cupon \!= None en vez de cupon is not None.  
- Cómo la encontré: ruff (E711)  
- Severidad: baja

## pedidos.py

### F-28 · Un error de checkout deja un pedido guardado a medias

- Archivo y línea: pedidos.py, líneas 39-50  
- Categoría: manejo de errores  
- Regla: R10 (si calcular\_total lanza CheckoutError, no queda nada guardado)  
- Qué pasa: el pedido se inserta y se hace commit antes de calcular; con talle "ZZ" sale el error pero queda un pedido con total 0 y sin ítems.  
- Cómo la encontré: lectura del código y probando con otra conexión (1 pedido, 0 ítems)  
- Severidad: alta

### F-29 · El pedido terminado no queda guardado

- Archivo y línea: pedidos.py, líneas 52-71  
- Categoría: efectos laterales  
- Regla: R10 (cuando guardar\_pedido termina, otra conexión lo ve completo)  
- Qué pasa: después del UPDATE y de los INSERT de ítems no hay commit; otra conexión ve el pedido con total 0 y sin ítems. Por eso el GET de la API devuelve el pedido recién creado con montos en 0 y "items": \[\].  
- Cómo la encontré: probando con una segunda conexión y con un POST seguido de un GET  
- Severidad: alta

### F-30 · Los montos pierden precisión al guardarse

- Archivo y línea: pedidos.py, líneas 12-15, 23, 55-58, 68 y 88-97  
- Categoría: numéricos  
- Regla: R10 (los montos son idénticos a los de checkout, Decimal, sin pérdida)  
- Qué pasa: las columnas son REAL y se guarda float(monto); una campera vuelve como Decimal("47999.9899999999979627...") en vez de 47999.99.  
- Cómo la encontré: guardando una campera y leyéndola de otra conexión  
- Severidad: alta

### F-31 · precio\_unitario usa el precio del cliente

- Archivo y línea: pedidos.py, línea 64  
- Categoría: seguridad  
- Regla: R10 (precio\_unitario es el del catálogo, nunca uno enviado por el cliente)  
- Qué pasa: con "precio": 1 en el ítem se guarda precio\_unitario 1\.  
- Cómo la encontré: lectura del código (misma idea que F-03)  
- Severidad: alta

### F-32 · Inyección SQL en pedidos\_de

- Archivo y línea: pedidos.py, línea 107  
- Categoría: seguridad  
- Regla: R10 (ningún valor del email puede alterar la consulta)  
- Qué pasa: el email se pega en el SQL con un f-string; "x' OR '1'='1" devuelve los pedidos de todos, y un email real como "o'[brien@mail.com](mailto:brien@mail.com)" rompe con OperationalError.  
- Cómo la encontré: lectura del código (la única consulta sin ?)  
- Severidad: alta

### F-33 · Datos que no son texto rompen con AttributeError

- Archivo y línea: pedidos.py, líneas 42-44  
- Categoría: tipos  
- Regla: —  
- Qué pasa: un email, una zona o un cupón que no son texto tiran AttributeError antes de llegar a checkout.  
- Cómo la encontré: lectura del código  
- Severidad: baja

## api.py

### F-34 · Los montos viajan como número JSON

- Archivo y línea: api.py, línea 18  
- Categoría: tipos  
- Regla: R11 (los montos viajan siempre como texto)  
- Qué pasa: json.dumps(..., default=float) convierte los Decimal en número: la respuesta trae "total": 27499.9 en vez de "27499.90".  
- Cómo la encontré: haciendo un POST real  
- Severidad: alta

### F-35 · Todo error devuelve 500

- Archivo y línea: api.py, líneas 53-54 y 67-68  
- Categoría: manejo de errores  
- Regla: R11 (CheckoutError → 422 con su code; nunca 500; formato único de error)  
- Qué pasa: un talle "XXXL" responde 500 con {"error": "Talle inválido: XXXL"}, sin code y con otro formato.  
- Cómo la encontré: haciendo un POST con talle inválido  
- Severidad: alta

### F-36 · JSON inválido devuelve 500

- Archivo y línea: api.py, líneas 31-32  
- Categoría: manejo de errores  
- Regla: R11 (cuerpo que no es JSON → 400 JSON\_INVALIDO)  
- Qué pasa: el cuerpo "{no" responde 500 con el mensaje interno del parser.  
- Cómo la encontré: POST con cuerpo roto  
- Severidad: media

### F-37 · No valida los datos obligatorios

- Archivo y línea: api.py, líneas 37-39  
- Categoría: tipos  
- Regla: R11 (falta email, zona o carrito, o tienen otro tipo → 400 DATOS\_INCOMPLETOS)  
- Qué pasa: un POST sin email responde 500 ("'email'") y uno con zona 123 también.  
- Cómo la encontré: POST sin email y con zona numérica  
- Severidad: media

### F-38 · La fecha se pasa como texto sin convertir

- Archivo y línea: api.py, línea 41  
- Categoría: fechas  
- Regla: R11 (la fecha viaja como AAAA-MM-DD; si no tiene ese formato → 400 FECHA\_INVALIDA)  
- Qué pasa: "2026-11-30" llega a checkout como texto; con cupón se compara texto con date y responde 500\. Una fecha "30/11/2026" sin cupón se acepta con 201\.  
- Cómo la encontré: POST con cupón y fecha, y POST con fecha mal escrita  
- Severidad: alta

### F-39 · Un pedido que no existe devuelve 200

- Archivo y línea: api.py, líneas 64-66  
- Categoría: manejo de errores  
- Regla: R11 (pedido que no existe → 404 PEDIDO\_INEXISTENTE)  
- Qué pasa: GET /api/v1/pedidos/999 responde 200 con el cuerpo null.  
- Cómo la encontré: GET de un id que no existe  
- Severidad: media

### F-40 · La conexión no se cierra si hay un error

- Archivo y línea: api.py, líneas 34-44 y 63-65  
- Categoría: code smell  
- Regla: —  
- Qué pasa: con.close() está dentro del try; si algo falla antes, la conexión queda abierta.  
- Cómo la encontré: lectura del código  
- Severidad: baja

### F-41 · Los errores muestran detalles internos

- Archivo y línea: api.py, líneas 54 y 68  
- Categoría: seguridad  
- Regla: —  
- Qué pasa: se responde str(e), que muestra mensajes internos de Python (por ejemplo "'\<' not supported between instances of 'str' and 'datetime.date'").  
- Cómo la encontré: mirando las respuestas 500 de las pruebas anteriores  
- Severidad: baja

## Resumen de las fallas, de la más grave a la menos grave

| Falla | Archivo y línea | Categoría | Regla | Severidad |
| :---- | :---- | :---- | :---- | :---- |
| F-03 Usa el precio que manda el cliente | checkout.py 49 | seguridad | R1 | alta |
| F-14 Cupón oculto de 100% | checkout.py 23 | seguridad | R6 | alta |
| F-31 precio\_unitario del cliente | pedidos.py 64 | seguridad | R10 | alta |
| F-32 Inyección SQL en pedidos\_de | pedidos.py 107 | seguridad | R10 | alta |
| F-28 Error deja un pedido a medias | pedidos.py 39-50 | manejo de errores | R10 | alta |
| F-29 El pedido no queda guardado | pedidos.py 52-71 | efectos laterales | R10 | alta |
| F-30 Montos con pérdida al guardarse | pedidos.py 12-15, 55-58, 88-97 | numéricos | R10 | alta |
| F-01 Montos en float | checkout.py 13-15, 45, 58 | numéricos | R7 | alta |
| F-02 Redondeo no comercial | checkout.py 54, 84, 117 | numéricos | R7 | alta |
| F-04 Productos inexistentes se saltean | checkout.py 48-51 | manejo de errores | R1 | alta |
| F-09 Cantidad 10 rechazada | checkout.py 40 | lógica y límites | R3 | alta |
| F-12 5 prendas sin descuento | checkout.py 60 | lógica y límites | R5 | alta |
| F-13 Cupón acumulado con cantidad | checkout.py 60-82 | lógica y límites | R6 | alta |
| F-18 EGRESADOS2026 vence un día antes | checkout.py 72 | fechas | R6 | alta |
| F-20 fecha=None rompe el cupón | checkout.py 57, 72 | fechas | R6 | alta |
| F-22 Método join que no existe | checkout.py 93 | alucinación | R8 | alta |
| F-34 Montos como número JSON | api.py 18 | tipos | R11 | alta |
| F-35 Todo error devuelve 500 | api.py 53-54, 67-68 | manejo de errores | R11 | alta |
| F-38 Fecha sin convertir | api.py 41 | fechas | R11 | alta |
| F-05 No valida producto y orden incorrecto | checkout.py 34-41 | lógica y límites | R1, sección 3 | media |
| F-06 Talle con espacios rechazado | checkout.py 35 | strings | R2 | media |
| F-07 Modifica el ítem recibido | checkout.py 35 | efectos laterales | R4 | media |
| F-10 Acepta cantidades no enteras | checkout.py 40 | tipos | R3 | media |
| F-11 Carrito vacío sin error | checkout.py 44-54, 102-103 | lógica y límites | R4 | media |
| F-15 Descuento mayor al subtotal | checkout.py 58-84 | lógica y límites | R6 | media |
| F-16 Cupón distingue mayúsculas | checkout.py 64 | strings | R6 | media |
| F-17 Cupón vacío da error | checkout.py 63-67 | strings | R6 | media |
| F-19 Fecha por defecto al importar | checkout.py 57, 102 | fechas | R6 | media |
| F-23 Envío gratis sin el descuento | checkout.py 110 | lógica y límites | R8 | media |
| F-36 JSON inválido devuelve 500 | api.py 31-32 | manejo de errores | R11 | media |
| F-37 No valida datos obligatorios | api.py 37-39 | tipos | R11 | media |
| F-39 Pedido inexistente devuelve 200 | api.py 64-66 | manejo de errores | R11 | media |
| F-08 Talle no texto rompe | checkout.py 35 | tipos | R2 | baja |
| F-21 Cupón no texto rompe | checkout.py 64 | tipos | sección 1 | baja |
| F-24 Zona no texto rompe | checkout.py 88 | tipos | sección 1 | baja |
| F-25 Ítem sin clave rompe | checkout.py 35, 40, 49, 107 | manejo de errores | sección 1 | baja |
| F-33 Datos no texto rompen en pedidos | pedidos.py 42-44 | tipos | — | baja |
| F-40 Conexión sin cerrar | api.py 34-44, 63-65 | code smell | — | baja |
| F-41 Errores con detalles internos | api.py 54, 68 | seguridad | — | baja |
| F-26 Import sin usar | checkout.py 1 | code smell | — | baja |
| F-27 Comparación con \!= None | checkout.py 63 | code smell | — | baja |

