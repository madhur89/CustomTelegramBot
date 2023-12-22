from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

TOKEN = "6685619767:AAFMEjP3toYFgvQa7AnkIVih09STE-nqJD0"

# Replace with your group chat IDs and their respective names
GROUP_CHAT_IDS = {"Group1": -1001788330922, "Group2": -1002115769902}

# Dictionary to store the previous member counts for each group
previous_member_counts = {group_name: 0 for group_name in GROUP_CHAT_IDS}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bot is active. You will receive notifications for new joins and leaves.")
    # Schedule the job to send member count every 20 seconds for each group
    for group_name, group_chat_id in GROUP_CHAT_IDS.items():
        context.job_queue.run_repeating(send_member_count, interval=20, first=0, context=(group_name, group_chat_id))

def new_member(update: Update, context: CallbackContext) -> None:
    user = update.message.new_chat_members[0]
    group_chat_id = update.message.chat_id
    context.bot.send_message(chat_id=group_chat_id, text=f"{user.first_name} joined the group!")

def left_member(update: Update, context: CallbackContext) -> None:
    user = update.message.left_chat_member
    group_chat_id = update.message.chat_id
    context.bot.send_message(chat_id=group_chat_id, text=f"{user.first_name} left the group!")

def send_member_count(context: CallbackContext) -> None:
    group_name, group_chat_id = context.job.context
    global previous_member_counts

    # Get the current member count
    current_member_count = context.bot.get_chat_member_count(chat_id=group_chat_id)

    # Calculate the difference in member count
    joined_count = current_member_count - previous_member_counts[group_name]
    left_count = previous_member_counts[group_name] - current_member_count

    # Send a message with the member count changes
    context.bot.send_message(chat_id=group_chat_id, text=f"Members Joined in 24hrs  {joined_count}, Members Left in 24hrs: {left_count}")

    # Update the previous member count for the next interval
    previous_member_counts[group_name] = current_member_count

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_member))

    updater.start_polling()
    updater.idle()
   

if __name__ == "__main__":
    main()
