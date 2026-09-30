import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db
import models

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'study_hub_production_grade_secret_key_2026')

# Initialize DB on start
with app.app_context():
    init_db()

# Global Context Processor
@app.context_processor
def inject_global_data():
    current_user = None
    user_id = session.get('user_id')
    if user_id:
        current_user = models.get_user_by_id(user_id)
        if not current_user:
            session.pop('user_id', None)
    
    platform_stats = models.get_platform_stats()
    return {
        'current_user': current_user,
        'platform_stats': platform_stats,
        'app_name': 'StudyHub',
        'subjects_list': [
            'Computer Science', 'Mathematics', 'Physics', 'Data Science', 
            'Web Development', 'Engineering', 'Literature', 'General Study'
        ]
    }

# ----------------- Auth Routes -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = models.get_user_by_username(username)
        if not user:
            user = models.get_user_by_email(username)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['full_name'] or user['username']}! Ready to conquer your study goals?", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username/email or password. Hint: You can use demo account (alex_learner / study123).", 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '').strip()

        if len(username) < 3:
            flash("Username must be at least 3 characters.", 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters.", 'error')
            return render_template('register.html')

        if models.get_user_by_username(username):
            flash("Username is already taken. Please choose another.", 'error')
            return render_template('register.html')

        if models.get_user_by_email(email):
            flash("An account with this email already exists.", 'error')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        user_id = models.create_user(username, email, password_hash, full_name)
        session['user_id'] = user_id
        session['username'] = username
        flash("Welcome to Online Study Hub! Your study space is ready.", 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out. Great work today!", 'info')
    return redirect(url_for('index'))

@app.route('/demo-login')
def demo_login():
    user = models.get_user_by_username('alex_learner')
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Logged in as Demo User ({user['full_name']})! Enjoy exploring all features.", 'success')
    return redirect(url_for('dashboard'))

# ----------------- Main Landing & Dashboard -----------------
@app.route('/')
def index():
    featured_resources = models.get_all_resources()[:4]
    decks = models.get_all_decks()[:3]
    quizzes = models.get_all_quizzes()[:3]
    rooms = models.get_all_rooms()[:3]
    return render_template('index.html', 
                           featured_resources=featured_resources,
                           decks=decks,
                           quizzes=quizzes,
                           rooms=rooms)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_stats = models.get_user_stats(user_id)
    recent_tasks = models.get_user_tasks(user_id)[:5]
    quiz_results = models.get_user_quiz_results(user_id)[:4]
    bookmarked_resources = models.get_user_bookmarks(user_id)[:4]
    active_rooms = models.get_all_rooms()[:3]

    return render_template('dashboard.html',
                           stats=user_stats,
                           tasks=recent_tasks,
                           quiz_results=quiz_results,
                           bookmarks=bookmarked_resources,
                           active_rooms=active_rooms)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = models.get_user_by_id(user_id)
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        bio = request.form.get('bio', '').strip()
        study_goal_hours = int(request.form.get('study_goal_hours', 20))
        avatar = request.form.get('avatar', user['avatar'])

        models.update_user_profile(user_id, full_name, bio, study_goal_hours, avatar)
        flash("Profile updated successfully!", 'success')
        return redirect(url_for('profile'))

    user_stats = models.get_user_stats(user_id)
    return render_template('profile.html', user=user, stats=user_stats)

# ----------------- Resource Library -----------------
@app.route('/resources')
def resources():
    subject = request.args.get('subject', 'All')
    category = request.args.get('category', 'All')
    difficulty = request.args.get('difficulty', 'All')
    search = request.args.get('search', '').strip()

    all_res = models.get_all_resources(subject=subject, category=category, difficulty=difficulty, search=search)
    return render_template('resources.html',
                           resources=all_res,
                           selected_subject=subject,
                           selected_category=category,
                           selected_difficulty=difficulty,
                           search_query=search)

@app.route('/resources/<int:resource_id>')
def resource_detail(resource_id):
    resource = models.get_resource_by_id(resource_id)
    if not resource:
        flash("Resource not found.", 'error')
        return redirect(url_for('resources'))

    models.increment_resource_views(resource_id)
    user_id = session.get('user_id')
    is_saved = models.is_bookmarked(user_id, resource_id) if user_id else False
    
    # Related resources
    related = [r for r in models.get_all_resources(subject=resource['subject']) if r['id'] != resource_id][:3]

    return render_template('resource_detail.html',
                           resource=resource,
                           is_bookmarked=is_saved,
                           related=related)

@app.route('/resources/new', methods=['GET', 'POST'])
def new_resource():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to submit a study guide.", 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject = request.form.get('subject', 'Computer Science')
        category = request.form.get('category', 'Study Notes')
        difficulty = request.form.get('difficulty', 'Beginner')
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        key_takeaways = request.form.get('key_takeaways', '').strip()
        user = models.get_user_by_id(user_id)
        author = user['full_name'] or user['username']

        if not title or not content:
            flash("Title and Content are required fields.", 'error')
            return render_template('new_resource.html')

        res_id = models.create_resource(title, subject, category, difficulty, description, content, key_takeaways, author)
        flash("Study resource published to the Study Hub community!", 'success')
        return redirect(url_for('resource_detail', resource_id=res_id))

    return render_template('new_resource.html')

@app.route('/resources/<int:resource_id>/download')
def download_resource(resource_id):
    resource = models.get_resource_by_id(resource_id)
    if not resource:
        return "Resource not found", 404

    models.increment_resource_downloads(resource_id)
    content = f"""# {resource['title']}
Subject: {resource['subject']} | Category: {resource['category']} | Difficulty: {resource['difficulty']}
Author: {resource['author']}
Source: StudyHub Online Study Hub

=========================================
OVERVIEW:
{resource['description']}

KEY TAKEAWAYS:
{resource['key_takeaways']}

=========================================
CONTENT:
{resource['content']}

---
Downloaded from Online Study Hub Platform.
"""
    filename = f"{resource['title'].replace(' ', '_')[:30]}.md"
    return Response(content, mimetype="text/markdown", headers={"Content-disposition": f"attachment; filename={filename}"})

@app.route('/api/resources/<int:resource_id>/bookmark', methods=['POST'])
def api_toggle_bookmark(resource_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please login to bookmark.'}), 401
    
    state = models.toggle_bookmark(user_id, resource_id)
    return jsonify({'success': True, 'is_bookmarked': state})

# ----------------- Pomodoro Study Space -----------------
@app.route('/pomodoro')
def pomodoro():
    user_id = session.get('user_id')
    tasks = models.get_user_tasks(user_id) if user_id else []
    return render_template('pomodoro.html', tasks=tasks)

@app.route('/api/pomodoro/log', methods=['POST'])
def api_log_pomodoro():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Session saved locally (sign in to sync stats)'})

    data = request.get_json() or {}
    duration = int(data.get('duration_mins', 25))
    subject = data.get('subject', 'General Study')

    models.log_pomodoro(user_id, duration, subject)
    return jsonify({'success': True, 'message': f'Logged {duration} minutes of deep study!'})

# ----------------- Flashcards & Spaced Repetition -----------------
@app.route('/flashcards')
def flashcards():
    decks = models.get_all_decks()
    return render_template('flashcards.html', decks=decks)

@app.route('/flashcards/<int:deck_id>')
def study_deck(deck_id):
    deck = models.get_deck_by_id(deck_id)
    if not deck:
        flash("Flashcard deck not found.", 'error')
        return redirect(url_for('flashcards'))

    cards = models.get_deck_cards(deck_id)
    cards_list = [dict(c) for c in cards]
    return render_template('flashcard_study.html', deck=deck, cards=cards_list)

@app.route('/api/flashcards/deck/create', methods=['POST'])
def api_create_deck():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    title = request.form.get('title', '').strip()
    subject = request.form.get('subject', 'General Study')
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'bi-card-text')

    if not title:
        flash("Title is required for creating a deck.", 'error')
        return redirect(url_for('flashcards'))

    deck_id = models.create_deck(title, subject, description, icon)
    flash(f"Flashcard deck '{title}' created! Now add your first cards.", 'success')
    return redirect(url_for('study_deck', deck_id=deck_id))

@app.route('/api/flashcards/card/add', methods=['POST'])
def api_add_card():
    deck_id = request.form.get('deck_id')
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    hint = request.form.get('hint', '').strip()

    if deck_id and question and answer:
        models.add_flashcard(deck_id, question, answer, hint)
        flash("New flashcard added successfully!", 'success')
    else:
        flash("Question and answer are required.", 'error')

    return redirect(url_for('study_deck', deck_id=deck_id))

# ----------------- Quizzes & Knowledge Checks -----------------
@app.route('/quizzes')
def quizzes():
    all_quizzes = models.get_all_quizzes()
    user_id = session.get('user_id')
    past_results = models.get_user_quiz_results(user_id) if user_id else []
    
    # Map best score per quiz
    best_scores = {}
    for r in past_results:
        qid = r['quiz_id']
        if qid not in best_scores or r['percentage'] > best_scores[qid]['percentage']:
            best_scores[qid] = r

    return render_template('quizzes.html', quizzes=all_quizzes, best_scores=best_scores)

@app.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        flash("Quiz not found.", 'error')
        return redirect(url_for('quizzes'))

    questions = models.get_quiz_questions(quiz_id)
    q_data = []
    for q in questions:
        q_data.append({
            'id': q['id'],
            'question': q['question'],
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d'],
            'correct_option': q['correct_option'],
            'explanation': q['explanation']
        })

    return render_template('quiz_runner.html', quiz=quiz, questions=q_data)

@app.route('/api/quiz/<int:quiz_id>/submit', methods=['POST'])
def api_submit_quiz(quiz_id):
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': 'Quiz not found'}), 404

    data = request.get_json() or {}
    user_answers = data.get('answers', {}) # {question_id: 'A'/'B'/...}

    questions = models.get_quiz_questions(quiz_id)
    score = 0
    total = len(questions)
    breakdown = []

    for q in questions:
        qid = str(q['id'])
        chosen = user_answers.get(qid, '')
        is_correct = (chosen.strip().upper() == q['correct_option'].strip().upper())
        if is_correct:
            score += 1
        
        breakdown.append({
            'id': q['id'],
            'question': q['question'],
            'chosen': chosen,
            'correct': q['correct_option'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    percentage = round((score / total * 100) if total > 0 else 0, 1)
    passed = 1 if percentage >= quiz['pass_percentage'] else 0

    user_id = session.get('user_id')
    if user_id:
        models.save_quiz_result(user_id, quiz_id, score, total, percentage, passed)

    return jsonify({
        'success': True,
        'score': score,
        'total': total,
        'percentage': percentage,
        'passed': bool(passed),
        'pass_percentage': quiz['pass_percentage'],
        'breakdown': breakdown
    })

# ----------------- Virtual Study Rooms -----------------
@app.route('/rooms')
def rooms():
    all_rooms = models.get_all_rooms()
    return render_template('rooms.html', rooms=all_rooms)

@app.route('/room/<int:room_id>')
def study_room(room_id):
    room = models.get_room_by_id(room_id)
    if not room:
        flash("Study room not found.", 'error')
        return redirect(url_for('rooms'))

    messages = models.get_room_messages(room_id)
    return render_template('room_detail.html', room=room, initial_messages=messages)

@app.route('/rooms/new', methods=['POST'])
def new_room():
    name = request.form.get('name', '').strip()
    subject = request.form.get('subject', 'General Study')
    description = request.form.get('description', '').strip()
    bg_sound = request.form.get('bg_sound', 'rain')

    if name:
        r_id = models.create_study_room(name, subject, description, bg_sound)
        flash(f"Room '{name}' created! Invite your study peers.", 'success')
        return redirect(url_for('study_room', room_id=r_id))
    
    flash("Room name is required.", 'error')
    return redirect(url_for('rooms'))

@app.route('/api/room/<int:room_id>/messages', methods=['GET', 'POST'])
def api_room_messages(room_id):
    if request.method == 'POST':
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'success': False, 'message': 'Message is empty'}), 400

        user_id = session.get('user_id')
        user = models.get_user_by_id(user_id) if user_id else None
        username = user['username'] if user else (session.get('guest_name') or 'Guest Scholar')
        avatar = user['avatar'] if user else 'avatar-1'

        models.add_room_message(room_id, username, avatar, message)

        # Simulation: occasional encouraging reply from peer in room
        bot_peers = [
            ("Sophia_Code", "avatar-3", "Nice work! Keep pushing through those concepts. 💪"),
            ("Marcus_V", "avatar-2", "Great point. Focusing hard over here too!"),
            ("StudyBot", "avatar-4", "Quick tip: remember to drink water and blink frequently!")
        ]
        if random.random() < 0.25:
            peer = random.choice(bot_peers)
            models.add_room_message(room_id, peer[0], peer[1], peer[2])

        return jsonify({'success': True})

    # GET messages
    messages = models.get_room_messages(room_id)
    return jsonify({
        'messages': [{
            'id': m['id'],
            'username': m['username'],
            'avatar': m['avatar'],
            'message': m['message'],
            'created_at': m['created_at']
        } for m in messages]
    })

# ----------------- Planner & Tasks -----------------
@app.route('/planner')
def planner():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    tasks = models.get_user_tasks(user_id)
    user_stats = models.get_user_stats(user_id)
    return render_template('planner.html', tasks=tasks, stats=user_stats)

@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please login'}), 401

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject = request.form.get('subject', 'General Study')
        due_date = request.form.get('due_date', 'Today')
        priority = request.form.get('priority', 'Medium')
        pomodoro_count = int(request.form.get('pomodoro_count', 1))

        if title:
            models.add_user_task(user_id, title, subject, due_date, priority, pomodoro_count)
            flash("Study task added to your planner!", 'success')
        return redirect(url_for('planner'))

    tasks = [dict(t) for t in models.get_user_tasks(user_id)]
    return jsonify({'tasks': tasks})

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def api_toggle_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False}), 401
    
    new_status = models.toggle_user_task(task_id, user_id)
    return jsonify({'success': True, 'status': new_status})

@app.route('/api/tasks/<int:task_id>/delete', methods=['POST'])
def api_delete_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False}), 401
    
    models.delete_user_task(task_id, user_id)
    return jsonify({'success': True})

# ----------------- Community Forum & Q&A -----------------
@app.route('/community')
def community():
    category = request.args.get('category', 'All')
    search = request.args.get('search', '').strip()
    topics = models.get_community_topics(category=category, search=search)
    return render_template('community.html', topics=topics, selected_category=category, search=search)

@app.route('/community/<int:topic_id>')
def community_topic(topic_id):
    topic = models.get_community_topic(topic_id)
    if not topic:
        flash("Discussion topic not found.", 'error')
        return redirect(url_for('community'))

    replies = models.get_topic_replies(topic_id)
    return render_template('community_detail.html', topic=topic, replies=replies)

@app.route('/community/new', methods=['GET', 'POST'])
def new_topic():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to post a question.", 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Computer Science')
        tags = request.form.get('tags', '').strip()
        content = request.form.get('content', '').strip()
        user = models.get_user_by_id(user_id)

        if not title or not content:
            flash("Title and Content are required.", 'error')
            return render_template('new_topic.html')

        t_id = models.create_topic(user_id, title, category, content, user['full_name'] or user['username'], tags)
        flash("Your question has been posted to the Study Hub community!", 'success')
        return redirect(url_for('community_topic', topic_id=t_id))

    return render_template('new_topic.html')

@app.route('/api/community/<int:topic_id>/reply', methods=['POST'])
def api_reply_topic(topic_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please sign in to reply.", 'error')
        return redirect(url_for('login'))

    content = request.form.get('content', '').strip()
    if content:
        user = models.get_user_by_id(user_id)
        models.create_reply(topic_id, user_id, user['full_name'] or user['username'], user['avatar'], content)
        flash("Your answer was posted!", 'success')
    return redirect(url_for('community_topic', topic_id=topic_id))

@app.route('/api/community/<int:topic_id>/upvote', methods=['POST'])
def api_upvote_topic(topic_id):
    models.upvote_topic(topic_id)
    return jsonify({'success': True})

# ----------------- AI Study Assistant (EduBot) -----------------
@app.route('/api/ai/ask', methods=['POST'])
def api_ai_ask():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    context = data.get('context', 'general')

    if not query:
        return jsonify({'answer': 'Please ask a study question or topic you want explained!'})

    q_lower = query.lower()

    # Intelligent educational response synthesis engine
    if any(k in q_lower for k in ['python', 'decorator', 'async', 'generator', 'gil', 'lambda']):
        response_text = f"""**Python Core Concept Breakdown:**

1. **Python Philosophy**: Python balances readability with powerful high-level abstractions like list comprehensions, generators, and first-class functions.
2. **Key Insight regarding `{query}`**:
   - In Python, functions are first-class citizens. You can pass them as arguments, return them, and wrap them with decorators.
   - For memory efficiency, prefer generators (`yield`) over large lists to evaluate elements lazily.
   - For I/O concurrency, use `asyncio.gather()` to handle thousands of requests without multi-threading overhead.
3. **Quick Code Snippet**:
```python
# Practical demonstration
def memoize(fn):
    cache = {{}}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    return n if n <= 1 else fibonacci(n - 1) + fibonacci(n - 2)

print("Fibonacci 30:", fibonacci(30))
```
*Tip: Practice this in our Flashcards or Quiz section to cement your mastery!*"""

    elif any(k in q_lower for k in ['algorithm', 'big-o', 'sorting', 'tree', 'graph', 'bfs', 'dfs', 'dynamic programming']):
        response_text = f"""**Algorithms & Data Structures Strategy:**

1. **Algorithmic Complexity**:
   - Quick/Merge Sort: $O(N \\log N)$
   - Hash Table Search: $O(1)$ average
   - Binary Search: $O(\\log N)$ on sorted sequences
2. **Solving `{query}`**:
   - **Step 1**: Identify if the state can be decomposed into smaller subproblems (Optimal Substructure).
   - **Step 2**: Check for repeated overlapping computations (Memoization / Tabulation).
   - **Step 3**: Use two pointers or sliding window when dealing with contiguous sub-arrays.
3. **Recommended Study Plan**:
   - Solve 3-5 variations on StudyHub.
   - Test yourself on our 'Data Structures & Algorithms Rapid Fire' deck!"""

    elif any(k in q_lower for k in ['math', 'calculus', 'derivative', 'integral', 'matrix', 'eigen', 'linear algebra']):
        response_text = f"""**Mathematical Analysis & Intuition:**

1. **Fundamental Principle**:
   - Derivatives represent instantaneous rates of change (tangent slopes).
   - Integrals represent cumulative accumulation (area under curves).
2. **Linear Algebra Perspective**:
   - Matrices represent linear geometric transformations (rotations, scales, shears).
   - Eigenvectors represent the directions that remain invariant (only scaled by eigenvalue $\\lambda$) during the transformation:
     $$A v = \\lambda v$$
3. **Study Advice**:
   - Draw graphs to visualize functions. Check out the Calculus study guide in our Resource Library for complete step-by-step proofs!"""

    elif any(k in q_lower for k in ['pomodoro', 'focus', 'study habit', 'productivity', 'motivation', 'time management']):
        response_text = f"""**High-Performance Study Protocol:**

1. **The 25/5 Pomodoro Cycle**:
   - 25 minutes of unbroken focus on a single concept or problem.
   - Silenced phone and notifications.
   - 5-minute break: stand up, hydrate, stretch.
2. **Active Recall & Spaced Repetition**:
   - Avoid passive re-reading! Instead, test yourself with Flashcards and Quizzes right after reading a guide.
3. **Join a Virtual Room**:
   - Study accountability boosts focus by over 60%. Try joining one of our Quiet Study Rooms now!"""

    else:
        response_text = f"""**StudyHub AI Assistant Insight:**

Thank you for asking about **"{query}"**!

Here is a structured study breakdown to master this topic:
1. **Core Concept Definition**: Start by breaking `{query}` down into its fundamental 3 building blocks.
2. **Practical Application**: Apply the concept directly in code, a mathematical proof, or a real-world summary.
3. **Self-Testing**: Use the Feynman technique: explain `{query}` in simple words as if teaching a classmate.
4. **Community Discussion**: Feel free to create a discussion thread in our Community forum to discuss questions with peers!

*Need a specific code example, formula derivation, or quiz question? Just let me know!*"""

    return jsonify({'answer': response_text})

if __name__ == '__main__':
    print("🚀 Online Study Hub starting on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
