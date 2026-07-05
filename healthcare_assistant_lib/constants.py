"""Project-wide constants — most importantly, the mandatory disclaimer.

This is a personal, homemade hobby project. The single most important thing this
package does is make sure the disclaimer below is shown before anything else. It
is prepended to the first reply of every conversation (see `service.py`) and is
also enforced on structured output by the safety guardrail.
"""

DISCLAIMER = (
    "⚠️ PLEASE READ FIRST\n"
    "This is a personal, homemade hobby project built only to demonstrate one "
    "possible application of a LangGraph multi-agent system. It has NO medical "
    "value whatsoever. No doctor, clinician, or medical professional was involved "
    "in building or reviewing it. Nothing it says is medical advice, a diagnosis, "
    "or a treatment recommendation, and it must NOT be used as a reference for any "
    "health-related decision. Always consult a qualified healthcare professional. "
    "In an emergency, call your local emergency number immediately."
)

EMERGENCY_MESSAGE = (
    "This may be a medical emergency. Please stop and call your local emergency "
    "number now (for example 112 in the EU, 911 in the US, 192 for SAMU in Brazil), "
    "or go to the nearest emergency department. This project cannot help with "
    "emergencies and is not a substitute for professional care."
)
