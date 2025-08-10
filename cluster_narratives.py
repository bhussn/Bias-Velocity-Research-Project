import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def score_to_label(score):
    if pd.isna(score):
        return "Unknown"
    elif score <= 33:
        return "Liberal"
    elif score <= 66:
        return "Moderate"
    else:
        return "Conservative"

def analyze_velocity(input_csv="news_bias_articles_scored.csv"):
    # Load data with datetime parsing
    df = pd.read_csv(input_csv, parse_dates=['datetime'])

    # Map numeric ideological stance to label
    df['combined_ideology_label'] = df['ideological_stance'].apply(score_to_label)

    # Clean dataset
    df = df.dropna(subset=['datetime', 'combined_ideology_label', 'outlet'])

    # Sort by datetime ascending
    df = df.sort_values('datetime')

    print(f"Total articles analyzed: {len(df)}\n")

    # === Per ideology summary ===
    first_article_times = {}
    for ideology in ['Liberal', 'Moderate', 'Conservative']:
        sub = df[df['combined_ideology_label'] == ideology]
        if len(sub) == 0:
            print(f"No articles found for ideology: {ideology}\n")
            continue

        start_time = sub['datetime'].min()
        end_time = sub['datetime'].max()
        count = len(sub)
        first_article_times[ideology] = start_time

        print(f"Ideology: {ideology}")
        print(f"  Articles: {count}")
        print(f"  Time range: {start_time} to {end_time}")
        print(f"  First 3 articles:")
        print(sub[['datetime', 'outlet', 'title']].head(3).to_string(index=False))
        print(f"  Last 3 articles:")
        print(sub[['datetime', 'outlet', 'title']].tail(3).to_string(index=False))
        print()

    # === Publication counts per day per ideology ===
    df['date'] = df['datetime'].dt.date
    counts = df.groupby(['date', 'combined_ideology_label']).size().unstack(fill_value=0)
    print("Publication counts per day per ideology:")
    print(counts)
    print()

    # === Calculate lag times between first article publications (in hours) per ideology ===
    print("Lag times between first article publications (hours):")
    ideologies = ['Liberal', 'Moderate', 'Conservative']
    for i in range(len(ideologies)):
        for j in range(i+1, len(ideologies)):
            a, b = ideologies[i], ideologies[j]
            if a in first_article_times and b in first_article_times:
                lag = (first_article_times[b] - first_article_times[a]).total_seconds() / 3600
                print(f"  {a} -> {b}: {lag:.2f} hours")
    print()

    # === Per outlet first article times (to find initiators) ===
    print("First article publication times per outlet:")
    outlets = df['outlet'].unique()
    outlet_first_times = {}
    for outlet in outlets:
        out_sub = df[df['outlet'] == outlet]
        first_time = out_sub['datetime'].min()
        outlet_first_times[outlet] = first_time
        print(f"  {outlet}: {first_time}")
    print()

    # === Visualization: Timeline scatter plot with ideological stance ===
    plt.figure(figsize=(14, 7))
    sns.scatterplot(
        data=df, 
        x='datetime', 
        y='ideological_stance', 
        hue='combined_ideology_label', 
        style='combined_ideology_label',
        palette={'Liberal':'blue', 'Moderate':'green', 'Conservative':'red'}, 
        s=100,
        alpha=0.7
    )
    plt.title("Publication Timeline: Ideological Stance Over Time")
    plt.xlabel("Publication DateTime")
    plt.ylabel("Ideological Stance Score (0=Liberal, 100=Conservative)")
    plt.legend(title="Ideology")
    plt.tight_layout()
    plt.show()

    # === Additional Visualization: Article count over time by ideology and outlet ===
    plt.figure(figsize=(14, 6))
    sns.lineplot(
        data=df, 
        x='date', 
        y=df.groupby(['date', 'combined_ideology_label']).size().reindex(df['date']).values, 
        hue='combined_ideology_label',
        palette={'Liberal':'blue', 'Moderate':'green', 'Conservative':'red'}
    )
    plt.title("Daily Publication Counts by Ideology")
    plt.xlabel("Date")
    plt.ylabel("Number of Articles")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_velocity()