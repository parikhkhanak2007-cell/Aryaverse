import os
import re
import html
import ast
import asyncio
from pathlib import Path

from strands import Agent
from strands.models.ollama import OllamaModel
import edge_tts


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b",
)


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

LANGUAGES = {
    "en": {"name": "English", "voice": "en-IN-NeerjaNeural"},
    "hi": {"name": "हिन्दी", "voice": "hi-IN-SwaraNeural"},
    "gu": {"name": "ગુજરાતી", "voice": "gu-IN-DhwaniNeural"},
    "mr": {"name": "मराठी", "voice": "mr-IN-AarohiNeural"},
    "bn": {"name": "বাংলা", "voice": "bn-IN-TanishaaNeural"},
    "ta": {"name": "தமிழ்", "voice": "ta-IN-PallaviNeural"},
    "te": {"name": "తెలుగు", "voice": "te-IN-ShrutiNeural"},
    "kn": {"name": "ಕನ್ನಡ", "voice": "kn-IN-SapnaNeural"},
    "ml": {"name": "മലയാളം", "voice": "ml-IN-SobhanaNeural"},
    "pa": {"name": "ਪੰਜਾਬੀ", "voice": "pa-IN-VaaniNeural"},
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):
    """Convert stored story HTML / escaped text into plain text."""

    if value is None:
        return ""

    text = str(value)

    # HTML line breaks / paragraphs
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.IGNORECASE)

    # Remove all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode entities such as &amp;
    text = html.unescape(text)

    # Convert literal escaped newlines
    text = text.replace("\\r\\n", "\n")
    text = text.replace("\\n", "\n")

    # Normalize spaces without destroying paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# STRANDS RESPONSE EXTRACTION
# ============================================================

def _extract_from_value(value):
    """Recursively extract human-readable text from Strands values."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        # Direct text block
        direct = value.get("text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        # Standard message structure: content -> [{text: ...}]
        content = value.get("content")
        if content is not None:
            extracted = _extract_from_value(content)
            if extracted:
                return extracted

        # Some result structures expose output
        output = value.get("output")
        if output is not None:
            extracted = _extract_from_value(output)
            if extracted:
                return extracted

        # Some structures expose message
        message = value.get("message")
        if message is not None:
            extracted = _extract_from_value(message)
            if extracted:
                return extracted

        return ""

    if isinstance(value, (list, tuple)):
        parts = []
        for item in value:
            extracted = _extract_from_value(item)
            if extracted:
                parts.append(extracted)
        return "\n".join(parts).strip()

    return ""


def extract_agent_text(result):
    """Return only the model text, never the raw Strands message object."""

    if result is None:
        return ""

    if isinstance(result, str):
        raw = result.strip()
    else:
        raw = ""

    # Best path: AgentResult.message -> content -> text
    message = getattr(result, "message", None)
    extracted = _extract_from_value(message)
    if extracted:
        return extracted.strip()

    # Some versions expose output directly
    output = getattr(result, "output", None)
    extracted = _extract_from_value(output)
    if extracted:
        return extracted.strip()

    # Handle a plain dict result
    extracted = _extract_from_value(result)
    if extracted:
        return extracted.strip()

    # AgentResult.__str__ may already be the clean answer
    if raw:
        # Do not return a raw Python-looking Strands message.
        if raw.startswith("{") and ("'role'" in raw or "'content'" in raw):
            try:
                parsed = ast.literal_eval(raw)
                extracted = _extract_from_value(parsed)
                if extracted:
                    return extracted.strip()
            except (ValueError, SyntaxError):
                pass

        return raw

    return ""


# ============================================================
# OLLAMA AGENT
# ============================================================

def create_agent():
    model = OllamaModel(
        host=OLLAMA_HOST,
        model_id=OLLAMA_MODEL,
        temperature=0.2,
        top_p=0.9,
        keep_alive="10m",
    )

    return Agent(
        model=model,
        callback_handler=None,
    )


# ============================================================
# TRANSLATION
# ============================================================

def translate_story(text, language_code):
    """Translate a folk story and return a clean response dictionary."""

    language_code = str(language_code or "en").strip().lower()

    if language_code not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language_code}")

    source_text = clean_text(text)

    if not source_text:
        raise ValueError("Story text is empty.")

    language_name = LANGUAGES[language_code]["name"]

    if language_code == "en":
        return {
            "text": source_text,
            "language": language_name,
            "language_code": language_code,
            "provider": "original",
        }

    prompt = f"""
You are Aryaverse Translation AI.

Translate the COMPLETE Indian folk story below from English into {language_name}.

Rules:
- Translate every part of the story.
- Do not summarize.
- Do not shorten.
- Do not add facts.
- Preserve names and cultural terms.
- Preserve the emotional meaning.
- Keep paragraph breaks where possible.
- Return ONLY the translated story.
- Do not return JSON.
- Do not return metadata.
- Do not return role/content fields.

ORIGINAL STORY:

{source_text}
"""

    try:
        result = create_agent()(prompt)
        translated = extract_agent_text(result)

        if not translated:
            raise RuntimeError("Translation returned empty text.")

        return {
            "text": clean_text(translated),
            "language": language_name,
            "language_code": language_code,
            "provider": "ollama",
        }

    except Exception as exc:
        print("ARYAVERSE TRANSLATION ERROR:", repr(exc))
        raise RuntimeError(
            "AI translation is currently unavailable."
        ) from exc


# ============================================================
# EDGE TTS
# ============================================================

async def _generate_audio_async(text, voice, output_path):
    source_text = clean_text(text)

    if not source_text:
        raise ValueError("Text for narration is empty.")

    communicator = edge_tts.Communicate(
        source_text,
        voice,
    )

    await communicator.save(output_path)


def _run_async(coro):
    """Run an async coroutine safely from normal Flask code."""

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # If called from a context that already has an event loop,
    # use a separate thread with its own event loop.
    import concurrent.futures

    def runner():
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(runner).result()


def synthesize_speech(text, language_code, output_path):
    """Create an MP3 with Edge TTS and return the created file path."""

    language_code = str(language_code or "en").strip().lower()

    if language_code not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language_code}")

    if not output_path:
        raise ValueError("Output path is required for TTS.")

    voice = LANGUAGES[language_code]["voice"]

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("ARYAVERSE TTS LANGUAGE:", language_code)
    print("ARYAVERSE TTS VOICE:", voice)
    print("ARYAVERSE TTS OUTPUT:", output_file)

    try:
        _run_async(
            _generate_audio_async(
                text,
                voice,
                str(output_file),
            )
        )
    except Exception as exc:
        print("ARYAVERSE EDGE TTS ERROR:", repr(exc))
        raise RuntimeError(
            f"TTS generation failed: {exc}"
        ) from exc

    if not output_file.exists():
        raise RuntimeError("TTS completed but the MP3 file was not created.")

    if output_file.stat().st_size < 1000:
        raise RuntimeError("Generated MP3 is unexpectedly small.")

    print(
        "ARYAVERSE TTS COMPLETE:",
        output_file.stat().st_size,
        "bytes",
    )

    return str(output_file)


# ============================================================
# STORY AI
# ============================================================

def ask_story_ai(*args):
    """Answer a question using only the supplied story.

    Supports both:
      ask_story_ai(story_text, question)
    and:
      ask_story_ai(story_title, story_text, question)
    """

    if len(args) == 2:
        story_title = "Folk Story"
        story_text, question = args
    elif len(args) == 3:
        story_title, story_text, question = args
    else:
        raise TypeError(
            "ask_story_ai expects (story_text, question) "
            "or (story_title, story_text, question)."
        )

    story_title = clean_text(story_title)
    story_text = clean_text(story_text)
    question = clean_text(question)

    if not question:
        raise ValueError("Question is empty.")

    if not story_text:
        raise ValueError("Story text is empty.")

    prompt = f"""
You are Aryaverse Story AI.

Help a visitor understand this folk story.

STORY TITLE:
{story_title}

FOLK STORY:
{story_text}

VISITOR QUESTION:
{question}

Rules:
- Answer only from the story.
- Do not invent facts.
- Do not add historical information not contained in the story.
- Be respectful of Indian cultural traditions.
- Keep the answer concise but useful.
- If the answer is not present, say that the story does not provide that information.
- Return ONLY the answer text.
- Do not return JSON.
- Do not return metadata.
- Do not return role/content fields.
"""

    try:
        result = create_agent()(prompt)
        answer = extract_agent_text(result)

        if not answer:
            raise RuntimeError("The AI returned an empty answer.")

        return {
            "answer": clean_text(answer),
        }

    except Exception as exc:
        print("ARYAVERSE STORY AI ERROR:", repr(exc))
        raise RuntimeError(
            "The story assistant is currently unavailable."
        ) from exc


# ============================================================
# HEALTH CHECK
# ============================================================

def check_ai_health():
    try:
        result = create_agent()("Reply with exactly: OK")
        response = extract_agent_text(result)
        return {
            "status": "ok",
            "model": OLLAMA_MODEL,
            "response": response,
        }
    except Exception as exc:
        return {
            "status": "error",
            "model": OLLAMA_MODEL,
            "error": str(exc),
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ARYAVERSE AI SERVICE")
    print("=" * 60)
    print("Ollama host :", OLLAMA_HOST)
    print("Ollama model:", OLLAMA_MODEL)
    print("Languages   :", ", ".join(LANGUAGES.keys()))
    print("=" * 60)
