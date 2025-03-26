# gui.py
import tkinter as tk

def create_gui(start_voice_assistant_func, listen_func):
    root = tk.Tk()
    root.title("AI Assistant")
    root.configure(bg="#000000")

    # Set to fullscreen
    root.attributes("-fullscreen", True)

    # Make window content responsive
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Add border frame
    border_frame = tk.Frame(root, bg="#000000", bd=2, relief="solid", highlightbackground="#333333", highlightthickness=2)
    border_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    border_frame.grid_rowconfigure(0, weight=1)
    border_frame.grid_columnconfigure(0, weight=1)

    # Main content frame inside the border
    main_frame = tk.Frame(border_frame, bg="#000000")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    main_frame.grid_rowconfigure(0, weight=4)  # Video area
    main_frame.grid_rowconfigure(1, weight=1)  # Text area
    main_frame.grid_columnconfigure(0, weight=1)

    # Video frame with border
    video_outer_frame = tk.Frame(main_frame, bg="#000000", bd=1, relief="solid", highlightbackground="#333333",
                                 highlightthickness=1)
    video_outer_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    video_outer_frame.grid_rowconfigure(0, weight=1)
    video_outer_frame.grid_columnconfigure(0, weight=1)

    # Video frame
    video_frame = tk.Frame(video_outer_frame, bg="#000000")
    video_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    video_frame.grid_rowconfigure(0, weight=1)
    video_frame.grid_columnconfigure(0, weight=1)

    # Video label (to display the video)
    video_label = tk.Label(video_frame, bg="#000000")
    video_label.grid(row=0, column=0, sticky="nsew")

    # Text frame with border
    text_outer_frame = tk.Frame(main_frame, bg="#000000", bd=1, relief="solid", highlightbackground="#333333",
                                highlightthickness=1)
    text_outer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    text_outer_frame.grid_rowconfigure(0, weight=1)
    text_outer_frame.grid_columnconfigure(0, weight=1)

    # Text frame
    text_frame = tk.Frame(text_outer_frame, bg="#000000")
    text_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    text_frame.grid_rowconfigure(0, weight=1)
    text_frame.grid_rowconfigure(1, weight=1)
    text_frame.grid_rowconfigure(2, weight=1)
    text_frame.grid_columnconfigure(0, weight=1)

    # Slogan label
    slogan_label = tk.Label(
        text_frame,
        text="A NEW ERA OF INTELLIGENCE BEGINS NOW.",
        font=("Consolas", 18, "bold"),
        fg="#FFFFFF",
        bg="#000000"
    )
    slogan_label.grid(row=0, column=0, sticky="s", pady=5)

    # Status label
    status_label = tk.Label(
        text_frame,
        text="Waiting for command...",
        font=("Consolas", 14),
        fg="#00FFFF",
        bg="#000000"
    )
    status_label.grid(row=1, column=0, sticky="n", pady=5)

    # Button frame
    button_frame = tk.Frame(text_frame, bg="#000000")
    button_frame.grid(row=2, column=0, sticky="n", pady=10)

    # Listen Button functions
    def on_enter(e):
        listen_button.config(bg="#00FFFF", fg="#000000")

    def on_leave(e):
        listen_button.config(bg="#000000", fg="#00FFFF")

    # Listen Button
    listen_button = tk.Button(
        button_frame,
        text="ACTIVATE",
        command=lambda: start_voice_assistant_func(status_label, video_label, video_frame),
        font=("Consolas", 14, "bold"),
        bg="#000000",
        fg="#00FFFF",
        borderwidth=1,
        relief="solid",
        padx=20,
        pady=10,
        activebackground="#00FFFF",
        activeforeground="#000000"
    )
    listen_button.pack()
    listen_button.bind("<Enter>", on_enter)
    listen_button.bind("<Leave>", on_leave)

    # Keyboard bindings
    def exit_fullscreen(event=None):
        root.attributes("-fullscreen", False)
        root.geometry("800x600")

    def toggle_fullscreen(event=None):
        is_fullscreen = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not is_fullscreen)

    root.bind("<Escape>", exit_fullscreen)
    root.bind("<F11>", toggle_fullscreen)

    # Return components for reference in other modules
    components = {
        'root': root,
        'video_label': video_label,
        'status_label': status_label,
        'video_frame': video_frame
    }

    return root, components