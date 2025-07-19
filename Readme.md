Quiz Application with AI Chatbot
This is a dynamic web-based quiz application built with Flask (Python) for the backend and HTML, CSS (Bootstrap), and JavaScript for the frontend. A key feature of this application is an integrated AI chatbot that can generate custom multiple-choice quizzes on educational subjects and evaluate user answers with explanations.

Live Demo
Access the deployed application here:
👉 https://quiz-app-y90v.onrender.com/

Features
User Dashboard: Displays available quizzes with score summaries.

Quiz Management: Allows users to start existing quizzes or retake them.

AI Quiz Master Chatbot:

Accessible via a floating icon on the dashboard.

Generates 5 multiple-choice questions (MCQs) on a user-specified educational subject (e.g., History, Science, Mathematics).

Evaluates user answers as correct or wrong.

Provides a concise 2-line explanation for each answer.

Tracks score for the AI-generated quiz.

Restricts quiz generation to a predefined list of educational subjects.

Technologies Used
Backend: Python 3, Flask

Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript

AI Integration: Google Gemini API (gemini-2.0-flash model)

Dependency Management: pip, requirements.txt

Environment Variables: python-dotenv

HTTP Requests: requests library

CORS Handling: Flask-Cors

Local Development Setup
Follow these steps to get the application running on your local machine:

Clone the Repository:

git clone <your-repository-url>
cd quiz_app

Create a Virtual Environment (Recommended):

python -m venv venv

Activate the Virtual Environment:

Windows:

.\venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

If requirements.txt is missing or outdated, you can create it after installing the necessary packages:

pip install flask flask-cors python-dotenv requests
pip freeze > requirements.txt

Get Your Google Gemini API Key:

Go to Google AI Studio.

Create or select a project.

Generate an API key.

Create a .env File:
In the root directory of your project (the same directory as app.py), create a new file named .env.

Add Your API Key to .env:
Open the .env file and add your Gemini API key:

GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"

Important: Replace "YOUR_ACTUAL_GEMINI_API_KEY_HERE" with the key you obtained from Google AI Studio. Do not include spaces around the = sign.

Run the Flask Application:

python app.py

The application will typically run on http://127.0.0.1:5000/.

Deployment on Render
This application is designed to be easily deployed on platforms like Render.

Git Repository: Ensure your project is pushed to a Git repository (e.g., GitHub, GitLab, Bitbucket).

Crucially, make sure your .env file is NOT committed to Git. Add .env to your .gitignore file.

Ensure requirements.txt is up-to-date and committed.

Create a Web Service on Render:

Log in to your Render dashboard.

Click "New" -> "Web Service".

Connect your Git repository.

Render will automatically detect your Python project and suggest build/start commands.

Set Environment Variables on Render:

In your Render service settings, navigate to the "Environment Variables" section.

Add a new environment variable:

Key: GEMINI_API_KEY

Value: Your actual Gemini API key (the same one you put in your local .env file).

This is how Render securely provides your API key to your deployed application without hardcoding it in your code.

Deploy: Trigger a deploy from the Render dashboard. Render will build your application and make it accessible via a public URL.

Usage
Access the Dashboard: After logging in (or accessing the dashboard directly if authentication is handled elsewhere), you'll see your existing quizzes.

Open AI Chatbot: Click the floating robot icon in the bottom right corner of the screen.

Start a New Quiz: In the chatbot window, type an educational subject (e.g., "History", "Science", "Mathematics", "DBMS", "SST") into the input field and click "New Quiz".

Answer Questions: The chatbot will present 5 MCQs one by one. Select an option and click "Submit Answer".

Get Feedback: The AI will evaluate your answer and provide a 2-line explanation.

Continue/End: Click "Next Question" to proceed, or the quiz will end after 5 questions, showing your score. You can then start a new quiz.