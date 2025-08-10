# File Description: news_bias_articles_clustered.csv
#
# This CSV file contains news articles enriched with bias scores across five dimensions:
# ideological_stance, factual_grounding, framing_choices, emotional_tone, source_transparency.
# 
# Additionally, articles are clustered *within each topic* into three political-leaning clusters:
#   0 = Conservative-leaning cluster
#   1 = Unbiased/Centrist cluster
#   2 = Liberal-leaning cluster
#
# Columns:
# - topic: Article topic/category (e.g., AI_policy, ClimateChange, Elections)
# - outlet: News outlet name
# - datetime: Publication date and time
# - title: Article headline/title
# - url: Article URL
# - sample_text: Article snippet (first 500 characters)
# - ideological_stance: Numeric ideological bias score (0=Left, 50=Center, 100=Right)
# - factual_grounding: Numeric factual grounding score (0=Low, 50=Medium, 100=High)
# - framing_choices: Numeric framing bias score (0=Biased, 50=Balanced, 100=Unbiased)
# - emotional_tone: Numeric emotional tone score (0=Neutral, 50=Mild, 100=Inflammatory)
# - source_transparency: Numeric source transparency score (0=Opaque, 50=Moderate, 100=Transparent)
# - cluster: Assigned cluster label within each topic (0=Conservative, 1=Unbiased, 2=Liberal)
#
# This clustering helps group articles into narrative or ideological groups per topic, 
# enabling analysis of how bias propagates differently across political leanings.
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

def narrative_clustering_and_labeling(
    input_csv="news_bias_articles_scored.csv", 
    output_csv="news_bias_articles_clustered_labeled.csv", 
    n_clusters=3
):
    # Load the scored CSV with ideological_stance scores
    df = pd.read_csv(input_csv)

    # Load Sentence-BERT model for embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Prepare lists for cluster IDs and cluster labels
    cluster_ids = [-1] * len(df)
    cluster_labels = [None] * len(df)

    print(f"Clustering articles within each topic into {n_clusters} clusters each...")

    # Process each topic separately
    for topic in df['topic'].unique():
        subset_idx = df[df['topic'] == topic].index.tolist()
        texts = df.loc[subset_idx, 'sample_text'].fillna("").tolist()

        # Filter out empty texts (no embeddings for empty texts)
        valid_indices = [i for i, t in enumerate(texts) if t.strip() != ""]
        if len(valid_indices) == 0:
            print(f"No valid texts for topic '{topic}', skipping.")
            continue
        texts_nonempty = [texts[i] for i in valid_indices]

        print(f"Computing embeddings for topic '{topic}' with {len(texts_nonempty)} articles...")
        embeddings = model.encode(texts_nonempty, show_progress_bar=True)

        # Adjust number of clusters if fewer texts than clusters
        n_clust = min(n_clusters, len(texts_nonempty))
        print(f"Clustering topic '{topic}' into {n_clust} clusters...")
        kmeans = KMeans(n_clusters=n_clust, random_state=42)
        labels = kmeans.fit_predict(embeddings)

        # Assign cluster IDs back to full dataframe indices for valid texts
        for i, label in zip(valid_indices, labels):
            cluster_ids[subset_idx[i]] = label

        # Prepare a temporary DataFrame slice with cluster assignments
        sub_df = df.loc[subset_idx].copy()
        sub_df['cluster_id'] = -1
        for i, label in zip(valid_indices, labels):
            sub_df.at[subset_idx[i], 'cluster_id'] = label

        # Calculate mean ideological_stance per cluster to map cluster IDs to labels
        cluster_means = sub_df.groupby('cluster_id')['ideological_stance'].mean().dropna()

        # Sort cluster IDs by ideological_stance ascending (liberal to conservative)
        sorted_clusters = cluster_means.sort_values().index.tolist()

        # Map sorted cluster IDs to human-readable labels
        bias_labels = ["Liberal", "Unbiased", "Conservative"]
        cluster_label_map = {}
        for i, cluster_id in enumerate(sorted_clusters):
            cluster_label_map[cluster_id] = bias_labels[i] if i < len(bias_labels) else f"Cluster_{cluster_id}"

        print(f"Topic '{topic}' cluster label mapping: {cluster_label_map}")

        # Assign cluster labels to all articles in topic
        for idx in subset_idx:
            c_id = cluster_ids[idx]
            if c_id in cluster_label_map:
                cluster_labels[idx] = cluster_label_map[c_id]
            else:
                cluster_labels[idx] = None

    # Add cluster ID and cluster label columns to the DataFrame
    df['cluster_id'] = cluster_ids
    df['cluster_label'] = cluster_labels

    # Save to output CSV
    df.to_csv(output_csv, index=False)
    print(f"Saved clustered and labeled articles to {output_csv}")

if __name__ == "__main__":
    narrative_clustering_and_labeling()