# ᜆᜇ᜔ᜑᜈ᜔ Tadhana

A Filipino-themed tarot reading web app for logging and managing personal tarot readings.

---

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** Vue.js 3 (CDN), HTML/CSS
- **Database:** PostgreSQL

---

## Getting Started

### Prerequisites

- Python 3.x
- PostgreSQL running locally

### Installation

1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/YOUR_USERNAME/tadhana.git
   cd tadhana
   ```

2. Install dependencies:
   ```bash
   pip install flask psycopg2-binary flask-bcrypt flask-cors
   ```

3. Create the database in PostgreSQL:
   ```sql
   CREATE DATABASE tadhana_db;
   ```

4. Create the required tables:
   ```sql
   CREATE TABLE users (
       user_id SERIAL PRIMARY KEY,
       name VARCHAR(100) NOT NULL,
       email VARCHAR(150) UNIQUE NOT NULL,
       password TEXT NOT NULL,
       date_of_birth DATE,
       last_login TIMESTAMP
   );

   CREATE TABLE readings (
       reading_id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
       question TEXT NOT NULL,
       spread_type VARCHAR(50) NOT NULL,
       tags TEXT,
       notes TEXT,
       reading_date TIMESTAMP DEFAULT NOW()
   );
   ```

5. Run the app:
   ```bash
   python app.py
   ```

6. Open your browser and go to:
   ```
   http://localhost:3000
   ```
