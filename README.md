# Graph-Based Movie Recommendation System (Neo4j)

A **content-based movie recommendation system** built with **Neo4j**. The user searches for a movie title, and the system recommends **related movies** based on shared graph attributes such as **actors, directors, genres, and relationships**. The results are visualized as a **graph**, helping users explore connections between movies.

This project demonstrates how **graph databases** excel at discovering similarity and relationships in connected data.

---

## 🚀 Key Highlights
- Movie-to-movie recommendations based on graph similarity
- Neo4j graph model with movies, actors, directors, and genres
- Flask backend querying Neo4j using Cypher
- Interactive web interface with search and graph visualization

---

## 🧰 Tech Stack
- **Neo4j** – Graph database
- **Python** – Backend logic
- **Flask** – Web framework / API
- **Cypher** – Neo4j query language
- **HTML / CSS / JavaScript** – Frontend

---

## 🏗️ System Architecture
- Movies, actors,and directors are modeled as **nodes**
- Relationships describe how entities are connected (ACTED_IN, DIRECTED)
- Flask sends Cypher queries to Neo4j based on user input
- The frontend displays recommendations and a visual graph of relationships

---

## 🧠 Recommendation Logic
The recommendation engine follows a **content-based graph approach**:
- The user enters a movie title
- The system finds movies connected via:
  - Same actors
  - Same director
  - Same genre
- Related movies are ranked based on the number and type of shared relationships
- The resulting subgraph is returned and visualized

This approach leverages **graph traversal**, making similarity queries intuitive and efficient.

---

## 📂 Project Structure
```
movie-recommender/
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
├── templates/              # Frontend files
│   ├── index.html          # Search & graph visualization UI
│   ├── searchbar.css       # Styling
│   └── searchbar.js        # Frontend logic
└── README.md               # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/movie-recommender.git
cd movie-recommender
```

### 2️⃣ (Optional) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Neo4j
- Start a Neo4j instance (Neo4j Desktop or Docker)
- Ensure the database contains movies, actors, and directors
- Update Neo4j connection credentials in `app.py`

---

## ▶️ Running the Application
```bash
python app.py
```
Open your browser at:
```
http://127.0.0.1:5000
```

---

## 📊 Example Use Case
1. User searches for **"Inception"**
2. System finds related movies sharing actors (e.g. Leonardo DiCaprio), director (Christopher Nolan), or genre
3. Recommendations are displayed along with a **graph visualization** of relationships

---

## 🔮 Future Enhancements
- Weight relationships (actor > director > genre)
- Improve graph visualization (colors, sizes, filters)
- Add pagination and ranking controls
- Dockerize the application for deployment

---

## 👤 Author
- Hamza Znaidi

---

## 📄 License
This project is provided for educational and portfolio purposes.
