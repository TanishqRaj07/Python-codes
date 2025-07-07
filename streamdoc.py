import streamlit as st
import paramiko
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SSH config
HOST = "192.168.1.6"     # Replace with your RHEL9 IP
USERNAME = "root"        # Replace with your SSH username
PASSWORD = "redhat"      # Replace with your SSH password

# SSH Command Executor
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

# Sidebar Menu
st.sidebar.title("📌 Menu")
option = st.sidebar.selectbox("Select Action", ["Docker Commands", "Send Email"])

st.title("🧠 Remote Automation Dashboard")

# --- Docker Commands Section ---
if option == "Docker Commands":
    st.subheader("🐳 Docker Control Dashboard (RHEL9 via Paramiko)")
    st.markdown("Control and manage Docker containers on a remote RHEL9 system over SSH.")
    
    st.markdown("---")
    st.header("1️⃣ Launch New Container")
    image = st.text_input("Docker Image (e.g., nginx, ubuntu)", "")
    name = st.text_input("Container Name (optional)", "")
    port = st.text_input("Port Mapping (optional, format: host:container)", "")
    
    if st.button("Launch Container"):
        cmd = f"docker run -d"
        if name:
            cmd += f" --name {name}"
        if port:
            cmd += f" -p {port}"
        cmd += f" {image}"
        out, err = ssh_execute(cmd)
        if out:
            st.success("Container Launched:")
            st.code(out)
        if err:
            st.error("Error launching container:")
            st.code(err)

    st.markdown("---")
    st.header("2️⃣ Stop a Container")
    stop_id = st.text_input("Enter container name or ID to stop")
    if st.button("Stop Container"):
        out, err = ssh_execute(f"docker stop {stop_id}")
        if out:
            st.success(f"Stopped container {stop_id}")
            st.code(out)
        if err:
            st.error(f"Error stopping container {stop_id}")
            st.code(err)

    st.markdown("---")
    st.header("3️⃣ Remove a Container")
    remove_id = st.text_input("Enter container name or ID to remove")
    if st.button("Remove Container"):
        out, err = ssh_execute(f"docker rm {remove_id}")
        if out:
            st.success(f"Removed container {remove_id}")
            st.code(out)
        if err:
            st.error(f"Error removing container {remove_id}")
            st.code(err)

    st.markdown("---")
    st.header("4️⃣ Start a Container")
    start_id = st.text_input("Enter container name or ID to start")
    if st.button("Start Container"):
        out, err = ssh_execute(f"docker start {start_id}")
        if out:
            st.success(f"Started container {start_id}")
            st.code(out)
        if err:
            st.error(f"Error starting container {start_id}")
            st.code(err)

    st.markdown("---")
    st.header("5️⃣ List All Docker Images")
    if st.button("List Images"):
        out, err = ssh_execute("docker images")
        if out:
            st.code(out)
        if err:
            st.error("Error listing images:")
            st.code(err)

    st.markdown("---")
    st.header("6️⃣ List All Containers")
    if st.button("List Containers"):
        out, err = ssh_execute("docker ps -a")
        if out:
            st.code(out)
        if err:
            st.error("Error listing containers:")
            st.code(err)

    st.markdown("---")
    st.header("7️⃣ Pull Image from Docker Hub")
    pull_image = st.text_input("Enter image name to pull (e.g., nginx:latest)")
    if st.button("Pull Image"):
        out, err = ssh_execute(f"docker pull {pull_image}")
        if out:
            st.success("Image pulled successfully:")
            st.code(out)
        if err:
            st.error("Error pulling image:")
            st.code(err)

# --- Email Section ---
elif option == "Send Email":
    st.subheader("📧 Send Email via SMTP")
    
    sender_email = st.text_input("Your Email (Gmail recommended)")
    sender_password = st.text_input("App Password (for Gmail, use App Password)", type="password")
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

            st.success("Email sent successfully!")

        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
