from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable
import unicodedata
CENTAVO = Decimal("0.01")
DESCUENTO_COMBO_A = Decimal("0.10")
DIAS_SEMANA = frozenset({
    "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"
})
def redondear_bs(monto: Decimal) -> Decimal:
    """Redondea un monto en bolivianos a dos decimales."""
    return monto.quantize(CENTAVO, rounding=ROUND_HALF_UP)
def normalizar(texto: str) -> str:
    """Normaliza tildes y mayusculas para comparar dias y nombres."""
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(
        caracter for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return sin_tildes.strip().lower()
class Producto(ABC):
    def __init__(self, nombre: str, precio_base: Decimal | str | int | None) -> None:
        self.__nombre = nombre.strip()
        self.__precio_base = None if precio_base is None else Decimal(str(precio_base))
        if not self.__nombre:
            raise ValueError("El nombre del producto no puede estar vacio.")
        if self.__precio_base is not None:
            self.validar_precio()
    @property
    def nombre(self) -> str:
        return self.__nombre
    @property
    def precio_base(self) -> Decimal:
        if self.__precio_base is None:
            raise ValueError("El precio base del combo se deriva de sus componentes.")
        return self.__precio_base
    def validar_precio(self) -> None:
        if self.precio_base <= Decimal("0"):
            raise ValueError("El precio debe ser mayor que cero.")
    def calcular_descuento(self) -> Decimal:
        """Producto normal: no tiene descuento; Combo redefine este metodo."""
        return Decimal("0.00")
    def contiene_combo(self, combo: Combo) -> bool:
        """Platos y bebidas no contienen otros combos."""
        return False
    @abstractmethod
    def calcular_precio(self) -> Decimal:
        """Devuelve el precio de venta en Bs."""
    @abstractmethod
    def esta_disponible(self, dia: str) -> bool:
        """Indica si se vende en el dia indicado."""
    @abstractmethod
    def contar_platos(self) -> int:
        """Cantidad de platos que representa este producto."""
class Plato(Producto):
    def __init__(
        self,
        nombre: str,
        precio_base: Decimal | str | int,
        dias_disponibles: Iterable[str] | None = None,
    ) -> None:
        super().__init__(nombre, precio_base)
        dias = {normalizar(dia) for dia in (dias_disponibles or DIAS_SEMANA)}
        if not dias.issubset(DIAS_SEMANA):
            raise ValueError("Hay un dia de disponibilidad no valido.")
        # Regla adicional asignada en la Variante A.
        if normalizar(self.nombre) == "chicharron":
            dias = {"domingo"}
        self.__dias_disponibles = frozenset(dias)
    @property
    def dias_disponibles(self) -> frozenset[str]:
        return self.__dias_disponibles
    def calcular_precio(self) -> Decimal:
        return redondear_bs(self.precio_base)
    def esta_disponible(self, dia: str) -> bool:
        return normalizar(dia) in self.__dias_disponibles
    def contar_platos(self) -> int:
        return 1
class Bebida(Producto):
    def __init__(
        self,
        nombre: str,
        precio_base: Decimal | str | int,
        tipo: str,
        presentacion: str = "vaso",
    ) -> None:
        super().__init__(nombre, precio_base)
        self.__tipo = tipo.strip()
        self.__presentacion = normalizar(presentacion)
        if not self.__tipo:
            raise ValueError("El tipo de bebida no puede estar vacio.")
        if self.__presentacion not in {"vaso", "jarra"}:
            raise ValueError("La presentacion debe ser vaso o jarra.")
    @property
    def tipo(self) -> str:
        return self.__tipo
    @property
    def presentacion(self) -> str:
        return self.__presentacion
    def calcular_precio(self) -> Decimal:
        multiplicador = Decimal("3") if self.__presentacion == "jarra" else Decimal("1")
        return redondear_bs(self.precio_base * multiplicador)
    def esta_disponible(self, dia: str) -> bool:
        return normalizar(dia) in DIAS_SEMANA
    def contar_platos(self) -> int:
        return 0
def _validar_minimo_componentes(combo: Combo) -> None:
    if sum(fila.cantidad for fila in combo.productos) < 2:
        raise ValueError("Un combo debe contener al menos dos productos.")
class Combo(Producto):
    def __init__(self, nombre: str, productos: Iterable[ComboProducto] | None = None) -> None:
        # Su precio no se escribe manualmente: se calcula a partir de sus componentes.
        super().__init__(nombre, None)
        self.__descuento = DESCUENTO_COMBO_A
        self.__productos: list[ComboProducto] = []
        for componente in productos or ():
            self.agregar_producto(componente.producto, componente.cantidad)
    @property
    def descuento(self) -> Decimal:
        return self.__descuento
    @property
    def precio_base(self) -> Decimal:
        """Suma de los precios finales de los productos que contiene."""
        return redondear_bs(sum(
            (fila.producto.calcular_precio() * fila.cantidad for fila in self.__productos),
            Decimal("0"),
        ))
    @property
    def productos(self) -> tuple[ComboProducto, ...]:
        return tuple(self.__productos)
    def agregar_producto(self, producto: Producto, cantidad: int = 1) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 1:
            raise ValueError("La cantidad del componente debe ser un entero positivo.")
        if producto is self or producto.contiene_combo(self):
            raise ValueError("Un combo no puede contenerse a si mismo, directa o indirectamente.")
        for fila in self.__productos:
            if fila.producto is producto:
                fila.cantidad += cantidad
                return
        self.__productos.append(ComboProducto(producto, cantidad))
    def calcular_descuento(self) -> Decimal:
        _validar_minimo_componentes(self)
        descuentos_internos = sum(
            (fila.producto.calcular_descuento() * fila.cantidad for fila in self.__productos),
            Decimal("0"),
        )
        descuento_propio = self.precio_base * self.__descuento
        return redondear_bs(descuentos_internos + descuento_propio)
    def calcular_precio(self) -> Decimal:
        _validar_minimo_componentes(self)
        return redondear_bs(self.precio_base * (Decimal("1") - self.__descuento))
    def esta_disponible(self, dia: str) -> bool:
        _validar_minimo_componentes(self)
        return all(fila.producto.esta_disponible(dia) for fila in self.__productos)
    def contar_platos(self) -> int:
        _validar_minimo_componentes(self)
        return sum(
            fila.cantidad * fila.producto.contar_platos()
            for fila in self.__productos
        )
    def contiene_combo(self, combo: Combo) -> bool:
        return any(
            fila.producto is combo or fila.producto.contiene_combo(combo)
            for fila in self.__productos
        )
class ComboProducto:
    def __init__(self, producto: Producto, cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 1:
            raise ValueError("La cantidad del componente debe ser un entero positivo.")
        self.__producto = producto
        self.__cantidad = cantidad
    @property
    def producto(self) -> Producto:
        return self.__producto
    @property
    def cantidad(self) -> int:
        return self.__cantidad
    @cantidad.setter
    def cantidad(self, nueva_cantidad: int) -> None:
        if not isinstance(nueva_cantidad, int) or isinstance(nueva_cantidad, bool) or nueva_cantidad < 1:
            raise ValueError("La cantidad del componente debe ser un entero positivo.")
        self.__cantidad = nueva_cantidad