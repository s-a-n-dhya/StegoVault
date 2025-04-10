import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import random
import string
import shutil
from auth import login, signup
from rsa_utils import generate_keys, encrypt_rsa, decrypt_rsa
from steg_utils import hide_data_in_image, extract_data_from_image
from PIL import Image, ImageTk

# Set default theme and appearance mode
ctk.set_appearance_mode("Light")  # Always dark
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

        ctk.CTkLabel(self.root, text="Username").pack()
        username_entry = ctk.CTkEntry(self.root, width=300)
        username_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="Password").pack()
        password_entry = ctk.CTkEntry(self.root, show="*", width=300)
        password_entry.pack(pady=5)

        def try_login():
            username = username_entry.get()
            password = password_entry.get()
            if login(username, password):
                self.username = username
                self.dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        def try_signup():
            username = username_entry.get()
            password = password_entry.get()
            if signup(username, password):
                messagebox.showinfo("Success", "User registered successfully!")
            else:
                messagebox.showwarning("Error", "User already exists!")

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
            messagebox.showwarning("Warning", "Please select both files!")
            return self.dashboard()

        with open(text_path, "rb") as f:
            data = f.read()

        priv, pub = generate_keys()
        encrypted_data = encrypt_rsa(data, pub)

        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        output_image_path = f"users/{self.username}/steg/{random_filename}.png"
        hide_data_in_image(image_path, encrypted_data, output_image_path)

        key_path = f"users/{self.username}/keys/{random_filename}_private.pem"
        with open(key_path, "wb") as f:
            f.write(priv)

        img = Image.open(output_image_path)
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)

        ctk.CTkLabel(self.root, text="✅ Stego Image Created!", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.root, image=img_tk, text="").pack()
        self.root.image = img_tk  # prevent garbage collection

        ctk.CTkLabel(self.root, text=f"Filename: {random_filename}.png").pack(pady=5)

        def download_stego():
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png")],
                initialfile=f"{random_filename}.png"
            )
            if save_path:
                shutil.copy(output_image_path, save_path)
                messagebox.showinfo("Saved", f"Image saved to {save_path}")

        ctk.CTkButton(self.root, text="⬇️ Download Stego Image", command=download_stego).pack(pady=10)
        ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)

    def extract_view(self):
        self.clear()
        ctk.CTkLabel(self.root, text="🔍 Extract Hidden Message", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.root, text="Enter Stego Filename (without .png)").pack()
        filename_entry = ctk.CTkEntry(self.root)
        filename_entry.pack(pady=10)

        def extract():
            filename = filename_entry.get().strip()
            image_path = f"users/{self.username}/steg/{filename}.png"
            key_path = f"users/{self.username}/keys/{filename}_private.pem"

            if not os.path.exists(image_path) or not os.path.exists(key_path):
                messagebox.showerror("Error", "Stego image or key not found!")
                return

            with open(key_path, "rb") as f:
                priv = f.read()

            try:
                encrypted_data = extract_data_from_image(image_path)
                decrypted = decrypt_rsa(encrypted_data, priv)
                decrypted_text = decrypted.decode(errors="ignore")
            except Exception:
                messagebox.showerror("Error", "Failed to decrypt hidden data!")
                return

            def download_text():
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text Files", "*.txt")],
                    initialfile=f"{filename}_output.txt"
                )
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(decrypted_text)
                    messagebox.showinfo("Saved", f"Text saved to {save_path}")

            ctk.CTkLabel(self.root, text="✅ Decrypted Message:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            text_box = ctk.CTkTextbox(self.root, width=450, height=150, wrap="word")
            text_box.insert("1.0", decrypted_text)
            text_box.configure(state="disabled")
            text_box.pack(pady=10)

            ctk.CTkButton(self.root, text="⬇️ Download as .txt", command=download_text).pack(pady=10)
            ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)

        ctk.CTkButton(self.root, text="🔓 Extract", command=extract).pack(pady=10)
        ctk.CTkButton(self.root, text="🔙 Back to Dashboard", command=self.dashboard).pack(pady=10)

# Run the app
if __name__ == "__main__":
    root = ctk.CTk()
    app = StegoVaultApp(root)
    root.mainloop()
