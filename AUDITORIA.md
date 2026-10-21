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

- 