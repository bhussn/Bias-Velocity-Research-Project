# Step 2: Bias Scoring
import pandas as pd
from transformers import pipeline
import numpy as np
import time

OUTLET_TO_IDEOLOGY = {
    # Conservative outlets (matching your new keys exactly)
    "Fox News Politics": "conservative",
    "Fox News US Immigration": "conservative",
    "The Daily Caller": "conservative",
    "The Blaze": "conservative",
    "Breitbart": "conservative",
    "Breitbart Politics": "conservative",
    "National Review": "conservative",
    "The Washington Times": "conservative",
    "The Epoch Times": "conservative",
    "Newsmax": "conservative",
    "Townhall": "conservative",
    "The Federalist": "conservative",
    "Daily Wire": "conservative",
    "One America News": "conservative",
    "Washington Examiner": "conservative",
    "American Thinker": "conservative",
    "The American Conservative": "conservative",
    "The Daily Signal": "conservative",

    # Moderate outlets
    "Reuters": "moderate",
    "Associated Press Top News": "moderate",
    "Associated Press Politics": "moderate",
    "NPR General": "moderate",
    "NPR Politics": "moderate",
    "USA Today Nation": "moderate",
    "USA Today Politics": "moderate",
    "PBS NewsHour": "moderate",
    "PBS Newshour Politics": "moderate",
    "Bloomberg Politics": "moderate",
    "Politico": "moderate",
    "The Hill": "moderate",
    "CBS News Politics": "moderate",
    "ABC News Politics": "moderate",
    "The Wall Street Journal General": "moderate",
    "The Wall Street Journal Politics": "moderate",
    "Financial Times": "moderate",
    "The Christian Science Monitor": "moderate",
    "Axios Politics": "moderate",
    "BBC News US & Canada": "moderate",
    "Al Jazeera English": "moderate",

    # Liberal outlets
    "CNN Politics": "liberal",
    "CNN Immigration": "liberal",
    "The Guardian Immigration": "liberal",
    "Mother Jones": "liberal",
    "MSNBC Latest": "liberal",
    "HuffPost Politics": "liberal",
    "Vox": "liberal",
    "Daily Kos": "liberal",
    "Salon": "liberal",
    "The New Republic": "liberal",
    "The Atlantic": "liberal",
    "Slate": "liberal",
    "ThinkProgress (Archive)": "liberal",
    "The Nation": "liberal",
    "Common Dreams": "liberal",
    "Raw Story": "liberal",
    "Truthout": "liberal",
    "Democracy Now": "liberal",
}


# Bias dimensions, model returns lowercase labels, so lowercase here
BIAS_DIMENSIONS = {
    "ideological_stance": ["left", "center", "right"],
    "factual_grounding": ["low", "medium", "high"],
    "framing_choices": ["biased", "balanced", "unbiased"],
    "emotional_tone": ["neutral", "mild", "inflammatory"],
    "source_transparency": ["opaque", "moderate", "transparent"]
}

# Load zero-shot classifier pipeline once
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Map model labels to numeric ideology scores
model_label_to_score = {"left": 0, "center": 50, "right": 100}
# Map outlet labels (lowercase) to numeric ideology scores to match your ideology labels in data
outlet_label_to_score = {"liberal": 0, "moderate": 50, "conservative": 100}

def score_text(text, max_retries=3):
    results = {}
    for dim, labels in BIAS_DIMENSIONS.items():
        for attempt in range(max_retries):
            try:
                res = classifier(text, labels, multi_label=False)
                returned_labels = [label.lower() for label in res['labels']]
                probs = np.array(res['scores'])
                probs = probs / probs.sum()  # normalize
                
                label_to_score = {label: idx * 50 for idx, label in enumerate(labels)}
                weighted_score = sum(probs[i] * label_to_score[returned_labels[i]] for i in range(len(labels)))
                
                results[dim] = round(weighted_score, 2)
                break
            except Exception as e:
                print(f"Error scoring '{dim}', attempt {attempt + 1}/{max_retries}: {e}")
                time.sleep(1)
                if attempt == max_retries - 1:
                    results[dim] = None
    return results

def main():
    df = pd.read_csv("news_bias_articles.csv")
    total_rows = len(df)
    print(f"Total articles to process: {total_rows}")

    # Do NOT lowercase outlet names — keep as is for matching
    df['outlet'] = df['outlet'].str.strip()  # Just strip spaces, no lowercase

    # Add columns if missing
    for col in list(BIAS_DIMENSIONS.keys()) + ["ideology_label", "combined_ideological_stance"]:
        if col not in df.columns:
            df[col] = np.nan

    weight_outlet = 0.7  # weight of outlet ideology in final score
    weight_model = 0.3   # weight of model predicted ideology in final score

    for idx, row in df.iterrows():
        text = row.get('sample_text', "")
        if pd.isna(text) or not text.strip():
            print(f"Skipping empty text at index {idx}")
            continue

        outlet = row.get('outlet', "")
        outlet_label = OUTLET_TO_IDEOLOGY.get(outlet)
        if outlet_label is None:
            print(f"Unknown outlet ideology for '{outlet}' at index {idx}, skipping...")
            continue

        # Store outlet ideology label (lowercase)
        df.at[idx, "ideology_label"] = outlet_label

        # Get outlet ideology numeric score
        outlet_score = outlet_label_to_score[outlet_label]

        # Get model scores for all dimensions, including ideological_stance
        scores = score_text(text.strip())
        for dim in BIAS_DIMENSIONS.keys():
            df.at[idx, dim] = scores.get(dim)

        # Combine outlet and model ideological stance scores
        model_score = scores.get("ideological_stance")
        if model_score is None:
            combined_score = outlet_score  # fallback if model failed
        else:
            combined_score = round(weight_outlet * outlet_score + weight_model * model_score, 2)

        df.at[idx, "combined_ideological_stance"] = combined_score

        if (idx + 1) % 10 == 0 or (idx + 1) == total_rows:
            print(f"Processed {idx + 1}/{total_rows} ({(idx + 1) / total_rows * 100:.1f}%)")

    df.to_csv("news_bias_articles_scored.csv", index=False)
    print("Saved scored CSV as news_bias_articles_scored.csv")

if __name__ == "__main__":
    main()
