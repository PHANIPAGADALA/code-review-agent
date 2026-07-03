# Autonomous Code Review & Bug Fix Agent
### Powered by Groq + LLaMA 3.1 and Genetic Algorithms

## 📌 Overview
An AI-powered autonomous agent that detects bugs in Python code, evolves fixes using a Genetic Algorithm, validates the fixes, and generates a detailed PDF report — all in a Streamlit web UI.

## ✨ Features
- 🐛 **Bug Detection** — Detects bugs using Groq LLaMA 3.1 AI model
- 🧬 **Genetic Algorithm Fix Evolution** — Evolves the best fix over 3 generations
- 🧠 **Memory System** — Recalls similar fixes from past sessions
- ✅ **Fix Validator** — Validates syntax and scores the quality of each fix
- 📄 **PDF Report Generator** — Downloads a full code review report as PDF
- 🌐 **Streamlit UI** — Clean and interactive web interface

## 🛠️ Tech Stack
| Technology | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web UI |
| Groq API | AI inference (fast LLaMA 3.1) |
| LLaMA 3.1 8B Instant | Bug detection & fix generation |
| Genetic Algorithm | Fix evolution (no external library) |
| fpdf2 | PDF report generation |
| difflib | Code diff generation |
| JSON | Memory storage |

## 📁 Project Structure
```
code-review-agent/
│
├── app.py            # Main Streamlit UI
├── detector.py       # Bug detection using Groq + LLaMA
├── ga_engine.py       # Genetic Algorithm for fix evolution
├── validator.py       # Fix syntax validation & scoring
├── memory.py           # Local JSON memory for past fixes
├── report.py            # Markdown + PDF report generator
├── requirements.txt     # Dependencies
└── README.md            # Project documentation
```

## ⚙️ Installation

**1. Clone the repository**
```
git clone https://github.com/PHANIPAGADALA/code-review-agent.git
cd code-review-agent
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Get your Groq API Key**
- Go to console.groq.com
- Sign up and create a free API key

**4. Run the app**
```
streamlit run app.py
```

**5. Enter API Key in sidebar**
- Open http://localhost:8501
- Paste your Groq API Key in the sidebar

## 🚀 How to Use
1. Go to **Code Input** tab — paste your Python code or load a sample
2. Click **Start Analysis** — AI detects all bugs
3. Go to **Bug Detection** tab — see bugs with severity levels
4. Go to **Fix Evolution** tab — click **Evolve Fixes** to run the Genetic Algorithm
5. Go to **Results & Report** tab — download your PDF report

## 🧬 How the Genetic Algorithm Works
1. Generate 4 fix candidates using LLaMA 3.1
2. Score each candidate (syntax + line count + character count)
3. Keep top 2 (elites)
4. Crossover — combine top 2 to create a child
5. Mutate — improve child using AI
6. Repeat for 3 generations
7. Return best scoring fix

## 📊 Sample Bugs Detected
| Bug Type | Severity |
|---|---|
| Division by Zero | 🔴 High |
| File Not Closed | 🟡 Medium |
| Infinite Recursion | 🔴 High |
| Index Out of Range | 🔴 High |
| Type Error (str + int) | 🔴 High |
| Missing Return Statement | 🟡 Medium |

## 📦 Requirements
```
streamlit
groq
fpdf2
pandas
```

## 🙋 Author
**PHANIPAGADALA** — Built as an internship project using Groq + LLaMA + Genetic Algorithms

🔗 [github.com/PHANIPAGADALA/code-review-agent](https://github.com/PHANIPAGADALA/code-review-agent)

## 📄 License
This project is open source and available under the MIT License.
