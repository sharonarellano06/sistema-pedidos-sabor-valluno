from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from modelo.clientes import Cliente
from modelo.pagos import PagoEfectivo, PagoQR, PagoTarjeta
from modelo.pedidos import (
    ESTADO_CANCELADO,
    ESTADO_EN_PREPARACION,
    ESTADO_ENTREGADO,
    ESTADO_LISTO,
    ESTADO_REGISTRADO,
    Pedido,
    PedidoDelivery,
    PedidoLocal,
    PedidoParaLlevar,
)
from modelo.productos import Bebida, Combo, Plato, Producto, normalizar
productos: list[Producto] = []
clientes: list[Cliente] = []
pedidos: list[Pedido] = []
DIA_SEMANA_ES = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
def cargar_productos_de_referencia() -> None:
    productos.extend([
        Plato("Silpancho", "35.00"),
        Bebida("Mocochinchi", "6.00", "refresco natural", "vaso"),
    ])
def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                raise ValueError
            if maximo is not None and valor > maximo:
                raise ValueError
            return valor
        except ValueError:
            print("Ingresa un numero entero valido dentro del rango indicado.")
def leer_decimal(mensaje: str, minimo: Decimal | None = None) -> Decimal:
    while True:
        try:
            valor = Decimal(input(mensaje).strip().replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"El monto debe ser como minimo {minimo}.")
                continue
            return valor
        except InvalidOperation:
            print("Ingresa un monto numerico, por ejemplo 35.50.")
def elegir_indice(elementos: list, mensaje: str):
    if not elementos:
        print("No hay elementos registrados.")
        return None
    for indice, elemento in enumerate(elementos, start=1):
        if hasattr(elemento, "telefono") and hasattr(elemento, "nombre"):
            descripcion = f"{elemento.nombre} ({elemento.telefono})"
        elif hasattr(elemento, "codigo") and hasattr(elemento, "cliente"):
            descripcion = f"Pedido {elemento.codigo} - {elemento.cliente.nombre} - {elemento.estado}"
        elif hasattr(elemento, "calcular_precio") and hasattr(elemento, "nombre"):
            descripcion = f"{elemento.nombre} - Bs {elemento.calcular_precio():.2f}"
        else:
            descripcion = str(elemento)
        print(f"{indice}. {descripcion}")
    opcion = leer_entero(mensaje, 1, len(elementos))
    return elementos[opcion - 1]
def mostrar_menu(dia: str | None = None) -> list[Producto]:
    if dia is None:
        dia_actual = DIA_SEMANA_ES[date.today().weekday()]
        print("Dias: lunes, martes, miercoles, jueves, viernes, sabado, domingo")
        dia = input(f"Dia a consultar (Enter para {dia_actual}): ").strip() or dia_actual
    dia = normalizar(dia)
    disponibles = [producto for producto in productos if producto.esta_disponible(dia)]
    print(f"\nMENU DISPONIBLE - {dia.upper()}")
    if not disponibles:
        print("No hay productos disponibles para ese dia.")
        return []
    for indice, producto in enumerate(disponibles, start=1):
        print(f"{indice}. {producto.nombre} - Bs {producto.calcular_precio():.2f}")
    return disponibles
def registrar_producto() -> None:
    print("\n1. Plato\n2. Bebida\n3. Combo")
    tipo = leer_entero("Tipo de producto: ", 1, 3)
    nombre = input("Nombre: ").strip()
    if tipo == 1:
        precio = leer_decimal("Precio en Bs: ", Decimal("0.01"))
        dias_texto = input("Dias disponibles separados por coma (vacio = todos): ").strip()
        dias = None if not dias_texto else [parte.strip() for parte in dias_texto.split(",")]
        nuevo = Plato(nombre, precio, dias)
    elif tipo == 2:
        precio = leer_decimal("Precio por vaso en Bs: ", Decimal("0.01"))
        tipo_bebida = input("Tipo (refresco natural/gaseosa/otro): ").strip()
        presentacion = input("Presentacion (vaso/jarra): ").strip().lower() or "vaso"
        nuevo = Bebida(nombre, precio, tipo_bebida, presentacion)
    else:
        nuevo = registrar_combo(nombre)
    productos.append(nuevo)
    print(f"Producto registrado: {nuevo.nombre}, Bs {nuevo.calcular_precio():.2f}.")
def registrar_combo(nombre: str) -> Combo:
    combo = Combo(nombre)
    disponibles = list(productos)
    if not disponibles:
        raise ValueError("Registra primero platos o bebidas para armar un combo.")
    print("Selecciona los componentes. Un combo debe incluir dos o mas unidades de producto.")
    while sum(fila.cantidad for fila in combo.productos) < 2:
        componente = elegir_indice(disponibles, "Numero del producto componente: ")
        if componente is None:
            raise ValueError("No se pudo seleccionar un producto para el combo.")
        cantidad = leer_entero("Cantidad de ese producto en el combo: ", 1)
        combo.agregar_producto(componente, cantidad)
        if sum(fila.cantidad for fila in combo.productos) < 2:
            print("Aun falta al menos un producto para completar el combo.")
    print(f"Precio del combo con descuento A: Bs {combo.calcular_precio():.2f}.")
    return combo
def registrar_cliente() -> None:
    nombre = input("Nombre del cliente: ").strip()
    telefono = input("Telefono (8 digitos, empieza con 6 o 7): ").strip()
    cliente = Cliente(nombre, telefono)
    clientes.append(cliente)
    print(f"Cliente registrado: {cliente.nombre} ({cliente.telefono}).")
def mesa_disponible(mesa: int) -> bool:
    return all(
        not isinstance(pedido, PedidoLocal)
        or pedido.mesa != mesa
        or pedido.estado in {ESTADO_ENTREGADO, ESTADO_CANCELADO}
        for pedido in pedidos
    )
def crear_pedido() -> None:
    cliente = elegir_indice(clientes, "Elige el numero del cliente: ")
    if cliente is None:
        return
    print("\n1. Local\n2. Para llevar\n3. Delivery")
    tipo = leer_entero("Tipo de pedido: ", 1, 3)
    codigo = max((pedido.codigo for pedido in pedidos), default=0) + 1
    if tipo == 1:
        mesa = leer_entero("Mesa (1 a 15): ", 1, 15)
        if not mesa_disponible(mesa):
            raise ValueError("Esa mesa ya tiene un pedido abierto.")
        pedido = PedidoLocal(codigo, cliente, mesa)
    elif tipo == 2:
        pedido = PedidoParaLlevar(codigo, cliente)
    else:
        zona = input("Zona (Cercado/Quillacollo/Sacaba/Vinto): ").strip()
        pedido = PedidoDelivery(codigo, cliente, zona)
    while True:
        disponibles = mostrar_menu(DIA_SEMANA_ES[date.today().weekday()])
        if not disponibles:
            raise ValueError("Registra productos disponibles antes de crear un pedido.")
        opcion = leer_entero("Producto para agregar (0 para terminar): ", 0, len(disponibles))
        if opcion == 0:
            break
        producto = disponibles[opcion - 1]
        cantidad = leer_entero("Cantidad (1 a 20): ", 1, 20)
        pedido.agregar_producto(producto, cantidad)
        print(f"Agregado: {producto.nombre} x {cantidad}.")
    if not pedido.detalles:
        raise ValueError("No se registro el pedido porque no agregaste productos.")
    if isinstance(pedido, PedidoDelivery):
        pedido.validar_pedido_minimo()
    pedidos.append(pedido)
    print(f"Pedido {pedido.codigo} creado. Estado: {pedido.estado}.")
    print(pedido.generar_comprobante())
def seleccionar_pedido() -> Pedido | None:
    return elegir_indice(pedidos, "Elige el numero del pedido: ")
def mostrar_detalle_pedido() -> None:
    pedido = seleccionar_pedido()
    if pedido is not None:
        print(pedido.generar_comprobante())
def modificar_pedido() -> None:
    pedido = seleccionar_pedido()
    if pedido is None:
        return
    if pedido.estado != ESTADO_REGISTRADO:
        raise ValueError("Solo se puede modificar un pedido REGISTRADO.")
    print("\n1. Agregar producto\n2. Quitar producto")
    accion = leer_entero("Accion: ", 1, 2)
    if accion == 1:
        disponibles = mostrar_menu(DIA_SEMANA_ES[date.today().weekday()])
        if not disponibles:
            raise ValueError("No hay productos disponibles para agregar hoy.")
        opcion = leer_entero("Producto para agregar: ", 1, len(disponibles))
        cantidad = leer_entero("Cantidad (1 a 20): ", 1, 20)
        pedido.agregar_producto(disponibles[opcion - 1], cantidad)
    else:
        if not pedido.detalles:
            raise ValueError("El pedido no tiene productos para quitar.")
        producto = elegir_indice([detalle.producto for detalle in pedido.detalles], "Producto a quitar: ")
        if producto is not None:
            pedido.quitar_producto(producto)
    print(pedido.generar_comprobante())
def cambiar_estado_pedido() -> None:
    pedido = seleccionar_pedido()
    if pedido is None:
        return
    print(f"Estado actual: {pedido.estado}")
    opciones = {
        ESTADO_REGISTRADO: [ESTADO_EN_PREPARACION, ESTADO_CANCELADO],
        ESTADO_EN_PREPARACION: [ESTADO_LISTO],
        ESTADO_LISTO: [ESTADO_ENTREGADO],
    }.get(pedido.estado, [])
    if not opciones:
        print("Este pedido ya esta en un estado final.")
        return
    for indice, estado in enumerate(opciones, start=1):
        print(f"{indice}. {estado}")
    nuevo_estado = opciones[leer_entero("Nuevo estado: ", 1, len(opciones)) - 1]
    pedido.cambiar_estado(nuevo_estado)
    print(f"Pedido actualizado a {pedido.estado}.")
def cobrar_pedido() -> None:
    pedido = seleccionar_pedido()
    if pedido is None:
        return
    if pedido.metodo_pago is not None:
        raise ValueError("Ese pedido ya tiene un pago registrado.")
    total = pedido.calcular_total()
    print(f"Total del pedido: Bs {total:.2f}")
    print("\n1. Efectivo\n2. QR\n3. Tarjeta")
    tipo = leer_entero("Medio de pago: ", 1, 3)
    if tipo == 1:
        metodo = PagoEfectivo(leer_decimal("Monto recibido en Bs: ", Decimal("0")))
    elif tipo == 2:
        metodo = PagoQR(input("Codigo de transaccion QR (10 digitos): ").strip())
    else:
        metodo = PagoTarjeta()
    print(f"Monto a cobrar con {metodo.nombre_metodo()}: Bs {metodo.calcular_monto_a_cobrar(total):.2f}")
    if pedido.registrar_pago(metodo):
        print("Pago registrado correctamente.")
        print(pedido.generar_comprobante())
    else:
        print("Pago rechazado: el monto recibido no cubre el total.")
def _sumar_productos_vendidos(producto: Producto, cantidad: int, ventas: Counter) -> None:
    """Cuenta los productos pedidos; si se vendio un combo, cuenta el combo."""
    ventas[producto.nombre] += cantidad
def generar_reporte() -> None:
    texto_fecha = input("Fecha del reporte (AAAA-MM-DD): ").strip()
    fecha = date.fromisoformat(texto_fecha)
    pedidos_del_dia = [
        pedido for pedido in pedidos
        if pedido.fecha_hora_registro.date() == fecha
        and pedido.estado != ESTADO_CANCELADO
        and pedido.metodo_pago is not None
    ]
    ventas_tipo = defaultdict(Decimal)
    cantidad_tipo = Counter()
    unidades: Counter = Counter()
    total_dia = Decimal("0.00")
    for pedido in pedidos_del_dia:
        nombre_tipo = type(pedido).__name__.removeprefix("Pedido")
        ventas_tipo[nombre_tipo] += pedido.calcular_total()
        cantidad_tipo[nombre_tipo] += 1
        total_dia += pedido.calcular_total()
        for detalle in pedido.detalles:
            _sumar_productos_vendidos(detalle.producto, detalle.cantidad, unidades)
    print(f"\nREPORTE DE VENTAS - {fecha.isoformat()}")
    if not pedidos_del_dia:
        print("No hay pedidos pagados para esa fecha.")
        return
    print(f"Pedidos pagados: {len(pedidos_del_dia)}")
    for tipo, monto in sorted(ventas_tipo.items()):
        print(f"{tipo}: {cantidad_tipo[tipo]} pedido(s), Bs {monto:.2f}")
    print(f"Total del dia: Bs {total_dia:.2f}")
    print("Tres productos mas vendidos:")
    for puesto, (nombre, cantidad) in enumerate(unidades.most_common(3), start=1):
        print(f"{puesto}. {nombre}: {cantidad} unidad(es)")
def ejecutar_accion(opcion: int) -> None:
    acciones = {
        1: lambda: mostrar_menu(),
        2: registrar_producto,
        3: registrar_cliente,
        4: crear_pedido,
        5: mostrar_detalle_pedido,
        6: modificar_pedido,
        7: cambiar_estado_pedido,
        8: cobrar_pedido,
        9: generar_reporte,
    }
    acciones[opcion]()
def main() -> None:
    cargar_productos_de_referencia()
    print("Sistema de pedidos Sabor Valluno - Variante A")
    print("Precios de referencia cargados: Silpancho Bs 35 y mocochinchi en vaso Bs 6.")
    while True:
        print(
            "\nMENU PRINCIPAL"
            "\n1. Ver menu disponible"
            "\n2. Registrar plato, bebida o combo"
            "\n3. Registrar cliente"
            "\n4. Crear pedido"
            "\n5. Ver detalle/comprobante"
            "\n6. Modificar pedido registrado"
            "\n7. Cambiar estado/cancelar pedido"
            "\n8. Cobrar pedido"
            "\n9. Reporte de ventas"
            "\n0. Salir"
        )
        opcion = leer_entero("Elige una opcion: ", 0, 9)
        if opcion == 0:
            print("Hasta luego.")
            break
        try:
            ejecutar_accion(opcion)
        except (ValueError, InvalidOperation) as error:
            print(f"No se pudo completar la accion: {error}")
if __name__ == "__main__":
    main()