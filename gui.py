import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import random
import string
import shutil

from auth import login, signup
from rsa_utils import generate_keys, encrypt_rsa, decrypt_rsa
from steg_utils import hide_data_in_image, extract_data_from_image

# Setup UI theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class StegoVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StegoVault 2.0")
        self.root.geometry("600x650")
        self.username = None
        self.login_screen()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.clear()
        ctk.CTkLabel(self.root, text="🔐 StegoVault Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)

        username_entry = ctk.CTkEntry(self.root, placeholder_text="Username", width=300)
        username_entry.pack(pady=5)

        password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*", width=300)
        password_entry.pack(pady=5)

        def try_login():
            username = username_entry.get()
            password = password_entry.get()
            if login(username, password):
                self.username = username
                os.makedirs(f"users/{self.username}/steg", exist_ok=True)
                os.makedirs(f"users/{self.username}/keys", exist_ok=True)
                self.dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        def try_signup():
            username = username_entry.get()
            password = password_entry.get()
            if signup(username, password):
                messagebox.showinfo("Success", "User registered successfully!")
            else:
                messagebox.showwarning("Error", "User already exists.")

        ctk.CTkButton(self.root, text="Login", command=try_login).pack(pady=10)
        ctk.CTkButton(self.root, text="Sign Up", command=try_signup).pack(pady=5)

    def dashboard(self):
        self.clear()
        ctk.CTkLabel(self.root, text=f"👋 Welcome, {self.username}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=30)
        ctk.CTkButton(self.root, text="🔐 Hide Text in Image", command=self.hide_view, width=200).pack(pady=10)
        ctk.CTkButton(self.root, text="🧩 Extract from Image", command=self.extract_view, width=200).pack(pady=10)
        ctk.CTkButton(self.root, text="🚪 Logout", command=self.login_screen, width=200).pack(pady=10)

    def hide_view(self):
        self.clear()
        ctk.CTkLabel(self.root, text="📁 Select Text File").pack(pady=5)
        text_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        ctk.CTkLabel(self.root, text="🖼️ Select Cover Image (PNG)").pack(pady=5)
        image_path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])

        if not text_path or not image_path:
            messagebox.showwarning("Warning", "Please select both a text file and an image.")
            self.dashboard()
            return

        with open(text_path, "rb") as f:
            data = f.read()

        priv_key, pub_key = generate_keys()
        encrypted_data = encrypt_rsa(data, pub_key)

        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        steg_path = f"users/{self.username}/steg/{filename}.png"
        key_path = f"users/{self.username}/keys/{filename}_private.pem"

        hide_data_in_image(image_path, encrypted_data, steg_path)

        with open(key_path, "wb") as f:
            f.write(priv_key)

        img = Image.open(steg_path)
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)

        ctk.CTkLabel(self.root, text="✅ Stego Image Created!", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.root, image=img_tk, text="").pack()
        self.root.image = img_tk
        ctk.CTkLabel(self.root, text=f"Filename: {filename}.png").pack(pady=5)

        def download_image():
            save_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"{filename}.png")
            if save_path:
                shutil.copy(steg_path, save_path)
                messagebox.showinfo("Saved", f"Stego image saved to {save_path}")

        ctk.CTkButton(self.root, text="⬇️ Download Stego Image", command=download_image).pack(pady=10)
        ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)

    def extract_view(self):
        self.clear()
        ctk.CTkLabel(self.root, text="🔍 Extract Hidden Message", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        filename_entry = ctk.CTkEntry(self.root, placeholder_text="Enter filename (without .png)")
        filename_entry.pack(pady=10)

        def extract_data():
            filename = filename_entry.get().strip()
            steg_path = f"users/{self.username}/steg/{filename}.png"
            key_path = f"users/{self.username}/keys/{filename}_private.pem"

            if not os.path.exists(steg_path) or not os.path.exists(key_path):
                messagebox.showerror("Error", "Stego image or key not found!")
                return

            try:
                with open(key_path, "rb") as f:
                    priv_key = f.read()

                encrypted_data = extract_data_from_image(steg_path)
                decrypted_data = decrypt_rsa(encrypted_data, priv_key)
                decrypted_text = decrypted_data.decode(errors="ignore")
            except Exception:
                messagebox.showerror("Error", "Failed to decrypt or extract data.")
                return

            ctk.CTkLabel(self.root, text="✅ Decrypted Message:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            text_box = ctk.CTkTextbox(self.root, width=450, height=150, wrap="word")
            text_box.insert("1.0", decrypted_text)
            text_box.configure(state="disabled")
            text_box.pack(pady=10)

            def save_txt():
                save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"{filename}_output.txt")
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(decrypted_text)
                    messagebox.showinfo("Saved", f"Text saved to {save_path}")

            ctk.CTkButton(self.root, text="⬇️ Download as .txt", command=save_txt).pack(pady=10)
            ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)

        ctk.CTkButton(self.root, text="🔓 Extract", command=extract_data).pack(pady=10)
        ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)


if __name__ == "__main__":
    root = ctk.CTk()
    app = StegoVaultApp(root)
    root.mainloop()
