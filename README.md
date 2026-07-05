# fotoowl-ai-video-pipeline
# 🎬 FotoOwl AI Video Pipeline

An end-to-end **multi-agent AI system** that converts a folder of images and a natural language prompt into a fully rendered cinematic video using **LangGraph + LLM agents + Remotion**.

---

## 🚀 Overview

This project simulates a production-grade AI video generation system similar to FotoOwl’s core engine.

It takes:
- A folder of raw images
- A user prompt (creative brief)

And generates:
- A structured storyboard
- A Remotion video script
- A compiled and rendered MP4 video

---

## 🧠 System Architecture

The pipeline is built using **LangGraph** and consists of 5 core agents:

```text
Images + Prompt
      ↓
[1] Image Analyzer (vision understanding)
      ↓
[2] Intent Parser (VideoIntent structure)
      ↓
[3] Storyboard Writer (RAG-enhanced planning)
      ↓
[4] Script Generator (Remotion code generation)
      ↓
[5] Compiler & Fixer (error recovery loop)
      ↓
[6] Renderer (Remotion → MP4)
