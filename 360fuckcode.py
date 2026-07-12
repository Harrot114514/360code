import tkinter as tk
from tkinter import ttk
import hashlib
import webbrowser
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

CONFIG_FILE = "360code_config.json"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("360工厂模式密码生成器")
        root.geometry("480x530")
        root.resizable(False, False)

        self.create_menu()

        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 设置窗口图标
        try:
            root.iconbitmap("my_icon.ico")
        except:
            try:
                icon = tk.PhotoImage(file="my_icon.png")
                root.iconphoto(True, icon)
            except:
                pass

        # ===== 字段定义 =====
        # (标签, 存储key, 所属分组: "dk"=有DeviceKey时需要, "no_dk"=无DeviceKey时需要, "always"=始终需要)
        self.field_defs = [
            ("Device Key",  "device_key",  "dk"),
            ("Device ID",   "device_id",   "dk"),
            ("IMEI",        "imei",        "no_dk"),
            ("QR Code",     "qr_code",     "no_dk"),
            ("Hard Code",   "hard_code",   "always"),
        ]

        self.entries = {}
        self.labels   = {}

        for i, (label_text, name, group) in enumerate(self.field_defs):
            lbl = tk.Label(main_frame, text=f"  {label_text}:", anchor="w")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=4)
            self.labels[name] = lbl

            entry = ttk.Entry(main_frame, width=32)
            entry.grid(row=i, column=1, padx=12, pady=4, sticky=tk.EW)
            self.entries[name] = entry

        # ----- 路径提示条 -----
        self.path_var = tk.StringVar()
        path_lbl = tk.Label(main_frame, textvariable=self.path_var,
                            font=("微软雅黑", 9), fg="#888888", anchor="w")
        path_lbl.grid(row=5, column=0, columnspan=2, pady=(4, 10), sticky=tk.W)

        # ----- 分隔线 -----
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=4)

        # ----- 模式选择 -----
        mode_label = tk.Label(main_frame, text="  密码类型:", anchor="w",
                              font=("微软雅黑", 10))
        mode_label.grid(row=7, column=0, sticky=tk.W, pady=6)
        self.mode_var = tk.StringVar(value="develop")
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=7, column=1, sticky=tk.W, pady=6)
        ttk.Radiobutton(mode_frame, text="开发者模式",
                        variable=self.mode_var, value="develop").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="工厂模式",
                        variable=self.mode_var, value="factory").pack(side=tk.LEFT, padx=(18, 0))

        # ----- 生成按钮 -----
        gen_btn = ttk.Button(main_frame, text="★ 生成密码",
                             command=self.generate_password)
        gen_btn.grid(row=8, column=0, columnspan=2, pady=14)

        # ----- 结果展示 -----
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=9, column=0, columnspan=2, pady=4)
        tk.Label(result_frame, text="生成密码:", font=("微软雅黑", 11),
                 anchor="w").pack(side=tk.LEFT)
        self.result_var = tk.StringVar(value="——————")
        tk.Label(result_frame, textvariable=self.result_var,
                 font=("Consolas", 22, "bold"), fg="#E65100").pack(side=tk.LEFT, padx=14)

        # ----- 绑定事件 -----
        self.entries["device_key"].bind("<KeyRelease>",
                                        lambda e: self.on_device_key_changed())

        # ----- 加载 & 更新 -----
        self.load_config()
        self.update_field_states()

        # 关闭窗口时自动保存
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # =============================================
    #  菜单
    # =============================================
    def create_menu(self):
        menubar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="清除缓存并重置", command=self.clear_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("320x300")
        about_window.resizable(False, False)

        content_frame = ttk.Frame(about_window)
        content_frame.pack(padx=24, pady=18, fill=tk.BOTH, expand=True)

        tk.Label(content_frame, text="360工厂模式密码生成器",
                 font=("微软雅黑", 13, "bold")).grid(row=0, column=0, pady=6)
        tk.Label(content_frame, text="版本: Beta1.2.1").grid(row=1, column=0, sticky=tk.W)
        tk.Label(content_frame, text="作者: Bilibili_不会起名的萝卜君").grid(row=2, column=0, sticky=tk.W)

        tk.Label(content_frame, text="GitHub开源:",
                 font=("微软雅黑", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(14, 0))
        self.create_link_label(content_frame,
                               text="https://github.com/Harrot114514/360code",
                               url="https://github.com/Harrot114514/360code",
                               row=4)

        tk.Label(content_frame, text="B站主页:",
                 font=("微软雅黑", 9, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(12, 0))
        self.create_link_label(content_frame,
                               text="https://space.bilibili.com/1732976071",
                               url="https://space.bilibili.com/1732976071",
                               row=6)

    def create_link_label(self, parent, text, url, row):
        link_label = tk.Label(parent, text=text, foreground="#1565C0",
                              cursor="hand2", font=("微软雅黑", 9, "underline"))
        link_label.grid(row=row, column=0, sticky=tk.W)
        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))

    # =============================================
    #  智能字段状态
    # =============================================
    def on_device_key_changed(self):
        """DeviceKey 输入框内容变化时实时更新高亮"""
        self.update_field_states()

    def update_field_states(self):
        dk = self.entries["device_key"].get().strip()
        has_dk = len(dk) > 0

        COLOR_ACTIVE  = "#1565C0"   # 必填 — 蓝色粗体
        COLOR_INACTIVE = "#b0b0b0"  # 不必填 — 灰色

        if has_dk:
            self.path_var.set("✓  路径A: 使用 Device Key + Device ID + Hard Code")
            for name, entry in self.entries.items():
                group = self._get_group(name)
                if group == "dk":
                    self.labels[name].config(fg=COLOR_ACTIVE, font=("微软雅黑", 9, "bold"))
                elif group == "no_dk":
                    self.labels[name].config(fg=COLOR_INACTIVE, font=("微软雅黑", 9))
                else:
                    self.labels[name].config(fg=COLOR_ACTIVE, font=("微软雅黑", 9, "bold"))
        else:
            self.path_var.set("○  路径B: 使用 IMEI + QR Code + Hard Code")
            for name, entry in self.entries.items():
                group = self._get_group(name)
                if group == "dk":
                    self.labels[name].config(fg=COLOR_INACTIVE, font=("微软雅黑", 9))
                elif group == "no_dk":
                    self.labels[name].config(fg=COLOR_ACTIVE, font=("微软雅黑", 9, "bold"))
                else:
                    self.labels[name].config(fg=COLOR_ACTIVE, font=("微软雅黑", 9, "bold"))

    def _get_group(self, name):
        for _, n, g in self.field_defs:
            if n == name:
                return g
        return "always"

    # =============================================
    #  配置持久化
    # =============================================
    def save_config(self):
        data = {name: entry.get() for name, entry in self.entries.items()}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 静默失败，不影响用户操作

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, entry in self.entries.items():
                if name in data and data[name]:
                    entry.delete(0, tk.END)
                    entry.insert(0, data[name])
        except Exception:
            pass

    def clear_config(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.result_var.set("——————")
        self.update_field_states()
        try:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
        except Exception:
            pass

    def on_close(self):
        self.save_config()
        self.root.destroy()

     # =============================================
    #  密码生成核心
    # =============================================
    def generate_password(self):
        params = {k: v.get() for k, v in self.entries.items()}
        try:
            key = self.generate_key(
                params["device_key"],
                params["device_id"],
                params["imei"],
                params["qr_code"],
                params["hard_code"]
            )
            plaintext = "develop_mode_code" if self.mode_var.get() == "develop" else "factory_mode_code"
            encrypted = self.aes_encrypt(key, "eip97324acpamzbv", plaintext)
            code = self.calculate_code(encrypted)
            self.result_var.set(code)
        except Exception as e:
            self.result_var.set(f"错误: {str(e)}")

    def generate_key(self, device_key, device_id, imei, qr_code, hard_code):
        """
        复现 generateKey():
          MD5Utils.encode() → hex string (32 chars)
          StrUtil.sort()    → String.compareTo() 字典序
          StrUtil.dumpStringArray("", arr) → 空字符串直接拼接
        """
        hard_md5 = hashlib.md5(hard_code.encode()).hexdigest()

        if device_key.strip():
            parts = [device_key, device_id, hard_md5]
        else:
            parts = [imei, qr_code, hard_md5]

        sorted_parts = sorted(parts)          # 等同于 Java String.compareTo()
        combined = "".join(sorted_parts)      # 空分隔符直接拼接!
        return hashlib.md5(combined.encode()).hexdigest()

    def aes_encrypt(self, key_hex, iv_str, plaintext):
        """
        复现 AESUtils.encryptAESBase64():
          key_hex (MD5 hex, 32 chars) → getBytes("UTF-8") → 32 bytes → AES-256
          IV = "eip97324acpamzbv"
        """
        key = key_hex.encode("utf-8")       # 32 字节 → AES-256
        iv  = iv_str.encode("utf-8")        # 16 字节

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()

        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(ciphertext).decode()

    def calculate_code(self, encrypted_b64):
        length = len(encrypted_b64) // 6
        code = []
        for i in range(6):
            idx = i * length
            char = encrypted_b64[idx] if idx < len(encrypted_b64) else "\0"
            code.append(str(ord(char) % 10))
        return "".join(code)


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
