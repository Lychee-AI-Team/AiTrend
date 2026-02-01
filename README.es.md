# AiTrend Skill v0.1.1

> 🚀 Recopilador de Tendencias AI Multi-fuente - **AI Weekly para Todos**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Características

### 🔥 Minería Multi-fuente
- **6 Fuentes de Datos**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- **Búsqueda AI-Nativo**: Tavily diseñado para LLMs, devuelve contenido completo
- **Hotspots en Tiempo Real**: Monitoreo de redes sociales
- **Inicio Zero-config**: Solo se necesita Tavily Key

### 🔄 Deduplicación Inteligente
- **Ventana Deslizante 24h**: El mismo contenido no se repite
- **Deduplicación URL**: Filtra automáticamente enlaces duplicados
- **Memoria Persistente**: Seguimiento local de contenido enviado
- **Forzar 10 Items**: Mínimo 10 productos por salida

### 🤖 Integración OpenClaw
- **Depende de OpenClaw**: Enrutamiento de mensajes, programación, resumen LLM
- **Colección de Datos Pura**: Enfocado en minería, no en envío/resumen
- **Multi-canal**: Enviar a cualquier plataforma vía OpenClaw
- **Programación Automática**: Entrega diaria a las 09:00

### 🌐 Soporte Multi-idioma
- **5 Idiomas**: Chino, Inglés, Japonés, Coreano, Español
- **Cambio con Un Clic**: Cambiar idioma de salida en la configuración
- **Adaptación Inteligente**: La recopilación de datos es independiente del idioma
- **Descripciones Detalladas**: 200+ palabras por producto

## 🚀 Inicio Rápido

### 🎯 Método 1: Dejar que AI Instale Automáticamente (Recomendado)

**Simplemente dile a tu AI:**

> "Por favor lee https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md e instala AiTrend Skill"

Tu AI automáticamente:
1. Clona el repositorio en la ubicación correcta
2. Verifica y solicita la API Key necesaria (solo Tavily)
3. Ejecuta y recopila datos
4. Genera resumen conversacional vía OpenClaw LLM
5. Envía a tu plataforma preferida

**Inicio sin configuración** - ¡Solo se necesita una API Key de Tavily!

---

### 💻 Método 2: Instalación Manual

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# Edita el archivo .env
python3 -m src
```

## 📊 Fuentes de Datos

| Fuente | Tipo | API Key Requerida | Descripción |
|--------|------|-------------------|-------------|
| Tavily | Búsqueda AI | ✅ Requerida | Búsqueda AI-nativa, devuelve contenido completo |
| HackerNews | Comunidad de Desarrolladores | ❌ No | Show HN y discusiones populares |
| GitHub | Código Abierto | ❌ No | Proyectos AI en tendencia |
| Reddit | Comunidad | ❌ No | SideProject y más |
| Twitter/X | Tiempo Real | ⚠️ Opcional | Contenido viral y discusiones |
| Product Hunt | Nuevos Productos | ⚠️ Opcional | Nuevos lanzamientos diarios |

## 🌐 Configuración de Idioma

Edita `config/config.json`:

```json
{
  "language": "es",
  "sources": { ... },
  "summarizer": { ... }
}
```

Soportado: `zh` (Chino), `en` (Inglés), `ja` (Japonés), `ko` (Coreano), `es` (Español)

Predeterminado: `zh` (Chino Simplificado)

**Nota**: La recopilación de datos es independiente del idioma. Solo la salida final del resumen AI respeta la configuración de idioma.

## 📄 Licencia

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
