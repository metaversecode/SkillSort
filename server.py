from flask import Flask, jsonify, request, render_template, send_file
import os
import pandas as pd
import re
import string
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import send_from_directory

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CSV_FILE = "Resume.csv"
OUTPUT_FILE = "ranked_candidates.txt"
OUTPUT_PATH = os.path.join(os.getcwd(), OUTPUT_FILE)

def load_resume_data():
    """Loads resume data only when required."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8")
        if 'Resume_str' in df.columns:
            df['cleaned_resume'] = df['Resume_str'].apply(clean_text)
        return df
    return pd.DataFrame(columns=["ID", "Resume_str", "Category"])

def clean_text(text):
    """Cleans text for processing."""
    if isinstance(text, str):
        text = text.lower()
        text = re.sub(r'http\S+\s*', ' ', text)
        text = re.sub(r'RT|cc', ' ', text)
        text = re.sub(r'#\S+', '', text)
        text = re.sub(r'@\S+', ' ', text)
        text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
        text = re.sub(r'[^\x00-\x7f]', r' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    return ""

# -----------------------------------------------------------------
# 📊 Category Distribution API (Pie Chart Data)
# -----------------------------------------------------------------
@app.route('/api/category_distribution', methods=['GET'])
def category_distribution():
    resume_df = load_resume_data()
    if 'Category' in resume_df.columns:
        category_counts = resume_df['Category'].value_counts()
        data = {
            'labels': list(category_counts.index.astype(str)),
            'values': [int(v) for v in category_counts.values]
        }
    else:
        data = {'labels': [], 'values': []}
    return jsonify(data)

# -----------------------------------------------------------------
# 🏆 Candidate Ranking API (Bar Chart Data)
# -----------------------------------------------------------------
def get_candidate_rankings(skill_query):
    """Fetch top candidates based on skill matching."""
    resume_df = load_resume_data()
    if resume_df.empty:
        return []

    skill_query = skill_query.strip().lower()
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
    resume_tfidf = vectorizer.fit_transform(resume_df['cleaned_resume'])
    query_tfidf = vectorizer.transform([skill_query])

    similarity_scores = cosine_similarity(query_tfidf, resume_tfidf)[0]

    if max(similarity_scores) == 0:
        resume_df['Match_Score'] = resume_df['cleaned_resume'].apply(lambda x: x.split().count(skill_query))
    else:
        resume_df['Match_Score'] = similarity_scores

    ranked_candidates = resume_df[['ID', 'Resume_str', 'Match_Score']].sort_values(by='Match_Score', ascending=False)
    top_candidates = ranked_candidates[ranked_candidates['Match_Score'] > 0].reset_index(drop=True)
    top_candidates['Rank'] = top_candidates.index + 1

    return [
        {
            'ID': int(row['ID']),
            'Resume_str': row['Resume_str'],
            'Match_Score': float(row['Match_Score']),
            'Rank': int(row['Rank'])
        }
        for _, row in top_candidates.head(350).iterrows()
    ]

@app.route('/api/candidate_rankings', methods=['GET'])
def candidate_rankings():
    skill_query = request.args.get('skill', '')
    if not skill_query:
        return jsonify({'error': 'Skill parameter is required'}), 400
    results = get_candidate_rankings(skill_query)
    return jsonify(results)

# -----------------------------------------------------------------
# 📂 File Upload API
# -----------------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file.filename.endswith(".csv"):
        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)
        return jsonify({"message": f"File {file.filename} uploaded successfully!"})
    else:
        return jsonify({"message": "Only CSV files are allowed"}), 400

@app.route('/api/generate_ranked_candidates', methods=['GET'])
def generate_ranked_candidates():
    skill_query = request.args.get('skill', '').strip()
    if not skill_query:
        return jsonify({'message': 'Skill parameter is required'}), 400

    top_candidates = get_candidate_rankings(skill_query)
    if not top_candidates:
        return jsonify({'message': 'No matching candidates found'}), 404

    # Write results to the file using the absolute path
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("Ranked Candidates based on skill: " + skill_query + "\n\n")
        for candidate in top_candidates:
            f.write(f"Rank: {candidate['Rank']}, ID: {candidate['ID']}, Match Score: {candidate['Match_Score']:.2f}\n")
            f.write(f"Resume: {candidate['Resume_str'][:300]}...\n\n")

    return jsonify({'download_url': '/download_ranked_candidates'})

# -----------------------------------------------------------------
# Download the Generated Ranked Candidates File
# -----------------------------------------------------------------
@app.route('/download_ranked_candidates', methods=['GET'])
def download_ranked_candidates():
    if not os.path.exists(OUTPUT_PATH):
        return jsonify({'message': 'File not found'}), 404
    return send_file(OUTPUT_PATH, as_attachment=True)

#---------------------------------------------------------
# 🏠 Serve the UI (Optional)
# -----------------------------------------------------------------
@app.route('/')
def index():
    return render_template('main.html')
@app.route('/analysis')
def indexs():
    return render_template('analysis.html')
if __name__ == '__main__':
    app.run(debug=True, port=5300)
