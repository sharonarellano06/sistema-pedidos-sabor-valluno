from abc import ABC, abstractmethod
from decimal import Decimal
from .productos import redondear_bs
class MetodoPago(ABC):
    @abstractmethod
    def nombre_metodo(self) -> str:
        pass
    @abstractmethod
    def calcular_monto_a_cobrar(self, total_pedido: Decimal) -> Decimal:
        pass
    @abstractmethod
    def procesar_pago(self, total_pedido: Decimal) -> bool:
        pass
    @abstractmethod
    def permitido_para_delivery(self) -> bool:
        pass
    def calcular_cambio(self, total_pedido: Decimal) -> Decimal:
        return Decimal("0.00")
class PagoEfectivo(MetodoPago):
    def __init__(self, monto_recibido: Decimal | str | int) -> None:
        self.__monto_recibido = Decimal(str(monto_recibido))
        if self.__monto_recibido < 0:
            raise ValueError("El monto recibido no puede ser negativo.")
    def nombre_metodo(self) -> str:
        return "Efectivo"
    @property
    def monto_recibido(self) -> Decimal:
        return self.__monto_recibido
    def calcular_monto_a_cobrar(self, total_pedido: Decimal) -> Decimal:
        return redondear_bs(total_pedido)
    def procesar_pago(self, total_pedido: Decimal) -> bool:
        return self.__monto_recibido >= self.calcular_monto_a_cobrar(total_pedido)
    def permitido_para_delivery(self) -> bool:
        return True
    def calcular_cambio(self, total_pedido: Decimal) -> Decimal:
        return redondear_bs(self.__monto_recibido - self.calcular_monto_a_cobrar(total_pedido))
class PagoQR(MetodoPago):
    def __init__(self, codigo_transaccion: str) -> None:
        self.__codigo_transaccion = codigo_transaccion.strip()
        if not self.validar_codigo_transaccion():
            raise ValueError("El codigo QR debe tener exactamente 10 digitos.")
    def nombre_metodo(self) -> str:
        return "QR"
    @property
    def codigo_transaccion(self) -> str:
        return self.__codigo_transaccion
    def validar_codigo_transaccion(self) -> bool:
        return len(self.__codigo_transaccion) == 10 and self.__codigo_transaccion.isdigit()
    def calcular_monto_a_cobrar(self, total_pedido: Decimal) -> Decimal:
        return redondear_bs(total_pedido)
    def procesar_pago(self, total_pedido: Decimal) -> bool:
        return self.validar_codigo_transaccion()
    def permitido_para_delivery(self) -> bool:
        return True
class PagoTarjeta(MetodoPago):
    def __init__(self) -> None:
        self.__porcentaje_comision = Decimal("0.03")
    def nombre_metodo(self) -> str:
        return "Tarjeta"
    @property
    def porcentaje_comision(self) -> Decimal:
        return self.__porcentaje_comision
    def calcular_monto_a_cobrar(self, total_pedido: Decimal) -> Decimal:
        return redondear_bs(total_pedido * (Decimal("1") + self.__porcentaje_comision))
    def procesar_pago(self, total_pedido: Decimal) -> bool:
        return True  
    def permitido_para_delivery(self) -> bool:
        return False
