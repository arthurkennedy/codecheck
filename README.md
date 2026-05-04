# 🏥 CodeCheck AI — Healthcare Coding Validation Assistant (MVP)

CodeCheck AI is a lightweight, AI-powered healthcare coding validation assistant. It analyzes clinical notes or claim data to identify missing or incorrect medical codes and suggests corrections with clear explanations.

This MVP uses a Retrieval-Augmented Generation (RAG) approach to simulate intelligent medical coding validation using a small curated dataset.

---

## 🚀 Features

* 📝 Input clinical notes or claim data
* 🔍 Detect potential coding issues
* 💡 Suggest ICD/CPT codes
* 📖 Provide clear explanations for each suggestion
* ⚡ Fast, interactive Streamlit interface
* 🧠 RAG-based AI reasoning (retrieval + LLM)

---

## 🧱 Tech Stack

* **Python**
* **Streamlit** (UI)
* **OpenAI API** (LLM + embeddings)
* **FAISS / in-memory vector search**
* **JSON dataset** (coding guidelines)

---

## 📁 Project Structure

```
.
├── app.py                     # Main Streamlit application
├── data/
│   └── coding_guidelines.json # Small dataset of ICD/CPT codes
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. User enters a clinical note or claim text
2. The app:

   * Converts input into embeddings
   * Retrieves relevant coding guidelines
   * Sends context + input to the LLM
3. The model returns structured JSON:

   * Issues detected
   * Suggested codes
   * Explanations
4. Results are displayed in the UI

---

## 🧪 Example Use Case

**Input:**

> Patient presents with type 2 diabetes and high blood pressure for routine follow-up.

**Output:**

* Missing ICD code for diabetes (E11.9)
* Missing ICD code for hypertension (I10)
* Suggested CPT code for outpatient visit (99213)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/codecheck-ai.git
cd codecheck-ai
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_api_key_here
```

Or export manually:

```bash
export OPENAI_API_KEY=your_api_key_here   # Mac/Linux
set OPENAI_API_KEY=your_api_key_here      # Windows
```

---

### 5. Run the Application

```bash
streamlit run app.py
```

---

### 6. Open in Browser

Streamlit will automatically open a browser window.
If not, go to:

```
http://localhost:8501
```

---

## 📊 Sample Data

The app uses a small curated dataset located at:

```
data/coding_guidelines.json
```

This includes:

* ICD codes (diagnoses)
* CPT codes (procedures)
* Descriptions and usage notes

---

## ⚠️ Limitations (MVP)

* Uses a small, non-exhaustive dataset
* Not medically certified or production-ready
* CPT data may be simplified due to licensing constraints
* AI outputs may not always be fully accurate

---

## 🔮 Future Improvements

* Fine-tuned medical coding model
* Larger and more comprehensive datasets
* Integration with EHR systems
* Real-time validation workflows
* User authentication and history tracking

---

## 📌 Disclaimer

This tool is for demonstration and educational purposes only.
It should not be used for real medical billing or clinical decision-making.

---

## 👨‍💻 Author

Arthur A. Kennedy

---

## ⭐ Contributing

Contributions, ideas, and feedback are welcome!
Feel free to open an issue or submit a pull request.

---

## 📄 License

MIT License
