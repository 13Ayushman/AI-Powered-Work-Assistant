import win32com.client
import groq
import tkinter as tk

# Initialize Groq client with your API key
client = groq.Groq(api_key="Enter your Groq API key here")

# Defines a list of the last 10 email subjects
def last_10_emails():
    """Fetches the subjects of the last 10 emails from Outlook inbox."""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        messages = inbox.Items
        # Outlook items are often not directly indexable, so we iterate
        email_subjects = []
        for i, message in enumerate(messages):
            if i >= 10:
                break
            email_subjects.append(message.Subject)
        return email_subjects
    except Exception as e:
        print(f"Error fetching emails from Outlook: {e}")
        return ["Failed to load subjects"]

# --- Tkinter UI setup ---
root = tk.Tk()
root.title("AI Email Responder")
root.geometry("400x400")
root.configure(bg="#21232E")

email_subjects = last_10_emails()
selected_subject = tk.StringVar(root)

# Handle case where no emails are found
if email_subjects:
    selected_subject.set(email_subjects[0])
else:
    email_subjects = ["No emails found"]
    selected_subject.set(email_subjects[0])

# Create and style the dropdown menu
dropdown = tk.OptionMenu(root, selected_subject, *email_subjects)
dropdown.config(bg="#444654", fg="#ededf2", bd=0, activebackground="#555866", highlightbackground="#21232E")
dropdown["menu"].config(bg="#444654", fg="#ededf2", bd=0)
dropdown.pack(pady=20)

label = tk.Label(root, text="Select an email to reply to:", bg="#21232E", fg="#ededf2")
label.pack()

def reply():
    """Generates a professional reply using Groq and displays it with the original email in Outlook."""
    try:
        # Get the selected email object
        subject_to_find = selected_subject.get()
        if subject_to_find == "Failed to load subjects" or subject_to_find == "No emails found":
            print("Cannot generate a reply. No valid emails were loaded.")
            return

        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        email = inbox.Items.Find(f"[Subject] = '{subject_to_find}'")

        if not email:
            print(f"Email with subject '{subject_to_find}' not found.")
            return

        # Use the correct Groq API call and parameter structure
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are a professional email assistant. Write a concise and polite reply to the email below, addressing the sender. Do not include the original email body in your response."},
                {"role": "user", "content": f"The body of the email is: {email.Body}"},
            ],
            temperature=0.7,
            max_tokens=256,
        )

        # Access the response correctly from the new API structure
        ai_reply = response.choices[0].message.content

        # Create a new reply email and set its body
        reply_email = email.Reply()
        
        # Combine the AI's reply and the original email body
        original_body = email.Body
        full_body = f"{ai_reply}\n\n---\n\nOriginal Message:\n\n{original_body}"
        reply_email.Body = full_body
        
        reply_email.Display() # Show the user the reply before sending

    except Exception as e:
        print(f"An error occurred: {e}")

button = tk.Button(root, text="Generate Reply", command=reply, bg="#3b82f6", fg="white", bd=0, relief=tk.FLAT, font=("Inter", 10, "bold"))
button.pack(pady=10)

root.mainloop()
