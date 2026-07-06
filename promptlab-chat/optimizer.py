import os
import requests
from huggingface_hub import InferenceClient, get_token
from openai import OpenAI

SYSTEM_PROMPT = """You are a helpful, world-class Prompt Engineering Assistant.
Your goal is to help the user design, refine, optimize, and critique prompts to get the best possible results from Large Language Models (LLMs).

When the user provides a prompt, you should:
1. RESTORE/RESTURCTURE the prompt using elite prompt engineering frameworks (specifying clear Role, Objective, Context, Constraints, and Instructions).
2. Present the optimized prompt clearly inside a markdown code block so they can copy it easily.
3. Briefly explain the key changes/improvements you made (e.g. why you added specific constraints or clarified the instructions) so they can learn.

Be conversational, professional, and clear. If they ask follow-up questions or want to adjust the prompt, iterate with them dynamically."""

def run_chat_completion(messages: list, provider: str = "Hugging Face", hf_token: str = None, openai_key: str = None, gemini_key: str = None) -> str:
    """Runs conversational completion based on the configured active provider and keys."""
    provider_clean = provider.lower()
    
    # 1. Hugging Face (Qwen 72B)
    if "hugging" in provider_clean:
        model_name = "Qwen/Qwen2.5-72B-Instruct"
        token = hf_token.strip() if hf_token and hf_token.strip() else get_token()
        client = InferenceClient(model=model_name, token=token)
        
        chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat_completion(
                    messages=chat_messages,
                    max_tokens=2048,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    err_str = str(e).lower()
                    if "token" in err_str or "auth" in err_str or "unauthorized" in err_str or "api_key" in err_str or "401" in err_str or "402" in err_str or "403" in err_str or "payment" in err_str or "forbidden" in err_str or "permission" in err_str:
                        raise ValueError(
                            "Hugging Face credentials missing or unauthorized. "
                            "Please enter your HF token in the Settings sidebar. Ensure it has "
                            "'Make calls to Inference Providers' scope enabled!"
                        )
                    raise e
                time.sleep(2)

    # 2. OpenAI (GPT-4o-mini)
    elif "openai" in provider_clean:
        token = openai_key.strip() if openai_key and openai_key.strip() else os.environ.get("OPENAI_API_KEY")
        if not token:
            raise ValueError("OpenAI API Key is required. Please set it in the Settings sidebar.")
        
        client = OpenAI(api_key=token)
        chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_messages,
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content

    # 3. Google Gemini (Gemini 1.5 Flash)
    elif "gemini" in provider_clean or "google" in provider_clean:
        token = gemini_key.strip() if gemini_key and gemini_key.strip() else os.environ.get("GEMINI_API_KEY")
        if not token:
            raise ValueError("Google Gemini API Key is required. Please set it in the Settings sidebar.")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={token}"
        headers = {"Content-Type": "application/json"}
        
        # Convert standard OpenAI/HF messages list to Gemini API contents format
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
        
    else:
        raise ValueError(f"Unknown API Provider selected: {provider}")
