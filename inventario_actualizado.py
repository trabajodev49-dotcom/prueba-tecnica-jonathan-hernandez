from typing import Any


def _normalizar_claves(raw_dict: dict[str, Any]) -> dict[str, Any]:
    """Limpia espacios en blanco al inicio y final ."""
    return {str(clave).strip(): valor for clave, valor in raw_dict.items()}


def calcular_inventario_base(movimientos: list[dict[str, Any]]) -> dict[str, int]:
    """
     calcula el inventario final por producto sumando 'entrada'
    y restando 'salida'.
    """
    inventario: dict[str, int] = {}

    for raw_mov in movimientos:
        mov = _normalizar_claves(raw_mov)
        producto = str(mov["producto"]).strip()
        tipo = str(mov["tipo"]).strip().lower()
        cantidad = int(mov["cantidad"])

        inventario.setdefault(producto, 0)

        if tipo == "entrada":
            inventario[producto] += cantidad
        elif tipo == "salida":
            inventario[producto] -= cantidad

    return inventario


def calcular_inventario_controlado(
    movimientos: list[dict[str, Any]],
    estados: list[dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """
    cambio de requerimientos:
    - Ignora movimientos de productos descontinuados.
    - No permite inventarios negativos y reporta movimientos inválidos.
    - Incluye productos con inventario final igual a 0.
    - Ordena el inventario resultante de mayor a menor.
    """
    estado_por_producto: dict[str, str] = {}
    inventario: dict[str, int] = {}

    # Cargamos los estads de los productos y dejamos en 0 los no descontinuados.
    for raw_estado in estados:
        item = _normalizar_claves(raw_estado)
        producto = str(item.get("producto", "")).strip()
        estado = str(item.get("estado", "")).strip().lower()

        if producto:
            estado_por_producto[producto] = estado
            if estado != "descontinuado":
                inventario[producto] = 0

    movimientos_invalidos: list[dict[str, Any]] = []

    for indice, raw_mov in enumerate(movimientos):
        mov = _normalizar_claves(raw_mov)
        producto = str(mov.get("producto", "")).strip()
        tipo = str(mov.get("tipo", "")).strip().lower()
        cantidad_raw = mov.get("cantidad")

        estado_producto = estado_por_producto.get(producto, "disponible")
        if producto and producto not in inventario and estado_producto != "descontinuado":
            inventario[producto] = 0

        #  Ignorar movimientos de productos descontinuados.
        if estado_producto == "descontinuado":
            movimientos_invalidos.append(
                {
                    "indice": indice,
                    "movimiento": mov,
                    "motivo": f"Producto '{producto}' está descontinuado; movimiento ignorado.",
                }
            )
            continue

        #  Validr cantidad numérica y mayor que 0.
        if not isinstance(cantidad_raw, (int, float)) or isinstance(cantidad_raw, bool):
            movimientos_invalidos.append(
                {
                    "indice": indice,
                    "movimiento": mov,
                    "motivo": "Cantidad inválida (debe ser numérica).",
                }
            )
            continue

        cantidad = int(cantidad_raw)
        if cantidad <= 0:
            movimientos_invalidos.append(
                {
                    "indice": indice,
                    "movimiento": mov,
                    "motivo": f"Cantidad inválida ({cantidad}); debe ser mayor que 0.",
                }
            )
            continue

        # Aplicar entrada o salida evitando inventaro negativo.
        if tipo == "entrada":
            inventario[producto] += cantidad
        elif tipo == "salida":
            stock_actual = inventario.get(producto, 0)
            if stock_actual - cantidad < 0:
                movimientos_invalidos.append(
                    {
                        "indice": indice,
                        "movimiento": mov,
                        "motivo": (
                            f"Stock insuficiente para '{producto}': "
                            f"actual={stock_actual}, salida={cantidad}."
                        ),
                    }
                )
                continue
            inventario[producto] = stock_actual - cantidad
        else:
            movimientos_invalidos.append(
                {
                    "indice": indice,
                    "movimiento": mov,
                    "motivo": f"Tipo de movimiento no reconocido: '{tipo}'.",
                }
            )

    # 4. Ordenar de mayor a menor inventario.
    inventario_ordenado = dict(
        sorted(inventario.items(), key=lambda par: par[1], reverse=True)
    )
    return inventario_ordenado, movimientos_invalidos


if __name__ == "__main__":
    movimientos_base = [
        {"producto": "A", "tipo": "entrada", "cantidad": 10},
        {"producto": "A", "tipo": "salida", "cantidad": 3},
        {"producto": "B", "tipo": "entrada", "cantidad": 5},
        {"producto": "A", "tipo": "entrada", "cantidad": 2},
        {"producto": "B", "tipo": "salida", "cantidad": 1},
    ]
    print("Inventario base:", calcular_inventario_base(movimientos_base))

    movimientos_actualizados = [
        {"producto": "A", "tipo": "entrada", "cantidad": 20},
        {"producto": "A", "tipo": "salida", "cantidad": 3},
        {"producto": "B", "tipo": "entrada", "cantidad": 5},
        {"producto": "A", "tipo": "entrada", "cantidad": 2},
        {"producto": "B", "tipo": "salida", "cantidad": -5},
        {"producto": "B", "tipo": "entrada", "cantidad": 10},
        {"producto": "A", "tipo": " salida ", "cantidad": 9},
        {"producto": "B", "tipo": "salida", "cantidad": -5},
    ]

    estados_productos = [
        {"producto": "A", "estado": "disponible "},
        {"producto": "B", " estado ": "disponible"},
        {"producto": "C", " estado ": "descontinuado"},
    ]

    inventario_final, invalidos = calcular_inventario_controlado(
        movimientos_actualizados, estados_productos
    )

    print("\nInventario final (mayor a menor):")
    for producto, stock in inventario_final.items():
        print(f"  - {producto}: {stock}")

    print("\nMovimientos inválidos / ignorados:")
    for error in invalidos:
        print(f"  - {error}")