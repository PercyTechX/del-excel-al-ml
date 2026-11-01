"""Catálogos y parámetros de Distribuidora Andina S.A.C.

Las marcas y los nombres de negocios son inventados. Cualquier parecido con
una marca o un negocio real es coincidencia.
"""

import pandas as pd

# ----------------------------------------------------------------- empresa

# Sedes y su peso relativo en número de clientes.
SEDES = {
    "Lima": 0.40,
    "Arequipa": 0.15,
    "Trujillo": 0.13,
    "Chiclayo": 0.11,
    "Piura": 0.11,
    "Cusco": 0.10,
}

VENDEDORES_POR_SEDE = {
    "Lima": 4,
    "Arequipa": 2,
    "Trujillo": 2,
    "Chiclayo": 2,
    "Piura": 2,
    "Cusco": 2,
}

# --------------------------------------------------------------- productos

# (categoría, nombre, marca, presentación, precio mayorista de la presentación en soles)
PRODUCTOS = [
    ("Abarrotes", "Arroz extra 5 kg", "Valle Dorado", "Fardo x 5", 99.50),
    ("Abarrotes", "Arroz superior 1 kg", "Valle Dorado", "Fardo x 10", 42.00),
    ("Abarrotes", "Azúcar rubia 1 kg", "Cumbre", "Fardo x 10", 39.00),
    ("Abarrotes", "Aceite vegetal 1 L", "Sol del Sur", "Caja x 12", 105.00),
    ("Abarrotes", "Fideos spaghetti 500 g", "Nonna Lucía", "Fardo x 20", 56.00),
    ("Abarrotes", "Fideos tallarín 1 kg", "Nonna Lucía", "Fardo x 10", 52.00),
    ("Abarrotes", "Atún en trozos 170 g", "Puerto Azul", "Caja x 24", 118.00),
    ("Abarrotes", "Leche evaporada 400 g", "Pastizal", "Caja x 24", 88.00),
    ("Abarrotes", "Avena tradicional 900 g", "Cumbre", "Caja x 12", 84.00),
    ("Abarrotes", "Lentejas 500 g", "Del Huerto", "Fardo x 20", 88.00),
    ("Abarrotes", "Frejol canario 500 g", "Del Huerto", "Fardo x 20", 116.00),
    ("Abarrotes", "Sal de mesa 1 kg", "Nevado", "Fardo x 25", 38.00),
    ("Abarrotes", "Harina sin preparar 1 kg", "Cumbre", "Fardo x 10", 40.00),
    ("Abarrotes", "Salsa de tomate 400 g", "Del Huerto", "Caja x 24", 84.00),
    ("Abarrotes", "Panetón 900 g", "Cumbre", "Caja x 6", 120.00),
    ("Bebidas", "Agua sin gas 625 ml", "Nevado", "Paquete x 15", 16.50),
    ("Bebidas", "Agua sin gas 2.5 L", "Nevado", "Paquete x 6", 16.80),
    ("Bebidas", "Gaseosa sabor cola 3 L", "Burbuja", "Paquete x 4", 36.00),
    ("Bebidas", "Gaseosa sabor cola 500 ml", "Burbuja", "Paquete x 12", 24.00),
    ("Bebidas", "Gaseosa sabor naranja 1.5 L", "Burbuja", "Paquete x 6", 33.00),
    ("Bebidas", "Jugo de durazno 1 L", "Fruttal", "Caja x 12", 46.00),
    ("Bebidas", "Chicha morada 1 L", "Fruttal", "Caja x 12", 48.00),
    ("Bebidas", "Néctar de mango 1 L", "Fruttal", "Caja x 12", 46.00),
    ("Bebidas", "Bebida rehidratante 500 ml", "Recarga", "Paquete x 12", 33.00),
    ("Bebidas", "Café instantáneo 50 g", "Altura", "Caja x 12", 92.00),
    ("Bebidas", "Té filtrante 25 sobres", "Altura", "Caja x 12", 37.00),
    ("Limpieza", "Detergente en polvo 2 kg", "Limpix", "Fardo x 6", 128.00),
    ("Limpieza", "Detergente en polvo 500 g", "Limpix", "Fardo x 24", 140.00),
    ("Limpieza", "Lejía 1 L", "Limpix", "Caja x 12", 39.00),
    ("Limpieza", "Bolsas de basura 10 unidades", "Limpix", "Paquete x 20", 72.00),
    ("Limpieza", "Lavavajillas en pasta 900 g", "Destello", "Caja x 12", 88.00),
    ("Limpieza", "Jabón de lavar ropa 220 g", "Destello", "Caja x 50", 120.00),
    ("Limpieza", "Limpiatodo lavanda 900 ml", "Destello", "Caja x 12", 56.00),
    ("Limpieza", "Esponja multiuso 3 unidades", "Destello", "Paquete x 24", 70.00),
    ("Limpieza", "Suavizante de ropa 1 L", "Nube", "Caja x 12", 102.00),
    ("Cuidado personal", "Shampoo 400 ml", "Pétalo", "Caja x 12", 150.00),
    ("Cuidado personal", "Jabón de tocador 3 unidades", "Pétalo", "Caja x 24", 155.00),
    ("Cuidado personal", "Papel higiénico 4 rollos", "Pétalo", "Fardo x 12", 66.00),
    ("Cuidado personal", "Papel higiénico 24 rollos", "Pétalo", "Fardo x 3", 84.00),
    ("Cuidado personal", "Toallas húmedas 80 unidades", "Pétalo", "Caja x 12", 90.00),
    ("Cuidado personal", "Pasta dental 90 g", "Sonrisa", "Caja x 24", 100.00),
    ("Cuidado personal", "Cepillo dental", "Sonrisa", "Caja x 24", 78.00),
    ("Cuidado personal", "Desodorante en barra 50 g", "Fresco", "Caja x 12", 122.00),
    ("Snacks", "Galletas de soda 6 unidades", "Crujis", "Caja x 12", 40.00),
    ("Snacks", "Galletas rellenas de chocolate 6 unidades", "Crujis", "Caja x 12", 46.00),
    ("Snacks", "Papas fritas clásicas 150 g", "Crujis", "Caja x 12", 70.00),
    ("Snacks", "Chifles salados 100 g", "Norteñito", "Paquete x 20", 60.00),
    ("Snacks", "Cancha serrana 100 g", "Norteñito", "Paquete x 20", 50.00),
    ("Snacks", "Maní salado 100 g", "Norteñito", "Paquete x 20", 55.00),
    ("Snacks", "Chocolate con leche 30 g", "Cacao Andino", "Caja x 24", 45.00),
    ("Snacks", "Caramelos surtidos 100 unidades", "Dulcería Real", "Paquete x 10", 68.00),
]

# El costo es 85–92 % del precio: una distribuidora trabaja con márgenes bajos.
MARGEN_COSTO = (0.85, 0.92)

# ---------------------------------------------------------------- personas

NOMBRES_MUJER = [
    "María",
    "Rosa",
    "Carmen",
    "Ana",
    "Juana",
    "Luz",
    "Elena",
    "Silvia",
    "Patricia",
    "Gloria",
    "Milagros",
    "Lucía",
    "Karina",
    "Jessica",
    "Pilar",
    "Sofía",
    "Valeria",
    "Diana",
    "Yolanda",
    "Teresa",
    "Flor",
    "Liliana",
    "Roxana",
    "Mónica",
    "Verónica",
]
NOMBRES_HOMBRE = [
    "José",
    "Luis",
    "Carlos",
    "Juan",
    "Jorge",
    "Miguel",
    "César",
    "Víctor",
    "Pedro",
    "Manuel",
    "Raúl",
    "Javier",
    "Óscar",
    "Alberto",
    "Fernando",
    "Ricardo",
    "Julio",
    "Martín",
    "Diego",
    "Renzo",
    "Hugo",
    "Walter",
    "Edwin",
    "Marco",
    "Percy",
]
APELLIDOS = [
    "Quispe",
    "Flores",
    "Sánchez",
    "Rodríguez",
    "García",
    "Huamán",
    "Mamani",
    "Rojas",
    "Díaz",
    "Torres",
    "Chávez",
    "Ramírez",
    "Castillo",
    "Mendoza",
    "Vargas",
    "Gutiérrez",
    "Espinoza",
    "Ramos",
    "Vásquez",
    "López",
    "Pérez",
    "Cruz",
    "Fernández",
    "Gonzales",
    "Salazar",
    "Ríos",
    "Paredes",
    "Cárdenas",
    "Huanca",
    "Condori",
    "Aguilar",
    "Medina",
    "Silva",
    "Morales",
    "Herrera",
    "Castro",
    "Romero",
    "Ortiz",
    "Delgado",
    "Ccahuana",
]

# ---------------------------------------------------------------- clientes

N_CLIENTES = 300
TIPOS_CLIENTE = {"Bodega": 0.60, "Minimarket": 0.25, "Restaurante": 0.15}
PROPORCION_CLIENTES_NUEVOS = 0.15  # se incorporan durante 2024 y 2025
PROPORCION_CLIENTES_PERDIDOS = 0.10  # dejan de comprar antes de fin de 2025

_DON_DONA = [f"Don {n}" for n in NOMBRES_HOMBRE] + [f"Doña {n}" for n in NOMBRES_MUJER]
_NOMBRES_BODEGA = [
    "La Esquina",
    "Mi Barrio",
    "Santa Rosa",
    "El Sol",
    "La Bendición",
    "Los Andes",
    "La Económica",
    "El Vecino",
    "San Judas",
    "La Familia",
    "El Progreso",
    "Las Flores",
    "El Triunfo",
    "La Fortuna",
    "El Porvenir",
    "San Juan",
    "Mi Tiendita",
    "La Amistad",
] + _DON_DONA
_NOMBRES_MINIMARKET = [
    "El Ahorro",
    "San Martín",
    "Santa Rosa",
    "La Económica",
    "Del Pueblo",
    "Los Andes",
    "Express",
    "El Sol",
    "La Familia",
    "Central",
    "Mi Barrio",
    "El Progreso",
    "Primavera",
    "Las Palmeras",
    "San Pedro",
    "La Victoria",
    "El Mirador",
    "Los Olivos",
    "Santa Ana",
    "El Porvenir",
    "Nuevo Amanecer",
    "La Unión",
    "Bella Vista",
    "Los Pinos",
    "Señorial",
    "La Perla",
    "Las Begonias",
    "El Trébol",
]

# Para cada tipo de cliente: prefijo → nombres que tienen sentido con ese prefijo.
NOMBRES_NEGOCIO = {
    "Bodega": {p: _NOMBRES_BODEGA for p in ["Bodega", "Abarrotes", "Bodeguita"]},
    "Minimarket": {p: _NOMBRES_MINIMARKET for p in ["Minimarket", "Market", "Autoservicio"]},
    "Restaurante": {
        "Restaurante": [
            "El Buen Sabor",
            "La Sazón",
            "Sabor Criollo",
            "La Tradición",
            "La Casona",
            "El Fogón",
            "Los Faroles",
            "El Paisano",
            "La Cabaña",
            "El Rincón Norteño",
            "Don Lucho",
            "El Huarique",
        ],
        "Cevichería": [
            "El Muelle",
            "Mar y Tierra",
            "La Caleta",
            "El Pescador",
            "Las Gaviotas",
            "El Anzuelo",
            "Brisa Marina",
            "El Velero",
            "La Red",
        ],
        "Pollería": [
            "El Chalán",
            "La Brasa",
            "El Pollo Dorado",
            "Las Brasas de Oro",
            "El Leñador",
            "El Carbón",
            "Brasa Real",
            "El Horno",
            "Don Pollo",
        ],
        "Picantería": [
            "El Rocoto",
            "La Chomba",
            "Doña Chela",
            "Mi Tierra",
            "La Mistiana",
            "El Batán",
            "La Tradicional",
        ],
        "Chifa": [
            "Gran Dragón",
            "Jardín Oriental",
            "Fénix Dorado",
            "Perla de Oriente",
            "Loto Rojo",
            "Bambú",
            "Gran Muralla",
            "Oriente Express",
        ],
    },
}

LIMITES_CREDITO = {
    "Bodega": [3000, 5000, 8000],
    "Minimarket": [10000, 15000, 25000],
    "Restaurante": [8000, 12000, 20000],
}

# ------------------------------------------------------------------ ventas

N_VENTAS = 50_000
INICIO = pd.Timestamp("2024-01-01")
FIN = pd.Timestamp("2025-12-31")
CRECIMIENTO_ANUAL = 1.08

# Peso de cada mes en el número de ventas: caída en enero y febrero, picos en
# Fiestas Patrias (julio) y Navidad (diciembre).
ESTACIONALIDAD_MES = {
    1: 0.80,
    2: 0.85,
    3: 0.95,
    4: 0.95,
    5: 1.00,
    6: 1.00,
    7: 1.25,
    8: 1.00,
    9: 0.95,
    10: 1.00,
    11: 1.10,
    12: 1.45,
}
# Lunes = 0 ... domingo = 6. Los domingos casi no hay despacho.
ESTACIONALIDAD_DIA = {0: 1.05, 1: 1.00, 2: 1.00, 3: 1.00, 4: 1.10, 5: 1.15, 6: 0.40}

# Feriados nacionales de Perú: ese día no hay despachos.
FERIADOS = pd.to_datetime(
    [
        "2024-01-01",
        "2024-03-28",
        "2024-03-29",
        "2024-05-01",
        "2024-06-29",
        "2024-07-28",
        "2024-07-29",
        "2024-08-30",
        "2024-10-08",
        "2024-11-01",
        "2024-12-08",
        "2024-12-09",
        "2024-12-25",
        "2025-01-01",
        "2025-04-17",
        "2025-04-18",
        "2025-05-01",
        "2025-06-29",
        "2025-07-28",
        "2025-07-29",
        "2025-08-30",
        "2025-10-08",
        "2025-11-01",
        "2025-12-08",
        "2025-12-09",
        "2025-12-25",
    ]
)

# Cómo cambia la mezcla de productos según el mes: en verano (diciembre a marzo)
# se venden más bebidas y snacks; el panetón se vende casi solo en noviembre y diciembre.
_VERANO_BEBIDAS = {
    1: 1.35,
    2: 1.35,
    3: 1.20,
    4: 1.00,
    5: 0.90,
    6: 0.80,
    7: 0.80,
    8: 0.80,
    9: 0.90,
    10: 1.00,
    11: 1.10,
    12: 1.30,
}
_VERANO_SNACKS = {
    1: 1.15,
    2: 1.15,
    3: 1.10,
    4: 1.00,
    5: 1.00,
    6: 0.90,
    7: 0.95,
    8: 0.90,
    9: 1.00,
    10: 1.00,
    11: 1.05,
    12: 1.20,
}
ESTACIONALIDAD_CATEGORIA = {"Bebidas": _VERANO_BEBIDAS, "Snacks": _VERANO_SNACKS}
ESTACIONALIDAD_PRODUCTO = {
    "Panetón 900 g": {
        1: 0.10,
        2: 0.02,
        3: 0.02,
        4: 0.02,
        5: 0.02,
        6: 0.02,
        7: 0.05,
        8: 0.02,
        9: 0.05,
        10: 0.40,
        11: 3.00,
        12: 8.00,
    },
}

# Cuánto compra cada tipo de cliente.
ACTIVIDAD_POR_TIPO = {"Bodega": 1.0, "Minimarket": 1.6, "Restaurante": 1.3}
PREFERENCIA_CATEGORIA = {
    "Bodega": {"Snacks": 1.5, "Bebidas": 1.3},
    "Minimarket": {"Cuidado personal": 1.3, "Limpieza": 1.2},
    "Restaurante": {
        "Abarrotes": 3.0,
        "Limpieza": 1.5,
        "Bebidas": 1.2,
        "Snacks": 0.2,
        "Cuidado personal": 0.3,
    },
}
# Presentaciones (cajas, fardos) por venta: muchas compras chicas y algunas grandes.
CANTIDAD_MEDIA = {"Bodega": 2, "Minimarket": 4, "Restaurante": 3}
DISPERSION_CANTIDAD = 1.5

# Descuento por volumen: (desde cuántas presentaciones, descuento en %).
DESCUENTOS = [(20, 10), (10, 5)]

METODOS_PAGO = ["Efectivo", "Billetera digital", "Transferencia", "Crédito"]
PROBABILIDAD_PAGO = {
    "Bodega": [0.45, 0.30, 0.15, 0.10],
    "Minimarket": [0.25, 0.25, 0.30, 0.20],
    "Restaurante": [0.15, 0.15, 0.35, 0.35],
}

# ---------------------------------------------------------------- créditos

# Días de plazo para pagar una compra al crédito.
PLAZO_CREDITO = {"Bodega": 15, "Minimarket": 30, "Restaurante": 30}
# Una compra es morosa si se paga con más de estos días de atraso tras vencer el plazo.
DIAS_MOROSIDAD = 30
# Fecha en que se "toma la foto": lo que vence después todavía no se sabe.
CORTE_CREDITOS = FIN

# Coeficientes con los que se decide la mora (escala logit). Se publican a propósito: lo que
# un modelo encuentre aquí refleja lo programado, no un hallazgo sobre negocios reales.
MORA_BASE = 0.4
MORA_POR_MONTO = 0.5  # por cada unidad de logaritmo natural de monto / límite de crédito
MORA_POR_ANIO = -0.08  # por cada año de antigüedad del cliente
MORA_POR_TIPO = {"Bodega": 0.3, "Minimarket": -0.2, "Restaurante": 0.0}
MORA_DISPERSION_CLIENTE = 1.0  # riesgo propio de cada cliente, que no se publica

# --------------------------------------------------------------- despachos

# Distancia del cliente a su sede, en km (mediana por ciudad; se sortea alrededor de ella).
DISTANCIA_MEDIANA = {
    "Lima": 12,
    "Arequipa": 14,
    "Trujillo": 12,
    "Chiclayo": 14,
    "Piura": 18,
    "Cusco": 22,
}
DISTANCIA_DISPERSION = 0.7
DISTANCIA_MAXIMA = 60
# Probabilidad de usar un transportista tercero: sube con la distancia.
TERCERO_BASE = 0.25
TERCERO_POR_KM = 0.006
TERCERO_MAXIMO = 0.70

# Coeficientes con los que se decide la entrega tardía (escala logit). Se publican a propósito:
# son reglas que solo actúan en combinación, y un árbol puede encontrarlas.
TARDE_BASE = -3.2
TARDE_POR_KM = 0.006
TARDE_LLUVIA_CUSCO = 3.6  # Cusco, de diciembre a marzo y desde LLUVIA_KM de distancia
LLUVIA_MESES = (12, 1, 2, 3)
LLUVIA_KM = 20
TARDE_TERCERO_SABADO = 3.0  # transportista tercero en sábado
TARDE_CAMPANA_CARGA = 3.0  # julio o diciembre, desde CAMPANA_BULTOS presentaciones
CAMPANA_MESES = (7, 12)
CAMPANA_BULTOS = 10

# ----------------------------------------------------------------- tickets

N_TICKETS = 3600
CANALES_TICKET = {"WhatsApp": 0.6, "Teléfono": 0.25, "Correo": 0.15}
# Parte de los tickets que nace de una entrega tardía real.
TICKETS_DE_TARDANZA = 0.22
# Parte de los tickets en que el cliente mezcla dos temas, y parte mal clasificada a mano.
TICKETS_MIXTOS = 0.12
TICKETS_MAL_ETIQUETADOS = 0.04
PESO_CATEGORIA_TICKET = {
    "Facturación": 0.26,
    "Producto": 0.24,
    "Cobranza": 0.22,
    "Consulta comercial": 0.28,
}
SALUDOS_TICKET = [
    "",
    "",
    "Buenas, ",
    "Buenos días, ",
    "Buenas tardes, ",
    "Hola, ",
    "Estimados, ",
    "Joven, ",
    "Señorita, ",
]
CIERRES_TICKET = ["", "", "", "Por favor.", "Gracias.", "Es urgente.", "Quedo atento."]
# Se repiten palabras entre categorías ("llegó", "pedido", "cobrar"): así pasa en un negocio real.
FRASES_TICKET = {
    "Despacho": [
        "el pedido que hice {dia} no llegó hasta ahora",
        "todavía no me llega mi pedido, ya {tiempo}",
        "el camión no vino {dia} y mi tienda está sin mercadería",
        "me dijeron que el pedido llegaba {dia} y sigo esperando",
        "el repartidor no pasó por mi local",
        "el despacho llegó tarde y ya había cerrado",
        "¿a qué hora llega mi pedido? Ya debería estar aquí",
        "el chofer dice que no encuentra la dirección",
        "reprogramaron mi entrega sin avisarme",
        "llegó incompleto el pedido, faltan {n} cajas",
        "la mercadería sigue sin llegar, necesito saber cuándo la mandan",
        "mi pedido salió {dia} y no hay noticias del carro",
    ],
    "Facturación": [
        "la factura salió con otro RUC",
        "no me llegó la factura del pedido que recibí {dia}",
        "necesito que corrijan la razón social en la factura",
        "me cobraron de más en la factura, no aplicaron el descuento",
        "pido una nota de crédito por el pedido que recibí {dia}",
        "la boleta tiene el monto equivocado",
        "el comprobante electrónico no llega a mi correo",
        "cambiaron el precio en la factura y no coincide con la cotización",
        "anulen esa factura y emitan otra",
        "la guía de remisión no coincide con la factura",
        "me falta el comprobante de la compra que hice {dia}, lo pide mi contador",
        "el IGV de la factura está mal calculado",
    ],
    "Producto": [
        "llegaron {n} cajas abolladas",
        "el producto vino vencido",
        "el aceite llegó con la caja rota y manchada",
        "las gaseosas están por vencer, quiero cambiarlas",
        "el arroz vino con gorgojos",
        "me mandaron otra marca, yo pedí otra cosa",
        "las bolsas llegaron rotas y quiero devolverlas",
        "el paquete vino abierto y faltan unidades adentro",
        "quiero devolver {n} fardos porque están mojados",
        "los panetones llegaron aplastados",
        "el detergente se derramó dentro de la caja",
        "enviaron la presentación equivocada, cámbienla",
    ],
    "Cobranza": [
        "ya pagué la deuda y me siguen llamando para cobrar",
        "quiero mi estado de cuenta",
        "hice el depósito {dia}, les mando el voucher",
        "necesito más plazo para pagar el crédito",
        "no reconozco esa deuda de {n} mil soles",
        "¿cuánto debo a la fecha?",
        "me dicen que tengo deuda vencida y ya estoy al día",
        "pagué por transferencia y no lo registran",
        "quiero fraccionar lo que debo",
        "el cobrador pasó {dia} y ya había cancelado",
        "me llegó una carta de cobranza por error",
        "¿a qué cuenta deposito lo del pedido anterior?",
    ],
    "Consulta comercial": [
        "¿cuál es el precio del fardo de arroz?",
        "quiero el catálogo actualizado",
        "¿tienen promoción de panetones para esta campaña?",
        "¿desde cuántas cajas hay descuento?",
        "quiero que me visite el vendedor esta semana",
        "¿venden al por mayor a restaurantes?",
        "quiero cotizar {n} cajas de leche",
        "¿llegó stock de chicha morada?",
        "¿pueden aumentar mi línea de crédito?",
        "cambiaron a mi vendedor y no me visitan",
        "¿qué marcas de detergente manejan?",
        "quiero hacer un pedido grande para la próxima semana",
    ],
}
DIAS_SEMANA_TICKET = [
    "el lunes",
    "el martes",
    "el miércoles",
    "el jueves",
    "el viernes",
    "el sábado",
    "el domingo",
]
# Frases del panetón: solo tienen sentido en su temporada.
MESES_PANETON = (11, 12)
# Desde esta fecha los clientes escriben también con otras palabras, que no había al entrenar.
INICIO_FRASES_NUEVAS = pd.Timestamp("2025-07-01")
PROPORCION_FRASES_NUEVAS = 0.15
FRASES_NUEVAS_TICKET = {
    "Despacho": [
        "sigo aguardando la movilidad con mi encargo",
        "la unidad nunca apareció por la tienda",
    ],
    "Facturación": [
        "mi CPE no aparece en SUNAT",
        "emitieron el documento a otra empresa",
    ],
    "Producto": [
        "vino malogrado el lote de lejía",
        "la mercancía presenta humedad",
    ],
    "Cobranza": [
        "ya hice el abono por Yape",
        "mi saldo pendiente figura mal",
    ],
    "Consulta comercial": [
        "¿manejan lista de precios para mayoristas?",
        "busco proveedor de snacks para mi negocio",
    ],
}
# Cómo escriben algunos clientes por WhatsApp.
ABREVIATURAS_TICKET = {
    " por favor": " porfa",
    " que ": " q ",
    " porque ": " xq ",
    " por ": " x ",
    " todavía ": " todavia ",
    " días": " dias",
    "llegó": "llego",
    "pagué": "pague",
}

# ----------------------------------------------------------- postulaciones

N_POSTULACIONES = 3200
CARGOS_POSTULACION = {
    "Vendedor": 0.30,
    "Almacenero": 0.25,
    "Repartidor": 0.25,
    "Asistente administrativo": 0.20,
}
PROPORCION_MUJERES_POSTULACION = {
    "Vendedor": 0.45,
    "Almacenero": 0.25,
    "Repartidor": 0.15,
    "Asistente administrativo": 0.65,
}
# Meses sin empleo formal antes de postular: las mujeres tienen pausas más largas en estos datos.
# Es lo que vuelve a esta columna un "indicador indirecto" del sexo. No mide capacidad.
PAUSA_MEDIA_MESES = {"F": 14, "M": 4}
# Otro indicador indirecto: quién declara poder viajar. Tampoco mide capacidad.
PROBABILIDAD_VIAJAR = {"F": 0.35, "M": 0.70}

# Coeficientes de la decisión histórica de entrevistar (escala logit). El puntaje de la prueba
# se sortea igual para todos, así que no explica ninguna diferencia entre grupos. El sesgo
# está programado a propósito para el episodio de ética: no describe a ninguna empresa real.
ENTREVISTA_BASE = -1.9
ENTREVISTA_POR_PUNTAJE = 0.05  # por cada punto sobre 60
ENTREVISTA_POR_ANIO = 0.12  # por cada año de experiencia
ENTREVISTA_POR_MES_PAUSA = -0.05  # por cada mes de pausa: el reclutador la castiga
ENTREVISTA_POR_VIAJAR = 0.8  # si declara poder viajar: el reclutador lo premia en todo cargo
ENTREVISTA_SESGO_MUJER = -0.8  # además, directo contra las mujeres en estos cargos
CARGOS_CON_SESGO = ("Vendedor", "Almacenero", "Repartidor")
