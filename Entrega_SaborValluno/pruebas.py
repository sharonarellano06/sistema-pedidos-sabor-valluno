from decimal import Decimal
from modelo.clientes import Cliente
from modelo.pagos import PagoEfectivo, PagoQR, PagoTarjeta
from modelo.pedidos import (
    ESTADO_CANCELADO,
    ESTADO_EN_PREPARACION,
    PedidoDelivery,
    PedidoParaLlevar,
)
from modelo.productos import Bebida, Combo, ComboProducto, Plato
def debe_rechazar(accion, tipo_error=ValueError):
    try:
        accion()
    except tipo_error:
        return
    raise AssertionError(f"Se esperaba {tipo_error.__name__}.")
def ejecutar_pruebas():
    cliente = Cliente("Ana", "71234567")
    silpancho = Plato("Silpancho", "35")
    mocochinchi = Bebida("Mocochinchi", "6", "refresco natural")
    combo = Combo("Combo valluno", [
        ComboProducto(silpancho, 1), ComboProducto(mocochinchi, 1)
    ])
    assert combo.calcular_precio() == Decimal("36.90")
    jarra = Bebida("Mocochinchi", "6", "refresco natural", "jarra")
    assert jarra.calcular_precio() == Decimal("18.00")
    chicharron = Plato("Chicharrón", "30")
    assert chicharron.esta_disponible("domingo")
    assert not chicharron.esta_disponible("lunes")
    combo_anidado = Combo("Combo grande", [
        ComboProducto(combo, 1), ComboProducto(mocochinchi, 1)
    ])
    assert combo_anidado.calcular_precio() == Decimal("38.61")
    debe_rechazar(lambda: combo.agregar_producto(combo_anidado))
    pedido_llevar = PedidoParaLlevar(1, cliente)
    pedido_llevar.agregar_producto(combo, 2)
    assert pedido_llevar.calcular_cargo() == Decimal("4.00")
    assert pedido_llevar.calcular_total() == Decimal("77.80")
    pedido_delivery = PedidoDelivery(2, cliente, "Quillacollo")
    pedido_delivery.agregar_producto(combo, 2)
    assert pedido_delivery.calcular_total() == Decimal("88.80")
    pedido_cercado = PedidoDelivery(3, cliente, "Cercado")
    pedido_cercado.agregar_producto(Plato("Especial", "150"), 1)
    assert pedido_cercado.calcular_cargo() == Decimal("0.00")
    minimo = PedidoDelivery(4, cliente, "Sacaba")
    minimo.agregar_producto(Plato("Plato económico", "39.99"), 1)
    debe_rechazar(minimo.calcular_total)
    debe_rechazar(lambda: Cliente("Eva", "51234567"))
    efectivo = PagoEfectivo("100")
    assert efectivo.procesar_pago(Decimal("88.80"))
    assert efectivo.calcular_cambio(Decimal("88.80")) == Decimal("11.20")
    qr = PagoQR("1234567890")
    assert qr.procesar_pago(Decimal("10"))
    debe_rechazar(lambda: PagoQR("1234"))
    tarjeta = PagoTarjeta()
    assert tarjeta.calcular_monto_a_cobrar(Decimal("100")) == Decimal("103.00")
    assert not tarjeta.permitido_para_delivery()
    debe_rechazar(lambda: pedido_delivery.registrar_pago(tarjeta))
    pedido_llevar.cambiar_estado(ESTADO_EN_PREPARACION)
    debe_rechazar(lambda: pedido_llevar.cambiar_estado(ESTADO_CANCELADO))
    pedido_cancelable = PedidoParaLlevar(5, cliente)
    pedido_cancelable.cambiar_estado(ESTADO_CANCELADO)
    assert pedido_cancelable.estado == ESTADO_CANCELADO
    debe_rechazar(lambda: pedido_llevar.agregar_producto(silpancho, 21))
    print("14 pruebas de aceptación completadas correctamente.")
if __name__ == "__main__":
    ejecutar_pruebas()