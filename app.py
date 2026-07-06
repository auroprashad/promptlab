import os
import gradio as gr
import gradio_client.utils

# Monkey-patch Gradio Client schema parser to resolve Pydantic-FastAPI boolean schema crashes (TypeError: argument of type 'bool' is not iterable)
orig_private = getattr(gradio_client.utils, "_json_schema_to_python_type", None)
orig_public = getattr(gradio_client.utils, "json_schema_to_python_type", None)

if orig_private:
    def patched_private(schema, defs):
        if isinstance(schema, bool):
            schema = {}
        return orig_private(schema, defs)
    gradio_client.utils._json_schema_to_python_type = patched_private

if orig_public:
    def patched_public(schema):
        if isinstance(schema, bool):
            schema = {}
        return orig_public(schema)
    gradio_client.utils.json_schema_to_python_type = patched_public
from optimizer import optimize_prompt
from analyzer import analyze_prompt
from templates import search_templates, get_categories, TEMPLATES
from utils import generate_html_diff, estimate_tokens, create_export_file

# Define minimal, standard styles
CUSTOM_CSS = """
body {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
}
.gradio-container {
    max-width: 1200px !important;
    background-color: #0f172a !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}
/* Flat, minimal panel layouts */
.sidebar-panel {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
.main-panel {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
.card-panel {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
}
/* Typography updates */
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}
.title-grad {
    color: #f8fafc !important;
    font-weight: 800 !important;
}
/* Input boxes styling */
textarea {
    background-color: #090d16 !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 6px !important;
}
textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}
/* Primary Button styling */
.btn-primary {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 6px !important;
}
.btn-primary:hover {
    background-color: #4338ca !important;
}
/* Custom tabs navigation */
.tabs button {
    font-weight: 500 !important;
    color: #94a3b8 !important;
}
.tabs button.selected {
    color: #818cf8 !important;
    border-bottom: 2px solid #6366f1 !important;
}
"""

def generate_score_dashboard_html(scores: dict) -> str:
    """Generates a styled, high-impact HTML visualization of scoring metrics."""
    overall = scores.get("overall", 50)
    clarity = scores.get("clarity", 50)
    specificity = scores.get("specificity", 50)
    structure = scores.get("structure", 50)
    context = scores.get("context", 50)
    constraints = scores.get("constraints", 50)
    
    # Decide score label and color
    if overall >= 85:
        eval_label = "EXCELLENT PROMPT"
        label_color = "#10b981" # emerald
        circle_color = "#10b981"
    elif overall >= 70:
        eval_label = "GOOD PROMPT"
        label_color = "#3b82f6" # blue
        circle_color = "#3b82f6"
    elif overall >= 50:
        eval_label = "BALANCED PROMPT"
        label_color = "#f59e0b" # amber
        circle_color = "#f59e0b"
    else:
        eval_label = "WEAK PROMPT"
        label_color = "#ef4444" # red
        circle_color = "#ef4444"

    html = f"""
    <div style="display: flex; gap: 32px; align-items: center; background-color: #0f172a; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; color: #cbd5e1; flex-wrap: wrap; margin-bottom: 20px;">
        <!-- Overall Score Circular Gauge -->
        <div style="flex: 1; min-width: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-right: 1px solid #1e293b; padding-right: 16px;">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; margin-bottom: 12px; letter-spacing: 0.1em; font-weight: 600;">Overall Rating</div>
            <div style="width: 110px; height: 110px; border-radius: 50%; border: 6px solid {circle_color}; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif; box-shadow: 0 0 20px rgba(255, 255, 255, 0.02);">
                <span style="font-size: 36px; font-weight: 800; color: #f8fafc; line-height: 1;">{overall}</span>
                <span style="font-size: 11px; color: #64748b; margin-top: 2px;">/ 100</span>
            </div>
            <div style="font-size: 12px; margin-top: 14px; color: {label_color}; font-weight: 700; letter-spacing: 0.05em;">
                {eval_label}
            </div>
        </div>
        
        <!-- Metrics Breakdown -->
        <div style="flex: 2; min-width: 280px; display: flex; flex-direction: column; gap: 14px;">
            <!-- Clarity -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; font-weight: 500;">
                    <span style="color: #94a3b8;">Clarity</span>
                    <span style="color: #f1f5f9;">{clarity}%</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1e293b; border-radius: 3px; overflow: hidden;">
                    <div style="width: {clarity}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 3px;"></div>
                </div>
            </div>
            <!-- Specificity -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; font-weight: 500;">
                    <span style="color: #94a3b8;">Specificity</span>
                    <span style="color: #f1f5f9;">{specificity}%</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1e293b; border-radius: 3px; overflow: hidden;">
                    <div style="width: {specificity}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 3px;"></div>
                </div>
            </div>
            <!-- Structure -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; font-weight: 500;">
                    <span style="color: #94a3b8;">Structure</span>
                    <span style="color: #f1f5f9;">{structure}%</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1e293b; border-radius: 3px; overflow: hidden;">
                    <div style="width: {structure}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 3px;"></div>
                </div>
            </div>
            <!-- Context -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; font-weight: 500;">
                    <span style="color: #94a3b8;">Context / Role</span>
                    <span style="color: #f1f5f9;">{context}%</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1e293b; border-radius: 3px; overflow: hidden;">
                    <div style="width: {context}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 3px;"></div>
                </div>
            </div>
            <!-- Constraints -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; font-weight: 500;">
                    <span style="color: #94a3b8;">Constraints</span>
                    <span style="color: #f1f5f9;">{constraints}%</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1e293b; border-radius: 3px; overflow: hidden;">
                    <div style="width: {constraints}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 3px;"></div>
                </div>
            </div>
        </div>
    </div>
    """
    return html

# App Logic Handlers
def handle_optimize_and_analyze(
    raw_prompt, provider, api_key, model_name, target_model, prompt_type, optimization_level, goal
):
    """Orchestrates optimization and analysis in a single user action."""
    # Safety Check
    if not raw_prompt.strip():
        raise gr.Error("Please enter a raw prompt in the textbox.")
    # 1. Run prompt optimization
    optimized_text = optimize_prompt(
        raw_prompt=raw_prompt,
        provider=provider,
        api_key=api_key,
        model_name=model_name,
        target_model=target_model,
        prompt_type=prompt_type,
        optimization_level=optimization_level,
        goal=goal
    )
    
    # 2. Run prompt analysis & grading
    scores_dict = analyze_prompt(
        raw_prompt=raw_prompt,
        provider=provider,
        api_key=api_key,
        model_name=model_name
    )
    
    # 3. Compile output widgets
    score_html = generate_score_dashboard_html(scores_dict)
    
    # Render weaknesses and suggestions markdown lists
    weaknesses_md = "\n".join([f"- <span style='color: #ef4444; font-weight: 500;'>•</span> {w}" for w in scores_dict.get("weaknesses", [])])
    suggestions_md = "\n".join([f"- <span style='color: #10b981; font-weight: 500;'>•</span> {s}" for s in scores_dict.get("suggestions", [])])
    
    # 4. Generate visual diff
    diff_html = generate_html_diff(raw_prompt, optimized_text)
    
    # 5. Compute token estimates
    orig_tokens = estimate_tokens(raw_prompt)
    opt_tokens = estimate_tokens(optimized_text)
    
    orig_stats = f"Characters: {orig_tokens['characters']} | Words: {orig_tokens['words']} | Est. Tokens: {orig_tokens['tokens']}"
    opt_stats = f"Characters: {opt_tokens['characters']} | Words: {opt_tokens['words']} | Est. Tokens: {opt_tokens['tokens']}"

    return (
        optimized_text,
        score_html,
        weaknesses_md,
        suggestions_md,
        diff_html,
        orig_stats,
        opt_stats
    )

def handle_template_load(template_prompt):
    """Loads prompt template content into input box and resets counters."""
    tokens = estimate_tokens(template_prompt)
    stats = f"Characters: {tokens['characters']} | Words: {tokens['words']} | Est. Tokens: {tokens['tokens']}"
    return template_prompt, stats

def handle_token_estimate(text):
    """Direct typing helper to compute token stats on the fly."""
    tokens = estimate_tokens(text)
    return f"Characters: {tokens['characters']} | Words: {tokens['words']} | Est. Tokens: {tokens['tokens']}"

# Build Gradio Blocks Layout
with gr.Blocks(theme=gr.themes.Default(primary_hue="violet", secondary_hue="indigo"), css=CUSTOM_CSS, title="PromptLab - Workspace") as demo:
    
    # Page Header
    with gr.Row():
        with gr.Column(scale=8):
            gr.HTML("""
            <div style="margin-top: 10px; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 32px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 36px;">🧪</span> 
                    <span class="title-grad">PromptLab</span>
                </h1>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 14px;">
                    An intelligent prompt engineering workspace that analyzes, improves, and critiques prompts.
                </p>
            </div>
            """)
    
    with gr.Row():
        
        # LEFT PANEL: Input & Settings Sidebar (Scale 4)
        with gr.Column(scale=4, variant="panel", elem_classes="sidebar-panel"):
            gr.Markdown("### ⚙️ Workspace Configuration")
            
            # API Provider Settings Group
            with gr.Group():
                api_provider = gr.Dropdown(
                    label="API Engine Provider",
                    choices=["Hugging Face", "OpenAI", "Google Gemini", "Anthropic"],
                    value="Hugging Face",
                    info="Choose your execution backend."
                )
                
                api_key = gr.Textbox(
                    label="API Secret Key",
                    placeholder="Enter API token/key here...",
                    type="password",
                    info="Keys are held locally in your browser's session state."
                )
                
                model_name = gr.Dropdown(
                    label="Optimizer Model Name",
                    choices=["Qwen/Qwen2.5-72B-Instruct", "meta-llama/Llama-3-8B-Instruct"],
                    value="Qwen/Qwen2.5-72B-Instruct",
                    allow_custom_value=True,
                    info="Select backend engine model or type custom hub repository."
                )
                
                api_notice = gr.Markdown(
                    "💡 **Hugging Face Free Tier**: By default, this Space runs completely free. If you see authorization/quota errors, please create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and paste it into the **API Secret Key** box above."
                )
            
            # Dynamic selector options helper
            def update_model_dropdown(provider):
                if provider == "Hugging Face":
                    return gr.update(choices=["Qwen/Qwen2.5-72B-Instruct", "meta-llama/Llama-3-8B-Instruct"], value="Qwen/Qwen2.5-72B-Instruct")
                elif provider == "OpenAI":
                    return gr.update(choices=["gpt-4o-mini", "gpt-4o"], value="gpt-4o-mini")
                elif provider == "Google Gemini":
                    return gr.update(choices=["gemini-1.5-flash", "gemini-1.5-pro"], value="gemini-1.5-flash")
                elif provider == "Anthropic":
                    return gr.update(choices=["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"], value="claude-3-5-sonnet-20240620")
                return gr.update(choices=[], value="")
                
            def update_notice_text(provider):
                if provider == "Hugging Face":
                    return "💡 **Hugging Face Free Tier**: By default, this Space runs completely free. If you see authorization/quota errors, please create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and paste it into the **API Secret Key** box above."
                elif provider == "OpenAI":
                    return "💡 **OpenAI API**: Enter your OpenAI API key above. You can manage your API keys on the [OpenAI API Keys platform](https://platform.openai.com/api-keys)."
                elif provider == "Google Gemini":
                    return "💡 **Google Gemini API**: Enter your Gemini API key above. Get a free API key in minutes from [Google AI Studio](https://aistudio.google.com/)."
                elif provider == "Anthropic":
                    return "💡 **Anthropic API**: Enter your Claude API key above. You can create keys in your [Anthropic Console](https://console.anthropic.com/)."
                return ""
                
            api_provider.change(
                fn=update_model_dropdown,
                inputs=api_provider,
                outputs=model_name
            )
            api_provider.change(
                fn=update_notice_text,
                inputs=api_provider,
                outputs=api_notice
            )

            gr.HTML("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'/>")
            gr.Markdown("### 🛠️ Optimization Settings")
            
            target_model = gr.Dropdown(
                label="Target Model",
                choices=["GPT-4", "GPT-3.5", "Claude 3.5 Sonnet", "Gemini 1.5 Pro", "Llama 3", "Qwen 2.5"],
                value="Qwen 2.5",
                info="LLM that will run the final optimized prompt."
            )
            
            prompt_type = gr.Dropdown(
                label="Prompt Type / Domain",
                choices=["General", "Coding", "Marketing", "Creative Writing", "Research", "Education", "Roleplay", "System Prompt"],
                value="General"
            )
            
            optimization_level = gr.Radio(
                label="Optimization Level",
                choices=["Light", "Balanced", "Aggressive"],
                value="Balanced",
                info="Determines structural depth added to prompt."
            )
            
            opt_goal = gr.Dropdown(
                label="Optimization Goal",
                choices=["Better quality", "Conciseness", "Creativity", "Safety/Alignment"],
                value="Better quality"
            )
            
        # RIGHT PANEL: Prompt Box & Result Tabs (Scale 8)
        with gr.Column(scale=8):
            
            with gr.Column(variant="panel", elem_classes="main-panel"):
                gr.Markdown("### ✍️ Active Editor")
                
                raw_prompt_input = gr.Textbox(
                    label="Input Prompt",
                    placeholder="Type or paste your raw prompt here...",
                    lines=8,
                    max_lines=20
                )
                
                raw_stats = gr.Markdown("Characters: 0 | Words: 0 | Est. Tokens: 0")
                
                raw_prompt_input.change(
                    fn=handle_token_estimate,
                    inputs=raw_prompt_input,
                    outputs=raw_stats
                )
                
                optimize_btn = gr.Button("🔮 Optimize & Analyze Prompt", elem_classes="btn-primary")
            
            # Workspace Output Tabs
            with gr.Tabs(elem_classes="tabs"):
                
                # Tab 1: Optimize Results
                with gr.TabItem("✨ Optimized Output"):
                    with gr.Column():
                        optimized_output = gr.Textbox(
                            label="Improved Prompt Template",
                            placeholder="Optimized prompt will generate here...",
                            lines=10,
                            max_lines=20
                        )
                        
                        opt_stats = gr.Markdown("Characters: 0 | Words: 0 | Est. Tokens: 0")
                        
                        with gr.Row():
                            with gr.Column(scale=2):
                                export_format = gr.Radio(
                                    label="Export Format",
                                    choices=["TXT", "Markdown", "JSON"],
                                    value="TXT",
                                    container=False
                                )
                            with gr.Column(scale=1):
                                copy_btn = gr.Button("📋 Copy Prompt")
                            with gr.Column(scale=1):
                                download_btn = gr.Button("📥 Download File")
                                
                        download_output = gr.File(label="Download Links", visible=False)
                            
                        # Clipboard Copy Handler
                        def notify_copy(text):
                            if not text.strip():
                                raise gr.Error("No optimized prompt available to copy.")
                            gr.Info("Prompt copied to clipboard!")

                        copy_btn.click(
                            fn=notify_copy,
                            inputs=optimized_output,
                            js="(text) => { if(text) navigator.clipboard.writeText(text); }"
                        )

                        # Handle Export
                        def trigger_export(text, fmt):
                            if not text.strip():
                                raise gr.Error("No optimized content available to export.")
                            file_path = create_export_file(text, fmt)
                            return gr.update(value=file_path, visible=True)
                            
                        download_btn.click(
                            fn=trigger_export,
                            inputs=[optimized_output, export_format],
                            outputs=download_output
                        )
                
                # Tab 2: Score & Critical Analysis
                with gr.TabItem("📊 Score & Critique"):
                    with gr.Column():
                        gr.Markdown("### 🎯 Prompt Engineering Scorecard")
                        
                        # Custom Circular Indicator Dashboard
                        score_dashboard_container = gr.HTML(
                            value="<div style='text-align: center; color: #64748b; padding: 40px;'>Run analysis to view scorecard.</div>"
                        )
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("#### ⚠️ Identified Weaknesses")
                                weaknesses_list = gr.Markdown("No analysis data. Click **Optimize & Analyze** to inspect.", line_breaks=True)
                            with gr.Column():
                                gr.Markdown("#### 💡 Structural Suggestions")
                                suggestions_list = gr.Markdown("No analysis data. Click **Optimize & Analyze** to inspect.", line_breaks=True)

                # Tab 3: Git-style Changes Diff
                with gr.TabItem("🔍 Diff Inspector"):
                    with gr.Column():
                        gr.Markdown("### 🔄 Unified Diff Comparison")
                        gr.Markdown("Highlights exact code structure shifts and additions (`+`) or deletions (`-`).")
                        
                        diff_inspector_container = gr.HTML(
                            value="<div style='text-align: center; color: #64748b; padding: 40px;'>Run optimization to inspect code diff.</div>"
                        )
                
                # Tab 4: Searchable Prompt Templates
                with gr.TabItem("🗂️ Reusable Templates"):
                    with gr.Column():
                        gr.Markdown("### 📚 Prompt Blueprint Library")
                        
                        with gr.Row():
                            search_box = gr.Textbox(
                                label="Search Keywords",
                                placeholder="Search by title or description...",
                                scale=3
                            )
                            category_filter = gr.Dropdown(
                                label="Filter by Category",
                                choices=get_categories(),
                                value="All",
                                scale=2
                            )
                        
                        # Templates Grid Container
                        # We instantiate static cards for the templates and toggle their visibility
                        template_card_containers = []
                        template_inputs = []
                        
                        with gr.Column():
                            for index, t in enumerate(TEMPLATES):
                                # Wrap each template in a container to toggle visibility easily
                                with gr.Column(variant="panel", elem_classes="card-panel") as card_container:
                                    gr.HTML(f"""
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span style="font-weight:700; font-size:16px; color:#a78bfa;">{t['title']}</span>
                                        <span style="background-color:rgba(139,92,246,0.15); color:#a78bfa; font-size:10px; padding:2px 8px; border-radius:12px; font-weight:600; text-transform:uppercase;">{t['category']}</span>
                                    </div>
                                    <p style="margin:8px 0; font-size:13px; color:#94a3b8; line-height:1.4;">{t['description']}</p>
                                    """)
                                    
                                    # Safe text component to pass value
                                    t_prompt_text = gr.State(t['prompt'])
                                    load_btn = gr.Button("📋 Load into Editor", size="sm")
                                    
                                    # Click event updates the active raw prompt editor textbox
                                    load_btn.click(
                                        fn=handle_template_load,
                                        inputs=t_prompt_text,
                                        outputs=[raw_prompt_input, raw_stats]
                                    )
                                    
                                    template_card_containers.append(card_container)
                                    template_inputs.append(t)
                        
                        # Filtering callback function
                        def filter_templates_view(search_val, category_val):
                            updates = []
                            for t, container in zip(template_inputs, template_card_containers):
                                # Determine matching
                                matches_category = (category_val == "All") or (t["category"] == category_val)
                                matches_query = (not search_val) or (
                                    search_val.lower() in t["title"].lower() or 
                                    search_val.lower() in t["description"].lower() or 
                                    search_val.lower() in t["prompt"].lower()
                                )
                                is_visible = matches_category and matches_query
                                updates.append(gr.update(visible=is_visible))
                            return updates

                        # Wire filters to search and dropdowns
                        search_box.change(
                            fn=filter_templates_view,
                            inputs=[search_box, category_filter],
                            outputs=template_card_containers
                        )
                        category_filter.change(
                            fn=filter_templates_view,
                            inputs=[search_box, category_filter],
                            outputs=template_card_containers
                        )
                
                # Tab 5: Learn Prompt Engineering
                with gr.TabItem("📖 Learn"):
                    with gr.Column():
                        gr.Markdown("### 🎓 Core Prompt Engineering Methodologies")
                        gr.Markdown("Why does the optimizer restructure your prompt? Here is the cognitive science of Large Language Models:")
                        
                        with gr.Row():
                            with gr.Column(variant="panel", elem_classes="card-panel"):
                                gr.HTML("<h4>🎭 Define a Clear Role</h4>")
                                gr.Markdown(
                                    "**Why:** Instructing an LLM to act as a specific expert (e.g., 'Senior QA Engineer') aligns its internal probability weights with specialized terminology, tone, and professional methodologies.\n\n"
                                    "**Example:** Changing *'Write a marketing outline'* into *'Act as a Senior Copywriter and CMO'* improves strategic reasoning by 40%."
                                )
                            with gr.Column(variant="panel", elem_classes="card-panel"):
                                gr.HTML("<h4>⚠️ Impose Hard Constraints</h4>")
                                gr.Markdown(
                                    "**Why:** LLMs naturally drift and hallucinate options unless bounded. Adding negative constraints (e.g., *'Do NOT suggest external APIs'*) prevents toxic patterns and off-topic outputs.\n\n"
                                    "**Example:** Adding *'Word limit: strictly 300 words'* or *'Limit answer to verified facts'* reduces hallucinations significantly."
                                )
                        
                        with gr.Row():
                            with gr.Column(variant="panel", elem_classes="card-panel"):
                                gr.HTML("<h4>🧱 Logical Structure & Heading Delimiters</h4>")
                                gr.Markdown(
                                    "**Why:** LLMs process tokens sequentially. Using clear Markdown headers (`# Role`, `# Context`) or XML tags (`<data></data>`) prevents instruction confusion, ensuring the model knows which text is instruction and which is input.\n\n"
                                    "**Example:** Separating long text inputs with triple quotes or XML tags preserves contextual priority."
                                )
                            with gr.Column(variant="panel", elem_classes="card-panel"):
                                gr.HTML("<h4>📤 Explicit Output Formats</h4>")
                                gr.Markdown(
                                    "**Why:** By default, LLMs chat naturally. If you need clean CSV, JSON, or markdown tables, you must describe the target schema, keys, and values explicitly in your prompt.\n\n"
                                    "**Example:** Specifying a JSON schema format avoids wrapping markdown text blocks (` ```json `), making the output directly parseable."
                                )

    # Connect major button click action
    optimize_btn.click(
        fn=handle_optimize_and_analyze,
        inputs=[
            raw_prompt_input,
            api_provider,
            api_key,
            model_name,
            target_model,
            prompt_type,
            optimization_level,
            opt_goal
        ],
        outputs=[
            optimized_output,
            score_dashboard_container,
            weaknesses_list,
            suggestions_list,
            diff_inspector_container,
            raw_stats,
            opt_stats
        ]
    )

# Dummy function to satisfy Hugging Face ZeroGPU platform check if hosted on GPU hardware
try:
    import spaces
    @spaces.GPU
    def dummy_gpu_fn():
        return None
except Exception:
    pass

# Run app
if __name__ == "__main__":
    demo.launch()
