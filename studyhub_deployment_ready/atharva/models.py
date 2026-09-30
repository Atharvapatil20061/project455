import sqlite3
from database import get_db

# ----------------- User Helpers -----------------
def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def create_user(username, email, password_hash, full_name=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name)
        VALUES (?, ?, ?, ?)
    ''', (username, email, password_hash, full_name))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_user_profile(user_id, full_name, bio, study_goal_hours, avatar):
    conn = get_db()
    conn.execute('''
        UPDATE users
        SET full_name = ?, bio = ?, study_goal_hours = ?, avatar = ?
        WHERE id = ?
    ''', (full_name, bio, study_goal_hours, avatar, user_id))
    conn.commit()
    conn.close()

def add_study_time(user_id, minutes):
    conn = get_db()
    conn.execute('''
        UPDATE users
        SET total_study_minutes = total_study_minutes + ?
        WHERE id = ?
    ''', (minutes, user_id))
    conn.commit()
    conn.close()

# ----------------- Resource Helpers -----------------
def get_all_resources(subject=None, difficulty=None, search=None, category=None):
    conn = get_db()
    query = "SELECT * FROM resources WHERE 1=1"
    params = []

    if subject and subject != 'All':
        query += " AND subject = ?"
        params.append(subject)
    if difficulty and difficulty != 'All':
        query += " AND difficulty = ?"
        params.append(difficulty)
    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR content LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " ORDER BY featured DESC, created_at DESC"
    resources = conn.execute(query, params).fetchall()
    conn.close()
    return resources

def get_resource_by_id(resource_id):
    conn = get_db()
    resource = conn.execute("SELECT * FROM resources WHERE id = ?", (resource_id,)).fetchone()
    conn.close()
    return resource

def increment_resource_views(resource_id):
    conn = get_db()
    conn.execute("UPDATE resources SET views_count = views_count + 1 WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()

def increment_resource_downloads(resource_id):
    conn = get_db()
    conn.execute("UPDATE resources SET downloads_count = downloads_count + 1 WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()

def create_resource(title, subject, category, difficulty, description, content, key_takeaways, author):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resources (title, subject, category, difficulty, description, content, key_takeaways, author)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, subject, category, difficulty, description, content, key_takeaways, author))
    conn.commit()
    res_id = cursor.lastrowid
    conn.close()
    return res_id

def toggle_bookmark(user_id, resource_id):
    conn = get_db()
    existing = conn.execute("SELECT id FROM bookmarks WHERE user_id = ? AND resource_id = ?", (user_id, resource_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM bookmarks WHERE user_id = ? AND resource_id = ?", (user_id, resource_id))
        is_bookmarked = False
    else:
        conn.execute("INSERT INTO bookmarks (user_id, resource_id) VALUES (?, ?)", (user_id, resource_id))
        is_bookmarked = True
    conn.commit()
    conn.close()
    return is_bookmarked

def is_bookmarked(user_id, resource_id):
    if not user_id:
        return False
    conn = get_db()
    row = conn.execute("SELECT id FROM bookmarks WHERE user_id = ? AND resource_id = ?", (user_id, resource_id)).fetchone()
    conn.close()
    return bool(row)

def get_user_bookmarks(user_id):
    conn = get_db()
    bookmarks = conn.execute('''
        SELECT r.* FROM resources r
        JOIN bookmarks b ON r.id = b.resource_id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return bookmarks

# ----------------- Flashcard Helpers -----------------
def get_all_decks():
    conn = get_db()
    decks = conn.execute('''
        SELECT d.*, COUNT(f.id) as card_count
        FROM flashcard_decks d
        LEFT JOIN flashcards f ON d.id = f.deck_id
        GROUP BY d.id
        ORDER BY d.created_at DESC
    ''').fetchall()
    conn.close()
    return decks

def get_deck_by_id(deck_id):
    conn = get_db()
    deck = conn.execute("SELECT * FROM flashcard_decks WHERE id = ?", (deck_id,)).fetchone()
    conn.close()
    return deck

def get_deck_cards(deck_id):
    conn = get_db()
    cards = conn.execute("SELECT * FROM flashcards WHERE deck_id = ? ORDER BY id ASC", (deck_id,)).fetchall()
    conn.close()
    return cards

def create_deck(title, subject, description, icon='bi-card-text'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flashcard_decks (title, subject, description, icon)
        VALUES (?, ?, ?, ?)
    ''', (title, subject, description, icon))
    conn.commit()
    deck_id = cursor.lastrowid
    conn.close()
    return deck_id

def add_flashcard(deck_id, question, answer, hint=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flashcards (deck_id, question, answer, hint)
        VALUES (?, ?, ?, ?)
    ''', (deck_id, question, answer, hint))
    conn.commit()
    card_id = cursor.lastrowid
    conn.close()
    return card_id

# ----------------- Quiz Helpers -----------------
def get_all_quizzes():
    conn = get_db()
    quizzes = conn.execute('''
        SELECT q.*, COUNT(qq.id) as question_count
        FROM quizzes q
        LEFT JOIN quiz_questions qq ON q.id = qq.quiz_id
        GROUP BY q.id
        ORDER BY q.created_at DESC
    ''').fetchall()
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id):
    conn = get_db()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    conn.close()
    return quiz

def get_quiz_questions(quiz_id):
    conn = get_db()
    questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY id ASC", (quiz_id,)).fetchall()
    conn.close()
    return questions

def save_quiz_result(user_id, quiz_id, score, total_questions, percentage, passed):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_results (user_id, quiz_id, score, total_questions, percentage, passed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, quiz_id, score, total_questions, percentage, passed))
    conn.commit()
    res_id = cursor.lastrowid
    conn.close()
    return res_id

def get_user_quiz_results(user_id):
    conn = get_db()
    results = conn.execute('''
        SELECT qr.*, q.title as quiz_title, q.subject
        FROM quiz_results qr
        JOIN quizzes q ON qr.quiz_id = q.id
        WHERE qr.user_id = ?
        ORDER BY qr.completed_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return results

# ----------------- Task / Planner Helpers -----------------
def get_user_tasks(user_id):
    conn = get_db()
    tasks = conn.execute('''
        SELECT * FROM study_tasks
        WHERE user_id = ?
        ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END,
                 CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                 id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return tasks

def add_user_task(user_id, title, subject, due_date, priority, pomodoro_count=1):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_tasks (user_id, title, subject, due_date, priority, pomodoro_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, subject, due_date, priority, pomodoro_count))
    conn.commit()
    t_id = cursor.lastrowid
    conn.close()
    return t_id

def toggle_user_task(task_id, user_id):
    conn = get_db()
    task = conn.execute("SELECT status FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()
    if task:
        new_status = 'completed' if task['status'] == 'pending' else 'pending'
        conn.execute("UPDATE study_tasks SET status = ? WHERE id = ? AND user_id = ?", (new_status, task_id, user_id))
        conn.commit()
    conn.close()
    return new_status if task else None

def delete_user_task(task_id, user_id):
    conn = get_db()
    conn.execute("DELETE FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

# ----------------- Study Room Helpers -----------------
def get_all_rooms():
    conn = get_db()
    rooms = conn.execute("SELECT * FROM study_rooms ORDER BY active_users DESC, id ASC").fetchall()
    conn.close()
    return rooms

def get_room_by_id(room_id):
    conn = get_db()
    room = conn.execute("SELECT * FROM study_rooms WHERE id = ?", (room_id,)).fetchone()
    conn.close()
    return room

def get_room_messages(room_id, limit=50):
    conn = get_db()
    messages = conn.execute('''
        SELECT * FROM room_messages
        WHERE room_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    ''', (room_id, limit)).fetchall()
    conn.close()
    return messages

def add_room_message(room_id, username, avatar, message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO room_messages (room_id, username, avatar, message)
        VALUES (?, ?, ?, ?)
    ''', (room_id, username, avatar, message))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def create_study_room(name, subject, description, bg_sound='rain'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_rooms (name, subject, description, bg_sound)
        VALUES (?, ?, ?, ?)
    ''', (name, subject, description, bg_sound))
    conn.commit()
    r_id = cursor.lastrowid
    conn.close()
    return r_id

# ----------------- Community / Forum Helpers -----------------
def get_community_topics(category=None, search=None):
    conn = get_db()
    query = '''
        SELECT t.*, COUNT(r.id) as reply_count
        FROM community_topics t
        LEFT JOIN community_replies r ON t.id = r.topic_id
        WHERE 1=1
    '''
    params = []
    if category and category != 'All':
        query += " AND t.category = ?"
        params.append(category)
    if search:
        query += " AND (t.title LIKE ? OR t.content LIKE ? OR t.tags LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " GROUP BY t.id ORDER BY t.upvotes DESC, t.created_at DESC"
    topics = conn.execute(query, params).fetchall()
    conn.close()
    return topics

def get_community_topic(topic_id):
    conn = get_db()
    topic = conn.execute("SELECT * FROM community_topics WHERE id = ?", (topic_id,)).fetchone()
    conn.close()
    return topic

def get_topic_replies(topic_id):
    conn = get_db()
    replies = conn.execute('''
        SELECT * FROM community_replies
        WHERE topic_id = ?
        ORDER BY is_solution DESC, upvotes DESC, created_at ASC
    ''', (topic_id,)).fetchall()
    conn.close()
    return replies

def create_topic(user_id, title, category, content, author_name, tags=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO community_topics (user_id, title, category, content, author_name, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, category, content, author_name, tags))
    conn.commit()
    t_id = cursor.lastrowid
    conn.close()
    return t_id

def create_reply(topic_id, user_id, author_name, avatar, content):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO community_replies (topic_id, user_id, author_name, avatar, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic_id, user_id, author_name, avatar, content))
    conn.commit()
    r_id = cursor.lastrowid
    conn.close()
    return r_id

def upvote_topic(topic_id):
    conn = get_db()
    conn.execute("UPDATE community_topics SET upvotes = upvotes + 1 WHERE id = ?", (topic_id,))
    conn.commit()
    conn.close()

# ----------------- Pomodoro Log Helpers -----------------
def log_pomodoro(user_id, duration_mins, subject="General Study"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pomodoro_logs (user_id, duration_mins, subject)
        VALUES (?, ?, ?)
    ''', (user_id, duration_mins, subject))
    # Also increment user's total study time
    conn.execute('''
        UPDATE users
        SET total_study_minutes = total_study_minutes + ?
        WHERE id = ?
    ''', (duration_mins, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return None

    # Tasks stats
    total_tasks = conn.execute("SELECT COUNT(*) FROM study_tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    completed_tasks = conn.execute("SELECT COUNT(*) FROM study_tasks WHERE user_id = ? AND status = 'completed'", (user_id,)).fetchone()[0]

    # Quizzes stats
    quizzes_taken = conn.execute("SELECT COUNT(*) FROM quiz_results WHERE user_id = ?", (user_id,)).fetchone()[0]
    quizzes_passed = conn.execute("SELECT COUNT(*) FROM quiz_results WHERE user_id = ? AND passed = 1", (user_id,)).fetchone()[0]

    # Pomodoro count
    pomo_sessions = conn.execute("SELECT COUNT(*), IFNULL(SUM(duration_mins), 0) FROM pomodoro_logs WHERE user_id = ?", (user_id,)).fetchone()

    # Bookmarks count
    bookmarks_count = conn.execute("SELECT COUNT(*) FROM bookmarks WHERE user_id = ?", (user_id,)).fetchone()[0]

    conn.close()
    return {
        "user": user,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_completion_pct": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0),
        "quizzes_taken": quizzes_taken,
        "quizzes_passed": quizzes_passed,
        "pomo_count": pomo_sessions[0],
        "pomo_minutes": pomo_sessions[1],
        "bookmarks_count": bookmarks_count
    }

def get_platform_stats():
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_resources = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
    total_decks = conn.execute("SELECT COUNT(*) FROM flashcard_decks").fetchone()[0]
    total_quizzes = conn.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    total_rooms = conn.execute("SELECT COUNT(*) FROM study_rooms").fetchone()[0]
    conn.close()
    return {
        "users": total_users + 1240, # Add social proof baseline
        "resources": total_resources,
        "decks": total_decks,
        "quizzes": total_quizzes,
        "rooms": total_rooms,
        "study_hours": 14850
    }
