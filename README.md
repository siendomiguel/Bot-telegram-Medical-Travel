# Medical Travel Colombia - Telegram Bot

Este proyecto es un **Bot de Telegram** inteligente diseñado para actuar como un asistente conversacional integrado directamente con **Zoho CRM**. Permite a usuarios autorizados de Medical Travel consultar, actualizar y gestionar información de pacientes, leads y registros del CRM directamente desde Telegram.

## Características Principales

1. **Agente de IA (Agentic Loop)**: Utiliza un LLM avanzado (a través de OpenRouter) para entender el flujo de la conversación, tomar decisiones y ejecutar herramientas automáticas contra Zoho CRM de forma autónoma.
2. **Soporte de Voz**: Procesamiento de notas de voz enviadas por Telegram utilizando el modelo Whisper de OpenAI, permitiendo una interacción de total manos libres.
3. **Memoria Persistente**: Utiliza PostgreSQL para mantener el contexto de la conversación a lo largo del tiempo, permitiendo que el bot responda con congruencia a interacciones continuas.
4. **Control de Acceso (Auth)**: Acceso restringido estrictamente a una lista blanca de IDs de Telegram, asegurando que solo el personal autorizado interactúe con el CRM.
5. **Arquitectura Limpia**: Separación clara de responsabilidades entre Controladores (`controllers/`), Servicios (`services/`), y el cliente integrador de Zoho (`zoho_client/`).

## Requisitos Previos

- Python 3.10+
- PostgreSQL
- Credenciales y Tokens de:
  - Telegram Bot (BotFather)
  - OpenRouter API
  - OpenAI API (opcional, para notas de voz)
  - Zoho CRM (API / OAuth)

## Configuración y Variables de Entorno

1. Renombra el archivo `.env.example` a `.env`
2. Llena las siguientes variables de entorno:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ALLOWED_TELEGRAM_IDS=123456789,987654321

# OpenRouter (LLM)
OPENROUTER_API_KEY=sk-or-v1-xxxx
OPENROUTER_MODEL=anthropic/claude-opus-4-1

# OpenAI (Opcional - Whisper para notas de voz)
OPENAI_API_KEY=sk-xxxx

# PostgreSQL (Base de datos para la memoria)
DATABASE_URL=postgresql://user:password@host:5432/telegram_bot

# Zoho CRM
ZOHO_CLIENT_ID=xxxx
ZOHO_CLIENT_SECRET=xxxx
ZOHO_REFRESH_TOKEN=xxxx
ZOHO_API_DOMAIN=https://www.zohoapis.com
ZOHO_ACCOUNTS_DOMAIN=https://accounts.zoho.com
```

## Instalación y Ejecución Local

1. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el bot:
   ```bash
   python app.py
   ```

## Estructura del Proyecto

```text
├── config/             # Configuraciones globales (Settings)
├── controllers/        # Controladores de Telegram (comandos, mensajes, voz)
├── middleware/         # Middleware (Auth, validaciones)
├── models/             # Esquemas de datos (Pydantic, Tool definitions)
├── services/           # Lógica de negocio (Agent, Memory, Voice)
├── zoho_client/        # Cliente y adaptadores de la API de Zoho CRM
├── app.py              # Entry point principal del Bot
├── requirements.txt    # Dependencias de Python
└── database_url        # (en .env) Cadena de conexión a PostgreSQL
```

## Despliegue (Railway)

El proyecto incluye configuración lista para ser desplegada en [Railway](https://railway.app/).
- Usa el `Dockerfile` preconfigurado.
- El archivo `railway.toml` especifica los detalles del build y reinicios automáticos.
- *Nota: Asegúrate de configurar todas las variables de entorno (`.env`) en la sección de Variables de Railway e incluir una base de datos PostgreSQL activa.*
