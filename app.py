import streamlit as st
import preprocessor
import utility
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os
#import shutil
#import pandas as pd
import datetime
import plotly.express as px





# Set up the basic Streamlit page configuration
st.set_page_config(page_title="WhatsApp Chat Analysis", layout="wide")

# Add a main title to the application
st.title("WhatsApp Chat Analysis Dashboard")

# --- Instructions for exporting WhatsApp chat data ---
with st.expander("How to export your WhatsApp chat data?"):
    st.markdown(
        """
        To analyze your WhatsApp chat data, you first need to export it from your mobile device.
        Follow these steps:

        **For Android Users:**
        1. Open the individual or group chat you want to export.
        2. Tap `More options` (three vertical dots) > `More` > `Export chat`.
        3. Choose `Without Media` (this is crucial for compatibility and faster processing).
        4. Select `Gmail` or another email client to send the `.zip` file to yourself.

        **For iOS Users (iPhone):**
        1. Open the individual or group chat you want to export.
        2. Tap the chat name in the top bar to open `Contact Info` or `Group Info`.
        3. Scroll down and tap `Export Chat`.
        4. Choose `Without Media` (this is crucial for compatibility and faster processing).
        5. Select `Mail` or another email client to send the `.zip` file to yourself.

        Once you have the `.zip` file(s), upload them using the file uploader below.
        """
    )

# Create a file uploader widget in the sidebar
st.sidebar.header("Upload Chat Files")
uploaded_files = st.sidebar.file_uploader('Upload WhatsApp Chat Zip Files (".zip")', type="zip", accept_multiple_files=True)

# Initialize chat_df as None or empty to handle cases where no file is uploaded yet
chat_df = None

sample_zip_filename = 'sample_whatsapp_chat.zip'

# Check if files are uploaded or use sample data
if uploaded_files:
    st.info("Using uploaded files for analysis.")
    # Create a temporary directory to save the uploaded zip files
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_file_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(tmpdir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            zip_file_paths.append(file_path)

        st.sidebar.success(f"Successfully uploaded {len(zip_file_paths)} files.")

        # 1. Load and preprocess data
        st.subheader("Data Loading and Preprocessing")
        with st.spinner('Loading and preprocessing chat data...'):
            chat_df = preprocessor.load_and_preprocess_data(zip_file_paths)

        if chat_df.empty:
            st.error("No valid chat data could be extracted from the uploaded files. Please ensure they are valid WhatsApp chat zip archives.")
        else:
            st.success(f"Successfully loaded {len(chat_df)} messages.\n")

            # 2. Preprocess messages for content analysis (before filtering to ensure all words are cleaned)
            with st.spinner('Cleaning messages for content analysis...'):
                chat_df = utility.preprocess_messages(chat_df)

            # --- Interactive Filters in Sidebar ---
            st.sidebar.header("Filter Data")

            # Sender filter
            all_senders = ['All'] + sorted(chat_df['Sender'].unique().tolist())
            selected_senders = st.sidebar.multiselect("Select Participants", all_senders, default='All')

            # Date range filter
            min_date = chat_df['Timestamp'].min().to_pydatetime()
            max_date = chat_df['Timestamp'].max().to_pydatetime()

            start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
            end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

            # Convert selected dates to datetime objects for filtering
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

            # Apply filters to create filtered_df
            filtered_df = chat_df[
                (chat_df['Timestamp'] >= start_datetime) &
                (chat_df['Timestamp'] <= end_datetime)
            ].copy() # Use .copy() to avoid SettingWithCopyWarning

            if 'All' not in selected_senders:
                filtered_df = filtered_df[filtered_df['Sender'].isin(selected_senders)]

            if filtered_df.empty:
                st.warning("No messages found for the selected filters.")
            else:
                st.success(f"Displaying {len(filtered_df)} messages after filtering.")

                # 3. Calculate metrics using filtered_df
                with st.spinner('Calculating chat metrics...'):
                    metrics = utility.calculate_metrics(filtered_df)

                # 4. Perform content analysis using filtered_df
                with st.spinner('Performing content analysis...'):
                    content_analysis_results = utility.perform_content_analysis(filtered_df)

                st.header("Dashboard Overview")
                st.subheader("Key Metrics")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Total Messages", value=metrics['total_messages'])
                with col2:
                    st.metric(label="Unique Participants (excl. System)", value=metrics['unique_participants'])
                with col3:
                    st.metric(label="Average Message Length", value=f"{metrics['average_message_length']:.2f} chars")

                st.subheader("Top 10 Senders")
                st.dataframe(metrics['messages_per_participant'].head(10), use_container_width=True)

                st.header("Interactive Charts")

                # Chart 1: Interactive Distribution of Messages per Hour of Day (Plotly)
                st.subheader("Message Distribution per Hour of Day")
                hourly_df = metrics['busiest_hours'].reset_index()
                hourly_df.columns = ['Hour of Day', 'Number of Messages']
                fig_hourly = px.bar(hourly_df, x='Hour of Day', y='Number of Messages',
                                    title='Interactive Distribution of Messages per Hour of Day',
                                    labels={'Hour of Day': 'Hour of Day', 'Number of Messages': 'Number of Messages'},
                                    color_discrete_sequence=px.colors.sequential.Viridis)
                st.plotly_chart(fig_hourly, use_container_width=True)

                # Chart 2: Distribution of Messages per Day of Week
                st.subheader("Message Distribution per Day of Week")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=metrics['busiest_days'].index, y=metrics['busiest_days'].values, palette='viridis', ax=ax)
                ax.set_title('Distribution of Messages per Day of Week')
                ax.set_xlabel('Day of Week')
                ax.set_ylabel('Number of Messages')
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig)
                plt.close(fig)

                # Chart 3: Daily Message Count Over Time
                st.subheader("Daily Message Count Over Time")
                daily_messages = chat_df.set_index('Timestamp').resample('D').size()
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.lineplot(x=daily_messages.index, y=daily_messages.values, color='purple', ax=ax)
                ax.set_title('Daily Message Count Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Messages')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig)
                plt.close(fig)

                # Chart 4: Hourly Activity of Top 5 Senders (Heatmap)
                st.subheader("Hourly Activity of Top 5 Senders")
                if not metrics['hourly_activity_top_senders'].empty:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    sns.heatmap(metrics['hourly_activity_top_senders'], cmap='viridis', annot=True, fmt='g', ax=ax)
                    ax.set_title('Hourly Activity of Top 5 Senders')
                    ax.set_xlabel('Hour of Day')
                    ax.set_ylabel('Sender')
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("Not enough data to show hourly activity for top senders with current filters.")

                st.header("Message Content Analysis")

                st.subheader("Top 20 Most Frequent Words")
                st.dataframe(content_analysis_results['top_20_words'], use_container_width=True)

                # Word Cloud Visualization
                st.subheader("Word Cloud")
                
                if content_analysis_results['word_cloud_image']:
                    st.image(content_analysis_results['word_cloud_image'], caption="Most Frequent Words (excluding common terms)")
                else:
                    st.warning("Word cloud could not be generated. Please ensure there is enough data for analysis.")

                st.subheader("Top 20 Most Frequent Bigrams")
                st.dataframe(content_analysis_results['top_20_bigrams'], use_container_width=True)

                # Keyphrase Extraction
                st.subheader("Top Keyphrases")
                st.dataframe(content_analysis_results['top_keyphrases'], use_container_width=True)

                # Topic Modeling Results
                st.subheader("Topic Modeling (LDA) Results")
                if content_analysis_results['topic_modeling_results'] is not None:
                    st.dataframe(content_analysis_results['topic_modeling_results'], use_container_width=True)
                else:
                    st.info("Not enough data to perform topic modeling or no clear topics found.")

                st.subheader("Sentiment Analysis Distribution")
                st.dataframe(content_analysis_results['sentiment_distribution'], use_container_width=True)

                st.subheader("Sample Messages by Sentiment")
                col_pos, col_neg, col_neu = st.columns(3)
                with col_pos:
                    st.info("Sample Positive Messages:")
                    st.dataframe(content_analysis_results['sample_positive_messages'], use_container_width=True)
                with col_neg:
                    st.warning("Sample Negative Messages:")
                    st.dataframe(content_analysis_results['sample_negative_messages'], use_container_width=True)
                with col_neu:
                    st.info("Sample Neutral Messages:")
                    st.dataframe(content_analysis_results['sample_neutral_messages'], use_container_width=True)

                with st.expander("View Raw Chat Data"):
                    st.dataframe(filtered_df, use_container_width=True)

else:
    # Use sample data if no files are uploaded
    if os.path.exists(sample_zip_filename):
        st.info(f"No files uploaded. Using sample data from '{sample_zip_filename}'.")
        zip_file_paths = [sample_zip_filename]

        st.subheader("Data Loading and Preprocessing")
        with st.spinner('Loading and preprocessing sample chat data...'):
            chat_df = preprocessor.load_and_preprocess_data(zip_file_paths)

        if chat_df.empty:
            st.error("No valid chat data could be extracted from the sample file.")
        else:
            st.success(f"Successfully loaded {len(chat_df)} messages from sample data.\n")

            # 2. Preprocess messages for content analysis (before filtering to ensure all words are cleaned)
            with st.spinner('Cleaning messages for content analysis...'):
                chat_df = utility.preprocess_messages(chat_df)

            # --- Interactive Filters in Sidebar ---
            st.sidebar.header("Filter Data")

            # Sender filter
            all_senders = ['All'] + sorted(chat_df['Sender'].unique().tolist())
            selected_senders = st.sidebar.multiselect("Select Participants", all_senders, default='All')

            # Date range filter
            min_date = chat_df['Timestamp'].min().to_pydatetime()
            max_date = chat_df['Timestamp'].max().to_pydatetime()

            start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
            end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

            # Convert selected dates to datetime objects for filtering
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

            # Apply filters to create filtered_df
            filtered_df = chat_df[
                (chat_df['Timestamp'] >= start_datetime) &
                (chat_df['Timestamp'] <= end_datetime)
            ].copy() # Use .copy() to avoid SettingWithCopyWarning

            if 'All' not in selected_senders:
                filtered_df = filtered_df[filtered_df['Sender'].isin(selected_senders)]

            if filtered_df.empty:
                st.warning("No messages found for the selected filters.")
            else:
                st.success(f"Displaying {len(filtered_df)} messages after filtering.")

                # 3. Calculate metrics using filtered_df
                with st.spinner('Calculating chat metrics...'):
                    metrics = utility.calculate_metrics(filtered_df)

                # 4. Perform content analysis using filtered_df
                with st.spinner('Performing content analysis...'):
                    content_analysis_results = utility.perform_content_analysis(filtered_df)

                st.header("Dashboard Overview")
                st.subheader("Key Metrics")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Total Messages", value=metrics['total_messages'])
                with col2:
                    st.metric(label="Unique Participants (excl. System)", value=metrics['unique_participants'])
                with col3:
                    st.metric(label="Average Message Length", value=f"{metrics['average_message_length']:.2f} chars")

                st.subheader("Top 10 Senders")
                st.dataframe(metrics['messages_per_participant'].head(10), use_container_width=True)

                st.header("Interactive Charts")

                # Chart 1: Interactive Distribution of Messages per Hour of Day (Plotly)
                st.subheader("Message Distribution per Hour of Day")
                hourly_df = metrics['busiest_hours'].reset_index()
                hourly_df.columns = ['Hour of Day', 'Number of Messages']
                fig_hourly = px.bar(hourly_df, x='Hour of Day', y='Number of Messages',
                                    title='Interactive Distribution of Messages per Hour of Day',
                                    labels={'Hour of Day': 'Hour of Day', 'Number of Messages': 'Number of Messages'},
                                    color_discrete_sequence=px.colors.sequential.Viridis)
                st.plotly_chart(fig_hourly, use_container_width=True)

                # Chart 2: Distribution of Messages per Day of Week
                st.subheader("Message Distribution per Day of Week")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=metrics['busiest_days'].index, y=metrics['busiest_days'].values, palette='viridis', ax=ax)
                ax.set_title('Distribution of Messages per Day of Week')
                ax.set_xlabel('Day of Week')
                ax.set_ylabel('Number of Messages')
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig)
                plt.close(fig)

                # Chart 3: Daily Message Count Over Time
                st.subheader("Daily Message Count Over Time")
                daily_messages = chat_df.set_index('Timestamp').resample('D').size()
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.lineplot(x=daily_messages.index, y=daily_messages.values, color='purple', ax=ax)
                ax.set_title('Daily Message Count Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Messages')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig)
                plt.close(fig)

                # Chart 4: Hourly Activity of Top 5 Senders (Heatmap)
                st.subheader("Hourly Activity of Top 5 Senders")
                if not metrics['hourly_activity_top_senders'].empty:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    sns.heatmap(metrics['hourly_activity_top_senders'], cmap='viridis', annot=True, fmt='g', ax=ax)
                    ax.set_title('Hourly Activity of Top 5 Senders')
                    ax.set_xlabel('Hour of Day')
                    ax.set_ylabel('Sender')
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("Not enough data to show hourly activity for top senders with current filters.")

                st.header("Message Content Analysis")

                st.subheader("Top 20 Most Frequent Words")
                st.dataframe(content_analysis_results['top_20_words'], use_container_width=True)

                # Word Cloud Visualization
                st.subheader("Word Cloud")
                
                if content_analysis_results['word_cloud_image']:
                    st.image(content_analysis_results['word_cloud_image'], caption="Most Frequent Words (excluding common terms)")
                else:
                    st.warning("Word cloud could not be generated. Please ensure there is enough data for analysis.")

                st.subheader("Top 20 Most Frequent Bigrams")
                st.dataframe(content_analysis_results['top_20_bigrams'], use_container_width=True)

                # Keyphrase Extraction
                st.subheader("Top Keyphrases")
                st.dataframe(content_analysis_results['top_keyphrases'], use_container_width=True)

                # Topic Modeling Results
                st.subheader("Topic Modeling (LDA) Results")
                if content_analysis_results['topic_modeling_results'] is not None:
                    st.dataframe(content_analysis_results['topic_modeling_results'], use_container_width=True)
                else:
                    st.info("Not enough data to perform topic modeling or no clear topics found.")

                st.subheader("Sentiment Analysis Distribution")
                st.dataframe(content_analysis_results['sentiment_distribution'], use_container_width=True)

                st.subheader("Sample Messages by Sentiment")
                col_pos, col_neg, col_neu = st.columns(3)
                with col_pos:
                    st.info("Sample Positive Messages:")
                    st.dataframe(content_analysis_results['sample_positive_messages'], use_container_width=True)
                with col_neg:
                    st.warning("Sample Negative Messages:")
                    st.dataframe(content_analysis_results['sample_negative_messages'], use_container_width=True)
                with col_neu:
                    st.info("Sample Neutral Messages:")
                    st.dataframe(content_analysis_results['sample_neutral_messages'], use_container_width=True)

                with st.expander("View Raw Chat Data"):
                    st.dataframe(filtered_df, use_container_width=True)

    else:
        st.warning("No sample_chat.zip found. Please upload your chat files or ensure 'sample_chat.zip' is in the correct directory.")