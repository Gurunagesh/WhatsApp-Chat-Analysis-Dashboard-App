import zipfile
import re
import pandas as pd

# Define the regex pattern for parsing chat lines
chat_pattern = r'^(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\u202f[ap]m) - (?:([^:]+): )?(.*)$'

def load_and_preprocess_data(zip_file_paths):
    """
    Loads multiple WhatsApp chat files from zip archives, consolidates, parses,
    and preprocesses the data into a pandas DataFrame.

    Args:
        zip_file_paths (list): A list of paths to WhatsApp chat zip files.

    Returns:
        pandas.DataFrame: A DataFrame containing the parsed and cleaned chat data.
    """
    all_raw_chat_content = []

    # 6. Iterate through each zip_path in zip_file_paths
    for zip_path in zip_file_paths:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 6.a & 6.b. Open each zip file and iterate through its contents, identify .txt files
                for name in zf.namelist():
                    if name.endswith('.txt') and 'WhatsApp Chat' in name:
                        with zf.open(name, 'r') as chat_file_in_zip:
                            # 6.c. Read the content and decode it
                            try:
                                file_content = chat_file_in_zip.read().decode('utf-8')
                            except UnicodeDecodeError:
                                try:
                                    file_content = chat_file_in_zip.read().decode('latin-1')
                                except UnicodeDecodeError:
                                    file_content = chat_file_in_zip.read().decode('cp1252')
                            # 6.d. Consolidate all decoded chat content
                            all_raw_chat_content.append(file_content)
        except FileNotFoundError:
            print(f"Error: The file '{zip_path}' was not found. Please ensure it's in the correct directory.")
        except zipfile.BadZipFile:
            print(f"Error: '{zip_path}' is not a valid zip file or is corrupted.")
        except Exception as e:
            print(f"An unexpected error occurred while processing {zip_path}: {e}")

    # Consolidate all raw chat content into a single string
    consolidated_data = '\n'.join(all_raw_chat_content)

    timestamps = []
    senders = []
    messages = []

    # 7. Split the consolidated string into individual lines
    lines = consolidated_data.split('\n')

    # 8. For each line, try to match it against the chat_pattern
    for line in lines:
        match = re.match(chat_pattern, line)
        if match:
            timestamps.append(match.group(1))
            senders.append(match.group(2))
            messages.append(match.group(3))
        else:
            # 8.b. If no match is found but there's a previous message, append current line
            if messages:
                messages[-1] += '\n' + line

    # 9. Create a pandas DataFrame
    chat_df = pd.DataFrame({
        'Timestamp': timestamps,
        'Sender': senders,
        'Message': messages
    })

    # 10. Standardize data types and handle nulls
    # 10.a. Replace the narrow no-break space with a regular space
    # First ensure 'Timestamp' column is string type before applying .str accessor
    if chat_df['Timestamp'].dtype != 'object':
        chat_df['Timestamp'] = chat_df['Timestamp'].astype(str)
    chat_df['Timestamp'] = chat_df['Timestamp'].str.replace('\u202f', ' ', regex=False)

    # 10.b. Convert the 'Timestamp' column to datetime objects
    chat_df['Timestamp'] = pd.to_datetime(chat_df['Timestamp'], format='%d/%m/%y, %I:%M %p', errors='coerce')

    # 10.c. Fill any NaN values in the 'Sender' column with 'System'
    chat_df['Sender'] = chat_df['Sender'].fillna('System')

    # 10.d. Convert the 'Sender' column to the 'category' dtype
    chat_df['Sender'] = chat_df['Sender'].astype('category')

    # 10.e. Convert the 'Message' column to the 'string' dtype
    chat_df['Message'] = chat_df['Message'].astype('string')

    # 11. Return the processed chat_df
    return chat_df