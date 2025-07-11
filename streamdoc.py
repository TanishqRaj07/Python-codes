import streamlit as st
import paramiko
import smtplib
import requests
import json
import tweepy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# SSH CONFIG
HOST = "192.168.35.201"
USERNAME = "root"
PASSWORD = "redhat"

def ssh_execute(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output.strip(), error.strip()
    except Exception as e:
        return "", str(e)

# Sidebar Navigation
st.sidebar.title("📌 Dashboard Sections")
section = st.sidebar.selectbox("Go To", ["Docker", "Messaging", "Social Media"])
st.title("🧠 Remote Automation Dashboard")

# ---------------- Docker Section -------------------
if section == "Docker":
    st.header("🐳 Docker Control Panel (via SSH)")
    image = st.text_input("Docker Image", "")
    name = st.text_input("Container Name", "")
    port = st.text_input("Port Mapping (host:container)", "")

    if st.button("Launch Container"):
        cmd = "docker run -d"
        if name:
            cmd += f" --name {name}"
        if port:
            cmd += f" -p {port}"
        cmd += f" {image}"
        out, err = ssh_execute(cmd)
        st.code(out if out else err)

    st.markdown("---")
    stop_id = st.text_input("Stop Container ID/Name")
    if st.button("Stop"):
        out, err = ssh_execute(f"docker stop {stop_id}")
        st.code(out if out else err)

    start_id = st.text_input("Start Container ID/Name")
    if st.button("Start"):
        out, err = ssh_execute(f"docker start {start_id}")
        st.code(out if out else err)

    remove_id = st.text_input("Remove Container ID/Name")
    if st.button("Remove"):
        out, err = ssh_execute(f"docker rm {remove_id}")
        st.code(out if out else err)

    st.markdown("---")
    if st.button("List Images"):
        out, err = ssh_execute("docker images")
        st.code(out if out else err)

    if st.button("List Containers"):
        out, err = ssh_execute("docker ps -a")
        st.code(out if out else err)

    pull_image = st.text_input("Image to Pull (e.g., nginx:latest)")
    if st.button("Pull Image"):
        out, err = ssh_execute(f"docker pull {pull_image}")
        st.code(out if out else err)

# ---------------- Messaging Section -------------------
elif section == "Messaging":
    message_option = st.sidebar.radio("Select Messaging Type", ["Email", "SMS"])

    if message_option == "Email":
        st.header("📧 Send Email")
        sender_email = st.text_input("Your Email")
        sender_password = st.text_input("App Password", type="password")
        receiver_email = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        body = st.text_area("Message")

        if st.button("Send Email"):
            try:
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = receiver_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()

                st.success("✅ Email sent!")
            except Exception as e:
                st.error(f"❌ Email failed: {str(e)}")

    elif message_option == "SMS":
        st.header("📱 Send SMS via Twilio")
        sid = st.text_input("Twilio Account SID")
        token = st.text_input("Twilio Auth Token", type="password")
        from_number = st.text_input("From (Twilio number)")
        to_number = st.text_input("To Phone Number")
        msg = st.text_area("Message")

        if st.button("Send SMS"):
            try:
                client = Client(sid, token)
                message = client.messages.create(
                    body=msg,
                    from_=from_number,
                    to=to_number
                )
                st.success(f"✅ SMS sent! SID: {message.sid}")
            except Exception as e:
                st.error(f"❌ SMS failed: {str(e)}")

# ---------------- Social Media Section -------------------
elif section == "Social Media":
    social_option = st.sidebar.radio("Choose Platform", ["LinkedIn", "Twitter", "Facebook", "Instagram", "WhatsApp"])

    # --- LinkedIn ---
    if social_option == "LinkedIn":
        st.header("🔗 Post to LinkedIn")
        token = st.text_input("LinkedIn Access Token", type="password")
        message = st.text_area("Post Content")

        if st.button("Post on LinkedIn"):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                user_id = requests.get("https://api.linkedin.com/v2/me", headers=headers).json().get("id")

                post_url = "https://api.linkedin.com/v2/ugcPosts"
                post_data = {
                    "author": f"urn:li:person:{user_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": message},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }

                res = requests.post(post_url, headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0"
                }, data=json.dumps(post_data))

                if res.status_code == 201:
                    st.success("✅ LinkedIn Post Successful!")
                else:
                    st.error(f"❌ Error: {res.text}")
            except Exception as e:
                st.error(str(e))

    # --- Twitter ---
    elif social_option == "Twitter":
        st.header("🐦 Post to Twitter")
        key = st.text_input("API Key")
        secret = st.text_input("API Secret", type="password")
        token = st.text_input("Access Token")
        token_secret = st.text_input("Access Token Secret", type="password")
        tweet = st.text_area("Tweet Content")

        if st.button("Tweet"):
            try:
                auth = tweepy.OAuth1UserHandler(key, secret, token, token_secret)
                api = tweepy.API(auth)
                api.update_status(tweet)
                st.success("✅ Tweet posted!")
            except Exception as e:
                st.error(str(e))

    # --- Facebook ---
    elif social_option == "Facebook":
        st.header("📘 Post to Facebook Page")
        fb_token = st.text_input("Page Access Token", type="password")
        page_id = st.text_input("Facebook Page ID")
        fb_message = st.text_area("Message")

        if st.button("Post to Facebook"):
            try:
                url = f"https://graph.facebook.com/{page_id}/feed"
                result = requests.post(url, params={"message": fb_message, "access_token": fb_token}).json()
                if "id" in result:
                    st.success(f"✅ Facebook Post ID: {result['id']}")
                else:
                    st.error(f"❌ Error: {result}")
            except Exception as e:
                st.error(str(e))

    # --- Instagram ---
    elif social_option == "Instagram":
        st.header("📸 Post to Instagram")
        token = st.text_input("Instagram Graph Access Token", type="password")
        page_id = st.text_input("Instagram Business Page ID")
        image_url = st.text_input("Public Image URL")
        caption = st.text_area("Caption")

        if st.button("Post to Instagram"):
            try:
                create_url = f"https://graph.facebook.com/v19.0/{page_id}/media"
                create_res = requests.post(create_url, data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": token
                }).json()
                creation_id = create_res.get("id")

                if creation_id:
                    publish_url = f"https://graph.facebook.com/v19.0/{page_id}/media_publish"
                    pub_res = requests.post(publish_url, data={
                        "creation_id": creation_id,
                        "access_token": token
                    }).json()
                    if "id" in pub_res:
                        st.success("✅ Instagram Post Successful!")
                    else:
                        st.error(pub_res)
                else:
                    st.error(create_res)
            except Exception as e:
                st.error(str(e))

    # --- WhatsApp ---
    elif social_option == "WhatsApp":
        st.header("💬 Send WhatsApp Message via Twilio")
        sid = st.text_input("Twilio Account SID")
        token = st.text_input("Twilio Auth Token", type="password")
        wa_from = st.text_input("From (e.g., whatsapp:+1415XXX)")
        wa_to = st.text_input("To (e.g., whatsapp:+91XXX)")
        msg = st.text_area("WhatsApp Message")

        if st.button("Send WhatsApp"):
            try:
                client = Client(sid, token)
                message = client.messages.create(body=msg, from_=wa_from, to=wa_to)
                st.success(f"✅ WhatsApp sent! SID: {message.sid}")
            except Exception as e:
                st.error(f"❌ WhatsApp failed: {str(e)}")
