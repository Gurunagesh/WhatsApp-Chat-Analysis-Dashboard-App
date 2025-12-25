import pandas as pd
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
from nltk.util import ngrams
#import matplotlib.pyplot as plt
#import seaborn as sns
from wordcloud import WordCloud
from gensim import corpora
from gensim.models import LdaModel

def calculate_metrics(chat_df):
    """
    Calculates key chat metrics from the preprocessed DataFrame.
    """
    metrics = {}

    # 2.a. Total number of messages
    metrics['total_messages'] = len(chat_df)

    # 2.b. Number of unique participants (excluding 'System')
    metrics['unique_participants'] = chat_df[chat_df['Sender'] != 'System']['Sender'].nunique()

    # 2.c. Messages sent per participant
    metrics['messages_per_participant'] = chat_df['Sender'].value_counts()

    # 2.d. Busiest hours
    metrics['busiest_hours'] = chat_df['Timestamp'].dt.hour.value_counts()

    # 2.e. Busiest days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    busiest_days = chat_df['Timestamp'].dt.day_name().value_counts()
    metrics['busiest_days'] = busiest_days.reindex(day_order)

    # 2.f. Average message length
    metrics['average_message_length'] = chat_df['Message'].str.len().mean()

    # 2.g. Hourly message distribution for top 5 active users (excluding 'System')
    top_senders = chat_df[chat_df['Sender'] != 'System']['Sender'].value_counts().head(5).index.tolist()
    metrics['hourly_activity_top_senders'] = chat_df[chat_df['Sender'].isin(top_senders)].groupby(['Sender', chat_df['Timestamp'].dt.hour], observed=False).size().unstack(fill_value=0)

    return metrics

def preprocess_messages(chat_df):
    """
    Cleans messages in the DataFrame by removing URLs, special characters,
    converting to lowercase, and removing stopwords.
    """
    # 4.a. Ensure NLTK resources are downloaded
    try:
        stopwords.words('english')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        nltk.download('omw-1.4')

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # 4.b. Define a nested helper function to clean individual messages
    def _clean_message(message):
        message = str(message)
        # i. Remove URLs
        message = re.sub(r'http\S+|www\S+|https\S+', '', message, flags=re.MULTILINE)
        # ii. Remove special characters, numbers, and punctuation
        message = re.sub(r'[^a-zA-Z]', ' ', message)
        # iii. Convert the text to lowercase
        message = message.lower()
        # iv. Tokenize and remove stopwords/single-character words
        words = word_tokenize(message)
        words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words and len(word) > 1] # Ensure `word` is defined for the comprehension
        return ' '.join(words)

    # 4.c. Apply this helper function to the 'Message' column
    chat_df['Cleaned_Message'] = chat_df['Message'].apply(_clean_message)

    # 4.d. Return the chat_df with the new 'Cleaned_Message' column
    return chat_df

def generate_word_cloud(cleaned_messages):
    """
    Generates a word cloud image from cleaned messages.
    Excludes common, less meaningful words like 'media' and 'omitted'.
    """
    text = " ".join(cleaned_messages)
    # Add 'media' and 'omitted' to stopwords for word cloud generation
    custom_stopwords = set(stopwords.words('english'))
    custom_stopwords.update(['media', 'omitted', 'null', 'nan'])

    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        stopwords=custom_stopwords,
        min_font_size=10
    ).generate(text)

    return wordcloud.to_image()

def extract_keyphrases(cleaned_messages, top_n=20):
    """
    Extracts keyphrases (noun phrases) from cleaned messages.
    """
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    except LookupError:
        nltk.download('averaged_perceptron_tagger_eng')

    all_phrases = []
    grammar = r"""
        NP: {<DT|JJ|NN.*>+}
    """
    chunk_parser = nltk.RegexpParser(grammar)

    for message in cleaned_messages:
        tokens = word_tokenize(message)
        pos_tags = nltk.pos_tag(tokens)
        tree = chunk_parser.parse(pos_tags)

        for subtree in tree.subtrees():
            if subtree.label() == 'NP':
                phrase = " ".join([word for word, tag in subtree.leaves()])
                all_phrases.append(phrase)

    # Filter out common, less meaningful phrases
    filtered_phrases = [phrase for phrase in all_phrases if phrase.lower() not in ['media omitted', 'security code', 'tap learn'] and len(phrase.split()) > 1]

    phrase_freq = Counter(filtered_phrases)
    return pd.DataFrame(phrase_freq.most_common(top_n), columns=['Keyphrase', 'Frequency'])

def perform_topic_modeling(cleaned_messages, num_topics=5):
    """
    Performs Latent Dirichlet Allocation (LDA) Topic Modeling on cleaned messages.
    """
    tokenized_messages = [message.split() for message in cleaned_messages if message.strip()]

    if not tokenized_messages:
        return None

    # Create a dictionary and corpus for LDA
    dictionary = corpora.Dictionary(tokenized_messages)
    corpus = [dictionary.doc2bow(text) for text in tokenized_messages]

    # Train the LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15, random_state=100)

    topics_data = []
    for idx, topic in lda_model.print_topics(-1):
        topics_data.append({'Topic': f"Topic {idx+1}", 'Words': topic})

    return pd.DataFrame(topics_data)

def perform_content_analysis(chat_df):
    """
    Performs content analysis including word frequency, bigram frequency, and sentiment analysis.
    """
    content_analysis_results = {}

    # 6.a. Tokenize all cleaned messages
    all_words = ' '.join(chat_df['Cleaned_Message']).split()

    # 6.b. Calculate and return the top 20 most frequent words
    word_freq = Counter(all_words)
    content_analysis_results['top_20_words'] = pd.DataFrame(word_freq.most_common(20), columns=['Word', 'Frequency'])

    # Generate and store word cloud image
    content_analysis_results['word_cloud_image'] = generate_word_cloud(chat_df['Cleaned_Message'])

    # 6.c. Generate bigrams from the cleaned messages
    all_bigrams = []
    for message in chat_df['Cleaned_Message']:
        tokens = message.split()
        all_bigrams.extend(list(ngrams(tokens, 2)))

    # 6.d. Calculate and return the top 20 most frequent bigrams
    bigram_freq = Counter(all_bigrams)
    content_analysis_results['top_20_bigrams'] = pd.DataFrame(bigram_freq.most_common(20), columns=['Bigram', 'Frequency'])

    # Extract and store keyphrases
    content_analysis_results['top_keyphrases'] = extract_keyphrases(chat_df['Cleaned_Message'])

    # Perform and store topic modeling results
    content_analysis_results['topic_modeling_results'] = perform_topic_modeling(chat_df['Cleaned_Message'])

    # 6.e. Ensure NLTK vader_lexicon is downloaded
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

    sia = SentimentIntensityAnalyzer()

    # Function to get sentiment score
    def get_sentiment_score(text):
        return sia.polarity_scores(text)['compound']

    # Apply sentiment analysis
    chat_df['Sentiment_Score'] = chat_df['Cleaned_Message'].apply(get_sentiment_score)

    # Categorize sentiment
    def categorize_sentiment(score):
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    chat_df['Sentiment'] = chat_df['Sentiment_Score'].apply(categorize_sentiment)

    # 6.g. Return the sentiment distribution and sample messages
    content_analysis_results['sentiment_distribution'] = chat_df['Sentiment'].value_counts()
    content_analysis_results['sample_positive_messages'] = chat_df[chat_df['Sentiment'] == 'Positive']['Message'].head(5)
    content_analysis_results['sample_negative_messages'] = chat_df[chat_df['Sentiment'] == 'Negative']['Message'].head(5)
    content_analysis_results['sample_neutral_messages'] = chat_df[chat_df['Sentiment'] == 'Neutral']['Message'].head(5)

    return content_analysis_results