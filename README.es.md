<h1 align="center">AiTrend Skill v0.2.0</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<p align="center">
  <b>🚀 Recolector de Tendencias AI Multi-fuente - Soporte Multi-canal</b>
</p>

<p align="center">
  <a href="#-inicio-rápido">Inicio Rápido</a> •
  <a href="#-características">Características</a> •
  <a href="#-configuración">Configuración</a> •
  <a href="#-canales">Canales</a> •
  <a href="#-idiomas">Idiomas</a>
</p>

---

## 🌍 Documentación Multi-idioma

<p align="center">
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ Características

- 🔥 **Multi-fuente**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- 📢 **Multi-canal**: Discord, Feishu, Telegram, Console
- 🌐 **Multi-idioma**: Chino, Inglés, Japonés, Coreano, Español
- 🔄 **Deduplicación Inteligente**: Ventana deslizante de 24 horas
- ⚡ **Cero Configuración**: Solo se necesita Tavily Key

---

## 🚀 Inicio Rápido

### 1️⃣ Clonar Repositorio

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2️⃣ Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env y agregar TAVILY_API_KEY
```

### 3️⃣ Configurar Canales de Salida

```bash
cp config/config.example.json config/config.json
# Editar config/config.json y habilitar los canales deseados
```

### 4️⃣ Ejecutar

```bash
python3 -m src
```

---

## 🔧 Configuración

### Configuración Básica

Editar `config/config.json`:

```json
{
  "language": "es",
  "sources": {
    "tavily": {
      "enabled": true,
      "api_key": "${TAVILY_API_KEY}"
    },
    "hackernews": { "enabled": true },
    "reddit": { "enabled": true },
    "github_trending": { "enabled": true }
  },
  "channels": {
    "console": { "enabled": true }
  }
}
```

---

## 📢 Configuración de Canales

AiTrend soporta múltiples canales de salida. Puedes habilitar varios canales simultáneamente:

### Console (Predeterminado)

```json
"channels": {
  "console": {
    "enabled": true
  }
}
```

### Discord

```json
"channels": {
  "discord": {
    "enabled": true,
    "channel_id": "1467767285044346933"
  }
}
```

**Obtener Channel ID:**
1. Configuración de Discord → Avanzado → Habilitar Modo Desarrollador
2. Clic derecho en el canal → Copiar ID del Canal

### Feishu

```json
"channels": {
  "feishu": {
    "enabled": true,
    "chat_id": "oc_9a3c218325fd2cfa42f2a8f6fe03ac02"
  }
}
```

### Telegram

```json
"channels": {
  "telegram": {
    "enabled": true,
    "chat_id": "-1001234567890"
  }
}
```

### Multi-canal

```json
"channels": {
  "console": { "enabled": true },
  "discord": {
    "enabled": true,
    "channel_id": "YOUR_DISCORD_CHANNEL_ID"
  },
  "feishu": {
    "enabled": true,
    "chat_id": "YOUR_FEISHU_CHAT_ID"
  }
}
```

---

## ⏰ Programación

### OpenClaw Cron

```bash
# Ejecución automática todos los días a las 9:00
openclaw cron add \
  --name "aitrend-daily" \
  --schedule "0 9 * * *" \
  --command "python3 -m src" \
  --cwd "~/.openclaw/workspace/AiTrend"
```

### Linux Cron

```bash
0 9 * * * cd /path/to/AiTrend && python3 -m src
```

---

## 📊 Fuentes de Datos

| Fuente | API Key Requerida | Descripción |
|--------|-------------------|-------------|
| Tavily | ✅ Requerida | Motor de búsqueda AI nativo |
| HackerNews | ❌ No | Comunidad de desarrolladores |
| GitHub | ❌ No | Proyectos AI en tendencia |
| Reddit | ❌ No | Discusiones de comunidad AI |
| Twitter/X | ⚠️ Opcional | Contenido viral |
| Product Hunt | ⚠️ Opcional | Lanzamientos de nuevos productos |

---

## 🌍 Soporte Multi-idioma

| Idioma | Código | Estado |
|--------|--------|--------|
| Chino Simplificado | zh | ✅ |
| Inglés | en | ✅ |
| Japonés | ja | ✅ |
| Coreano | ko | ✅ |
| Español | es | ✅ |

Cambia el campo `language` en `config/config.json` para cambiar de idioma.

---

## 📁 Estructura del Proyecto

```
AiTrend/
├── src/
│   ├── __main__.py              # Punto de entrada
│   ├── core/
│   │   ├── config_loader.py     # Cargador de configuración
│   │   ├── sender.py            # Enviador de canales
│   │   └── deduplicator.py      # Deduplicador
│   └── sources/                 # Implementaciones de fuentes
├── config/
│   ├── config.example.json      # Ejemplo de configuración
│   └── config.json              # Configuración del usuario
├── .env.example                 # Ejemplo de variables de entorno
├── .env                         # Variables del usuario
└── README.md
```

---

## 📝 Ejemplo Completo de Configuración

```json
{
  "language": "es",
  "sources": {
    "reddit": { "enabled": true },
    "hackernews": { "enabled": true },
    "github_trending": {
      "enabled": true,
      "languages": ["python", "typescript", "rust", "go"]
    },
    "tavily": {
      "enabled": true,
      "api_key": "${TAVILY_API_KEY}",
      "queries": [
        "latest AI tools launch 2026",
        "new AI models released this week"
      ]
    }
  },
  "channels": {
    "console": { "enabled": true },
    "discord": {
      "enabled": true,
      "channel_id": "1467767285044346933"
    }
  }
}
```

---

## 📄 Licencia

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
