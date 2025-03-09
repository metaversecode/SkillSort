# Import Libraries
import pandas as pd
import re
import string
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load Dataset
resume_df = pd.read_csv('Resume.csv', encoding='utf-8')

def clean_text(text):
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

# Apply cleaning to resume text (using the 'Resume_str' column)
resume_df['cleaned_resume'] = resume_df['Resume_str'].apply(clean_text)

# ------------------------------
# Pie Chart: Resume Category Distributions
# ------------------------------
if 'Category' in resume_df.columns:
    category_counts = resume_df['Category'].value_counts()
    plt.figure(figsize=(8,8))
    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title("Resume Category Distribution")
    plt.axis('equal')
    plt.show()

# ------------------------------
# Skill-based Candidate Matching & Rankings
# ------------------------------

# Get user input for the skill
skill_query = input("Enter the skill you are looking for: ").strip().lower()

# Build TF-IDF vectorizer (using unigrams and bigrams, and min_df=1 to keep rare terms)
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
resume_tfidf = vectorizer.fit_transform(resume_df['cleaned_resume'])
query_tfidf = vectorizer.transform([skill_query])

# Check if the query term is in the vocabulary
if skill_query not in vectorizer.vocabulary_:
    print(f"Note: The term '{skill_query}' is not in the vocabulary. Using count-based scoring instead.")

# Compute cosine similarity scores
similarity_scores = cosine_similarity(query_tfidf, resume_tfidf)[0]

# If maximum similarity is 0, use a fallback count-based matching:
if max(similarity_scores) == 0:
    print("Cosine similarity returned 0 for all candidates. Falling back to simple count-based matching.")
    resume_df['Match_Score'] = resume_df['cleaned_resume'].apply(lambda x: x.split().count(skill_query))
else:
    resume_df['Match_Score'] = similarity_scores

# Sort candidates by Match_Score in descending order
ranked_candidates = resume_df[['ID', 'Resume_str', 'Match_Score']].sort_values(by='Match_Score', ascending=False)

# Display Top Candidates (only showing candidates with a score > 0)
top_candidates = ranked_candidates[ranked_candidates['Match_Score'] > 0]
if top_candidates.empty:
    print(f"No candidates found with the skill: {skill_query}")
else:
    print("\nTop Ranked Candidates:")
    top_candidates = top_candidates.reset_index(drop=True)
    top_candidates['Rank'] = top_candidates.index + 1
    for _, row in top_candidates.iterrows():
        print(f"ID: {row['ID']} | Rank: {row['Rank']} | Score: {row['Match_Score']:.2f}")
        print(f"Summary: {row['Resume_str'][:300]}...")  # Show first 300 characters
        print("-" * 80)

    # Write the ranked candidate list to a text file
    with open("ranked_candidates.txt", "w", encoding="utf-8") as f:
        f.write("Top Ranked Candidates:\n")
        for _, row in top_candidates.iterrows():
            f.write(f"Rank: {row['Rank']} | ID: {row['ID']} | Score: {row['Match_Score']:.2f}\n")
            f.write(f"Summary: {row['Resume_str'][:300]}...\n")
            f.write("-" * 80 + "\n")
    print("\nRanked candidate details have been written to 'ranked_candidates.txt'.")

    # Bar Graph: Plot the top 10 candidates, increase also
    plot_data = top_candidates.head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Match_Score', y=plot_data['ID'].astype(str), data=plot_data, palette='viridis')
    plt.xlabel("Match Score")
    plt.ylabel("Candidate ID")
    plt.title(f"Top Candidates for '{skill_query}'")
    plt.show()
