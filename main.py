import requests
import os
import sys
import yt_dlp
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from yt_dlp.utils import DownloadError
import threading
import time

# Version Checking and Script Update Logic
CURRENT_VERSION = "3.0.1"  # Current version of the script
UPDATE_CHECK_INTERVAL = 28800  # 8 hours


def update_script(version_url, script_url):
    """Check for updates and replace the script if a new version is found."""
    try:
        # Fetch the latest version number
        latest_version = requests.get(version_url).text.strip()

        if latest_version != CURRENT_VERSION:
            # Fetch and update the script
            response = requests.get(script_url)
            with open(__file__, "w") as script_file:
                script_file.write(response.text)
            print(f"Updated to version {latest_version}. Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)  # Restart the script
        else:
            print("The script is up-to-date.")
    except Exception as e:
        print(f"Error checking for updates: {e}")


def update_check_thread(version_url, script_url):
    """Runs the update check in a separate thread to avoid blocking the GUI."""
    while True:
        update_script(version_url, script_url)
        time.sleep(
            UPDATE_CHECK_INTERVAL
        )  # Wait for the specified interval before checking again


# Download Logic for YouTube Audio
def download_youtube_audio(video_url, audio_format, output_path):
    try:
        status_var.set("Downloading...")
        status_label.config(
            foreground="blue"
        )  # Set status color to blue for downloading
        ydl_opts = {
            "format": "bestaudio/best",
            "extractaudio": True,  # Download only audio
            "audioformat": audio_format,  # Save as the specified format
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",  # Save with title
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        status_var.set("Download complete!")
        status_label.config(foreground="green")  # Set status color to green for success
        messagebox.showinfo(
            "Success", f"Audio downloaded successfully to {output_path}"
        )
    except DownloadError:
        status_var.set("Error during download.")
        status_label.config(foreground="red")  # Set status color to red for errors
        messagebox.showerror(
            "Download Error",
            "Failed to download video. Please check your internet connection and the video URL.",
        )
    except Exception as e:
        status_var.set("Unexpected error.")
        status_label.config(foreground="red")  # Set status color to red for errors
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


def start_download():
    video_url = url_entry.get()
    audio_format = format_var.get()
    output_path = output_path_var.get()

    if "https://" not in video_url and "http://" not in video_url:
        video_url = "https://" + video_url
        messagebox.showwarning(
            "Broken URL",
            "You have entered an invalid URL but we were able to fix it for you. Watch out for it.",
        )

    if not video_url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return
    if not audio_format:
        messagebox.showerror("Error", "Please select an audio format.")
        return
    if not output_path:
        messagebox.showerror("Error", "Please select an output folder.")
        return

    # Start the download in a new thread
    status_var.set("Preparing download...")
    status_label.config(
        foreground="orange"
    )  # Set status color to orange for preparation
    download_thread = threading.Thread(
        target=download_youtube_audio, args=(video_url, audio_format, output_path)
    )
    download_thread.start()


def get_music_directory():
    if os.name == "nt":  # For Windows
        music_dir = os.path.join(os.environ["USERPROFILE"], "Music")
    elif os.name == "posix":  # For Linux and MacOS
        music_dir = os.path.join(os.environ["HOME"], "Music")

    if os.path.exists(music_dir):
        return music_dir
    else:
        return "Music directory not found"


def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_path_var.set(folder_selected)


# GUI Setup
root = ttk.Window(themename="lumen")  # Initialize the window with a theme
root.title("YouTube Audio Downloader")
root.geometry("500x160")

icon = tk.PhotoImage(file="C:\\Users\\maraj\\Desktop\\Python\\YTAD\\Images\\icon.png")
root.iconphoto(False, icon)

url_var = tk.StringVar(value="")  # Set default value to placeholder

# Video URL
ttk.Label(root, text="Video URL:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
url_entry = ttk.Entry(root, textvariable=url_var, width=40)
url_entry.grid(row=0, column=1, padx=10, pady=5)

# Output Path
ttk.Label(root, text="Output Folder:").grid(
    row=2, column=0, padx=10, pady=5, sticky="w"
)

placeholder_text = get_music_directory()
placeholder_text = placeholder_text.replace("\\", "/")

output_path_var = tk.StringVar(
    value=placeholder_text
)  # Set default value to placeholder
output_entry = ttk.Entry(root, textvariable=output_path_var, width=30)
output_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Browse Button placed next to Output Path Entry
ttk.Button(root, text="Browse", command=select_output_folder).grid(
    row=2, column=1, padx=10, pady=5, sticky="e"
)

# Audio Format
ttk.Label(root, text="Audio Format:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
format_var = tk.StringVar(value="mp3")  # Default to mp3
ttk.OptionMenu(root, format_var, "mp3", "m4a", "wav", "aac", "mp3").grid(
    row=3, column=1, padx=10, pady=5, sticky="w"
)

# Download Status Label
status_var = tk.StringVar(value="Ready")
status_label = ttk.Label(
    root,
    textvariable=status_var,
    font=("Calibri", 12, "italic"),
    anchor="center",
    foreground="gray",
)
status_label.place(relx=0.5, rely=0.9, anchor="center")  # Change to 0.5 for center

# Download Button
ttk.Button(root, text="Download", command=start_download).grid(
    row=3, column=1, pady=5, padx=10, sticky="e"
)

# Check for updates in a separate thread before running the GUI
version_url = (
    "https://raw.githubusercontent.com/SimpleCarrot42/YTAD/refs/heads/main/versions.txt"
)
script_url = (
    "https://raw.githubusercontent.com/SimpleCarrot42/YTAD/refs/heads/main/main.py"
)

update_thread = threading.Thread(
    target=update_check_thread, args=(version_url, script_url)
)
update_thread.daemon = (
    True  # Daemonize the thread so it exits when the main program exits
)
update_thread.start()

# Run the GUI loop
root.mainloop()
