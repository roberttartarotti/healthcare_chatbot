Healthcare Assistant
====================

A LangGraph multi-agent healthcare assistant (hobby project, no medical value).

.. warning::

   This is a personal, homemade hobby project built only to demonstrate a
   LangGraph multi-agent system. It has no medical value, was not reviewed by any
   medical professional, and must not be used for any health-related decision.

A supervisor orchestrator routes each turn to a specialist agent (medication,
conditions, nutrition, fitness, or general). Each specialist answers using free,
no-registration open health APIs. A knowledge-base agent backed by a local vector
database is used as a last resort when no specialist can answer. Input and output
guardrails and a mandatory disclaimer keep the assistant safe.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api
