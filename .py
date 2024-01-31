import os
import datetime
import pickle
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import face_recognition
from tkinter import messagebox
import pandas as pd

# Updated get_button function to set background color, foreground color, and font size
def get_button(window, text, bg_color, command, fg_color='white', font_size=12, **kwargs):
    button = tk.Button(window, text=text, bg=bg_color, fg=fg_color, command=command, font=('Arial', font_size), **kwargs)
    return button

def get_img_label(window):
    label = tk.Label(window)
    return label

def recognize(image, db_dir):
    # Replace this with your actual recognition logic
    return "SampleUser"

def msg_box(title, message):
    # Replace this with your actual messagebox logic
    messagebox.showinfo(title, message)

def get_entry_text(window):
    entry = tk.Text(window, height=1, width=20)
    return entry

def get_text_label(window, text, font_size=12):
    label = tk.Label(window, text=text, font=('Arial', font_size))
    return label

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("600x400+350+100")
        self.main_window.title("Face Recognition App")


        # Disable resizing
        self.main_window.resizable(False, False)

        # Load the background image using Pillow (PIL)
        background_path = os.path.join("C:\\Users\\Elykin\\PycharmProjects\\pythonProject1\\Face", "National University black and white.jpg")
        background_image = Image.open(background_path)
        background_image = background_image.resize((800, 600),
                                                   Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Set a styled background with blue and gold pattern
        background_label = tk.Label(self.main_window, image=self.background_photo)
        background_label.place(relwidth=1, relheight=1)

        top_canvas = tk.Canvas(self.main_window, height=45, bg='#030C37')
        top_canvas.pack(side='top', fill='x')

        top_canvas.create_text(590, 22, text="NU FAIRVIEW", fill='white', font=('Arial', 12, 'bold'), anchor='e')

        border_canvas = tk.Canvas(self.main_window, height=45, bg='#B88D03')  #
        border_canvas.pack(side='bottom', fill='x')

        border_canvas.create_text(300, 22, text="WELCOME BULLDOGS!", fill='white', font=('Arial', 12, 'bold'))

        # Use the updated get_button function for login buttons
        self.login_button_main_window = get_button(self.main_window, 'Login', 'green', self.login, font_size=14)
        self.login_button_main_window.place(x=350, y=80)

        self.logout_button_main_window = get_button(self.main_window, 'Logout', 'red', self.logout, font_size=14)
        self.logout_button_main_window.place(x=350, y=150)

        self.register_new_user_button_main_window = get_button(self.main_window, 'Register New User', 'orange',
                                                              self.register_new_user, fg_color='black', font_size=14)
        self.register_new_user_button_main_window.place(x=350, y=220)

        self.webcam_label = get_img_label(self.main_window)
        self.webcam_label.place(x=20, y=60, width=300, height=230)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'
        self.cap = cv2.VideoCapture(0)  # Initialize the camera with index 0
        self.start_camera_feed()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self.webcam_label.imgtk = imgtk
        self.webcam_label.configure(image=imgtk)

        self.webcam_label.after(20, self.process_webcam)

    def start_camera_feed(self):
        self.process_webcam()

        # Load the attendance Excel file
        self.attendance_file = 'attendance.xlsx'
    def login(self):
        name = self.recognize_user(self.most_recent_capture_arr, self.db_dir)

        if name == "unknown_person":
            msg_box('Ups...', 'Unknown user. Please register new user or try again.')
        elif name == "no_persons_found":
            msg_box('Error', 'No face found in the image. Please try capturing a better image.')
        else:
            msg_box('Welcome back!', 'Welcome, {}.'.format(name))
            self.log_attendance(name, 'in')

    def logout(self):
        name = self.recognize_user(self.most_recent_capture_arr, self.db_dir)

        if name == "unknown_person":
            msg_box('Ups...', 'Unknown user. Please register first or contact IT Department.')
        elif name == "no_persons_found":
            msg_box('Error', 'No face found in the image. Please try capturing a better image.')
        else:
            msg_box('Hasta la vista baby!', 'Goodbye, {}.'.format(name))
            self.log_attendance(name, 'out')

    def recognize_user(self, image, db_dir):
        # Load the face embeddings of registered users
        registered_users = os.listdir(db_dir)

        # Capture face embeddings from the current image
        captured_embeddings = face_recognition.face_encodings(image)

        if not captured_embeddings:
            return "no_persons_found"  # No face found in the image

        captured_embeddings = captured_embeddings[0]  # Take the first face embedding

        # Compare with registered users
        for user in registered_users:
            user_folder = os.path.join(db_dir, user)
            embeddings_filename = os.path.join(user_folder, '{}.pickle'.format(user))

            # Load the stored face embeddings
            with open(embeddings_filename, 'rb') as file:
                stored_embeddings = pickle.load(file)

            # Compare the captured embeddings with the stored embeddings
            match = face_recognition.compare_faces([stored_embeddings], captured_embeddings)

            if match[0]:
                return user  # Return the recognized user

        return "unknown_person"  # No match found for any registered user

    def log_attendance(self, name, status):
        # Create or load the attendance DataFrame from the Excel file
        try:
            df = pd.read_excel(self.attendance_file, dtype={'TimeOut': 'object'})
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Name', 'TimeIn', 'TimeOut'])

        # Find the row for the current user
        user_row = df[df['Name'] == name]

        # Log the time based on status (in or out)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        if status == 'in':
            if user_row.empty:
                # If the user is not already in the DataFrame, add a new row
                new_row = pd.DataFrame({'Name': [name], 'TimeIn': [current_time], 'TimeOut': [None]})
                df = pd.concat([df, new_row], ignore_index=True, sort=False) if not df.empty else new_row
            else:
                df.loc[user_row.index, 'TimeIn'] = current_time
        elif status == 'out':
            if not user_row.empty:
                # Explicitly set the type to object for 'TimeOut' column
                df.loc[user_row.index, 'TimeOut'] = current_time

        # Save the updated DataFrame to the Excel file
        df.to_excel(self.attendance_file, index=False)

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("650x350+370+120")
        self.register_new_user_window.title("Register New User")

        self.accept_button_register_new_user_window = get_button(
            self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user, font_size=12
        )
        self.accept_button_register_new_user_window.place(x=447, y=215)

        self.try_again_button_register_new_user_window = get_button(
            self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user, font_size=12
        )
        self.try_again_button_register_new_user_window.place(x=440, y=265)

        self.capture_label = get_img_label(self.register_new_user_window)
        self.capture_label.place(x=30, y=50, width=270, height=265)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=400, y=150)

        self.text_label_register_new_user = get_text_label(
            self.register_new_user_window, 'Please, \ninput username:', font_size=13
        )
        self.text_label_register_new_user.place(x=425, y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        # Ensure the user entered a name
        if not name.strip():
            msg_box('Error', 'Please enter a valid username.')
            return

        # Create a subfolder within the db directory
        user_folder = os.path.join(self.db_dir, name)
        os.makedirs(user_folder, exist_ok=True)

        # Save the captured image
        image_filename = os.path.join(user_folder, '{}.jpg'.format(name))
        cv2.imwrite(image_filename, cv2.cvtColor(self.register_new_user_capture, cv2.COLOR_RGB2BGR))

        # Save the face embeddings
        embeddings = face_recognition.face_encodings(self.register_new_user_capture)

        if len(embeddings) > 0:
            embeddings = embeddings[0]

            # Save the embeddings to a pickle file
            embeddings_filename = os.path.join(user_folder, '{}.pickle'.format(name))
            with open(embeddings_filename, 'wb') as file:
                pickle.dump(embeddings, file)

            msg_box('Success!', 'Registered successfully!')
        else:
            # No face found in the image
            msg_box('Error', 'No face found in the image. Please try capturing a better image.')

        self.register_new_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()


