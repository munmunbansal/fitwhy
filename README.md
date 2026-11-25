# FitWhy

**Constraint-aware role matching with plain-English fit explanations.**

FitWhy goes beyond standard keyword job matching by separating what a candidate wants next from their non-negotiable dealbreakers (such as service bonds, rotational night shifts, or pure frontend roles). It strictly eliminates violating roles first, ranks the remaining opportunities, and explains *why* each match fits in plain English.

🔗 **Live Demo:** [https://YOUR_RENDER_URL](https://YOUR_RENDER_URL)

---

## Key Features
* **Hard Dealbreaker Filtering ("Veto Engine"):** Strictly excludes roles that violate user-defined constraints before ranking.
* **Schema-Enforced Structured Outputs:** Uses Pydantic models (`response_schema`) to guarantee valid, predictable JSON responses from the LLM.
* **Plain-English Fit Reasoning:** Generates concise, specific explanations linking the user's skills and goals directly to role requirements.
* **Graceful Degradation & Multi-Model Fallback:** Automatically retries across backup models during API traffic spikes (`503 UNAVAILABLE`) and falls back to a deterministic rule-and-keyword engine so the service stays online.

## Tech Stack
* **Backend:** Python, FastAPI, Uvicorn, Pydantic
* **AI / LLM:** Google GenAI SDK (`gemini-3.8-flash` / `gemini-2.0-flash` with JSON Schema enforcement)
* **Frontend:** Responsive HTML5, CSS3, Vanilla JavaScript

## Project Structure
```text
fitwhy/
├── main.py              # FastAPI server, Pydantic schemas, LLM matching & fallback engine
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── static/
    └── index.html       # Responsive two-column web interface
