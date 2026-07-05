---
title: PromptLab
emoji: 🧪
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
python_version: 3.11
app_file: app.py
pinned: false
---

# PromptLab: Intelligent Prompt Engineering Workspace

An intelligent prompt engineering workspace that analyzes, improves, and experiments with prompts for different AI models.

## Features
- **Optimize**: Automatically refine and restructure raw prompts using the best-performing open-source and commercial LLM engines.
- **Analyze**: Detailed critiques of your prompt, evaluating factors like Clarity, Specificity, Context, and Constraints.
- **Compare**: View exact differences side-by-side between the original and optimized prompts with a clean diff engine.
- **Templates**: Browse a curated library of high-performance prompt templates across multiple categories.
- **Learn**: Clear visual breakdowns explaining the reasoning behind why changes were made.

## Tech Stack
- **Frontend**: Gradio (with custom CSS styling)
- **Backend**: Python 3.10+
- **API integrations**: Hugging Face Inference API, OpenAI, Anthropic Claude, Google Gemini

## Local Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
