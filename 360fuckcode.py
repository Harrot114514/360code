import tkinter as tk
from tkinter import ttk
import hashlib
import webbrowser
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("360工厂模式密码生成器")
        root.geometry("400x450")
        style = ttk.Style()
        style.configure("TFrame", padding=10)
        style.configure("TButton", padding=5)
        style.configure("TLabel", padding=5)
        self.create_menu()

        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

                # 设置窗口图标（新增代码）
        try:
            # Windows/Linux系统使用ICO格式
            root.iconbitmap("my_icon.ico")
        except:
            try:
                # macOS/Linux备选方案
                icon = tk.PhotoImage(file="my_icon.png")
                root.iconphoto(True, icon)
            except Exception as e:
                print(f"图标加载失败: {str(e)}")

        # 输入字段
        fields = [
            ("Device Key", "device_key"),
            ("Device ID", "device_id"),
            ("IMEI", "imei"),
            ("QR Code", "qr_code"),
            ("Hard Code", "hard_code")
        ]

        self.entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(main_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(main_frame, width=25)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[name] = entry

        # 模式选择
        ttk.Label(main_frame, text="模式:").grid(row=5, column=0, sticky=tk.W)
        self.mode_var = tk.StringVar(value="develop")
        ttk.Radiobutton(main_frame, text="开发者模式", variable=self.mode_var, value="develop").grid(row=5, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="工厂模式", variable=self.mode_var, value="factory").grid(row=6, column=1, sticky=tk.W)

        # 生成按钮
        ttk.Button(main_frame, text="生成密码", command=self.generate_password).grid(row=7, column=0, columnspan=2, pady=10)

        # 结果显示
        self.result_var = tk.StringVar()
        ttk.Label(main_frame, text="生成密码:").grid(row=8, column=0, sticky=tk.W)
        ttk.Label(main_frame, textvariable=self.result_var, font=("Arial", 12, "bold")).grid(row=8, column=1, sticky=tk.W)

    # 新增菜单创建方法
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 创建"帮助"菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menubar)

    # 新增关于对话框方法
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("300x300")
        about_window.resizable(False, False)
        
        # 使用Frame容器
        content_frame = ttk.Frame(about_window)
        content_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        # 软件信息
        ttk.Label(content_frame, text="360工厂模式密码生成器", font=("微软雅黑", 12, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(content_frame, text="版本: Beta1.1.0").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(content_frame, text="作者: Bilibili_不会起名的萝卜君").grid(row=2, column=0, sticky=tk.W)

        # 开源链接
        ttk.Label(content_frame, text="GitHub开源:").grid(row=3, column=0, sticky=tk.W, pady=(10,0))
        self.create_link_label(content_frame, 
                             text="https://github.com/Harrot114514/360code",
                             url="https://github.com/Harrot114514/360code",
                             row=4)

        # B站链接
        ttk.Label(content_frame, text="B站主页:").grid(row=5, column=0, sticky=tk.W, pady=(10,0))
        self.create_link_label(content_frame,
                             text="https://space.bilibili.com/1732976071",
                             url="https://space.bilibili.com/1732976071",
                             row=6)

    # 创建可点击的链接标签（新增工具方法）
    def create_link_label(self, parent, text, url, row):
        link_label = ttk.Label(parent, text=text, foreground="blue", cursor="hand2")
        link_label.grid(row=row, column=0, sticky=tk.W)
        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))


    def generate_password(self):
        params = {k: v.get() for k, v in self.entries.items()}
        try:
            key = self.generate_key(
                params['device_key'],
                params['device_id'],
                params['imei'],
                params['qr_code'],
                params['hard_code']
            )
            plaintext = "develop_mode_code" if self.mode_var.get() == "develop" else "factory_mode_code"
            encrypted = self.aes_encrypt(key, "eip97324acpamzbv", plaintext)
            code = self.calculate_code(encrypted)
            self.result_var.set(code)
        except Exception as e:
            self.result_var.set(f"错误: {str(e)}")

    def generate_key(self, device_key, device_id, imei, qr_code, hard_code):
        hard_md5 = hashlib.md5(hard_code.encode()).hexdigest()
        
        if device_key.strip():
            parts = [device_key, device_id, hard_md5]
        else:
            parts = [imei, qr_code, hard_md5]
        
        sorted_parts = sorted(parts)
        combined = ",".join(sorted_parts)
        return hashlib.md5(combined.encode()).digest()

    def aes_encrypt(self, key, iv_str, plaintext):
        iv = iv_str.encode('utf-8')
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()
        
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(ciphertext).decode()

    def calculate_code(self, encrypted_b64):
        code = []
        length = len(encrypted_b64) // 6
        for i in range(6):
            idx = i * length
            char = encrypted_b64[idx] if idx < len(encrypted_b64) else '\0'
            code.append(str(ord(char) % 10))
        return ''.join(code)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()