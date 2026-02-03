# AiTrend v0.3.0

🔥 **Motor de Descubrimiento de Tendencias AI** - Recolección y publicación automática de noticias de productos AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

<p align="center">
  <b>🌍 Documentación Multi-idioma</b> |
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ Características

- 🧩 **Diseño Modular** - Combina fuentes de datos y canales de salida libremente
- 🤖 **Generación de Contenido AI** - Usa Gemini para generar descripciones de alta calidad
- 📊 **Soporte Multi-fuente** - GitHub, Product Hunt, HackerNews, Reddit, Tavily
- 📢 **Publicación Multi-canal** - Discord, Telegram, Feishu
- 🔄 **Deduplicación Automática** - Ventana deslizante de 24 horas previene duplicados

## 🚀 Inicio Rápido

### Opción 1: Instalación con un Clic

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
./install.sh
```

### Opción 2: Despliegue Docker

```bash
docker-compose up -d
```

### Configuración

```bash
# 1. Configurar claves API
nano .env.keys

# Requerido:
# - GEMINI_API_KEY
# - DISCORD_WEBHOOK_URL

# 2. Editar configuración
nano config/config.yaml

# 3. Ejecutar
python3 -m src.hourly
```

## 📁 Estructura del Proyecto

```
AiTrend/
├── src/              # Código principal
│   ├── sources/      # Módulos de fuentes de datos
│   ├── core/         # Funcionalidad principal
│   └── hourly.py     # Entrada principal
├── config/           # Archivos de configuración
├── docs/             # Documentación
├── install.sh        # Script de instalación
├── Dockerfile        # Imagen Docker
└── skill.yaml        # Descripción OpenClaw Skill
```

## 📄 Documentación

- [Guía de Configuración de API Key](docs/API_KEY_SETUP.md)
- [Guía de Desarrollo](docs/DEVELOPMENT_GUIDE.md)
- [Solución de Problemas](docs/TROUBLESHOOTING.md)
- [Referencia Rápida](docs/QUICK_REFERENCE.md)

## 🔧 Canales Soportados

| Canal | Estado | Descripción |
|-------|--------|-------------|
| Discord Forum | ✅ Soportado | Crear hilos diarios automáticamente |
| Discord Text | ✅ Soportado | Enviar al canal de texto |
| Telegram | 🚧 En Desarrollo | Próximamente |
| Feishu | 🚧 En Desarrollo | Próximamente |

## 📊 Fuentes de Datos

| Fuente | API Key | Descripción |
|--------|---------|-------------|
| GitHub Trending | Opcional | Proyectos AI en tendencia |
| Product Hunt | Opcional | Lanzamientos de nuevos productos |
| HackerNews | No necesario | Temas populares de la comunidad |
| Reddit | No necesario | Discusiones de la comunidad AI |
| Tavily | Opcional | Búsqueda AI |

## 📜 Licencia

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
