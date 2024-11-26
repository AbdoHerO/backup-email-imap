import imaplib
import email
from email.header import decode_header
import os
import shutil
import mailbox
import time


def get_user_credentials():
    """Prompt user for email and password."""
    email_account = input("Enter your email address: ").strip()
    password = input("Enter your password: ").strip()
    return email_account, password


def connect_to_mailbox(email_account, password):
    """Connect and log in to the email server."""
    IMAP_SERVER = "imap.hostinger.com"  # Hostinger's IMAP server
    IMAP_PORT = 993  # IMAP SSL port
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=1200)  # 20-minute timeout
    mail.login(email_account, password)
    return mail


def fetch_with_retry(mail, email_id):
    """Fetch email with retry logic in case of temporary failures."""
    for attempt in range(3):  # Retry up to 3 times
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status == "OK":
                return msg_data
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to fetch email {email_id}. Retrying...")
            time.sleep(5)  # Wait before retrying
    print(f"Failed to fetch email {email_id} after 3 attempts.")
    return None


def fetch_all_emails(mail, backup_dir, mbox_file_path):
    """Fetch and save all emails."""
    mail.select("inbox")  # Select the inbox folder
    status, messages = mail.search(None, "ALL")  # Fetch all emails

    if status != "OK":
        print("No messages found!")
        return

    email_ids = messages[0].split()
    print(f"Total emails to back up: {len(email_ids)}")

    # Open the mbox file for writing
    mbox = mailbox.mbox(mbox_file_path)

    for index, email_id in enumerate(email_ids, start=1):
        msg_data = fetch_with_retry(mail, email_id)
        if msg_data is None:
            continue  # Skip this email if retries fail

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                save_email(msg, index, backup_dir)
                save_to_mbox(mbox, msg)

    mbox.close()


def save_email(msg, index, backup_dir):
    """Save an email to a file."""
    # Decode the email subject, handle NoneType
    subject = msg["Subject"]
    if subject:
        subject, encoding = decode_header(subject)[0]
        if isinstance(subject, bytes):
            # Decode bytes to string
            subject = subject.decode(encoding if encoding else "utf-8")
    else:
        subject = "No_Subject"

    # Sanitize the subject for a valid filename
    sanitized_subject = "".join(c if c.isalnum() else "_" for c in subject)
    filename = f"email_{index}_{sanitized_subject[:50]}.eml"  # Limit filename length
    filepath = os.path.join(backup_dir, filename)

    # Save the email content to a file
    with open(filepath, "wb") as f:
        f.write(msg.as_bytes())

    print(f"Saved: {filepath}")


def save_to_mbox(mbox, msg):
    """Save an email to the mbox file."""
    mbox.add(msg)
    print("Saved email to mbox.")


def create_zip_file(backup_dir, email_account):
    """Compress the backup folder into a ZIP file."""
    zip_filename = f"{email_account.replace('@', '_').replace('.', '_')}_backup.zip"
    shutil.make_archive(zip_filename, "zip", backup_dir)
    print(f"All emails have been compressed into: {zip_filename}")


def main():
    try:
        # Get user credentials
        email_account, password = get_user_credentials()

        # Set up backup directory
        backup_dir = os.path.join(os.getcwd(), f"backup_{email_account.replace('@', '_').replace('.', '_')}")
        os.makedirs(backup_dir, exist_ok=True)

        # Define the mbox file path
        mbox_file_path = os.path.join(os.getcwd(), f"{email_account.replace('@', '_').replace('.', '_')}_INBOX.mbox")

        # Connect to mailbox
        mail = connect_to_mailbox(email_account, password)

        # Fetch and save all emails
        fetch_all_emails(mail, backup_dir, mbox_file_path)

        # Create a ZIP file
        create_zip_file(backup_dir, email_account)
        print(f"Backup process completed successfully! MBOX file created at: {mbox_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'mail' in locals():
            mail.logout()


if __name__ == "__main__":
    main()
