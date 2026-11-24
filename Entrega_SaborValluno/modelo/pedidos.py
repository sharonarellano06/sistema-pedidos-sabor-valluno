from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from .clientes import Cliente
from .pagos import MetodoPago
from .productos import Producto, normalizar, redondear_bs
ESTADO_REGISTRADO = "REGISTRADO"
ESTADO_EN_PREPARACION = "EN_PREPARACION"
ESTADO_LISTO = "LISTO"
ESTADO_ENTREGADO = "ENTREGADO"
ESTADO_CANCELADO = "CANCELADO"
ESTADOS_FINALES = {ESTADO_ENTREGADO, ESTADO_CANCELADO}
DIAS_ORDEN = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
COSTO_ENVASE_POR_PLATO_A = Decimal("2.00")
PEDIDO_MINIMO_DELIVERY_A = Decimal("40.00")
ENVIO_GRATIS_CERCADO_A = Decimal("150.00")
TARIFAS_DELIVERY = {
    "cercado": Decimal("8.00"),
    "quillacollo": Decimal("15.00"),
    "sacaba": Decimal("15.00"),
    "vinto": Decimal("20.00"),
}
def _subtotal_neto(pedido: Pedido) -> Decimal:
    """Subtotal luego de descuentos de combos, antes de cargos por pedido."""
    return redondear_bs(pedido.calcular_subtotal() - pedido.calcular_descuentos())
class DetallePedido:
    def __init__(self, producto: Producto, cantidad: int) -> None:
        self.__producto = producto
        self.cantidad = cantidad
    @property
    def producto(self) -> Producto:
        return self.__producto
    @property
    def cantidad(self) -> int:
        return self.__cantidad
    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or not 1 <= valor <= 20:
            raise ValueError("La cantidad de un producto en el pedido debe estar entre 1 y 20.")
        self.__cantidad = valor
    def calcular_subtotal(self) -> Decimal:
        """Importe de linea antes de mostrar/restar el descuento del combo."""
        precio_final = self.__producto.calcular_precio()
        descuento = self.__producto.calcular_descuento()
        return redondear_bs((precio_final + descuento) * self.__cantidad)
    def calcular_descuento(self) -> Decimal:
        return redondear_bs(self.__producto.calcular_descuento() * self.__cantidad)
class Pedido(ABC):
    def __init__(self, codigo: int, cliente: Cliente) -> None:
        self.__codigo = codigo
        self.__cliente = cliente
        self.__estado = ESTADO_REGISTRADO
        self.__fecha_hora_registro = datetime.now()
        self.__detalles: list[DetallePedido] = []
        self.__metodo_pago: MetodoPago | None = None
    @property
    def codigo(self) -> int:
        return self.__codigo
    @property
    def cliente(self) -> Cliente:
        return self.__cliente
    @property
    def estado(self) -> str:
        return self.__estado
    @property
    def fecha_hora_registro(self) -> datetime:
        return self.__fecha_hora_registro
    @property
    def detalles(self) -> tuple[DetallePedido, ...]:
        return tuple(self.__detalles)
    @property
    def metodo_pago(self) -> MetodoPago | None:
        return self.__metodo_pago
    def _exigir_registrado(self) -> None:
        if self.__estado != ESTADO_REGISTRADO:
            raise ValueError("Solo se puede modificar un pedido en estado REGISTRADO.")
    def agregar_producto(self, producto: Producto, cantidad: int) -> None:
        self._exigir_registrado()
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or not 1 <= cantidad <= 20:
            raise ValueError("La cantidad debe estar entre 1 y 20.")
        dia = DIAS_ORDEN[self.__fecha_hora_registro.weekday()]
        if not producto.esta_disponible(dia):
            raise ValueError(f"{producto.nombre} no esta disponible el {dia}.")
        for detalle in self.__detalles:
            if detalle.producto is producto:
                detalle.cantidad = detalle.cantidad + cantidad
                return
        self.__detalles.append(DetallePedido(producto, cantidad))
    def quitar_producto(self, producto: Producto) -> None:
        self._exigir_registrado()
        for detalle in self.__detalles:
            if detalle.producto is producto:
                self.__detalles.remove(detalle)
                return
        raise ValueError("Ese producto no forma parte del pedido.")
    def calcular_subtotal(self) -> Decimal:
        return redondear_bs(sum(
            (detalle.calcular_subtotal() for detalle in self.__detalles), Decimal("0")
        ))
    def calcular_descuentos(self) -> Decimal:
        return redondear_bs(sum(
            (detalle.calcular_descuento() for detalle in self.__detalles), Decimal("0")
        ))
    @abstractmethod
    def calcular_cargo(self) -> Decimal:
        """Calcula envases o envio segun el tipo de pedido."""
    def calcular_total(self) -> Decimal:
        if not self.__detalles:
            raise ValueError("No se puede calcular el total de un pedido vacio.")
        total = self.calcular_subtotal() - self.calcular_descuentos() + self.calcular_cargo()
        return redondear_bs(total)
    def cambiar_estado(self, nuevo_estado: str) -> None:
        nuevo = nuevo_estado.strip().upper()
        if nuevo == ESTADO_CANCELADO:
            if self.__estado != ESTADO_REGISTRADO:
                raise ValueError("El pedido solo se puede cancelar desde REGISTRADO.")
            self.__estado = ESTADO_CANCELADO
            return
        transiciones = {
            ESTADO_REGISTRADO: ESTADO_EN_PREPARACION,
            ESTADO_EN_PREPARACION: ESTADO_LISTO,
            ESTADO_LISTO: ESTADO_ENTREGADO,
        }
        if transiciones.get(self.__estado) != nuevo:
            raise ValueError(f"Cambio de estado no permitido: {self.__estado} -> {nuevo}.")
        self.__estado = nuevo
    def registrar_pago(self, metodo_pago: MetodoPago) -> bool:
        if self.__metodo_pago is not None:
            raise ValueError("Este pedido ya tiene un pago registrado.")
        if not self.__detalles:
            raise ValueError("Agrega productos antes de cobrar el pedido.")
        if self.es_delivery() and not metodo_pago.permitido_para_delivery():
            raise ValueError("Para delivery solo se acepta efectivo o QR.")
        total_a_cobrar = metodo_pago.calcular_monto_a_cobrar(self.calcular_total())
        if metodo_pago.procesar_pago(total_a_cobrar):
            self.__metodo_pago = metodo_pago
            return True
        return False
    def es_delivery(self) -> bool:
        return False
    def generar_comprobante(self) -> str:
        lineas = [
            f"COMPROBANTE - Pedido {self.__codigo}",
            f"Cliente: {self.__cliente.nombre} | Telefono: {self.__cliente.telefono}",
            f"Fecha: {self.__fecha_hora_registro:%Y-%m-%d %H:%M}",
            f"Estado: {self.__estado}",
            "Detalle:",
        ]
        for detalle in self.__detalles:
            lineas.append(
                f"  {detalle.cantidad} x {detalle.producto.nombre}: "
                f"Bs {detalle.calcular_subtotal():.2f}"
            )
        lineas.extend([
            f"Subtotal antes de descuentos: Bs {self.calcular_subtotal():.2f}",
            f"Descuentos de combos: Bs {self.calcular_descuentos():.2f}",
            f"Cargo: Bs {self.calcular_cargo():.2f}",
            f"TOTAL: Bs {self.calcular_total():.2f}",
        ])
        if self.__metodo_pago is not None:
            lineas.append(f"Pago: {self.__metodo_pago.nombre_metodo()}")
            cambio = self.__metodo_pago.calcular_cambio(self.calcular_total())
            if cambio > 0:
                lineas.append(f"Cambio: Bs {cambio:.2f}")
        return "\n".join(lineas)
class PedidoLocal(Pedido):
    def __init__(self, codigo: int, cliente: Cliente, mesa: int) -> None:
        if not isinstance(mesa, int) or isinstance(mesa, bool) or not 1 <= mesa <= 15:
            raise ValueError("La mesa debe estar entre 1 y 15.")
        self.__mesa = mesa
        super().__init__(codigo, cliente)
    @property
    def mesa(self) -> int:
        return self.__mesa
    def calcular_cargo(self) -> Decimal:
        return Decimal("0.00")
class PedidoParaLlevar(Pedido):
    def __init__(self, codigo: int, cliente: Cliente) -> None:
        super().__init__(codigo, cliente)
    def calcular_cargo(self) -> Decimal:
        platos = sum(
            detalle.cantidad * detalle.producto.contar_platos()
            for detalle in self.detalles
        )
        costo_por_plato = Decimal(platos) * COSTO_ENVASE_POR_PLATO_A
        return redondear_bs(costo_por_plato)
class PedidoDelivery(Pedido):
    def __init__(self, codigo: int, cliente: Cliente, zona: str) -> None:
        clave_zona = normalizar(zona)
        if clave_zona not in TARIFAS_DELIVERY:
            raise ValueError("Zona invalida. Usa Cercado, Quillacollo, Sacaba o Vinto.")
        self.__zona = clave_zona.title()
        self.__tarifa_zona = TARIFAS_DELIVERY[clave_zona]
        super().__init__(codigo, cliente)
    @property
    def zona(self) -> str:
        return self.__zona
    @property
    def tarifa_zona(self) -> Decimal:
        return self.__tarifa_zona
    def es_delivery(self) -> bool:
        return True
    def validar_pedido_minimo(self) -> None:
        if _subtotal_neto(self) < PEDIDO_MINIMO_DELIVERY_A:
            raise ValueError(
                f"El delivery requiere un subtotal minimo de Bs {PEDIDO_MINIMO_DELIVERY_A:.2f}."
            )
    def calcular_cargo(self) -> Decimal:
        self.validar_pedido_minimo()
        es_cercado_gratis = (
            normalizar(self.__zona) == "cercado"
            and _subtotal_neto(self) >= ENVIO_GRATIS_CERCADO_A
        )
        return Decimal("0.00") if es_cercado_gratis else self.__tarifa_zona