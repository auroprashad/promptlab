import os
from huggingface_hub import InferenceClient, get_token

SYSTEM_PROMPT = """You are a helpful, world-class Prompt Engineering Assistant.
Your goal is to help the user design, refine, optimize, and critique prompts to get the best possible results from Large Language Models (LLMs).

When the user provides a prompt, you should:
1. RESTORE/RESTURCTURE the prompt using elite prompt engineering frameworks (specifying clear Role, Objective, Context, Constraints, and Instructions).
2. Present the optimized prompt clearly inside a markdown code block so they can copy it easily.
3. Briefly explain the key changes/improvements you made (e.g. why you added specific constraints or clarified the instructions) so they can learn.

Be conversational, professional, and clear. If they ask follow-up questions or want to adjust the prompt, iterate with them dynamically."""

def run_chat_completion(messages: list) -> str:
    """Runs conversational completion on Qwen 72B using default HF serverless token."""
    model_name = "Qwen/Qwen2.5-72B-Instruct"
    
    # Auto-resolve token from environment or local auth caches
    token = get_token()
    client = InferenceClient(model=model_name, token=token)
    
    # Inject system instruction as first message
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
                        "Please configure a Space Secret named 'HF_TOKEN' with the 'Make calls to Inference Providers' scope enabled."
                    )
                raise e
            time.sleep(2)
