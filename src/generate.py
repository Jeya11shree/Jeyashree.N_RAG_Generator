from dotenv import load_dotenv
load_dotenv()
import os, json, logging, re
from guardrails import sanitize

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USE_GROQ = bool(GROQ_API_KEY)
logger = logging.getLogger(__name__)

if USE_GROQ:
    from groq import Groq
else:
    print("GROQ_API_KEY not set! Cannot generate.")

def generate(query: str, evidence_chunks):
    if not evidence_chunks:
        return {
            "output_json": [{
                "status": "insufficient_evidence",
                "message": "No relevant documentation found. Please add files.",
                "clarifying_questions": [
                    "What information are you seeking?",
                    "Do you have more relevant documents to upload?"
                ]
            }],
            "status": "insufficient_evidence"
        }
    avg_score = sum(c.get("score", 0) for c in evidence_chunks) / len(evidence_chunks)
    if avg_score < 0.2:
        return {
            "output_json": [{
                "status": "low_confidence",
                "message": f"Evidence too weak (avg score: {avg_score:.2f}).",
                "clarifying_questions": [
                    "Can you upload more complete docs/examples?",
                    "Which specific aspect are you inquiring about?"
                ]
            }],
            "status": "low_confidence"
        }
    prompt = _build_json_prompt(query, evidence_chunks)
    try:
        if not USE_GROQ:
            return {
                "output_json": [{
                    "status": "error",
                    "message": "GROQ_API_KEY missing, cannot generate."
                }],
                "status": "error"
            }
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        "You are a QA Engineer. Answer ONLY using the evidence. "
                        "ALWAYS output ALL test/use cases as a SINGLE JSON ARRAY, with objects containing: "
                        "'Use Case Title', 'Goal', 'Preconditions', 'Test Data', 'Steps', 'Expected Results', 'Negative cases', 'Boundary cases'. "
                        "If you can't answer, output a single object with 'status', 'clarifying_questions'."
                    )
                },
                { 'role': 'user', 'content': prompt }
            ],
            temperature=0.1,
            max_tokens=1800,
            top_p=0.92
        )
        output = response.choices[0].message.content.strip()
        arr = _extract_json_array(output)
        result = json.loads(arr)
        return {
            "output_json": result,
            "status": "success",
            "model_used": "llama-3.3-70b-versatile",
            "avg_evidence_score": round(avg_score, 3),
            "evidence_summary": [
                {
                    'source': c.get('source'),
                    'score': round(c.get('score', 0), 3),
                    'snippet': c.get('text', '')[:120] + '...'
                }
                for c in evidence_chunks[:5]
            ]
        }
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {
            "output_json": [{
                "status": "error",
                "message": "LLM/generation error.",
                "raw_exception": str(e)
            }],
            "status": "error"
        }

def _build_json_prompt(query: str, chunks):
    ctx = ""
    for i, c in enumerate(chunks, 1):
        ctx += f"[{i}] {sanitize(c['text'])}\n"
    return f"CONTEXT:\n{ctx}\nQUERY: {query}\n\nOUTPUT JSON AS A SINGLE ARRAY BELOW:"

def _extract_json_array(text: str):
    # Find the first JSON array in the text
    arr = re.search(r"(\[\s*{[\s\S]+}\s*\])", text)  
    if arr:
        return arr.group(1)
    # Fallback: try any text between []
    start, end = text.find("["), text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    # Fallback: wrap {...}{...} as array
    objects = re.findall(r'({.*?})', text, re.DOTALL)
    if len(objects) > 1:
        return "[" + ",".join(objects) + "]"
    elif objects:
        return objects[0]
    return text