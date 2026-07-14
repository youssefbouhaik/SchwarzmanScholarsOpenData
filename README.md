# The Subtext Engine: Schwarzman Scholars Video Analysis

Welcome to the **Subtext Engine**, an open-source project designed to reverse-engineer the unspoken cues that make a global leader stand out.

While traditional advice focuses on the text of an application, human judgment relies heavily on **subtext**: lighting, setting, pacing, body language, and environmental cues. This project aggregates public introduction videos from admitted Schwarzman Scholars to systematically analyze the visual and tonal subtext of successful applicants.

## 🎯 The Vision
We believe that the intuitive cues humans use to judge "leadership potential" (e.g., choosing to film outside vs. in a formal office, dynamic camera movement vs. static framing, the warmth of the lighting) can be translated to a machine.

**Our ultimate goal:** To provide a GitHub Pages web app where future applicants can submit their draft YouTube video links. The engine will run the video against our historical dataset of admitted scholars, extracting the visual/subtextual cues, and provide a "Standout Percentage" to help them refine their narrative.

## ⚠️ Acknowledging the Limitations
We are building this with our eyes wide open to the inherent limitations of the data:
1. **Survivorship & Sharing Bias:** Our dataset relies entirely on scholars who chose to make their introduction videos public. 
2. **The Video is Not the Application:** The intro video is just one piece of the puzzle. We do not have access to essays, transcripts, or recommendation letters. 
3. **Correlation vs. Causation:** Filming outside doesn't *get* you admitted, but it may correlate with a specific archetype of candidate that the committee is currently looking for.

Despite these limitations, analyzing the subtext of the one piece of the application we *can* see is a powerful tool for demystifying elite admissions.

## 🧠 How It Works (Roadmap)
1. **Historical Video Corpus:** Aggregating public 1-minute intro videos from past cohorts.
2. **Subtext Extraction:** Using multimodal AI to analyze non-verbal cues:
   - *Setting:* Indoor vs. Outdoor, Office vs. Field.
   - *Production Value:* Smartphone raw vs. highly edited.
   - *Lighting & Tone:* Warm, harsh, dynamic, static.
3. **The Standout Scorer:** A web interface hosted on GitHub Pages that compares a user-submitted video against the established archetypes of admitted scholars.

## 🤝 Contributing
Are you a Schwarzman Scholar with a public video? Or an AI engineer interested in computer vision and multimodal subtext extraction? 
Check out [CONTRIBUTING.md](CONTRIBUTING.md) to see how you can help build the Subtext Engine.
