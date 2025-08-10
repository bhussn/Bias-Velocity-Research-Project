# Proof of Concept: Narrative Velocity in ICE-related Media Coverage

## Overview  
This project demonstrates the concept of **narrative velocity** — how immigration-related narratives about ICE emerge and spread at different speeds across media outlets with varying ideological stances.

## Framework Workflow  
The workflow consists of four main steps:  
1. **Scrape Outlets:** Collect articles from diverse news outlets across ideological spectrums using RSS feeds and web scraping.  
2. **Score Bias:** Apply AI-powered models to assign multidimensional bias scores to each article (ideological stance, factual grounding, framing choices, emotional tone, source transparency).  
3. **Cluster Labels:** Group articles based on similarity in bias scores and narrative content to identify coherent narrative clusters.  
4. **Cluster Narrative:** Analyze temporal patterns within clusters to map narrative velocity — who initiates, amplifies, or responds to narratives over time.

## Methodology  
We collected 9 articles mentioning ICE from conservative, moderate, and liberal news outlets over a three-day period. Each article was labeled by outlet ideology and timestamped. We analyzed the volume and timing of publications across ideologies to understand narrative propagation.

## Preliminary Findings  
- **Narrative Initiation:** Liberal outlets led coverage, publishing earliest (Aug 7–8).  
- **Narrative Spread:** Conservative outlets followed about a day later, while moderate outlets published later and in a tighter time frame (Aug 9).  
- **Publication Volume:** Liberal and conservative outlets’ publications were more spread out over time; moderate outlets clustered their coverage.  
- **Implication:** Temporal patterns suggest narratives spread non-uniformly, supporting the hypothesis that different ideological communities function as initiators, amplifiers, or late responders in biased narrative propagation.  
- **Roles in This Study:** Liberal outlets acted as initiators, conservative outlets as amplifiers, and moderate outlets as late responders in the spread of ICE-related narratives.

## Limitations  
- Small sample size (9 articles) and limited time frame may not capture full narrative complexity.  
- Focused solely on ICE-related coverage; results may not generalize to other topics.  
- Automated bias scoring models may introduce classification errors or bias.  
- Data collection via RSS feeds and web scraping might have missed relevant content.

## Future Steps  
- Expand dataset with more articles, longer time frames, and multiple topics.  
- Include social media and digital-native outlets for broader ecosystem coverage.  
- Refine bias scoring models with additional training and human validation.  
- Develop interactive visualizations and real-time dashboards to track narrative velocity.  
- Collaborate with media experts for qualitative validation and to explore early intervention strategies based on narrative detection.
