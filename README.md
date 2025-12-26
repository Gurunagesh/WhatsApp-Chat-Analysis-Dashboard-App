---
title: WhatsApp Chat Analysis
emoji: 📊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.25.0"
app_file: app.py
pinned: false
---

# 📊 WhatsApp Chat Analysis Dashboard

## Overview

WhatsApp chats contain a huge amount of hidden information—activity patterns, engagement levels, sentiment, and recurring topics—but they are completely unstructured and hard to analyze manually.
This is a Streamlit-based app for analyzing WhatsApp chat data. Upload your chat files to visualize insights such as message distribution, sentiment analysis, and more.

This project is an **interactive Streamlit-based dashboard** that converts raw WhatsApp chat exports into **clear, visual, and actionable insights**. Instead of scrolling through thousands of messages, users can instantly understand **who talks the most, when conversations peak, what topics dominate, and what the overall sentiment looks like**.

The application is built using **Python, Pandas, NLP (NLTK), and interactive visualization libraries**, and works for both **group chats and individual conversations**.

---

## Problem Statement

### The Challenge of Unstructured Chat Data

WhatsApp conversations are rich in information but difficult to analyze due to:

1. **Manual analysis being impractical**
   Large chats can contain thousands of messages, making trend identification slow and error-prone.

2. **Lack of visibility into chat dynamics**
   Users cannot easily identify active participants, peak activity times, or conversation flow.

3. **Content overload**
   Important topics, recurring phrases, or emotional trends are buried inside raw message logs.

### Solution

This dashboard **automates the entire analysis pipeline**, transforming raw `.zip` WhatsApp exports into **interactive reports, metrics, and visualizations**, enabling fast and meaningful insights with minimal effort.

---

## Key Features

### 📂 Data Handling

* **Multi-file upload support**: Analyze multiple WhatsApp chat `.zip` files together
* **Robust chat parsing**: Handles timestamps, senders, multi-line messages, emojis, and special characters
* **Automated data cleaning**: Unicode normalization, missing sender handling, and data-type corrections

### 📈 Analytics & Metrics

* Total messages and unique participants
* Messages per participant
* Busiest hours of the day and days of the week
* Average message length

### 📊 Interactive Visualizations

* Hour-wise message distribution (interactive bar chart – Plotly)
* Day-wise message distribution
* Daily message trend over time
* Heatmap showing hourly activity of top 5 participants

### 🧠 Content & NLP Analysis

* Top 20 most frequent words and bigrams
* Word Cloud for commonly used terms
* **Keyphrase extraction** to identify important phrases
* **Sentiment analysis** (Positive / Neutral / Negative) with sample messages

### 🎛 User Controls

* Filter results by specific participants
* Filter analysis by date range
* Preloaded **sample data** for instant exploration
* Built-in step-by-step guide for exporting WhatsApp chats

---

## Technologies Used

* **Python** – Core application logic and data processing
* **Streamlit** – Interactive web dashboard
* **Pandas** – Data manipulation and analysis
* **NLTK** – Tokenization, stopwords, POS tagging, VADER sentiment analysis
* **Regex** – Reliable parsing of WhatsApp chat formats
* **Matplotlib & Seaborn** – Static visualizations
* **Plotly Express** – Interactive charts
* **WordCloud** – Visual representation of frequent terms

---

## Insights & Metrics Provided

The dashboard enables users to quickly understand:

* **Chat scale**: Total messages and number of participants
* **Top contributors**: Most active participants by message count
* **Peak activity periods**:

  * Commonly busy hours (often evenings, e.g., 7–9 PM in sample data)
  * Most active days (e.g., Fridays showing higher engagement)
* **Conversation style**: Average message length trends
* **Topic discovery**:

  * Word clouds and frequent terms reveal recurring subjects
  * Keyphrases highlight important discussions
* **Emotional tone**:

  * Neutral messages often indicate information sharing
  * Positive spikes reflect celebrations or good news
  * Negative sentiment may signal conflicts or challenges

These insights act as **benchmarks for engagement, communication health, and interaction patterns**.

---

## Demo

🔗 *Live demo walkthrough link goes here*
((https://gurunagesh1477-whatsapp-chat-analysis-dashboard-app.hf.space))
---

## Getting Started

### Prerequisites

* Python **3.8 or higher**

### Installation & Setup

1. **Save project files**
   Place the following in one directory:

   * `app.py`
   * `preprocessor.py`
   * `utility.py`
   * `requirements.txt`
   * `sample_chat.zip` (optional, for demo use)

2. **Open terminal and navigate to the directory**

3. **Create and activate a virtual environment (recommended)**

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Run the application**

```bash
streamlit run app.py
```

6. **Open in browser**
   The app will launch automatically (usually at `http://localhost:8501`).

---

## Exporting WhatsApp Chat Data

> These instructions are also available inside the app UI.

### Android

1. Open the chat (group or individual)
2. Tap **More options (⋮)** → **More** → **Export chat**
3. Select **Without Media**
4. Send the `.zip` file to yourself via email

### iOS (iPhone)

1. Open the chat
2. Tap the chat name → **Contact Info / Group Info**
3. Tap **Export Chat**
4. Select **Without Media**
5. Send the `.zip` file via Mail

---

## Future Enhancements

* Topic modeling for automatic theme discovery
* Sender interaction network visualization
* Message volume and topic trend forecasting
* Emotion-level sentiment analysis
* Conversation summarization
* Exportable reports (CSV / PDF)
* UI/UX enhancements and accessibility improvements

---

## Contributing

Contributions are welcome.
Fork the repository, open issues, or submit pull requests to improve the project.

---

## License

This project is open-source and available under the **MIT License** .

---
