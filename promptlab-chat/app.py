import os
import json
import gradio as gr
import gradio_client.utils

# Monkey-patch Gradio Client schema parser to resolve Pydantic-FastAPI boolean schema crashes on Gradio 4.44.0
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

from optimizer import run_chat_completion

# Define modern minimal styles (ChatGPT/Claude dark slate theme)
CUSTOM_CSS = """
body, html {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    margin: 0;
    padding: 0;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    height: 100vh !important;
    width: 100vw !important;
    overflow: hidden !important;
}
.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    background-color: #0f172a !important;
    height: 100vh !important;
    width: 100vw !important;
}
#main-wrapper {
    display: flex !important;
    height: 100vh !important;
    width: 100vw !important;
    overflow: hidden !important;
    flex-direction: row !important;
    gap: 0 !important;
}

/* Sidebar Panel Styling */
#sidebar-panel {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    background-color: #1e293b !important;
    border-right: 1px solid #334155 !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 15px !important;
    box-sizing: border-box !important;
    height: 100vh !important;
    flex-shrink: 0 !important;
    gap: 10px !important;
    border-radius: 0 !important;
    border-top: none !important;
    border-bottom: none !important;
    border-left: none !important;
}
.sidebar-header {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #f8fafc;
    padding-left: 5px;
}
#new-chat-btn {
    width: 100%;
    background-color: transparent !important;
    border: 1px solid #475569 !important;
    color: #e2e8f0 !important;
    padding: 10px !important;
    border-radius: 6px !important;
    text-align: left !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    margin-bottom: 5px !important;
    box-shadow: none !important;
}
#new-chat-btn:hover {
    background-color: #334155 !important;
    border-color: #64748b !important;
}
.sidebar-chat-list {
    flex-grow: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 6px;
    height: calc(100vh - 350px);
}
.sidebar-chat-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: #cbd5e1;
    transition: background 0.15s;
}
.sidebar-chat-item:hover {
    background-color: #334155;
    color: #f8fafc;
}
.sidebar-chat-item.active {
    background-color: #475569;
    color: #f8fafc;
    font-weight: 500;
}
.chat-item-title {
    flex-grow: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-right: 8px;
}
.chat-item-delete {
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    padding: 2px 4px;
    font-size: 12px;
    border-radius: 4px;
    transition: color 0.15s;
}
.chat-item-delete:hover {
    color: #ef4444;
    background-color: rgba(239, 68, 68, 0.1);
}

/* Collapsible Settings Styling */
.sidebar-divider {
    height: 1px;
    background-color: #334155;
    margin: 10px 0;
}
.settings-drawer {
    margin-top: auto;
    border-top: 1px solid #334155;
    padding-top: 10px;
}
.settings-summary {
    cursor: pointer;
    font-size: 13px;
    color: #94a3b8;
    font-weight: 600;
    user-select: none;
    padding: 5px 0;
    outline: none;
}
.settings-summary:hover {
    color: #f1f5f9;
}
.settings-content {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background-color: #0f172a;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #334155;
}
.settings-group {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.settings-label {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
}
.settings-select, .settings-input {
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    color: #f1f5f9 !important;
    font-size: 12px !important;
    padding: 6px !important;
    border-radius: 4px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
.settings-input:focus, .settings-select:focus {
    outline: none !important;
    border-color: #8b5cf6 !important;
}
.settings-btn {
    background-color: #8b5cf6 !important;
    border: none !important;
    color: #f1f5f9 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 8px !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    transition: background 0.15s !important;
    width: 100% !important;
    margin-top: 5px;
    box-shadow: none !important;
}
.settings-btn:hover {
    background-color: #7c3aed !important;
}
.settings-status {
    font-size: 11px;
    text-align: center;
    color: #10b981;
    height: 12px;
}

/* Chat Main Panel Styling */
#chat-main-panel {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    background-color: #0f172a !important;
    position: relative !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    gap: 0 !important;
    border: none !important;
    border-radius: 0 !important;
}
.chat-header {
    height: 60px;
    border-bottom: 1px solid #1e293b;
    display: flex;
    align-items: center;
    padding: 0 20px;
    font-weight: 600;
    color: #e2e8f0;
    background-color: #0f172a;
}
#chat-container {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 20px !important;
    overflow-y: auto !important;
    max-width: 800px !important;
    width: 100% !important;
    margin: 0 auto !important;
    box-sizing: border-box !important;
    height: calc(100vh - 60px) !important;
    justify-content: space-between !important;
    border: none !important;
}
#chatbot-component {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    flex-grow: 1 !important;
    margin-bottom: 20px !important;
}
#chatbot-component .message.user {
    background-color: #1e293b !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
}
#chatbot-component .message.bot {
    background-color: #0f172a !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
#input-row {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    padding: 10px 0 10px 0;
    background-color: #0f172a;
    border: none !important;
    box-shadow: none !important;
    gap: 10px !important;
}
#msg-input-box {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 20px !important;
    color: #f8fafc !important;
}
#msg-input-box textarea {
    background-color: transparent !important;
    border: none !important;
    color: #f8fafc !important;
}
.help-notes {
    font-size: 11px;
    color: #475569;
    text-align: center;
    margin-top: 8px;
}
"""

# HTML block to inject Javascript bridge for Sidebar, LocalStorage, and Settings Drawer
JS_BRIDGE = """
<script>
    const STORAGE_KEY = "promptlab_chat_history";
    const CONFIG_KEY = "promptlab_api_config";
    
    function getChats() {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : {};
    }
    
    function saveChats(chats) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    }
    
    function getSettings() {
        const data = localStorage.getItem(CONFIG_KEY);
        return data ? JSON.parse(data) : { provider: "Hugging Face", hf_token: "", openai_key: "", gemini_key: "" };
    }
    
    function saveSettings(config) {
        localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
    }
    
    function renderSidebar() {
        const chats = getChats();
        const sidebarList = document.getElementById("sidebar-chat-list");
        if (!sidebarList) return;
        
        sidebarList.innerHTML = "";
        
        const sortedIds = Object.keys(chats).sort((a, b) => chats[b].updatedAt - chats[a].updatedAt);
        const activeIdInput = document.querySelector("#current_chat_id textarea");
        const activeId = activeIdInput ? activeIdInput.value : "";
        
        sortedIds.forEach(id => {
            const chat = chats[id];
            const item = document.createElement("div");
            item.className = `sidebar-chat-item ${id === activeId ? 'active' : ''}`;
            
            const title = document.createElement("span");
            title.className = "chat-item-title";
            title.innerText = chat.title || "New Chat";
            title.onclick = () => loadChat(id);
            
            const delBtn = document.createElement("button");
            delBtn.className = "chat-item-delete";
            delBtn.innerText = "🗑️";
            delBtn.onclick = (e) => {
                e.stopPropagation();
                deleteChat(id);
            };
            
            item.appendChild(title);
            item.appendChild(delBtn);
            sidebarList.appendChild(item);
        });
    }
    
    function createNewChat() {
        const chats = getChats();
        const newId = "chat_" + Date.now();
        chats[newId] = {
            id: newId,
            title: "New Chat",
            messages: [],
            updatedAt: Date.now()
        };
        saveChats(chats);
        setActiveChat(newId, []);
    }
    
    function setActiveChat(id, messages) {
        const idInput = document.querySelector("#current_chat_id textarea");
        const jsonInput = document.querySelector("#loaded_chat_json textarea");
        const loadBtn = document.getElementById("trigger_load_btn");
        
        if (idInput && jsonInput && loadBtn) {
            idInput.value = id;
            idInput.dispatchEvent(new Event("input"));
            
            jsonInput.value = JSON.stringify(messages);
            jsonInput.dispatchEvent(new Event("input"));
            
            setTimeout(() => {
                loadBtn.click();
            }, 100);
        }
    }
    
    function loadChat(id) {
        const chats = getChats();
        if (chats[id]) {
            setActiveChat(id, chats[id].messages);
        }
    }
    
    function deleteChat(id) {
        const chats = getChats();
        delete chats[id];
        saveChats(chats);
        
        const activeIdInput = document.querySelector("#current_chat_id textarea");
        const activeId = activeIdInput ? activeIdInput.value : "";
        
        if (activeId === id) {
            createNewChat();
        } else {
            renderSidebar();
        }
    }
    
    function syncSettingsToGradio() {
        const config = getSettings();
        
        const providerInput = document.querySelector("#active_provider textarea");
        const hfInput = document.querySelector("#stored_hf_token textarea");
        const openaiInput = document.querySelector("#stored_openai_key textarea");
        const geminiInput = document.querySelector("#stored_gemini_key textarea");
        
        if (providerInput && hfInput && openaiInput && geminiInput) {
            providerInput.value = config.provider;
            providerInput.dispatchEvent(new Event("input"));
            
            hfInput.value = config.hf_token;
            hfInput.dispatchEvent(new Event("input"));
            
            openaiInput.value = config.openai_key;
            openaiInput.dispatchEvent(new Event("input"));
            
            geminiInput.value = config.gemini_key;
            geminiInput.dispatchEvent(new Event("input"));
        }
    }
    
    function saveSettingsFromUI() {
        const provider = document.getElementById("api-provider-select").value;
        const hf_token = document.getElementById("hf-token-input").value;
        const openai_key = document.getElementById("openai-key-input").value;
        const gemini_key = document.getElementById("gemini-key-input").value;
        
        const config = { provider, hf_token, openai_key, gemini_key };
        saveSettings(config);
        syncSettingsToGradio();
        
        const status = document.getElementById("settings-status");
        if (status) {
            status.innerText = "Config Saved!";
            setTimeout(() => { status.innerText = ""; }, 2500);
        }
    }
    
    // Background interval check to auto-save chatbot updates from Python
    let lastSavedValue = "";
    setInterval(() => {
        const trigger = document.querySelector("#save_chat_trigger textarea");
        const activeIdInput = document.querySelector("#current_chat_id textarea");
        if (!trigger || !activeIdInput) return;
        
        const currentValue = trigger.value;
        const activeId = activeIdInput.value;
        
        if (currentValue && currentValue !== lastSavedValue && activeId) {
            lastSavedValue = currentValue;
            try {
                const messages = JSON.parse(currentValue);
                const chats = getChats();
                
                if (!chats[activeId]) {
                    chats[activeId] = { id: activeId };
                }
                
                chats[activeId].messages = messages;
                chats[activeId].updatedAt = Date.now();
                
                if (messages.length > 0 && messages[0][0]) {
                    const firstUserMsg = messages[0][0];
                    chats[activeId].title = firstUserMsg.substring(0, 20) + (firstUserMsg.length > 20 ? "..." : "");
                } else {
                    chats[activeId].title = "New Chat";
                }
                
                saveChats(chats);
                renderSidebar();
            } catch (e) {
                console.error("Error saving chat:", e);
            }
        }
    }, 500);
    
    // Bootstrap Sidebar and Settings on Load
    function init() {
        const activeIdInput = document.querySelector("#current_chat_id textarea");
        const saveBtn = document.getElementById("save-settings-btn");
        if (!activeIdInput || !saveBtn) {
            setTimeout(init, 200);
            return;
        }
        
        // Load API inputs from storage
        const config = getSettings();
        document.getElementById("api-provider-select").value = config.provider;
        document.getElementById("hf-token-input").value = config.hf_token;
        document.getElementById("openai-key-input").value = config.openai_key;
        document.getElementById("gemini-key-input").value = config.gemini_key;
        
        saveBtn.onclick = saveSettingsFromUI;
        
        // Bind New Chat click
        document.getElementById("new-chat-btn").onclick = createNewChat;
        
        // Sync config values to hidden Python inputs
        syncSettingsToGradio();
        
        // Load most recent chat or build new
        const chats = getChats();
        const keys = Object.keys(chats);
        if (keys.length > 0) {
            const sorted = keys.sort((a, b) => chats[b].updatedAt - chats[a].updatedAt);
            loadChat(sorted[0]);
        } else {
            createNewChat();
        }
    }
    
    window.addEventListener("DOMContentLoaded", () => {
        setTimeout(init, 500);
    });
</script>
"""

# Backend triggers
def load_chat_history(json_str):
    """Parses JSON-serialized chat history from JS and updates the chatbot."""
    try:
        if not json_str:
            return [], ""
        messages = json.loads(json_str)
        return messages, ""
    except Exception as e:
        print("Failed to load chat history:", e)
        return [], ""

def handle_user_input(user_message, history):
    """Appends user message to history, yields thinking indicator, and clears input textbox."""
    if not user_message.strip():
        return "", history, ""
    
    history.append([user_message, "⏳ RESTORING & OPTIMIZING PROMPT..."])
    return "", history, ""

def generate_llm_response(history, provider, hf_token, openai_key, gemini_key):
    """Queries selected backend model and streams/updates the chatbot response and save trigger."""
    if not history:
        yield history, ""
        return
        
    user_message = history[-1][0]
    
    # Format chat history context
    api_messages = []
    for user, bot in history[:-1]:
        api_messages.append({"role": "user", "content": user})
        api_messages.append({"role": "assistant", "content": bot})
    api_messages.append({"role": "user", "content": user_message})
    
    try:
        bot_response = run_chat_completion(
            api_messages,
            provider=provider,
            hf_token=hf_token,
            openai_key=openai_key,
            gemini_key=gemini_key
        )
        history[-1][1] = bot_response
    except Exception as e:
        history[-1][1] = f"❌ Error: {str(e)}"
        
    # Yield final history and serialize it to save_chat_trigger for JavaScript storage
    yield history, json.dumps(history)

# Build Layout
with gr.Blocks(theme=gr.themes.Default(primary_hue="violet"), css=CUSTOM_CSS, title="PromptLab Chat", head=JS_BRIDGE) as demo:
    
    # Hidden components for JavaScript local storage / Settings sync bridge
    loaded_chat_json = gr.Textbox(visible=False, elem_id="loaded_chat_json")
    current_chat_id = gr.Textbox(visible=False, elem_id="current_chat_id")
    save_chat_trigger = gr.Textbox(visible=False, elem_id="save_chat_trigger")
    trigger_load_btn = gr.Button(visible=False, elem_id="trigger_load_btn")
    
    # Hidden settings inputs
    active_provider = gr.Textbox(visible=False, elem_id="active_provider")
    stored_hf_token = gr.Textbox(visible=False, elem_id="stored_hf_token")
    stored_openai_key = gr.Textbox(visible=False, elem_id="stored_openai_key")
    stored_gemini_key = gr.Textbox(visible=False, elem_id="stored_gemini_key")
    
    # Main Wrapper Grid Layout
    with gr.Row(elem_id="main-wrapper"):
        
        # 1. Left Sidebar Column
        with gr.Column(scale=1, elem_id="sidebar-panel"):
            gr.HTML("""
            <div class="sidebar-header">
                <span>💬</span> PromptLab Chat
            </div>
            """)
            new_chat_btn = gr.Button("+ New Chat", elem_id="new-chat-btn")
            gr.HTML("""
            <div class="sidebar-chat-list" id="sidebar-chat-list">
                <!-- Javascript populated chat list -->
            </div>
            
            <div class="sidebar-divider"></div>
            
            <details class="settings-drawer" open>
                <summary class="settings-summary">⚙️ API Settings</summary>
                <div class="settings-content">
                    <div class="settings-group">
                        <label class="settings-label">Active Provider</label>
                        <select id="api-provider-select" class="settings-select">
                            <option value="Hugging Face">Hugging Face (Qwen 72B)</option>
                            <option value="OpenAI">OpenAI (GPT-4o-mini)</option>
                            <option value="Google Gemini">Google Gemini (Gemini 1.5 Flash)</option>
                        </select>
                    </div>
                    <div class="settings-group">
                        <label class="settings-label">Hugging Face Token</label>
                        <input type="password" id="hf-token-input" class="settings-input" placeholder="hf_... (optional)">
                    </div>
                    <div class="settings-group">
                        <label class="settings-label">OpenAI API Key</label>
                        <input type="password" id="openai-key-input" class="settings-input" placeholder="sk-... (optional)">
                    </div>
                    <div class="settings-group">
                        <label class="settings-label">Gemini API Key</label>
                        <input type="password" id="gemini-key-input" class="settings-input" placeholder="AIzaSy... (optional)">
                    </div>
                    <button id="save-settings-btn" class="settings-btn">💾 Save Config</button>
                    <div id="settings-status" class="settings-status"></div>
                </div>
            </details>
            """)
            
        # 2. Main Chat Panel Column
        with gr.Column(scale=4, elem_id="chat-main-panel"):
            gr.HTML("""
            <div class="chat-header">
                🧪 Prompt Engineering Assistant
            </div>
            """)
            
            with gr.Column(elem_id="chat-container"):
                chatbot = gr.Chatbot(
                    label="Restructure prompt",
                    show_label=False,
                    elem_id="chatbot-component"
                )
                
                with gr.Row(elem_id="input-row"):
                    msg_input = gr.Textbox(
                        placeholder="Paste your raw prompt here to optimize...",
                        show_label=False,
                        lines=1,
                        max_lines=5,
                        elem_id="msg-input-box",
                        scale=10
                    )
                    submit_btn = gr.Button("🚀 Optimize", variant="primary", scale=1)
                    
                gr.Markdown(
                    "💡 Powered by Qwen, GPT, and Gemini. Save your API keys locally in Settings to run privately.",
                    elem_classes="help-notes"
                )
    
    # Wire events
    trigger_load_btn.click(
        fn=load_chat_history,
        inputs=loaded_chat_json,
        outputs=[chatbot, msg_input]
    )
    
    # Submit actions (Enter key or Click submit button)
    submit_event = submit_btn.click(
        fn=handle_user_input,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, save_chat_trigger]
    ).then(
        fn=generate_llm_response,
        inputs=[chatbot, active_provider, stored_hf_token, stored_openai_key, stored_gemini_key],
        outputs=[chatbot, save_chat_trigger]
    )
    
    input_event = msg_input.submit(
        fn=handle_user_input,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, save_chat_trigger]
    ).then(
        fn=generate_llm_response,
        inputs=[chatbot, active_provider, stored_hf_token, stored_openai_key, stored_gemini_key],
        outputs=[chatbot, save_chat_trigger]
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
