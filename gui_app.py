import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import bot
import pandas as pd
import os
from datetime import datetime
import ctypes
from PIL import Image

# ─── MONOKROM PREMIUM RENK PALETİ ─────────────────────────────────────────────
BG_DEEP      = "#0a0a0a"   # En koyu arka plan (SaaS tarzı derin siyah)
BG_PANEL     = "#121212"   # Panel arka planı (Koyu gri)
BG_CARD      = "#181818"   # Kart yüzeyleri (Orta-koyu gri)
BG_ELEVATED  = "#242424"   # Butonlar ve giriş kutuları için hafif yüksek gri
BORDER       = "#282828"   # Kart ve panel kenarlıkları için ince çizgi
TEXT_MAIN    = "#ffffff"   # Birincil metin (Saf beyaz)
TEXT_SUB     = "#a6a6a6"   # İkincil metin (Gümüş/Gri)
TEXT_MUTED   = "#5c5c5c"   # Soluk metin (Koyu gri)
ACCENT       = "#ffffff"   # Saf beyaz vurgu
ACCENT_HOVER = "#e5e5e5"   # Buton hover rengi (Açık gri)
ACCENT_GLOW  = "#2a2a2a"   # Satır seçimi arka planı
RED          = "#333333"   # Durdur butonu için koyu gri
WHITE        = "#ffffff"

# Log Renkleri
COLOR_SUCCESS = "#5ebb78"  # Soft zümrüt yeşili
COLOR_ERROR   = "#dd5f5f"  # Soft yakut kırmızısı
COLOR_INFO    = "#d1a11f"  # Soft altın sarısı
COLOR_MUTED   = "#626262"  # Muted gri
COLOR_ACCENT  = "#ffffff"  # Saf beyaz

# CustomTkinter Başlangıç Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def set_dark_title_bar(window):
    window.update()
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value), ctypes.sizeof(value))
    except: pass

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("T Bot — TÜGVA Yaz Okulu Otomasyonu")
        self.root.geometry("1360x860")
        self.root.minsize(1150, 750)
        self.root.configure(fg_color=BG_DEEP)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.file_path = ""
        self.df_preview = None

        if os.path.exists("yaz_okulu_test.xlsx"):
            self.file_path = "yaz_okulu_test.xlsx"
        elif os.path.exists("33.csv"):
            self.file_path = "33.csv"

        self.is_running = False
        self._dot_count  = 0
        self._status_job = None
        self.var_audio_captcha = tk.BooleanVar(value=getattr(bot.config, 'USE_AUDIO_CAPTCHA', True))
        self.var_token_captcha = tk.BooleanVar(value=False)

        # Görseller (PIL ile logo yükleme)
        self._load_assets()

        # TTK Stilleri (Treeview için)
        self._setup_styles()

        # Arayüz Bileşenlerini İnşa Et
        self._build_ui()

        # Windows Başlık Çubuğunu Dark Mode Yap
        set_dark_title_bar(self.root)

        # İlk Dosya Önizlemesi
        if self.file_path and os.path.exists(self.file_path):
            self.root.after(300, self.load_preview_data)

        # Başlangıç Logu
        self.log_message("⬛  T Bot hazır. Dosya seçin ve Botu Başlatın.")

    # ──────────────────────────────────────────────────────────────────────────
    # ASSET YÜKLEME
    # ──────────────────────────────────────────────────────────────────────────
    def _load_assets(self):
        self.img_owl = None
        self.img_owl_sm = None
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "owl_logo.png")
            if os.path.exists(logo_path):
                # CustomTkinter CTkImage yapısı, yüksek çözünürlüklü ekranları (HiDPI) destekler
                self.img_owl = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(40, 40)
                )
                
                # Pencere ikonu için normal PhotoImage
                img = Image.open(logo_path).convert("RGBA")
                ico = img.resize((32, 32), Image.LANCZOS)
                from PIL import ImageTk
                self.img_owl_sm = ImageTk.PhotoImage(ico)
                self.root.iconphoto(True, self.img_owl_sm)
        except Exception as e:
            print(f"Logo yüklenemedi: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # TTK STİLLERİ (Yalnızca Treeview Tabloları İçin)
    # ──────────────────────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview Tablo Alanı
        style.configure("Modern.Treeview",
            background=BG_CARD, foreground=TEXT_MAIN,
            fieldbackground=BG_CARD, borderwidth=0,
            rowheight=32, font=("Segoe UI", 9))
            
        style.configure("Modern.Treeview.Heading",
            background=BG_PANEL, foreground=TEXT_SUB,
            font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat")
            
        style.map("Modern.Treeview",
            background=[("selected", ACCENT_GLOW)],
            foreground=[("selected", WHITE)])
            
        style.map("Modern.Treeview.Heading",
            background=[("active", BG_ELEVATED)])

    # ──────────────────────────────────────────────────────────────────────────
    # MODERN ARAYÜZ TASARIMI (CustomTkinter)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # 1. Üst Kontrol Toolbarı
        self._build_topbar()

        # 2. Ana İçerik Paneli (3 Kolonlu Responsive Grid Düzeni)
        self.content_area = ctk.CTkFrame(self.root, fg_color=BG_DEEP, corner_radius=0)
        self.content_area.pack(fill="both", expand=True, padx=8, pady=8)

        # 3 responsive sütun tanımlayalım
        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=3, minsize=330) # Sol: Sayaçlar ve Başarılı Liste
        self.content_area.columnconfigure(1, weight=4, minsize=430) # Orta: Dosya ve Log
        self.content_area.columnconfigure(2, weight=5, minsize=450) # Sağ: Excel Önizleme

        # Sütun Frame'leri
        self.col_left = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_left.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)

        self.col_middle = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_middle.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)

        self.col_right = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_right.grid(row=0, column=2, sticky="nsew", padx=6, pady=4)

        # Alt Bölümleri İnşa Et
        self._build_left_col()
        self._build_middle_col()
        self._build_right_col()

        # 3. Alt Status Bar
        self._build_statusbar()

    # ──────────────────────────────────────────────────────────────────────────
    # TOOLBAR (Header)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        self.top_bar = ctk.CTkFrame(self.root, fg_color=BG_PANEL, height=64, corner_radius=0)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)

        # Logo + Başlık + Canlı Pulsing Badge
        title_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=16, pady=8)

        if self.img_owl:
            lbl_ico = ctk.CTkLabel(title_frame, image=self.img_owl, text="")
            lbl_ico.pack(side="left", padx=(0, 10))

        name_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        name_frame.pack(side="left")
        
        # Üst sıra (Başlık + Durum Badgesi)
        title_row = ctk.CTkFrame(name_frame, fg_color="transparent")
        title_row.pack(anchor="w")
        
        ctk.CTkLabel(title_row, text="T Bot", fg_color="transparent",
                     text_color=WHITE, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(side="left")
                     
        # Pulsing Status Badge
        self.pulse_badge = ctk.CTkLabel(title_row, text="● HAZIR", fg_color="transparent",
                                        text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"))
        self.pulse_badge.pack(side="left", padx=(10, 0), pady=(4, 0))

        # Alt sıra (Altyazı)
        ctk.CTkLabel(name_frame, text="TÜGVA Yaz Okulu Kayıt Otomasyonu", fg_color="transparent",
                     text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=9)).pack(anchor="w", pady=(2, 0))

        # Kontrol Butonları
        btn_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=12)

        self.btn_stop = ctk.CTkButton(btn_frame, text="⏹  DURDUR",
            fg_color=RED, text_color=WHITE, hover_color="#3e3e3e",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            state="disabled", command=self.stop_bot, height=32, width=100)
        self.btn_stop.pack(side="right", padx=(8, 0))

        self.btn_start = ctk.CTkButton(btn_frame, text="▶  BOTU BAŞLAT",
            fg_color=ACCENT, text_color="#000000", hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.start_bot, height=32, width=130)
        self.btn_start.pack(side="right")

        # İnce Bölücü Yatay Çizgi
        divider = ctk.CTkFrame(self.root, fg_color=BORDER, height=1, corner_radius=0)
        divider.pack(fill="x")

    # ──────────────────────────────────────────────────────────────────────────
    # SOL SÜTUN (Sayaçlar & Tamamlanan Başvurular)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_left_col(self):
        # 1. Sayaç Kartları Bölümü
        stats_frame = ctk.CTkFrame(self.col_left, fg_color="transparent")
        stats_frame.pack(fill="x", padx=4, pady=(6, 6))

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        self.card_total = self._build_stat_card(stats_frame, 0, "TOPLAM", "0")
        self.card_done  = self._build_stat_card(stats_frame, 1, "TAMAMLANAN", "0")
        self.card_skip  = self._build_stat_card(stats_frame, 2, "ATLANAN", "0")

        # 2. Tamamlanan Tablo Kartı
        list_card = ctk.CTkFrame(self.col_left, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        list_card.pack(fill="both", expand=True, padx=4, pady=(6, 6))

        header = ctk.CTkFrame(list_card, fg_color=BG_PANEL, corner_radius=0, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="✅  Tamamlanan Başvurular", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=14, pady=8)
        ctk.CTkButton(header, text="Sıfırla", text_color=TEXT_SUB, fg_color="transparent",
                      hover_color=BG_ELEVATED, command=self._clear_completed, width=60, height=24,
                      font=ctk.CTkFont(family="Segoe UI", size=9)).pack(side="right", padx=14, pady=8)

        tree_frame = ctk.CTkFrame(list_card, fg_color="transparent", corner_radius=0)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.completed_tree = ttk.Treeview(tree_frame,
            style="Modern.Treeview",
            selectmode="browse", show="headings",
            columns=("TC", "Soyad / OkulNo", "Saat"))

        self.completed_tree.heading("TC",            text="TC / Kimlik",      anchor="w")
        self.completed_tree.heading("Soyad / OkulNo", text="Soyad / Okul No", anchor="w")
        self.completed_tree.heading("Saat",          text="Zaman",            anchor="w")

        self.completed_tree.column("TC",              anchor="w", width=110, minwidth=90)
        self.completed_tree.column("Soyad / OkulNo",  anchor="w", width=130, minwidth=110)
        self.completed_tree.column("Saat",            anchor="w", width=65,  minwidth=50)

        vsb = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.completed_tree.yview)
        self.completed_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.completed_tree.pack(fill="both", expand=True)

        self.completed_tree.tag_configure("even", background=BG_CARD)
        self.completed_tree.tag_configure("odd",  background=BG_PANEL)

        self.load_completed_from_file()

    def _build_stat_card(self, parent, col, label, value):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card.grid(row=0, column=col, padx=4 if col != 0 else (0, 4), pady=0, sticky="nsew")

        ctk.CTkLabel(card, text=label, text_color=TEXT_SUB,
                     font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).pack(pady=(10, 2))
                     
        # Kart içi yatay çizgi
        div = ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0)
        div.pack(fill="x", padx=16, pady=2)

        val_lbl = ctk.CTkLabel(card, text=value, text_color=WHITE,
                               font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"))
        val_lbl.pack(pady=(4, 10))
        return val_lbl

    # ──────────────────────────────────────────────────────────────────────────
    # ORTA SÜTUN (Dosya Seçimi & Canlı Log)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_middle_col(self):
        # 1. Dosya Seçim Kartı
        card_file = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_file.pack(fill="x", padx=4, pady=(6, 6))

        header = ctk.CTkFrame(card_file, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(header, text="📂  Veri Dosyası", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left")

        row = ctk.CTkFrame(card_file, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 12))

        file_box = ctk.CTkFrame(row, fg_color=BG_ELEVATED, corner_radius=6)
        file_box.pack(side="left", fill="x", expand=True)

        self.lbl_file = ctk.CTkLabel(file_box,
                                     text=os.path.basename(self.file_path) if self.file_path else "Dosya seçilmedi…",
                                     text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=10),
                                     anchor="w", padx=10, pady=7)
        self.lbl_file.pack(fill="x")

        browse_btn = ctk.CTkButton(row, text="Gözat", fg_color=BG_ELEVATED, text_color=TEXT_MAIN,
                                   hover_color=BORDER, command=self.browse_file, width=80, height=28,
                                   font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"))
        browse_btn.pack(side="right", padx=(8, 0))

        # 1.5. Ayarlar Kartı
        card_settings = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_settings.pack(fill="x", padx=4, pady=(6, 6))

        settings_header = ctk.CTkFrame(card_settings, fg_color="transparent")
        settings_header.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(settings_header, text="⚙️   Ayarlar", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left")

        # Sesli Doğrulama Checkbox
        self.chk_audio_captcha = ctk.CTkCheckBox(card_settings, text="Sesli Doğrulama Kullan (Ücretsiz reCAPTCHA)",
                                                  variable=self.var_audio_captcha,
                                                  fg_color=TEXT_MAIN, text_color=TEXT_MAIN,
                                                  checkmark_color="#000000",
                                                  font=ctk.CTkFont(family="Segoe UI", size=10))
        self.chk_audio_captcha.pack(anchor="w", padx=14, pady=(0, 8))

        # Token Doğrulama Checkbox
        self.chk_token_captcha = ctk.CTkCheckBox(card_settings, text="Ücretli Token Çözücüleri Kullan (2captcha / CapSolver)",
                                                  variable=self.var_token_captcha,
                                                  fg_color=TEXT_MAIN, text_color=TEXT_MAIN,
                                                  checkmark_color="#000000",
                                                  font=ctk.CTkFont(family="Segoe UI", size=10))
        self.chk_token_captcha.pack(anchor="w", padx=14, pady=(0, 12))

        # 2. Log Kartı
        card_log = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_log.pack(fill="both", expand=True, padx=4, pady=(6, 6))

        log_header = ctk.CTkFrame(card_log, fg_color=BG_PANEL, corner_radius=0, height=40)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        ctk.CTkLabel(log_header, text="📋  İşlem Kayıtları (Log)", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=14, pady=8)
                     
        ctk.CTkButton(log_header, text="Temizle", text_color=TEXT_SUB, fg_color="transparent",
                      hover_color=BG_ELEVATED, command=self._clear_log, width=60, height=24,
                      font=ctk.CTkFont(family="Segoe UI", size=9)).pack(side="right", padx=14, pady=8)

        # CTkTextbox entegre scrollbar barındırır
        self.txt_log = ctk.CTkTextbox(card_log, fg_color=BG_DEEP, text_color=TEXT_SUB,
                                      font=("Cascadia Code", 9), corner_radius=6)
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)
        self.txt_log.configure(state="disabled")

        # Log Renk Etiketleri (NameError DÜZELTİLDİ: C kütüphanesi yerine doğrudan renk atamaları kullanıldı)
        self.txt_log.tag_config("success", foreground=COLOR_SUCCESS)
        self.txt_log.tag_config("error",   foreground=COLOR_ERROR)
        self.txt_log.tag_config("info",    foreground=COLOR_INFO)
        self.txt_log.tag_config("muted",   foreground=COLOR_MUTED)
        self.txt_log.tag_config("accent",  foreground=COLOR_ACCENT)

    # ──────────────────────────────────────────────────────────────────────────
    # SAĞ SÜTUN (Excel Veri Önizleme & Search Bar)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_right_col(self):
        card = ctk.CTkFrame(self.col_right, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card.pack(fill="both", expand=True, padx=4, pady=6)

        # Header bar
        header = ctk.CTkFrame(card, fg_color=BG_PANEL, corner_radius=0, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="📊  Veri Önizleme", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=14, pady=8)
                     
        self.lbl_row_count = ctk.CTkLabel(header, text="", text_color=TEXT_SUB,
                                          font=ctk.CTkFont(family="Segoe UI", size=10))
        self.lbl_row_count.pack(side="left", padx=8)

        # Tablo Arama Kutusu (Search Filter)
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right", padx=12, pady=6)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Tabloda ara...",
                                         fg_color=BG_DEEP, border_color=BORDER,
                                         width=160, height=26,
                                         font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_search.pack(side="right")
        self.entry_search.bind("<KeyRelease>", self.filter_preview_data)

        # Tablo Alanı
        tree_frame = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.preview_tree = ttk.Treeview(tree_frame,
            style="Modern.Treeview",
            selectmode="browse", show="headings")

        h_sb = ctk.CTkScrollbar(tree_frame, orientation="horizontal", command=self.preview_tree.xview)
        v_sb = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)
        
        h_sb.pack(side="bottom", fill="x")
        v_sb.pack(side="right",  fill="y")
        self.preview_tree.pack(fill="both", expand=True)

        self.preview_tree.tag_configure("even", background=BG_CARD)
        self.preview_tree.tag_configure("odd",  background=BG_PANEL)

    # ──────────────────────────────────────────────────────────────────────────
    # STATUS BAR
    # ──────────────────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        divider = ctk.CTkFrame(self.root, fg_color=BORDER, height=1, corner_radius=0)
        divider.pack(fill="x")
        
        bar = ctk.CTkFrame(self.root, fg_color=BG_PANEL, height=30, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.lbl_status = ctk.CTkLabel(bar, text="● Hazır", text_color=WHITE,
                                       font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), padx=14)
        self.lbl_status.pack(side="left", pady=3)

        self.progress = ctk.CTkProgressBar(bar, width=120, height=6, fg_color=BG_CARD, progress_color=WHITE)
        self.progress.configure(mode="indeterminate")

        ctk.CTkLabel(bar, text="T Bot v3.0  •  TÜGVA Otomasyonu", text_color=TEXT_SUB,
                     font=ctk.CTkFont(family="Segoe UI", size=9), padx=14).pack(side="right", pady=3)

    # ──────────────────────────────────────────────────────────────────────────
    # VERİ DOSYASI İŞLEMLERİ & FİLTRELEME
    # ──────────────────────────────────────────────────────────────────────────
    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Veri Dosyası Seç",
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv"), ("Tümü", "*.*")])
        if path:
            self.file_path = path
            self.lbl_file.configure(text=os.path.basename(path))
            self.load_preview_data()

    def load_preview_data(self):
        try:
            if self.file_path.lower().endswith(".csv"):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    sep = ";" if ";" in f.readline() else ","
                df = pd.read_csv(self.file_path, sep=sep, dtype=str).fillna("")
            else:
                df = pd.read_excel(self.file_path, dtype=str).fillna("")

            # Sütun Başlıklarını Ayarla
            self.df_preview = df
            cols = list(df.columns)
            self.preview_tree["columns"] = cols
            self.preview_tree.delete(*self.preview_tree.get_children())
            for col in cols:
                self.preview_tree.heading(col, text=col, anchor="w")
                w = max(90, min(180, len(col)*12))
                self.preview_tree.column(col, anchor="w", width=w,
                                         minwidth=70, stretch=True)

            for i, (_, row) in enumerate(df.head(200).iterrows()):
                tag = "even" if i % 2 == 0 else "odd"
                self.preview_tree.insert("", "end", values=list(row), tags=(tag,))

            self.lbl_row_count.configure(
                text=f"({len(df)} satır, {len(cols)} sütun)")
            
            # Toplam Sayısı Güncelle
            self.card_total.configure(text=str(len(df)))

            # Atlanan Sayısı Güncelle (completed.txt içindeki TC'lerle kıyasla)
            completed_tckns = set()
            if os.path.exists('completed.txt'):
                 with open('completed.txt', 'r') as f:
                     completed_tckns = {line.strip() for line in f if line.strip()}
            
            tc_col = None
            for col in df.columns:
                if col.strip().lower() in ['t.c.', 't.c. kimlik no', 't.c kimlik no', 'tc kimlik no','t.c'
                                           't.c. kimlik', 'tc kimlik', 'tc no', 'tc', 'tc_no', 'kimlik']:
                    tc_col = col
                    break
            
            skip_count = 0
            if tc_col is not None:
                for _, row in df.iterrows():
                    tc = str(row[tc_col]).strip()
                    if tc in completed_tckns:
                        skip_count += 1
            
            self.card_skip.configure(text=str(skip_count))

            self.log_message(f"⬛  Önizleme yüklendi → {len(df)} kayıt, {len(cols)} sütun", tag="info")
        except Exception as e:
            self.log_message(f"⛔  Önizleme hatası: {e}", tag="error")

    def filter_preview_data(self, event=None):
        if self.df_preview is None:
            return
        
        query = self.entry_search.get().strip().lower()
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        if query == "":
            filtered_df = self.df_preview.head(200)
        else:
            # Kolonların herhangi birinde arama sorgusu içeren satırları seçelim
            mask = self.df_preview.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)
            filtered_df = self.df_preview[mask].head(200)
            
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            self.preview_tree.insert("", "end", values=list(row), tags=(tag,))

    def load_completed_from_file(self):
        if not os.path.exists("completed.txt"):
            return
        try:
            with open("completed.txt", "r") as f:
                for i, line in enumerate(f):
                    entry = line.strip()
                    if entry:
                        tag = "even" if i % 2 == 0 else "odd"
                        self.completed_tree.insert(
                            "", "end",
                            values=(entry, "Önceki Oturum", "—"),
                            tags=(tag,))
            self._update_done_counter()
        except Exception as e:
            self.log_message(f"Tamamlananlar yüklenemedi: {e}", tag="error")

    def _clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state="disabled")

    def _clear_completed(self):
        if not messagebox.askyesno("Sıfırla", "Tamamlanan başvuruları sıfırlamak (tamamlananlar listesini ve completed.txt dosyasını temizlemek) istediğinize emin misiniz?"):
            return
        try:
            with open("completed.txt", "w") as f:
                f.write("")
            self.completed_tree.delete(*self.completed_tree.get_children())
            self._update_done_counter()
            if self.file_path and os.path.exists(self.file_path):
                self.load_preview_data()
            else:
                self.card_skip.configure(text="0")
            self.log_message("✅  Tamamlanan başvurular sıfırlandı.", tag="success")
        except Exception as e:
            self.log_message(f"⛔  Sıfırlama hatası: {e}", tag="error")

    # ──────────────────────────────────────────────────────────────────────────
    # LOG İLETİLERİ & YAZIMI
    # ──────────────────────────────────────────────────────────────────────────
    def log_message(self, msg_str, tag=None):
        self.txt_log.configure(state="normal")
        ts  = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg_str}\n"

        if tag is None:
            ml = msg_str.lower()
            if "[+]" in msg_str or "başarı" in ml or "success" in ml or "✅" in msg_str:
                tag = "success"
            elif "[!]" in msg_str or "hata" in ml or "error" in ml or "⛔" in msg_str:
                tag = "error"
            elif "[i]" in msg_str or "⬛" in msg_str:
                tag = "info"
            elif "===" in msg_str:
                tag = "accent"
            elif "---" in msg_str or "..." in msg_str:
                tag = "muted"

        self.txt_log.insert(tk.END, line, tag if tag else "")
        self.txt_log.see(tk.END)
        self.txt_log.configure(state="disabled")

        if "   [+] SUCCESS:" in msg_str:
            try:
                raw = msg_str.replace("   [+] SUCCESS:", "").strip()
                last_colon = raw.rfind(":")
                if last_colon != -1:
                    name_part   = raw[:last_colon]
                    tracking_id = raw[last_colon+1:]
                else:
                    name_part = tracking_id = raw
                n = len(self.completed_tree.get_children())
                tag2 = "even" if n % 2 == 0 else "odd"
                now_str = datetime.now().strftime("%H:%M")
                self.completed_tree.insert("", 0,
                    values=(tracking_id, name_part, now_str),
                    tags=(tag2,))
                self._update_done_counter()
            except: pass

    def _update_done_counter(self):
        n = len(self.completed_tree.get_children())
        self.card_done.configure(text=str(n))

    # ──────────────────────────────────────────────────────────────────────────
    # BOT KONTROL METOTLARI
    # ──────────────────────────────────────────────────────────────────────────
    def start_bot(self):
        if self.is_running: return
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showwarning("Dosya Seç", "Lütfen önce bir veri dosyası seçin.")
            return

        self.is_running = True
        self.btn_start.configure(state="disabled", fg_color=TEXT_MUTED, text_color=TEXT_SUB)
        self.btn_stop.configure(state="normal")
        self.progress.pack(side="left", padx=10, pady=3)
        self.progress.start()
        self._animate_dots()
        self.log_message("🚀  Bot başlatılıyor…", tag="accent")

        self.thread = threading.Thread(target=self._bot_thread)
        self.thread.daemon = True
        self.thread.start()

    def stop_bot(self):
        if self.is_running:
            bot.STOP_BOT = True
            self.log_message("⏹  Durdurma isteği gönderildi…", tag="error")
            self.btn_stop.configure(state="disabled")

    def _bot_thread(self):
        try:
            use_audio = self.var_audio_captcha.get()
            use_token = self.var_token_captcha.get()
            bot.run_bot(self.file_path, log_callback=self._safe_log, use_audio_captcha=use_audio, use_token_captcha=use_token)
        except Exception as e:
            self._safe_log(f"⛔  KRİTİK HATA: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self._on_bot_done)

    def _safe_log(self, msg):
        self.root.after(0, lambda m=msg: self.log_message(m))

    def _on_bot_done(self):
        self.btn_start.configure(state="normal", fg_color=ACCENT, text_color="#000000")
        self.btn_stop.configure(state="disabled")
        self.lbl_status.configure(text="● Durdu", text_color=TEXT_SUB)
        self.pulse_badge.configure(text="● DURDU", text_color=TEXT_SUB)
        self.progress.stop()
        self.progress.pack_forget()
        if self._status_job:
            self.root.after_cancel(self._status_job)
        self.log_message("🏁  Bot işlemi sonlandı.", tag="info")

    def _animate_dots(self):
        if not self.is_running: return
        
        # Canlı Pulsing/Yanıp Sönen Durum Badgesi & Animasyonlu Noktalar
        colors = ["#ffffff", "#e5e5e5", "#a6a6a6", "#5c5c5c"]
        current_color = colors[self._dot_count % len(colors)]
        dots = "." * (self._dot_count % 4)
        
        self.pulse_badge.configure(text=f"● ÇALIŞIYOR{dots}", text_color=current_color)
        self.lbl_status.configure(text=f"● Çalışıyor{dots}", text_color=WHITE)
        
        self._dot_count += 1
        self._status_job = self.root.after(400, self._animate_dots)

    def close_app(self):
        if self.is_running:
            if not messagebox.askyesno("Çıkış", "Bot çalışıyor. Yine de çıkılsın mı?"):
                return
            bot.STOP_BOT = True
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app  = App(root)
    root.mainloop()
