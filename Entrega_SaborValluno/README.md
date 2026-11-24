# Sistema de pedidos Sabor Valluno — Variante A

Aplicación de consola en Python para el proyecto individual de POO. Implementa las reglas generales y la Variante A. Según la indicación comunicada por la estudiante, no se modela la clase `Restaurante` y se excluye el punto 9 sobre retraso del delivery.

## Ejecutar

- Requiere Python 3.10 o posterior; no usa paquetes externos.
- Desde esta carpeta: `python main.py`
- Pruebas: `python pruebas.py`

El programa carga los precios del caso de referencia: silpancho Bs 35 y mocochinchi en vaso Bs 6. Los otros precios se ingresan al registrar productos porque la consigna no fija todos esos valores.

## Estructura

```text
Entrega_SaborValluno/
├── main.py
├── pruebas.py
├── README.md
├── modelo/
│   ├── productos.py
│   ├── clientes.py
│   ├── pedidos.py
│   └── pagos.py
└── docs/
    ├── diagrama_v1.png
    ├── diagrama_v2.png
    ├── diagrama_v2.mmd
    ├── bitacora_ia.md
    ├── registro_ia_arellano.md
    └── acta_consultas.md
```

## Reglas implementadas

- Descuento de combo: 10 %; admite combos dentro de combos y evita ciclos.
- Para llevar: Bs 2 por plato, incluidos los que forman parte de combos.
- Delivery: pedido mínimo Bs 40; tarifas Cercado Bs 8, Quillacollo Bs 15, Sacaba Bs 15 y Vinto Bs 20.
- Envío gratis desde Bs 150 únicamente en Cercado.
- Chicharrón disponible solo los domingos.
- Jarra: tres veces el precio del vaso.
- Efectivo debe cubrir el total; QR valida 10 dígitos; tarjeta suma comisión del 3 % y no se permite para delivery.
- Teléfono de 8 dígitos que comienza con 6 o 7; cantidad por detalle entre 1 y 20.
- Solo se modifica un pedido en estado `REGISTRADO`; solo desde ese estado se puede cancelar.
- Importes redondeados a dos decimales.

## Diseño

`Producto`, `Pedido` y `MetodoPago` son clases abstractas. Sus subclases implementan los comportamientos propios de platos, bebidas, combos, tipos de pedido y métodos de pago. `main.py` coordina el menú y las listas en memoria; no existe una clase `Restaurante` por indicación del docente. Los datos se pierden al cerrar el programa, ya que no se implementó persistencia.

## Pruebas y GitHub

`pruebas.py` contiene 14 comprobaciones con `assert`. El 24/11/2026 se ejecutaron en el entorno de trabajo y pasaron; también se comprobó la compilación y el inicio y salida del menú. Repite ambos comandos en el equipo de la estudiante antes de entregar.

El repositorio fue creado y el primer commit se subió a GitHub: [sistema-pedidos-sabor-valluno](https://github.com/sharonarellano06/sistema-pedidos-sabor-valluno). El historial actual tiene un commit inicial; cualquier requisito de commits semanales anteriores debe confirmarse con el docente, porque no se registran commits retrospectivos.

La bitácora y el acta incluyen campos por completar con fechas verificables, respuestas reales del docente y la firma de la estudiante. No deben presentarse esos campos pendientes como hechos confirmados.
