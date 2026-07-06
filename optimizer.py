import os
from huggingface_hub import InferenceClient
from openai import OpenAI

import anthropic

def load_system_prompt(filename: str) -> str:
    """Helper to load system prompts from files."""
    try:
        # Resolve absolute path relative to current module
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "prompts", filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # Fallback prompts if file read fails
        if "optimizer" in filename:
            return "You are an expert prompt engineer. Optimize the prompt structure."
        else:
            return "You are a prompt auditor. Critique the prompt and output JSON with overall score, weaknesses, and suggestions."

def run_llm_call(provider: str, api_key: str, model_name: str, system_prompt: str, user_prompt: str) -> str:
    """
    Standardized interface to call different LLM providers.
    Supports Hugging Face, OpenAI, Gemini, and Anthropic.
    """
    provider = provider.lower()
    clean_key = api_key.strip() if api_key else None
    
    if provider == "hugging face":
        # If model_name is not full path, use default Qwen
        if not model_name or "/" not in model_name:
            model_name = "Qwen/Qwen2.5-72B-Instruct"
        
        # Use Hugging Face serverless client (checking UI token first, then local/Space credentials)
        from huggingface_hub import get_token
        token = clean_key if clean_key else get_token()
        client = InferenceClient(model=model_name, token=token)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat_completion(
                    messages=messages,
                    max_tokens=2048,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    err_str = str(e).lower()
                    if "token" in err_str or "auth" in err_str or "unauthorized" in err_str or "api_key" in err_str or "401" in err_str or "402" in err_str or "403" in err_str or "payment" in err_str or "forbidden" in err_str or "permission" in err_str:
                        raise ValueError(
                            "A Hugging Face Token with 'Make calls to Inference Providers' scope is required. "
                            "Please create a token at huggingface.co/settings/tokens, making sure to check "
                            "the 'Inference' -> 'Make calls to Inference Providers' scope under permissions. "
                            "Then, enter it in the sidebar. If you are the Space owner, save this token as a Space Secret "
                            "named 'HF_TOKEN' in your Settings tab to let it run out-of-the-box for all visitors!"
                        )
                    raise e
                time.sleep(2)

    elif provider == "openai":
        token = clean_key if clean_key else os.environ.get("OPENAI_API_KEY")
        if not token:
            raise ValueError("OpenAI API Key is required. Please set it in the sidebar settings.")
        client = OpenAI(api_key=token)
        
        name = model_name if model_name else "gpt-4o-mini"
        response = client.chat.completions.create(
            model=name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content

    elif provider == "google gemini":
        token = clean_key if clean_key else os.environ.get("GEMINI_API_KEY")
        if not token:
            raise ValueError("Google Gemini API Key is required. Please set it in the sidebar settings.")
        
        name = model_name if model_name else "gemini-1.5-flash"
        import requests
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent?key={token}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"parts": [{"text": user_prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
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

    elif provider == "anthropic":
        token = clean_key if clean_key else os.environ.get("ANTHROPIC_API_KEY")
        if not token:
            raise ValueError("Anthropic API Key is required. Please set it in the sidebar settings.")
        client = anthropic.Anthropic(api_key=token)
        
        name = model_name if model_name else "claude-3-5-sonnet-20240620"
        response = client.messages.create(
            model=name,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.content[0].text

    else:
        raise ValueError(f"Unknown API provider: {provider}")

def optimize_prompt(
    raw_prompt: str,
    provider: str,
    api_key: str,
    model_name: str,
    target_model: str,
    prompt_type: str,
    optimization_level: str,
    goal: str
) -> str:
    """
    Constructs the optimization instructions, formats variables, and queries the LLM.
    """
    if not raw_prompt.strip():
        return "Please enter a prompt to optimize."

    base_system = load_system_prompt("optimizer.txt")
    
    # Inject parameters into the run-time context
    run_context = (
        f"\n\n--- OPTIMIZATION INSTRUCTIONS FOR THIS RUN ---\n"
        f"Target Model for output: {target_model}\n"
        f"Prompt Domain/Category: {prompt_type}\n"
        f"Optimization Level requested: {optimization_level}\n"
        f"Primary optimization goal: {goal}\n"
        f"Now, optimize the following prompt accordingly:\n"
    )
    
    system_prompt = base_system + run_context
    optimized_text = run_llm_call(
        provider=provider,
        api_key=api_key,
        model_name=model_name,
        system_prompt=system_prompt,
        user_prompt=raw_prompt
    )
    
    return optimized_text.strip()
