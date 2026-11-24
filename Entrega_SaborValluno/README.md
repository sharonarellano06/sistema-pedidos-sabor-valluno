# Sistema de pedidos Sabor Valluno — Variante A

Aplicación de consola para el proyecto individual de POO. Implementa las reglas generales del caso y la Variante A. Según la indicación comunicada por la estudiante, no se modela la clase `Restaurante` y se excluye la regla del punto 9 sobre retraso del delivery.

## Requisitos y ejecución

- Python 3.10 o posterior.
- No requiere instalar paquetes externos.
- Desde la carpeta `Entrega_SaborValluno`, ejecutar `python main.py`.
- Para ejecutar las pruebas: `python pruebas.py`.

Al iniciar, carga los dos precios del caso de referencia: silpancho Bs 35 y mocochinchi en vaso Bs 6. Los demás precios se registran desde el menú, porque la consigna no fija un precio para cada producto.

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
    ├── diagrama_v1_original.jpeg
    ├── diagrama_v2.png
    ├── diagrama_v2.mmd
    ├── bitacora_ia.md
    ├── registro_ia_arellano.md
    └── acta_consultas.md
```

## Reglas principales de Variante A

- Combo: 10 % de descuento sobre sus componentes; admite combos anidados y evita ciclos.
- Para llevar: Bs 2 por plato, contando también los platos dentro de combos; bebidas no suman platos.
- Delivery: mínimo Bs 40; tarifas Cercado Bs 8, Quillacollo Bs 15, Sacaba Bs 15 y Vinto Bs 20.
- Envío gratis desde Bs 150 únicamente en Cercado.
- Chicharrón disponible solo los domingos.
- Jarra: tres veces el precio del vaso.
- Efectivo debe cubrir el total; QR requiere código de 10 dígitos; tarjeta añade 3 % y no se acepta en delivery.
- Teléfono: 8 dígitos, comienza con 6 o 7. Cantidad por detalle: 1 a 20.
- El pedido solo se modifica en estado `REGISTRADO`; cancelar también solo es posible desde ese estado.
- Montos en Bs redondeados a dos decimales.

## Correspondencia entre código y UML

`modelo/` contiene las clases de productos y combos, cliente, pedidos y pagos. `main.py` coordina el menú y las colecciones en memoria, en lugar de una clase gestora `Restaurante`, por la instrucción reciente del docente. El diagrama v2 se entrega como PNG para lectura y Mermaid para revisar o editar el texto del diagrama.

## Entregables y estado de verificación

`pruebas.py` contiene 14 casos ejecutables con `assert`. Se ejecutaron en este entorno con Python 3.14.4 y pasaron; también compiló el código y se comprobó el inicio y salida del menú. Repite `python pruebas.py` y `python main.py` en tu equipo antes de entregar. El diagrama v1 se incluye en el formato original y como conversión PNG. La bitácora y el acta distinguen fechas confirmadas de fechas que deben verificarse con el historial o con el docente.

El documento también pide trabajar con Git/GitHub y mantener commits por semana. No se atribuyen commits anteriores que no estén en el historial; el repositorio de entrega aún debe vincularse al remoto GitHub indicado por la estudiante.
