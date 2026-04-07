"""Computer vision features using Claude Vision API."""

from __future__ import annotations

import json

import anthropic

MODEL = "claude-sonnet-4-20250514"


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def grade_flower_quality(image_base64: str, flower_type: str = "rose") -> dict:
    """Upload flower photo -> AI grades quality.

    Returns: {grade, confidence, details: {stem_straightness, petal_condition,
    color_vibrancy, blemishes, stem_length_estimate_cm}, recommendations}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64,
                    },
                },
                {
                    "type": "text",
                    "text": f"""Analiza esta imagen de una flor ({flower_type}) para grading de calidad floricola.

Evalua y responde en JSON:
{{
  "grade": "export_premium|first|second|third",
  "confidence": 0.0-1.0,
  "details": {{
    "stem_straightness": 1-10,
    "petal_condition": "excellent|good|fair|poor",
    "color_vibrancy": 1-10,
    "blemish_pct": 0-100,
    "stem_length_estimate_cm": number,
    "open_stage": "bud|opening|full|past_prime"
  }},
  "recommendations": "string with specific recommendations",
  "market_suitability": "exportacion|jamaica|central_de_abasto|eventos|retail"
}}

Solo responde con JSON, sin markdown.""",
                },
            ],
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "grade": "second",
            "confidence": 0.5,
            "details": {},
            "recommendations": text,
        }


def detect_disease(image_base64: str) -> dict:
    """Photo of flower/leaf -> identifies diseases, pests, deficiencies.

    Returns: {healthy, issues: [{name, severity, affected_area_pct, description,
    treatment}], overall_risk, preventive_actions}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64,
                    },
                },
                {
                    "type": "text",
                    "text": """Analiza esta imagen de una planta/flor para detectar enfermedades, plagas o deficiencias nutricionales.

Responde en JSON:
{
  "healthy": true|false,
  "issues": [
    {
      "name": "nombre de la enfermedad/plaga",
      "type": "fungal|bacterial|viral|pest|nutrient_deficiency|environmental",
      "severity": "low|medium|high|critical",
      "affected_area_pct": 0-100,
      "description": "descripcion detallada",
      "treatment": "tratamiento recomendado especifico",
      "urgency": "immediate|this_week|this_month|monitor"
    }
  ],
  "overall_risk": "low|medium|high|critical",
  "preventive_actions": ["accion 1", "accion 2"],
  "quarantine_recommended": true|false
}

Si la planta esta sana, devuelve healthy=true con issues vacio.
Solo responde con JSON, sin markdown.""",
                },
            ],
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "healthy": True,
            "issues": [],
            "overall_risk": "low",
            "preventive_actions": [],
            "raw": text,
        }
