from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue, ChatMemberHandler

TOKEN = "6685619767:AAFMEjP3toYFgvQa7AnkIVih09STE-nqJD0"  # Replace with your bot token

ADMIN_GROUP_CHAT_ID = -1001610346934  # Replace with your admin group chat ID

# Replace with your group chat IDs and their respective names
GROUP_CHAT_IDS = {"Group1": -1001788330922, "Group2": -1002115769902, "Group3": -1002052528123}

# Dictionary to store the previous member counts for each group
previous_member_counts = {group_name: 0 for group_name in GROUP_CHAT_IDS}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bot is active. You will receive notifications for new joins and leaves.")
    # Schedule the job to send member count every 20 seconds to the admin group
    context.job_queue.run_repeating(send_member_count, interval=200, first=0, context=(None, ADMIN_GROUP_CHAT_ID))
    

def new_member(update: Update, context: CallbackContext) -> None:
    user = update.message.new_chat_members[0]
    user_name = user.first_name

    try:
        invite_link = context.bot.export_chat_invite_link(chat_id=update.message.chat_id)
    except Exception as e:
        print(f"Error getting invite link for group {update.message.chat_id}: {e}")
        invite_link = None

    if invite_link:
        message = f"{user_name} joined the group {update.message.chat.title} using the invite link: {invite_link}"
    else:
        message = f"{user_name} joined the group {update.message.chat.title}."

    context.bot.send_message(chat_id=ADMIN_GROUP_CHAT_ID, text=message)

def left_member(update: Update, context: CallbackContext) -> None:
    user = update.message.left_chat_member
    context.bot.send_message(chat_id=ADMIN_GROUP_CHAT_ID, text=f"{user.first_name} left the group {update.message.chat.title}!")

def send_member_count(context: CallbackContext) -> None:
    _, admin_group_chat_id = context.job.context
    global previous_member_counts

    # Calculate and send the member count changes to the admin group
    for group_name, group_chat_id in GROUP_CHAT_IDS.items():
        current_member_count = context.bot.get_chat_member_count(chat_id=group_chat_id)
        joined_count = max(0, current_member_count - previous_member_counts[group_name])
        left_count = max(0, previous_member_counts[group_name] - current_member_count)

        message = f"{group_name} - Members Joined in 24hrs: {joined_count}, Members Left in 24hrs: {left_count}"
        context.bot.send_message(chat_id=admin_group_chat_id, text=message)

        # Update the previous member count for the next interval
        previous_member_counts[group_name] = current_member_count


def chat_member(update: Update, context: CallbackContext) -> None:
    pass  # You can customize this function if needed

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_member))
    dp.add_handler(ChatMemberHandler(chat_member))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
