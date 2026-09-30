# 📚 Online Study Hub (StudyHub)

A full-stack, high-performance web platform built with **Python (Flask)**, **SQLite3**, **HTML5**, **Modern CSS3**, and **Vanilla JavaScript (ES6+)**.

---

## 🌟 Key Features

1. **⏱️ Flow Pomodoro Focus Sanctuary**:
   - Customizable 25m Focus, 5m Short Break, and 15m Long Break intervals with circular animated SVG progress indicator.
   - Built-in **Web Audio API Ambient Synthesizer** (Gentle Rain, Warm Lo-Fi, White Noise, Deep Waves) generated natively in the browser without external streaming files.
   - Harmonic audio bell chime upon session completion.
   - Automatic study time tracking synced to user profile.

2. **🗂️ 3D Interactive Flashcards with Spaced Repetition**:
   - 3D flip card animations on click or `Spacebar`.
   - Self-grading recall ratings (*Easy*, *Medium*, *Hard*) with progress bars and deck shuffling.
   - Pre-loaded decks for **Python Mastery**, **Data Structures & Algorithms**, **Calculus**, and **Full-Stack Web Dev**.
   - Custom deck and flashcard creator.

3. **📝 Practice Quizzes & Timed Knowledge Checks**:
   - Timed multiple-choice evaluations with live countdown timer.
   - Instant automated grading with percentage calculation and pass/fail badges.
   - Comprehensive solution breakdown with explanations for every question.

4. **👥 Virtual Study Rooms & Collaborative Hub**:
   - Collaborative study rooms with active participant count and shared sound atmosphere.
   - **Interactive HTML5 Canvas Whiteboard**: Draw diagrams, adjust brush thickness, switch colors, erase, clear, and download scratchpad notes as PNG.
   - Live room discussion chat with real-time peer messaging.

5. **📖 STEM Curated Resource Library**:
   - Detailed guides, notes, and cheat sheets across Computer Science, Mathematics, Physics, Data Science, and Web Development.
   - Filter by subject, format (*Full Guide*, *Cheat Sheet*, *Study Notes*), and difficulty.
   - Download study guides as Markdown files (`.md`).
   - Personal bookmarking system.
   - Form for students to contribute and publish their own study notes.

6. **📅 Daily Study Planner & To-Do Tracker**:
   - Priority-based task manager with Pomodoro estimation counters (🍅).
   - Instant toggle completion and daily velocity progress meter.

7. **💬 Community Forum & Q&A Board**:
   - Ask homework and coding questions, post answers, and upvote insightful solutions.
   - Categorized by subject with searchable tags.

8. **🤖 EduBot AI Study Assistant**:
   - Built-in study mentor available globally on every page via a floating drawer widget.
   - Provides concept explanations, Python code examples, mathematical derivations, and study habit protocols.

9. **👤 Student Dashboard & Profile**:
   - Real-time study statistics: total study hours, weekly goal progress bar, daily consistency streak (🔥), completed tasks, and quiz scores.
   - 1-Click Instant Demo Login or custom account registration.
   - Dark / Light mode toggle with persistent state.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- `pip` package manager

### 1. Installation
Install the dependencies:
```bash
python -m pip install -r requirements.txt
```

### 2. Initialize Database & Seed Content
The SQLite database (`study_hub.db`) is automatically initialized and pre-seeded with sample courses, quizzes, flashcards, rooms, and discussion threads upon first launch. You can also run:
```bash
python database.py
```

### 3. Run the Web Application
Double-click `run.bat` on Windows, or run:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Account Credentials

You can test all user features immediately using the **1-Click Demo** button in the navbar or with these credentials:
- **Username:** `alex_learner`
- **Password:** `study123`

*(You can also register your own custom account at `/register`)*

---

## 📁 Project Architecture

```
atharva/
├── app.py                     # Flask application routes, REST APIs, and auth
├── database.py                # SQLite schema definition and comprehensive seed data
├── models.py                  # Database queries and data access layer
├── requirements.txt           # Dependencies (Flask, Werkzeug)
├── run.bat                    # 1-Click Windows execution script
├── README.md                  # Project documentation
├── static/
│   ├── css/
│   │   ├── style.css          # Design system, themes (dark/light), layout, cards
│   │   └── components.css     # Pomodoro, Flashcard 3D, Whiteboard, Quiz, EduBot
│   └── js/
│       ├── main.js            # Theme toggle, bookmarks, toasts, upvotes
│       ├── pomodoro.js        # Pomodoro timer & Web Audio synthesizer
│       ├── flashcards.js      # 3D card flip & spaced repetition ratings
│       ├── quiz.js            # Quiz runner, countdown timer, scoring engine
│       ├── room.js            # HTML5 Canvas whiteboard & live room chat
│       └── assistant.js       # EduBot interactive study assistant widget
└── templates/
    ├── base.html              # Base HTML layout with navbar, footer, EduBot drawer
    ├── index.html             # Homepage / hero landing page
    ├── dashboard.html         # User study dashboard & analytics
    ├── resources.html         # Curated resource library & filter catalog
    ├── resource_detail.html   # Markdown study guide reader & downloads
    ├── new_resource.html      # Contribute study guide form
    ├── pomodoro.html          # Flow Pomodoro focus sanctuary
    ├── flashcards.html        # Flashcard decks catalog
    ├── flashcard_study.html   # Active 3D flashcard study mode
    ├── quizzes.html           # Quiz assessments catalog
    ├── quiz_runner.html       # Active timed quiz runner
    ├── rooms.html             # Virtual study rooms catalog
    ├── room_detail.html       # Live room with whiteboard & chat
    ├── planner.html           # Daily study planner & task tracker
    ├── community.html         # Discussion forum & Q&A
    ├── community_detail.html  # Discussion topic & verified answers
    ├── new_topic.html         # Ask a question form
    ├── login.html             # Sign in with 1-click demo option
    ├── register.html          # User registration
    └── profile.html           # Learner profile settings & study goal calibrator
```
