<h1 align="center">DIAL Platform Course for Developers</h1>
<p align="center">
    <p align="center">
    <a href="https://dialx.ai/">
      <img src="https://dialx.ai/logo/dialx_logo.svg" alt="About DIALX">
    </a>
</p>
<h4 align="center">
    <a href="https://discord.gg/ukzj9U9tEe">
        <img src="https://img.shields.io/static/v1?label=DIALX%20Community%20on&message=Discord&color=blue&logo=Discord&style=flat-square" alt="Discord">
    </a>
</h4>

---

## About

This repository contains hands-on tasks for learning the [EPAM DIAL](https://dialx.ai/) platform. DIAL is a
vendor-neutral AI gateway that exposes a single OpenAI-compatible API while routing requests to models from OpenAI,
Anthropic, Google, and other providers. On top of the gateway you can build custom AI applications using the DIAL SDK.

The tasks take you from spinning up the platform locally all the way to building a multi-tool streaming agent. Each task
directory contains step-by-step instructions (`README.md`) and the completed reference implementation to work toward.

## Who This Is For

Backend and fullstack developers who want to integrate LLMs into products using the DIAL platform.

**Prerequisite:** familiarity with the OpenAI Chat Completions API — request/response structure, streaming (SSE), and
tool calls. DIAL is wire-compatible with the OpenAI API, so if you have worked with it before you already understand the
protocol.

## Platform Components

| Component               | Purpose                                                                         |
|-------------------------|---------------------------------------------------------------------------------|
| DIAL Core               | Central gateway — routes requests to model adapters; OpenAI-compatible REST API |
| DIAL Chat               | End-user chat UI                                                                |
| Themes                  | Icons and theme assets served to Chat                                           |
| Model adapters          | Thin proxies for OpenAI, AWS Bedrock (Anthropic), VertexAI (Gemini)             |
| DIAL SDK (`aidial-sdk`) | Python SDK for building custom AI applications behind the gateway               |

## Tasks

| #                                                  | Topic                     | What you will do                                                       |
|----------------------------------------------------|---------------------------|------------------------------------------------------------------------|
| [t1](tasks/t1_start_platform/README.md)            | Start the Platform        | Spin up the full Docker Compose stack                                  |
| [t2](tasks/t2_add_models/README.md)                | Add Models                | Connect OpenAI, Anthropic, and Gemini models via config and adapters   |
| [t3](tasks/t3_add_applications/README.md)          | Add Applications          | Build your first DIAL SDK apps (Echo and Essay Assistant)              |
| [t4](tasks/t4_stage_and_state/README.md)           | Stage & State             | Use Stages and State primitives for richer UX and conversation memory  |
| [t5](tasks/t5_files/README.md)                     | Files                     | Handle image uploads, multimodal LLMs, and TTS audio attachments       |
| [t6](tasks/t6_embeddings_and_frameworks/README.md) | Embeddings & Frameworks   | Build a RAG app with LangChain against DIAL's embedding endpoint       |
| [t7](tasks/t7_buttons/README.md)                   | Buttons                   | Expose a configuration endpoint and render interactive buttons in Chat |
| [t8](tasks/t8_themes/README.md)                    | Themes *(optional)*       | Customize Chat's color palette and branding                            |
| [t9](tasks/t9_chat_overlay/README.md)              | Chat Overlay *(optional)* | Embed DIAL Chat into an external web page via the overlay library      |
| [t10](tasks/t10_agent/README.md)                   | Agent — Capstone          | Build a multi-tool streaming agent combining all platform capabilities |

---

## Getting Started

### 0. ⭐️ **Star the repository** - it will help us grow ⭐️

### 1. ⑃ Fork and clone the repository

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```
