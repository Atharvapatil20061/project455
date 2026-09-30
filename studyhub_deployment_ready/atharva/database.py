import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'study_hub.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        avatar TEXT DEFAULT 'avatar-1',
        bio TEXT,
        study_goal_hours INTEGER DEFAULT 25,
        streak_days INTEGER DEFAULT 3,
        total_study_minutes INTEGER DEFAULT 740,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Resources Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        category TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Beginner',
        description TEXT,
        content TEXT,
        key_takeaways TEXT,
        author TEXT DEFAULT 'StudyHub Faculty',
        read_time_mins INTEGER DEFAULT 15,
        downloads_count INTEGER DEFAULT 0,
        views_count INTEGER DEFAULT 0,
        featured INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Flashcard Decks Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcard_decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT 'bi-card-text',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Flashcards Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deck_id INTEGER REFERENCES flashcard_decks(id) ON DELETE CASCADE,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        hint TEXT
    )
    ''')

    # Quizzes Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        duration_mins INTEGER DEFAULT 10,
        pass_percentage INTEGER DEFAULT 70,
        difficulty TEXT DEFAULT 'Intermediate',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Quiz Questions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL,
        explanation TEXT
    )
    ''')

    # Quiz Results Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
        score INTEGER,
        total_questions INTEGER,
        percentage REAL,
        passed INTEGER DEFAULT 0,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Study Tasks (Planner) Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        subject TEXT,
        due_date TEXT,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'pending',
        pomodoro_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Study Rooms Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        active_users INTEGER DEFAULT 1,
        max_users INTEGER DEFAULT 12,
        bg_sound TEXT DEFAULT 'rain',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Room Messages Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS room_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER REFERENCES study_rooms(id) ON DELETE CASCADE,
        username TEXT NOT NULL,
        avatar TEXT DEFAULT 'avatar-1',
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Community Topics (Discussion) Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS community_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        upvotes INTEGER DEFAULT 0,
        author_name TEXT NOT NULL,
        tags TEXT DEFAULT 'general',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Community Replies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS community_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER REFERENCES community_topics(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        author_name TEXT NOT NULL,
        avatar TEXT DEFAULT 'avatar-2',
        content TEXT NOT NULL,
        upvotes INTEGER DEFAULT 0,
        is_solution INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Bookmarks Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, resource_id)
    )
    ''')

    # Pomodoro Session Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pomodoro_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        duration_mins INTEGER NOT NULL,
        subject TEXT DEFAULT 'General Study',
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()

    # Seed default data if database is fresh
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # 1. Default Demo User
    demo_pw = generate_password_hash("study123")
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, avatar, bio, study_goal_hours, streak_days, total_study_minutes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'alex_learner',
        'alex@studyhub.edu',
        demo_pw,
        'Alex Mercer',
        'avatar-1',
        'Computer Science and Math enthusiast. Striving for daily consistency and deep focus!',
        30,
        5,
        960
    ))
    user_id = cursor.lastrowid

    # 2. Seed Resources (High Quality Tutorials, Cheatsheets, Notes)
    resources_data = [
        (
            'Python 3 Advanced Mastery Guide: Metaprogramming & AsyncIO',
            'Computer Science',
            'Full Guide',
            'Advanced',
            'Master asynchronous coroutines, custom decorators, context managers, and memory profiling in Python 3.12+.',
            r'''# Python 3 Advanced Mastery Guide

Python is a versatile, multi-paradigm high-level language. When building robust, concurrent applications, understanding its advanced internals is crucial.

---

### 1. Asynchronous Programming with `asyncio`
Traditional I/O in Python is blocking. With `asyncio`, cooperative multitasking allows thousands of I/O operations concurrently on a single thread.

```python
import asyncio
import time

async def fetch_study_data(resource_id: int):
    print(f"[Start] Fetching Resource #{resource_id}")
    await asyncio.sleep(1.5)  # Non-blocking I/O simulation
    print(f"[Done] Retrieved Resource #{resource_id}")
    return {"id": resource_id, "status": "200 OK"}

async def main():
    start = time.perf_counter()
    # Run 5 tasks concurrently
    tasks = [fetch_study_data(i) for i in range(1, 6)]
    results = await asyncio.gather(*tasks)
    print(f"All {len(results)} tasks completed in {time.perf_counter() - start:.2f}s!")

if __name__ == '__main__':
    asyncio.run(main())
```

---

### 2. Custom Decorators with Arguments and `functools.wraps`
Decorators dynamically wrap functions to enforce pre-conditions, caching, authentication, or timing without modifying the original function logic.

```python
from functools import wraps
import time

def execution_logger(prefix="[STUDY-LOG]"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            print(f"{prefix} {func.__name__}() executed in {duration:.3f} ms")
            return result
        return wrapper
    return decorator

@execution_logger(prefix="[TIMER]")
def solve_algorithm(n: int):
    return sum(x * x for x in range(n))

print("Result:", solve_algorithm(100_000))
```

---

### 3. Context Managers with `contextlib`
Safe resource acquisition and cleanup (files, sockets, database transactions):

```python
from contextlib import contextmanager

@contextmanager
def study_session_tracker(subject_name: str):
    print(f"📖 Starting intense study block: {subject_name}")
    try:
        yield
    except Exception as err:
        print(f"⚠️ Study session interrupted by: {err}")
    finally:
        print(f"✅ Concluded study session: {subject_name}")
```

### Key Highlights
* `asyncio.gather()` provides concurrent execution for non-blocking I/O.
* Use `functools.wraps` to maintain docstrings and function introspection.
* Generator-based context managers simplify try-finally cleanups.
''',
            '• Asynchronous concurrency with async/await\n• High performance decorators and wraps\n• Pythonic context managers and resource safety\n• Memory efficiency with generators and slots',
            'Dr. Sophia Vance',
            22,
            1420,
            4890,
            1
        ),
        (
            'Complete Data Structures & Algorithms Visual Handbook',
            'Computer Science',
            'Cheat Sheet',
            'Intermediate',
            'Big-O time complexity charts, trees, graphs, dynamic programming patterns, and Dijkstra implementation.',
            r'''# Data Structures & Algorithms Visual Handbook

Efficient algorithms make the difference between an application that scales effortlessly and one that grinds to a halt under load.

---

### 1. Big-O Complexity Comparison

| Data Structure / Op | Access | Search | Insertion | Deletion | Space |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dynamic Array** | $O(1)$ | $O(N)$ | $O(1)$ amortized | $O(N)$ | $O(N)$ |
| **Hash Table** | N/A | $O(1)$ avg | $O(1)$ avg | $O(1)$ avg | $O(N)$ |
| **Binary Search Tree** | $O(\log N)$ | $O(\log N)$ | $O(\log N)$ | $O(\log N)$ | $O(N)$ |
| **Min/Max Heap** | $O(1)$ peek | $O(N)$ | $O(\log N)$ | $O(\log N)$ | $O(N)$ |

---

### 2. Breadth-First Search (BFS) vs Depth-First Search (DFS)
Graph traversal fundamentals:

```python
from collections import deque

def bfs(graph, start_node):
    visited = set([start_node])
    queue = deque([start_node])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
```

---

### 3. Dynamic Programming: 0/1 Knapsack Pattern
Finding optimal subset weights without exponential $O(2^N)$ explosion:

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(values[i - 1] + dp[i - 1][w - weights[i - 1]], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][capacity]
```
''',
            '• Master Big-O complexities and time-space tradeoffs\n• Master BFS, DFS, and topological sort\n• Understand sliding window and two-pointer techniques\n• Dynamic Programming memoization vs tabulation',
            'Prof. Alan Thorne',
            28,
            2310,
            7850,
            1
        ),
        (
            'Calculus & Linear Algebra for Machine Learning',
            'Mathematics',
            'Study Notes',
            'Intermediate',
            'Gradient descent, partial derivatives, eigenvalues, eigenvectors, matrix decompositions, and vector spaces.',
            r'''# Mathematics for Machine Learning: Calculus & Linear Algebra

Behind every neural network and regression model lies pure linear algebra and multivariable calculus.

---

### 1. The Gradient Vector & Gradient Descent
For a scalar loss function $L(w_1, w_2, \dots, w_n)$, the gradient is the vector of partial derivatives pointing in the direction of steepest ascent:

$$\nabla L = \begin{bmatrix} \frac{\partial L}{\partial w_1} \\ \frac{\partial L}{\partial w_2} \\ \vdots \\ \frac{\partial L}{\partial w_n} \end{bmatrix}$$

Weights are updated in the opposite direction of the gradient:
$$w_{t+1} = w_t - \eta \nabla L(w_t)$$

Where $\eta$ represents the learning rate.

---

### 2. Eigenvalues and Eigenvectors
For an $n \\times n$ matrix $A$, a non-zero vector $v$ is an eigenvector if:
$$A v = \lambda v$$
where $\lambda$ is the corresponding scalar eigenvalue. This is fundamental in Principal Component Analysis (PCA) for dimensionality reduction.

---

### 3. Singular Value Decomposition (SVD)
Every real $m \\times n$ matrix $M$ can be factored into:
$$M = U \Sigma V^T$$
Where:
- $U$ is an $m \\times m$ orthogonal matrix (left singular vectors)
- $\Sigma$ is an $m \\times n$ diagonal matrix of singular values
- $V^T$ is the transpose of an $n \\times n$ orthogonal matrix
''',
            '• Understand the geometric intuition of gradient descent\n• Solve for eigenvalues and eigenvectors\n• Master matrix multiplication and vector projections\n• Apply SVD and PCA for dimensionality reduction',
            'Elena Rostova, Ph.D.',
            18,
            980,
            3420,
            1
        ),
        (
            'Modern Web Development: Full-Stack JavaScript & Architecture',
            'Web Development',
            'Full Guide',
            'Beginner',
            'Deep dive into the DOM, Fetch API, CSS Grid, Flexbox, Event Loop, and client-server REST communication.',
            r'''# Modern Web Development Handbook

The modern web is built on semantic HTML, expressive CSS architectures, and performant asynchronous JavaScript.

---

### 1. The Browser Event Loop
JavaScript is single-threaded and executes code via a Call Stack, Web APIs, Microtask Queue (Promises), and Macrotask Queue (setTimeout, I/O).

Microtasks always drain before the next macrotask is dispatched!

---

### 2. Native Modern Fetch with Async/Await & Error Handling

```javascript
async function loadStudyResources(category) {
  try {
    const response = await fetch(`/api/resources?category=${encodeURIComponent(category)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    renderCards(data.resources);
  } catch (error) {
    console.error('Failed to load study resources:', error);
    displayToast('Could not load resources. Please try again.', 'error');
  }
}
```

---

### 3. CSS Grid Layout Essentials
Creating responsive 12-column or auto-fit grid systems effortlessly without media queries:

```css
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}
```
''',
            '• Understand DOM manipulation and modern query selectors\n• Master Fetch API and async data flows\n• Modern CSS Grid and Flexbox responsive design\n• Event delegation and performance optimization',
            'David Kim',
            16,
            1850,
            6100,
            1
        ),
        (
            'Quantum Mechanics & Modern Physics: Core Principles',
            'Physics',
            'Study Notes',
            'Advanced',
            'Wave-particle duality, Schrödinger wave equation, Heisenberg uncertainty principle, and quantum entanglement.',
            r'''# Quantum Mechanics & Modern Physics Essentials

At atomic and subatomic scales, classical Newtonian mechanics breaks down and gives way to probabilistic wave mechanics.

---

### 1. Wave-Particle Duality & De Broglie Wavelength
Matter behaves simultaneously with particle and wave attributes:
$$\lambda = \frac{h}{p} = \frac{h}{m v}$$

Where $h = 6.626 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$ is Planck's constant.

---

### 2. The Time-Dependent Schrödinger Equation
The fundamental equation governing the quantum state of a physical system:

$$i \hbar \frac{\partial}{\partial t} \Psi(\mathbf{r}, t) = \hat{H} \Psi(\mathbf{r}, t)$$

Where:
- $\Psi(\mathbf{r}, t)$ is the quantum wave function
- $|\Psi(\mathbf{r}, t)|^2$ gives the probability density of locating the particle
- $\hat{H}$ is the Hamiltonian operator representing total energy
''',
            '• Understand probability wave functions\n• Heisenberg Uncertainty Principle: delta x * delta p >= hbar / 2\n• Quantum tunneling and potential wells\n• Spin states and Pauli Exclusion Principle',
            'Dr. Marcus Vance',
            25,
            640,
            2890,
            0
        ),
        (
            'Machine Learning & Deep Neural Networks from Scratch',
            'Data Science',
            'Full Guide',
            'Intermediate',
            'Backpropagation math, activation functions (ReLU, Sigmoid, GELU), loss functions, and model regularization.',
            r'''# Deep Neural Networks from Ground Up

A neural network is a universal function approximator composed of interconnected layers of artificial neurons.

---

### 1. Forward Propagation
For layer $l$:
$$Z^{[l]} = W^{[l]} A^{[l-1]} + b^{[l]}$$
$$A^{[l]} = g(Z^{[l]})$$
where $g$ is a non-linear activation function.

---

### 2. Common Activation Functions
- **ReLU**: $f(x) = \max(0, x)$ — prevents vanishing gradients in deep layers.
- **Sigmoid**: $\sigma(x) = \frac{1}{1 + e^{-x}}$ — maps outputs to probabilities $(0, 1)$.
- **Softmax**: Multi-class classification probability distribution.
''',
            '• Mathematical formulation of Backpropagation\n• Optimization algorithms: Adam, RMSProp, SGD with Momentum\n• Regularization techniques: Dropout, L1/L2, Batch Normalization\n• Convolutional & Transformer architectures overview',
            'Aisha Patel',
            30,
            1720,
            5430,
            1
        )
    ]

    for res in resources_data:
        cursor.execute('''
            INSERT INTO resources (title, subject, category, difficulty, description, content, key_takeaways, author, read_time_mins, downloads_count, views_count, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', res)

    # 3. Seed Flashcard Decks & Cards
    deck_data = [
        (
            'Python Core Concepts & Syntax',
            'Computer Science',
            'Essential Python questions: data types, decorators, memory management, and OOP.',
            'bi-code-slash'
        ),
        (
            'Data Structures & Algorithms Rapid Fire',
            'Computer Science',
            'Test your recall on sorting algorithms, tree traversals, and Big-O times.',
            'bi-diagram-3'
        ),
        (
            'Calculus & Mathematical Theorems',
            'Mathematics',
            'Derivatives, integrals, limits, and linear algebra definitions.',
            'bi-calculator'
        ),
        (
            'Web Development Mastery (HTML/CSS/JS)',
            'Web Development',
            'DOM events, CSS flex/grid properties, HTTP status codes, and JS scope.',
            'bi-globe'
        )
    ]

    for deck in deck_data:
        cursor.execute('''
            INSERT INTO flashcard_decks (title, subject, description, icon)
            VALUES (?, ?, ?, ?)
        ''', deck)
        deck_id = cursor.lastrowid

        if 'Python' in deck[0]:
            cards = [
                ("What is the difference between a list and a tuple in Python?",
                 "Lists are mutable (can be changed, appended, deleted) and use square brackets []. Tuples are immutable (cannot be modified after creation), use parentheses (), and are more memory-efficient and hashable as dictionary keys.",
                 "Think about mutability and memory overhead."),
                ("How does the Global Interpreter Lock (GIL) affect Python threads?",
                 "The GIL is a mutex in CPython that allows only one native thread to execute Python bytecode at a time, preventing multi-core speedup for CPU-bound tasks. For CPU-bound concurrency, multiprocessing is preferred; for I/O-bound tasks, threading or asyncio works well.",
                 "CPython thread synchronization lock."),
                ("What does the *args and **kwargs syntax mean in function definitions?",
                 "*args allows passing a variable number of non-keyword positional arguments as a tuple. **kwargs allows passing an arbitrary number of keyword arguments as a dictionary.",
                 "Positional vs keyword unpacking."),
                ("Explain the difference between deepcopy and shallow copy.",
                 "A shallow copy creates a new object but inserts references into it to the objects found in the original. A deep copy recursively copies all objects found within the original, making completely independent copies.",
                 "Look at nested structures."),
                ("What is a Python Generator and how does `yield` work?",
                 "A generator is a function that returns an iterator that produces a sequence of values lazily on-the-fly. The `yield` keyword pauses function execution, saves its state, and yields a value to the caller without storing the entire sequence in memory.",
                 "Lazy evaluation and memory efficiency.")
            ]
        elif 'Algorithms' in deck[0]:
            cards = [
                ("What is the worst-case time complexity of QuickSort and how can it be avoided?",
                 "Worst case is O(N^2) when the chosen pivot is always the smallest or largest element (e.g. on already sorted arrays). It can be avoided by using randomized pivot selection, median-of-three, or switching to Introsort.",
                 "Think of pivot selection on sorted arrays."),
                ("What is the difference between BFS and DFS traversal?",
                 "BFS (Breadth-First Search) explores neighbors level-by-level using a Queue (FIFO) and finds the shortest path on unweighted graphs. DFS (Depth-First Search) explores as deep as possible down each branch using a Stack or recursion (LIFO).",
                 "Queue vs Stack / Level vs Depth."),
                ("What makes a Dynamic Programming problem suitable for memoization?",
                 "Two core properties: 1) Optimal Substructure (an optimal solution can be constructed from optimal solutions of subproblems), and 2) Overlapping Subproblems (the same subproblems are computed repeatedly).",
                 "Optimal substructure & overlapping subproblems."),
                ("What is the average time complexity of inserting into a Hash Map?",
                 "O(1) average time complexity. Worst-case can degrade to O(N) if many hash collisions occur without proper resizing.",
                 "Hash table bucket lookup."),
                ("What is the difference between a Min-Heap and a Binary Search Tree (BST)?",
                 "In a Min-Heap, each parent is smaller than or equal to its children (no left/right ordering), allowing O(1) minimum extraction. In a BST, left child < parent < right child, allowing ordered O(log N) searches.",
                 "Heap property vs BST in-order sorting.")
            ]
        elif 'Calculus' in deck[0]:
            cards = [
                ("What is the derivative of f(x) = ln(x) for x > 0?",
                 "f'(x) = 1 / x",
                 "Standard logarithmic derivative rule."),
                ("State the Fundamental Theorem of Calculus (Part 1).",
                 "If f is continuous on [a, b] and F(x) = integral from a to x of f(t) dt, then F'(x) = f(x) for every x in [a, b]. It connects differentiation and integration as inverse processes.",
                 "Inverse connection between derivatives and integrals."),
                ("What condition must be met for a matrix to be invertible?",
                 "The matrix must be square (n x n) and its determinant must be non-zero (det(A) != 0). Equivalently, its columns must be linearly independent.",
                 "Check the determinant value."),
                ("What is Euler's formula?",
                 "e^(i * theta) = cos(theta) + i * sin(theta). For theta = pi, it yields the famous identity: e^(i * pi) + 1 = 0.",
                 "Complex exponential relating trig functions.")
            ]
        else:
            cards = [
                ("What is the difference between localStorage and sessionStorage?",
                 "localStorage persists data with no expiration time even after browser or tab is closed. sessionStorage keeps data only for the duration of the page session (cleared when tab is closed).",
                 "Persistence across browser restarts."),
                ("Explain CSS Flexbox vs CSS Grid.",
                 "Flexbox is designed for 1-dimensional layouts (either row OR column). Grid is designed for 2-dimensional layouts (simultaneous rows AND columns).",
                 "1D vs 2D layout model."),
                ("What is event bubbling in JavaScript?",
                 "Event bubbling is the phase of event propagation where an event triggered on a child DOM element bubbles up through its ancestors in the DOM tree unless event.stopPropagation() is called.",
                 "Bottom-up propagation.")
            ]

        for q, a, h in cards:
            cursor.execute('''
                INSERT INTO flashcards (deck_id, question, answer, hint)
                VALUES (?, ?, ?, ?)
            ''', (deck_id, q, a, h))

    # 4. Seed Quizzes & Questions
    quizzes_data = [
        (
            'Python Foundations & Architecture Quiz',
            'Computer Science',
            'Challenge your understanding of Python syntax, scoping, data structures, and best practices.',
            15,
            75,
            'Beginner'
        ),
        (
            'Data Structures & Algorithms Mastery Test',
            'Computer Science',
            'Timed evaluation on sorting, searching, graph algorithms, and time complexities.',
            20,
            70,
            'Intermediate'
        ),
        (
            'Full-Stack Web Technology Assessment',
            'Web Development',
            'Test your skills on HTTP, async JS, CSS layouts, and modern web application security.',
            15,
            70,
            'Intermediate'
        )
    ]

    for qz in quizzes_data:
        cursor.execute('''
            INSERT INTO quizzes (title, subject, description, duration_mins, pass_percentage, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', qz)
        quiz_id = cursor.lastrowid

        if 'Python' in qz[0]:
            questions = [
                ("What is the output of `bool([False])` in Python?",
                 "False", "True", "TypeError", "None",
                 "B", "Non-empty lists evaluate to True in a boolean context, even if their single element is False!"),
                ("Which built-in Python module is used for serialization and deserialization of objects?",
                 "json", "pickle", "marshal", "serialize",
                 "B", "Python's `pickle` module serializes arbitrary Python object hierarchies into byte streams."),
                ("What is the time complexity of looking up a key in a Python dict on average?",
                 "O(1)", "O(log N)", "O(N)", "O(N log N)",
                 "A", "Python dictionaries are implemented using optimized hash tables with open addressing, providing O(1) average lookup time."),
                ("What keyword is used to create an anonymous function in Python?",
                 "def", "func", "lambda", "inline",
                 "C", "The `lambda` keyword allows writing small anonymous, one-liner functions."),
                ("Which of the following is an immutable data type in Python?",
                 "List", "Set", "Tuple", "Dictionary",
                 "C", "Tuples cannot be altered after creation, making them immutable.")
            ]
        elif 'Algorithms' in qz[0]:
            questions = [
                ("What is the average time complexity of Merge Sort?",
                 "O(N)", "O(N log N)", "O(N^2)", "O(log N)",
                 "B", "Merge sort recursively divides the array in half (log N levels) and merges them in O(N) work per level, resulting in O(N log N) in all cases."),
                ("Which data structure operates on a First-In, First-Out (FIFO) basis?",
                 "Stack", "Queue", "Binary Tree", "Max Heap",
                 "B", "A Queue processes elements in First-In, First-Out (FIFO) sequence."),
                ("Dijkstra's Algorithm cannot be guaranteed to work correctly with:",
                 "Directed Graphs", "Dense Graphs", "Negative Edge Weights", "Trees",
                 "C", "Dijkstra assumes that adding an edge to a path cannot decrease its total weight; negative edges violate this greediness."),
                ("What is the maximum number of nodes at level `L` of a binary tree (root at level 0)?",
                 "2^L", "2^(L + 1)", "2L", "L^2",
                 "A", "Level 0 has 1 node (2^0), level 1 has 2 (2^1), level 2 has 4 (2^2), and level L has 2^L nodes."),
                ("Which sorting algorithm has a worst-case space complexity of O(1)?",
                 "Merge Sort", "Heap Sort", "Timsort", "Radix Sort",
                 "B", "Heap Sort sorts in-place using binary heap properties, requiring only O(1) auxiliary space.")
            ]
        else:
            questions = [
                ("What HTTP status code represents '404'?",
                 "Bad Request", "Unauthorized", "Not Found", "Internal Server Error",
                 "C", "HTTP 404 indicates that the requested resource could not be found on the server."),
                ("Which CSS property defines the space between cells in a CSS Grid?",
                 "padding", "margin", "gap", "border-spacing",
                 "C", "The `gap` property (formerly grid-gap) controls gutter spacing between grid tracks."),
                ("What method stops an event from bubbling up the DOM hierarchy?",
                 "event.preventDefault()", "event.stopPropagation()", "event.cancel()", "event.halt()",
                 "B", "event.stopPropagation() stops the event from proceeding up the parent chain."),
                ("What is the purpose of the 'async' attribute on a <script> tag?",
                 "Executes script synchronously", "Loads and executes script asynchronously without blocking HTML parsing", "Delays execution until user clicks", "Prevents cookies",
                 "B", "The `async` attribute downloads the script in parallel with page parsing and runs it as soon as it is ready.")
            ]

        for q in questions:
            cursor.execute('''
                INSERT INTO quiz_questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (quiz_id, q[0], q[1], q[2], q[3], q[4], q[5], q[6]))

    # 5. Seed Virtual Study Rooms
    rooms_data = [
        ('Quiet Library: CS & Coding Focus', 'Computer Science', 'Silent coding, algorithm grinding, and project building. Camera/chat optional.', 7, 15, 'lofi'),
        ('Mathematics & Calculus Problem Solvers', 'Mathematics', 'Work through problem sets, LaTeX formulas, and exam preparations together.', 4, 10, 'rain'),
        ('Late Night Lo-Fi Cafe', 'General Study', 'Mellow ambient lo-fi beats, warm atmosphere, Pomodoro sync sessions.', 9, 20, 'cafe'),
        ('Physics & Science Research Group', 'Physics', 'Quantum mechanics, electromagnetism, and classical mechanics discussion space.', 3, 10, 'whitenoise')
    ]

    for room in rooms_data:
        cursor.execute('''
            INSERT INTO study_rooms (name, subject, description, active_users, max_users, bg_sound)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', room)
        r_id = cursor.lastrowid

        # Seed initial messages for room
        cursor.execute('''
            INSERT INTO room_messages (room_id, username, avatar, message)
            VALUES (?, ?, ?, ?)
        ''', (r_id, 'Elena_R', 'avatar-3', 'Welcome everyone! Starting a 50-minute deep study sprint now. Stay focused! 🚀'))
        cursor.execute('''
            INSERT INTO room_messages (room_id, username, avatar, message)
            VALUES (?, ?, ?, ?)
        ''', (r_id, 'Marcus_Code', 'avatar-2', 'Joined! Tackling dynamic programming problems today. Let me know if anyone wants to bounce ideas.'))

    # 6. Seed Study Tasks (Planner)
    tasks_data = [
        (user_id, 'Complete Python Decorators & Metaclasses chapter', 'Computer Science', 'Today', 'High', 'pending', 3),
        (user_id, 'Review Calculus 3 Double Integrals problem set', 'Mathematics', 'Tomorrow', 'Medium', 'pending', 2),
        (user_id, 'Practice 20 Flashcards on Data Structures', 'Computer Science', 'Today', 'High', 'completed', 1),
        (user_id, 'Submit Web Dev API REST design assignment', 'Web Development', 'Oct 5', 'Medium', 'pending', 2),
        (user_id, 'Read Physics Wave-Particle Duality notes', 'Physics', 'Oct 7', 'Low', 'pending', 1)
    ]

    for t in tasks_data:
        cursor.execute('''
            INSERT INTO study_tasks (user_id, title, subject, due_date, priority, status, pomodoro_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', t)

    # 7. Seed Community Topics
    topics_data = [
        (
            user_id,
            'How do you maintain deep focus during 3+ hour coding study sessions?',
            'Study Techniques',
            'I often find my attention drifting after 45 minutes of staring at complex code. How do top students and developers structure their Pomodoro intervals and breaks to stay sharp all day without mental exhaustion?',
            28,
            'Alex Mercer',
            'productivity,pomodoro,focus'
        ),
        (
            user_id,
            'Best way to intuitively visualize Eigenvectors in 3D Linear Algebra?',
            'Mathematics',
            r'I understand the algebraic definition $A v = \lambda v$, but looking for physical and geometric analogies. How do you visualize why an eigenvector does not change its directional span when multiplied by transformation matrix A?',
            41,
            'Marcus Vance',
            'math,linear-algebra,geometry'
        ),
        (
            user_id,
            'Why use AsyncIO over Multiprocessing in Python for Web Scraping?',
            'Computer Science',
            'I am building an automated research aggregator. Should I spin up a ProcessPool or utilize `aiohttp` and `asyncio.gather`? What are the resource overheads?',
            34,
            'Elena Rostova',
            'python,async,architecture'
        )
    ]

    for top in topics_data:
        cursor.execute('''
            INSERT INTO community_topics (user_id, title, category, content, upvotes, author_name, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', top)
        t_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO community_replies (topic_id, user_id, author_name, avatar, content, upvotes, is_solution)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            t_id,
            user_id,
            'Dr. Sophia Vance',
            'avatar-4',
            'Great question! The secret is the "50/10 Ultradian Rhythm". Work for 50 minutes with all notifications silenced, then take a strict 10-minute break away from screens (walk, hydrate, look at distance). The key is not consuming social media or video during the break—give your dopamine receptors genuine rest.',
            19,
            1
        ))

    conn.commit()

if __name__ == '__main__':
    print("Initializing Study Hub database...")
    init_db()
    print("Database initialized and pre-seeded successfully!")
