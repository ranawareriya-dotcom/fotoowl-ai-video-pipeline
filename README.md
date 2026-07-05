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
```


🤖 Agents Description
1. Image Analyzer
Analyses event images using vision models / heuristics
Tags images (faces, emotions, scenes)
Selects best subset of images for storytelling
2. Intent Parser

Converts raw prompt into structured intent:

{
  "pacing": "slow",
  "visual_style": "cinematic",
  "caption_tone": "emotional",
  "transition_style": "fade"
}
3. Storyboard Writer (RAG powered)
Uses style guides + Remotion documentation
Builds structured narrative timeline
[
  {
    "image": "img1.jpg",
    "duration": 90,
    "caption": "A beautiful beginning",
    "transition": "fade"
  }
]
4. Script Generator
Converts storyboard into valid Remotion React code
Generates dynamic composition file
5. Compiler & Fixer
Detects runtime and compilation errors
Sends error back to LLM for correction
Retries generation (limited attempts)
6. Renderer
Uses Remotion CLI
Renders final video
Outputs MP4 file

🧰 Tech Stack
Python 3.11+
LangGraph (multi-agent orchestration)
OpenAI / Gemini / LLM APIs
ChromaDB (RAG vector database)
TypeScript + React (Remotion)
Node.js (video rendering engine)

📁 Project Structure
fotoowl-ai-video-pipeline/

├── src/
│   ├── agents/
│   │   ├── image_analyser.py
│   │   ├── intent_parser.py
│   │   ├── storyboard_writer.py
│   │   ├── script_generator.py
│   │   ├── compiler.py
│   │   └── renderer.py
│
│   ├── graph.py
│   ├── state.py
│   ├── schemas.py
│
├── rag/
│   ├── style_guides/
│   ├── remotion_docs/
│
├── remotion-video/
│   ├── src/
│   ├── public/images/
│
├── sample_output/
│   ├── graph.mmd
│   ├── FotoOwlReel.mp4
│
├── main.py
├── requirements.txt
├── package.json
└── README.md

⚙️ Installation
1. Clone repository
git clone https://github.com/your-username/fotoowl-ai-video-pipeline.git
cd fotoowl-ai-video-pipeline
2. Setup Python environment
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
3. Setup Remotion
cd remotion-video
npm install

▶️ How to Run
Step 1: Run full AI pipeline
python main.py --images images --prompt "Cinematic wedding reel, slow and emotional"
Step 2: Output files generated
sample_output/
 ├── graph.mmd
 ├── storyboard.json
 ├── FotoOwlReel.mp4
 
🎥 Final Output
sample_output/FotoOwlReel.mp4

🧪 Testing
pytest tests/

Includes:

Pipeline flow tests
Storyboard validation tests
LLM-as-judge evaluation for narrative quality

🧠 Key Features
Multi-agent LangGraph orchestration
Structured LLM outputs (no free-text parsing)
RAG-enhanced storyboard generation
Self-healing compiler loop
Automatic Remotion video rendering
Modular production-grade architecture

📌 Known Limitations
Requires stable LLM API access
Rendering depends on number of images
Limited retry attempts for fixes
No UI (CLI-based system)

🔮 Future Improvements
Web UI for preview
Faster rendering pipeline
Smarter image selection
Audio/music sync
Cloud batch rendering

🏆 Why this project matters

This project demonstrates:

Multi-agent AI system design
LangGraph orchestration
RAG-based reasoning systems
Code generation + self-healing pipelines
End-to-end AI video generation architecture

📜 License
MIT License

👤 Author

Built as part of an AI Engineering multi-agent video generation system inspired by FotoOwl production pipelines.
