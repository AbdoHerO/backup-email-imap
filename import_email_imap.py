import imaplib
import mailbox
import email
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


def import_mbox_to_imap(mbox_file, mail):
    """Import emails from a .mbox file to the IMAP server."""
    try:
        # Open the mbox file
        mbox = mailbox.mbox(mbox_file)
        print(f"Found {len(mbox)} emails in {mbox_file}")

        # Select the inbox to append emails
        status, _ = mail.select("INBOX")
        if status != "OK":
            print("Could not select the inbox. Please check the folder name.")
            return

        # Append each email to the inbox
        for index, message in enumerate(mbox, start=1):
            try:
                print(f"Uploading email {index}/{len(mbox)}...")
                raw_message = message.as_bytes()  # Get the raw email data
                mail.append("INBOX", None, None, raw_message)
                print(f"Uploaded email {index}")
            except Exception as e:
                print(f"Error uploading email {index}: {e}")
                continue

    except Exception as e:
        print(f"Error processing mbox file: {e}")


def main():
    try:
        # Get user credentials
        email_account, password = get_user_credentials()

        # Connect to mailbox
        mail = connect_to_mailbox(email_account, password)

        # Path to the .mbox file
        mbox_file = "m_sair_suhailglobal_ma_INBOX.mbox"

        # Import emails from .mbox file
        import_mbox_to_imap(mbox_file, mail)

        print("Import process completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'mail' in locals():
            mail.logout()


if __name__ == "__main__":
    main()
