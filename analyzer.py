from optimizer import run_llm_call, load_system_prompt
from scorer import PromptScorer

def analyze_prompt(
    raw_prompt: str,
    provider: str,
    api_key: str,
    model_name: str
) -> dict:
    """
    Evaluates the input prompt using the auditor system instructions.
    Returns a dictionary of scores (0-100) and lists of critiques/weaknesses.
    """
    if not raw_prompt.strip():
        return {
            "clarity": 0,
            "specificity": 0,
            "structure": 0,
            "context": 0,
            "constraints": 0,
            "overall": 0,
            "weaknesses": ["No prompt provided."],
            "suggestions": ["Please enter a prompt in the input area to analyze."]
        }

    system_prompt = load_system_prompt("analyzer.txt")
    user_prompt = f"Analyze the following prompt and return scores in valid JSON format:\n\n{raw_prompt}"

    try:
        raw_analysis = run_llm_call(
            provider=provider,
            api_key=api_key,
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        return PromptScorer.parse_analyzer_output(raw_analysis)
    except Exception as e:
        # Gracefully handle API errors and return safe defaults with error feedback
        error_msg = str(e)
        return {
            "clarity": 50,
            "specificity": 50,
            "structure": 50,
            "context": 50,
            "constraints": 50,
            "overall": 50,
            "weaknesses": [
                f"Evaluation interrupted: {error_msg[:100]}"
            ],
            "suggestions": [
                "Verify your API Key and Network connectivity.",
                "Ensure your model selector is compatible with the selected API provider."
            ]
        }
