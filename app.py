from flask import Flask, request, render_template, jsonify
from neo4j import GraphDatabase
import ast
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configure (use your confirmed credentials) ---
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "myneo4j123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), max_connection_lifetime=60)

# --- Helpers ---
def records_to_list(records):
    return [r.data() for r in records]

def parse_genres_property(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    try:
        return [s.strip().strip("'\"") for s in ast.literal_eval(value)]
    except Exception:
        return [s.strip().strip("'\"[]") for s in str(value).split(",") if s.strip()]

# --- Core recommendation logic ---
def get_recommendations(movie_title):
    with driver.session() as session:
        results = {}

        # fetch base movie info (title, year, genres, actors, directors)
        movie_info_q = """
        MATCH (m:Movies {title:$title})
        OPTIONAL MATCH (m)<-[:Acted_In]-(a:Actors)
        OPTIONAL MATCH (m)<-[:Directed_In]-(d:Directors)
        RETURN m.title AS title, m.year AS year, m.genres AS genres,
               collect(DISTINCT a.actor_name) AS actors,
               collect(DISTINCT d.director_name) AS directors
        LIMIT 1
        """
        mnode = session.run(movie_info_q, title=movie_title).single()
        if mnode:
            movie_info = {
                "title": mnode.get("title") or movie_title,
                "year": mnode.get("year"),
                "genres": parse_genres_property(mnode.get("genres")),
                "actors": mnode.get("actors") or [],
                "directors": mnode.get("directors") or []
            }
        else:
            movie_info = {"title": movie_title, "year": None, "genres": [], "actors": [], "directors": []}

        results["movie"] = movie_info

        actor_q = """
        MATCH (m:Movies {title:$title})<-[:Acted_In]-(a:Actors)-[:Acted_In]->(rec:Movies)
        WHERE rec <> m
        RETURN rec.title AS movie, collect(a.actor_name) AS shared_actors
        LIMIT 20
        """
        results["actors"] = records_to_list(session.run(actor_q, title=movie_title))

        director_q = """
        MATCH (m:Movies {title:$title})<-[:Directed_In]-(d:Directors)-[:Directed_In]->(rec:Movies)
        WHERE rec <> m
        RETURN rec.title AS movie, d.director_name AS shared_director
        
        """
        results["directors"] = records_to_list(session.run(director_q, title=movie_title))

        # Genre-based: compute overlap in Python using fetched movie_info
        target_genres = movie_info.get("genres") or []
        if target_genres:
            genre_q2 = """
            MATCH (rec:Movies)
            WHERE rec.title <> $title
            RETURN rec.title AS movie, rec.genres AS genres
            LIMIT 20
            """
            candidates = session.run(genre_q2, title=movie_title)
            shared = []
            for row in candidates:
                rec_genres = parse_genres_property(row["genres"])
                common = [g for g in rec_genres if g in target_genres]
                if common:
                    shared.append({"movie": row["movie"], "shared_genres": common})
            results["genres"] = shared
        else:
            results["genres"] = []

        year_q = """
        MATCH (m:Movies {title:$title}), (rec:Movies)
        WHERE rec <> m AND abs(rec.year - m.year) <= 2
        RETURN rec.title AS movie, rec.year AS year
        LIMIT 20
        """
        results["year"] = records_to_list(session.run(year_q, title=movie_title))

        return results

# --- API routes ---

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    try:
        with driver.session() as session:
            res = session.run(
                "MATCH (m:Movies) WHERE toLower(m.title) CONTAINS toLower($q) "
                "RETURN m.title AS title ORDER BY m.year DESC LIMIT 20", q=q
            )
            return jsonify([r["title"] for r in res])
    except Exception as e:
        logging.exception("Search endpoint error")
        return jsonify({"error": "internal server error"}), 500

@app.route("/api/recommend")
def api_recommend():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    try:
        recs = get_recommendations(title)
        return jsonify(recs)
    except Exception as e:
        logging.exception("Recommend endpoint error")
        return jsonify({"error": "internal server error"}), 500

@app.route("/api/graph")
def api_graph():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Missing title"}), 400

    # Use coalesce to prefer title, then actor_name, then director_name, then empty string
    query = """
    MATCH (m:Movies {title: $title})-[r]-(x)
    RETURN id(m) AS source,
           id(x) AS target,
           labels(m)[0] AS source_label,
           labels(x)[0] AS target_label,
           coalesce(m.title, m.movie_title, m.name, '') AS source_title,
           coalesce(x.title, x.actor_name, x.director_name, x.name, '') AS target_title,
           type(r) AS rel_type
    """

    try:
        with driver.session() as session:
            results = session.run(query, {"title": title})

            nodes = {}
            links = []

            for row in results:
                # add source node (movie)
                sid = row["source"]
                if sid not in nodes:
                    nodes[sid] = {
                        "id": sid,
                        "label": row["source_label"],
                        "title": row["source_title"] or ""
                    }

                # add target node (actor/director/other)
                tid = row["target"]
                if tid not in nodes:
                    nodes[tid] = {
                        "id": tid,
                        "label": row["target_label"],
                        "title": row["target_title"] or ""
                    }

                links.append({
                    "source": sid,
                    "target": tid,
                    "type": row["rel_type"]
                })

            return jsonify({"nodes": list(nodes.values()), "links": links})

    except Exception as e:
        app.logger.exception("GRAPH ERROR")
        return jsonify({"error": str(e)}), 500

# --- UI route ---
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
