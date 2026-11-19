from collections import defaultdict
from typing import Any


def resumir_ordenes_completadas(orders: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    """
    Se calcula el total comprado, la cantidad de órdenes y el promedio de compra
    por cliente cdejando nada mas las ordenes COMPLETADAS.
    """
    # Usamos defaultdict para inicializar automáticamente contadores en 0
    # la primera vez que vemos a un cliente con una orden COMPLETADA.
    acumulado: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"total": 0.0, "cantidad_ordenes": 0}
    )

    for order in orders:
        # Normalizacion de texto.
        estado = str(order.get("estado", "")).strip().upper()

        # las que sean diferente de completada se ignoran.
        if estado != "COMPLETADA":
            continue

        
        cliente = str(order["cliente"]).strip()
        monto = float(order["monto"])

        acumulado[cliente]["total"] += monto
        acumulado[cliente]["cantidad_ordenes"] += 1

    resumen: dict[str, dict[str, float | int]] = {}
    for cliente, datos in acumulado.items():
        total = round(float(datos["total"]), 2)
        cantidad = int(datos["cantidad_ordenes"])

        # Calculamos el promedio solo si hay órdenes (evita división por cero).
        promedio = round(total / cantidad, 2) if cantidad > 0 else 0.0

        resumen[cliente] = {
            "total_comprado": total,
            "cantidad_ordenes": cantidad,
            "promedio_compra": promedio,
        }

    return resumen


if __name__ == "__main__":
    orders = [
        {"cliente": "Ana", "estado": "COMPLETADA", "monto": 120},
        {"cliente": "Luis", "estado": "PENDIENTE", "monto": 50},
        {"cliente": "Ana", "estado": "COMPLETADA", "monto": 80},
        {"cliente": "Pedro", "estado": "COMPLETADA", "monto": 200},
    ]

    resultado = resumir_ordenes_completadas(orders)

    for cliente, metricas in resultado.items():
        print(f"{cliente}: {metricas}")