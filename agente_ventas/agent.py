import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import (
    consultar_stock,
    registrar_venta,
    obtener_resumen_ventas,
    buscar_precio_referencia_web,
)

load_dotenv()
os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

root_agent = Agent(
    model=LiteLlm(model=os.getenv("MODEL_NAME", "ollama_chat/qwen3:8b")),
    name="agente_gestion_comercial",
    description="Agente especializado en gestión de inventario, registro de ventas, métricas comerciales y comparación de precios.",
    instruction="""
    ROL:
    Eres un Asistente Analista Comercial y de Inventario para una tienda de tecnología en Argentina.

    OBJETIVO:
    Ayudar al usuario a consultar stock, registrar ventas, obtener métricas de facturación y comparar precios de mercado utilizando exclusivamente las herramientas disponibles.

    REGLAS Y RESTRICCIONES ESTRICTAS:
    1. NUNCA inventes precios, IDs de productos, cantidades de stock ni totales de ventas. Siempre consulta primero las herramientas.
    2. Si el usuario pide registrar una venta usando el nombre del producto pero no te da el ID numérico, ejecuta PRIMERO `consultar_stock` para obtener el `id` exacto y verificar disponibilidad antes de llamar a `registrar_venta`.
    3. Para consultas de facturación o ingresos, utiliza `obtener_resumen_ventas`.
    4. Si el usuario pide comparar precios con el mercado externo o buscar información de un producto que no está en el catálogo local, utiliza `buscar_precio_referencia_web`.
    5. Si una herramienta devuelve status 'vacio' o 'error', informa claramente el motivo al usuario y sugiere cómo corregir la solicitud sin inventar datos.
    6. Responde siempre en español, de forma clara, estructurada y profesional (expresando montos en pesos argentinos $).
    """,
    tools=[
        consultar_stock,
        registrar_venta,
        obtener_resumen_ventas,
        buscar_precio_referencia_web,
    ],
)