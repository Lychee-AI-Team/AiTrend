# AiTrend Skill v0.1.1

> 🚀 Recopilador de Tendencias AI Multi-fuente - **AI Weekly para Todos**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Características

- 🔥 **Recopilación Multi-fuente**: Twitter, Product Hunt, HackerNews, GitHub, Brave Search, Reddit
- 🤖 **Resumen AI**: Análisis inteligente con Gemini 3 Flash Preview
- 👥 **Amigable**: Herramientas que cualquiera puede usar inmediatamente
- 📝 **Estilo Conversacional**: Expresión natural como charlar con amigos
- 🚫 **Cero Dependencias**: Solo biblioteca estándar de Python, listo para usar
- 🌐 **Multi-idioma**: Soporte para 5+ idiomas (solo salida de resumen AI)
- 🎯 **Auto-instalación AI**: Proporciona [SKILL.md](SKILL.md) para auto-instalación

## 🚀 Inicio Rápido

### 🎯 Método 1: Dejar que AI Instale Automáticamente (Recomendado)

**Simplemente dile a tu AI:**

> "Por favor lee https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md e instala AiTrend Skill"

Tu AI automáticamente:
1. Clona el repositorio en la ubicación correcta
2. Verifica y solicita las API Keys necesarias (solo Gemini requerido)
3. Ejecuta y genera el primer contenido
4. Pregunta si deseas configurar más fuentes de datos

**Inicio sin configuración** - ¡Solo se necesita una API Key de Gemini!

---

### 💻 Método 2: Instalación Manual

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# Edita el archivo .env
python3 -m src
```

## 🌐 Configuración de Idioma

Edita `config/config.json`:

```json
{
  "language": "es",
  "sources": { ... },
  "summarizer": { ... }
}
```

Idiomas soportados: `zh` (Chino), `en` (Inglés), `ja` (Japonés), `ko` (Coreano), `es` (Español)

Predeterminado: `zh` (Chino Simplificado)

**Nota**: La recopilación de datos es independiente del idioma. Solo la salida final del resumen AI respeta la configuración de idioma.

## 📄 Licencia

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
