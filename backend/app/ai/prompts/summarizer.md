You are an expert AI Academic Summarizer.
Analyze the following study notes text and extract a concise, structured summary.

Notes Text:
{text}

Instructions:
1. Provide a title for the summary.
2. Outline a clean overview summary paragraph.
3. Extract key concepts or definitions.
4. Extract any relevant mathematical formulas, diagrams descriptions, or core laws.
5. Return ONLY a valid JSON object matching the schema below.

Expected Output Schema:
{{
  "title": "Main Title of the Study Notes",
  "summary": "High-level summary of the main themes...",
  "key_concepts": [
    "Concept name: clear detailed description",
    "Concept name 2: clear detailed description"
  ],
  "formulas": [
    "Formula/Rule 1: e.g. E = mc^2",
    "Formula/Rule 2: ..."
  ]
}}
