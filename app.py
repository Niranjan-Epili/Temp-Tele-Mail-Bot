from telebot import TeleBot
from requests import get
import shelve  # For simple data persistence

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
bot = TeleBot('YOUR_BOT_TOKEN')

# Database file for storing temporary emails
db_file = 'temp_emails.db'

# Function to create a new temporary email
@bot.message_handler(commands=['start', 'new'])
def create_temp_email(message):
    user_id = message.chat.id
    with shelve.open(db_file) as db:
        response = get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        if response.status_code == 200:
            temp_email = response.json()[0]
            db[str(user_id)] = temp_email  # Store the email with user_id as key
            bot.send_message(user_id, f"✨ Your new temporary email is: {temp_email} ✨\n\n"
                                      f"📬 Use this email to receive messages without exposing your real one. "
                                      f"Check your inbox anytime with the /inbox command!"
                                      f"By @ifeelnj01")
        else:
            bot.send_message(user_id, "😕 Sorry, I cannot create a temporary email at the moment. Please try again later.")

# Function to check the inbox of the temporary email
@bot.message_handler(commands=['inbox'])
def check_inbox(message):
    user_id = message.chat.id
    with shelve.open(db_file) as db:
        temp_email = db.get(str(user_id))  # Retrieve the email using user_id
        if temp_email:
            domain = temp_email.split('@')[1]
            login = temp_email.split('@')[0]
            response = get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}')
            if response.status_code == 200:
                emails = response.json()
                if emails:
                    for email in emails:
                        bot.send_message(user_id, f"📧 From: {email['from']}\n"
                                                  f"📄 Subject: {email['subject']}\n"
                                                  f"🔍 Read the full email with /read {email['id']}")
                else:
                    bot.send_message(user_id, "📭 Your inbox is empty.")
            else:
                bot.send_message(user_id, "😕 Sorry, I cannot check the inbox at the moment. Please try again later.")
        else:
            bot.send_message(user_id, "⚠️ You don't have a temporary email yet. Create one with /new")

# Function to read a specific email
@bot.message_handler(commands=['read'])
def read_email(message):
    user_id = message.chat.id
    with shelve.open(db_file) as db:
        temp_email = db.get(str(user_id))
        if temp_email:
            email_id = message.text.split()[1] if len(message.text.split()) > 1 else None
            if email_id:
                domain = temp_email.split('@')[1]
                login = temp_email.split('@')[0]
                response = get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={email_id}')
                if response.status_code == 200:
                    email_content = response.json()
                    bot.send_message(user_id, f"📧 From: {email_content['from']}\n"
                                              f"📄 Subject: {email_content['subject']}\n"
                                              f"📜 Body:\n{email_content['textBody']}")
                else:
                    bot.send_message(user_id, "😕 Sorry, I cannot read the email at the moment. Please try again later.")
            else:
                bot.send_message(user_id, "⚠️ Please provide the ID of the email you want to read. Use /inbox to see IDs.")
        else:
            bot.send_message(user_id, "⚠️ You don't have a temporary email yet. Create one with /new")

# Function to delete the temporary email
@bot.message_handler(commands=['delete'])
def delete_temp_email(message):
    user_id = message.chat.id
    with shelve.open(db_file) as db:
        if str(user_id) in db:
            del db[str(user_id)]  # Delete the email from the database
            bot.send_message(user_id, "🗑️ Your temporary email has been deleted. Your privacy is our priority!")
        else:
            bot.send_message(user_id, "⚠️ You don't have a temporary email to delete. Create one with /new")

# Start the bot
bot.polling()
