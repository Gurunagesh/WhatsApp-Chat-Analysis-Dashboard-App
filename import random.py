import random
from datetime import datetime, timedelta

# Participants
participants = [
    "~ Priya", "~ Ravi", "~ Sneha", "~ Arjun",
    "+91 98765 43210", "+91 91234 56789", "+91 99887 77665"
]

# Sample messages
messages = [
    "Hello everyone! Let's coordinate here.",
    "<Media omitted>",
    "Reminder: Registration closes tomorrow at 5 pm.",
    "Please don’t wait till the last minute.",
    "Joining the meeting now.",
    "Uploaded the company brochure.",
    "Agenda: Resume review and mock interviews.",
    "Thanks for the reminder!",
    "Don’t forget to update your resumes in the shared folder.",
    "This is important for tomorrow’s HR round.",
    "Updated mine, please check.",
    "Great discussion today, thanks everyone!",
    "Uploaded the mock interview schedule.",
    "All set for tomorrow’s drive!"
]

# Start date
start_date = datetime(2025, 2, 1, 8, 0)

lines = []
for i in range(1000):
    # Increment time randomly
    msg_time = start_date + timedelta(minutes=random.randint(1, 5000))
    date_str = msg_time.strftime("%d/%m/%y, %I:%M %p")

    
    # Pick participant and message
    sender = random.choice(participants)
    msg = random.choice(messages)
    
    # Format line
    line = f"{date_str} - {sender}: {msg}"
    lines.append(line)

# Add system messages at intervals
lines.insert(0, "01/02/25, 8:00 am - Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. Learn more.")
lines.insert(1, "01/02/25, 8:01 am - ~ Priya created group \"Campus Drive 2026 - Team A\"")
lines.insert(2, "01/02/25, 8:01 am - You were added")

# Save to file
with open("synthetic_whatsapp_chat.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Synthetic dataset with 1000+ lines generated!")
