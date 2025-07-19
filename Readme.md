# 📚 Quiz Application with AI Chatbot

This is a dynamic web-based quiz application built using **Flask** (Python) for the backend and **HTML, CSS (Bootstrap)**, and **JavaScript** for the frontend.

A key feature of this application is an **integrated AI chatbot** that:
- Generates multiple-choice quizzes based on user-selected educational topics
- Evaluates user answers
- Provides concise explanations
- Displays score at the end of each quiz

---

## 🚀 Live Demo

👉 [Click here to access the deployed application](https://quiz-app-y90v.onrender.com/)

---

## ✨ Features

- ✅ **User Dashboard**: Displays available quizzes and past scores
- 🤖 **AI Quiz Chatbot**:
  - Generates 5 MCQs per quiz session
  - Supports subjects like `Science`, `History`, `Maths`, `DBMS`, etc.
  - Evaluates answers with instant feedback
  - Shows correct answers and explanations
  - Tracks user score interactively
- 📦 **Backend**: Flask REST APIs
- 🧠 **AI Integration**: Google Gemini API (gemini-2.0-flash)

---

## 🛠️ Tech Stack

| Layer         | Technology                       |
|---------------|----------------------------------|
| Backend       | Python, Flask, Flask-CORS        |
| Frontend      | HTML5, CSS3, Bootstrap, JavaScript |
| AI Model      | Google Gemini (gemini-2.0-flash) |
| Deployment    | Render                           |

---

## 🧑‍💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Vansh-22f300/Quiz_App.git
cd Quiz_App
```

### 2. Create and Activate a Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Project Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a .env File
In the project root directory, create a `.env` file and add the following:
```env
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

### 5. Run the Flask App
```bash
python app.py
```

The app will be available at: [http://127.0.0.1:5000]
