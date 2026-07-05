import json
import re

class PromptScorer:
    """
    Parses and processes scoring results from the analyzer.
    Ensures robust extraction of metrics and feedback items even with malformed LLM responses.
    """
    @staticmethod
    def parse_analyzer_output(raw_output: str) -> dict:
        """
        Parses raw text from the analyzer model.
        Attempts JSON parsing first. Falls back to Regex if JSON parsing fails.
        """
        # Clean up output (sometimes LLMs wrap JSON in ```json ... ```)
        cleaned_output = raw_output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        cleaned_output = cleaned_output.strip()

        try:
            data = json.loads(cleaned_output)
            return PromptScorer._validate_data(data)
        except json.JSONDecodeError:
            # Fallback to regex parsing if JSON is broken
            return PromptScorer._fallback_parse(raw_output)

    @staticmethod
    def _validate_data(data: dict) -> dict:
        """ Ensures all keys exist and scores are integers between 0 and 100. """
        keys = ["clarity", "specificity", "structure", "context", "constraints", "overall"]
        validated = {}
        for key in keys:
            val = data.get(key, 50)
            try:
                validated[key] = max(0, min(100, int(val)))
            except (ValueError, TypeError):
                validated[key] = 50
        
        # Parse lists
        validated["weaknesses"] = data.get("weaknesses", [])
        if not isinstance(validated["weaknesses"], list):
            validated["weaknesses"] = [str(validated["weaknesses"])]
            
        validated["suggestions"] = data.get("suggestions", [])
        if not isinstance(validated["suggestions"], list):
            validated["suggestions"] = [str(validated["suggestions"])]

        # Ensure lists are cleaned strings
        validated["weaknesses"] = [str(w).strip() for w in validated["weaknesses"] if w]
        validated["suggestions"] = [str(s).strip() for s in validated["suggestions"] if s]
        
        return validated

    @staticmethod
    def _fallback_parse(raw_output: str) -> dict:
        """ Regex parser to extract fields when LLM output is malformed. """
        default_scores = {
            "clarity": 50,
            "specificity": 50,
            "structure": 50,
            "context": 50,
            "constraints": 50,
            "overall": 50
        }

        # Try to find digits next to keys
        for key in default_scores.keys():
            match = re.search(rf'"{key}"\s*:\s*(\d+)', raw_output, re.IGNORECASE)
            if not match:
                match = re.search(rf'{key}\s*:\s*(\d+)', raw_output, re.IGNORECASE)
            if match:
                try:
                    default_scores[key] = max(0, min(100, int(match.group(1))))
                except ValueError:
                    pass

        # Try to extract weaknesses and suggestions bullet points
        weaknesses = []
        suggestions = []
        
        # Look for bullet points in text
        lines = raw_output.split('\n')
        collect_mode = None
        for line in lines:
            line_str = line.strip().lower()
            if "weakness" in line_str:
                collect_mode = "weaknesses"
                continue
            elif "suggestion" in line_str or "recommend" in line_str:
                collect_mode = "suggestions"
                continue
            
            # If line starts with a bullet point
            if line.strip().startswith(("-", "*", "•", "1.", "2.", "3.")):
                clean_bullet = re.sub(r'^[-*•\d\.\s]+', '', line.strip())
                if clean_bullet:
                    if collect_mode == "weaknesses":
                        weaknesses.append(clean_bullet)
                    elif collect_mode == "suggestions":
                        suggestions.append(clean_bullet)

        # Fallback values if nothing extracted
        if not weaknesses:
            weaknesses = ["Prompt analysis encountered parsing errors, check layout consistency."]
        if not suggestions:
            suggestions = ["Ensure the prompt structure is clearly demarcated with headers or bullet points."]

        default_scores["weaknesses"] = weaknesses
        default_scores["suggestions"] = suggestions
        return default_scores
