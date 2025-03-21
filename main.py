import tkinter as tk
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import cv2
from PIL import Image, ImageTk
import time
from fuzzywuzzy import process

# Video Path
VIDEO_PATH = "animation.mp4"

# Initialize TTS Engine
engine = pyttsx3.init()

# Global flag
is_listening = False

# Commands Dictionary
commands = {
    "open youtube": "https://www.youtube.com",
    "open google": "https://www.google.com",
    "open github": "https://www.github.com",
    "open netflix": "https://www.netflix.com",
    "open youtube history": "https://www.youtube.com/feed/history",

    #sfit pages
    "open homepage": "https://sfiterp.sfit.co.in:98/studentPortal.asp",
    "open sfit homepage": "https://sfiterp.sfit.co.in:98/studentPortal.asp",
    "open attendance": "https://sfiterp.sfit.co.in:98/StudPortal_Attendance.asp",
    "open grace attendance": "https://sfiterp.sfit.co.in:98/studportal_apply_grace_attendance.asp",
    "open iat result": "https://sfiterp.sfit.co.in:98/StudPortal_ExaminationReport.asp",
    "open final exam result": "https://sfiterp.sfit.co.in:98/StudPortal_EXAM_MArks.asp#",
    "open honors and minors result": "https://sfiterp.sfit.co.in:98/StudPortal_Honours_EXAM_MArks.asp",
    "open mcqs practice": "https://sfiterp.sfit.co.in:98/Studportal_Online_Quiz_Practice.asp",
    "open online quiz": "https://sfiterp.sfit.co.in:98/studportal_Online_Quiz.asp",
    "open online poll": "https://sfiterp.sfit.co.in:98/studportal_Online_poll.asp",
    "open session plan": "https://sfiterp.sfit.co.in:98/Studportal_Session_Plan.asp",
    "open sfit fees": "https://sfiterp.sfit.co.in:98/studportal_annual_fees.asp",
    "open academic bank of credits": "https://sfiterp.sfit.co.in:98/Studportal_ABCID.asp",
    "open upload photo": "https://sfiterp.sfit.co.in:98/studportal_capture_photo.asp",
    "open elections": "https://sfiterp.sfit.co.in:98/studportal_election.asp",

    #youtube pages
    "open youtube shorts": "https://www.youtube.com/shorts",
    "open youtube subscriptions": "https://www.youtube.com/feed/subscriptions",
    "open youtube history": "https://www.youtube.com/feed/history",
    "open youtube playlist": "https://www.youtube.com/feed/playlists",
    "open youtube watch later": "https://www.youtube.com/playlist?list=WL",
    "open youtube liked videos": "https://www.youtube.com/playlist?list=LL",
    "open youtube downloads": "https://www.youtube.com/feed/downloads",


}



# Speak Function
def speak(text):
    text_label.config(text=text)
    root.update_idletasks()
    engine.say(text)
    engine.runAndWait()


# Process Commands
def process_command(command):
    command = command.lower()
    best_match, score = process.extractOne(command, commands.keys())
    if score > 80:  # Adjust threshold if needed
        site_name = best_match.replace("open ", "").capitalize()
        speak(f"Opening {site_name}, Sir")
        webbrowser.open(commands[best_match])
    else:
        speak("Sorry, I didn't understand that.")



# Listen for Voice Command
def listen():
    global is_listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        text_label.config(text="Listening...")
        root.update_idletasks()
        is_listening = True
        threading.Thread(target=play_video, daemon=True).start()

        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            text_label.config(text=f"You said: {command}")
            process_command(command)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            speak("There was an issue with the recognition service.")

        is_listening = False


# Play Video Animation
def play_video():
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    start_frame = int(fps * 1)
    end_frame = int(fps * 3)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    while is_listening:
        current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if current_frame >= end_frame:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (300, 300))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        root.update_idletasks()
        time.sleep(1 / fps)

    video_label.config(image="")
    cap.release()


# Start Assistant
def start_voice_assistant():
    threading.Thread(target=listen, daemon=True).start()


# UI Setup
root = tk.Tk()
root.title("AI Voice Assistant")
root.geometry("400x500")
root.configure(bg="#000000")

# Video Label
video_label = tk.Label(root, bg="#000000")
video_label.pack(pady=10)

# Text Label
text_label = tk.Label(root, text="Waiting for command...", font=("Arial", 14, "bold"), fg="#BB86FC", bg="#121212")
text_label.pack(pady=10)


# Listen Button Style
def on_enter(e):
    listen_button.config(bg="#BB86FC", fg="black")


def on_leave(e):
    listen_button.config(bg="#3700B3", fg="white")


listen_button = tk.Button(root, text="🎙 Start Listening", command=start_voice_assistant, font=("Arial", 12, "bold"),
                          bg="#3700B3", fg="white", relief="flat", padx=10, pady=5, activebackground="#BB86FC")
listen_button.pack(pady=10)
listen_button.bind("<Enter>", on_enter)
listen_button.bind("<Leave>", on_leave)

# Start GUI
root.mainloop()