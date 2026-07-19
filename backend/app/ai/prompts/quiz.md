You are an expert AI Quiz Designer.
Generate a multiple-choice practice quiz with 3 to 5 questions for the following topic:
Topic: {topic_title}
Subject: {subject_name}
Difficulty: {difficulty}

Instructions:
1. Generate 3 to 5 questions matching the difficulty of the topic.
2. For each question, provide exactly 4 options.
3. Specify the 0-indexed integer of the correct answer (answer_index).
4. Provide a clear explanation of why the correct option is right and the others are wrong.
5. Return ONLY a valid JSON object matching the schema below.

Expected Output Schema:
{{
  "questions": [
    {{
      "question": "What is the primary role of...",
      "options": [
        "Option A description",
        "Option B description",
        "Option C description",
        "Option D description"
      ],
      "answer_index": 0,
      "explanation": "This option is correct because..."
    }}
  ]
}}
