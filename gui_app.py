import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from datetime import datetime
import ctypes
from PIL import Image

import bot
import bot_munazara
import excel_munazara
import excel_handler
import config

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
        self.root.title("T Bot — TÜGVA Başvuru Otomasyonu")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 780)
        self.root.configure(fg_color=BG_DEEP)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.file_path = ""
        self.df_preview = None
        self.munazara_data = None

        if os.path.exists("munazara_ornek.csv"):
            self.file_path = "munazara_ornek.csv"
        elif os.path.exists("yaz_okulu_test.xlsx"):
            self.file_path = "yaz_okulu_test.xlsx"
        elif os.path.exists("33.csv"):
            self.file_path = "33.csv"

        self.is_running = False
        self._dot_count  = 0
        self._status_job = None
        
        # Seçenek Değişkenleri
        self.var_program = tk.StringVar(value="Türkiye Münazara Yarışması")
        self.var_audio_captcha = tk.BooleanVar(value=True)
        self.var_token_captcha = tk.BooleanVar(value=bool(getattr(config, 'TWOCAPTCHA_API_KEY', '').strip()))
        self.var_school_exists = tk.BooleanVar(value=True) # Listede var mı?

        # Görseller & Stiller
        self._load_assets()
        self._setup_styles()

        # Arayüzü İnşa Et
        self._build_ui()
        set_dark_title_bar(self.root)

        # İlk Dosya Önizlemesi
        if self.file_path and os.path.exists(self.file_path):
            self.root.after(300, self.load_preview_data)

        self.log_message("⬛  T Bot hazır. Program seçin, veri dosyasını yükleyin ve Botu Başlatın.")

    def _load_assets(self):
        self.img_owl = None
        self.img_owl_sm = None
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "owl_logo.png")
            if os.path.exists(logo_path):
                self.img_owl = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(40, 40)
                )
                img = Image.open(logo_path).convert("RGBA")
                ico = img.resize((32, 32), Image.LANCZOS)
                from PIL import ImageTk
                self.img_owl_sm = ImageTk.PhotoImage(ico)
                self.root.iconphoto(True, self.img_owl_sm)
        except Exception as e:
            print(f"Logo yüklenemedi: {e}")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

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

    def _build_ui(self):
        self._build_topbar()

        self.content_area = ctk.CTkFrame(self.root, fg_color=BG_DEEP, corner_radius=0)
        self.content_area.pack(fill="both", expand=True, padx=8, pady=8)

        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=3, minsize=320) # Sol: Sayaçlar & Tamamlanan
        self.content_area.columnconfigure(1, weight=5, minsize=460) # Orta: Ayarlar, Dosya, Log
        self.content_area.columnconfigure(2, weight=5, minsize=460) # Sağ: Tablo Önizleme

        self.col_left = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_left.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.col_middle = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_middle.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.col_right = ctk.CTkFrame(self.content_area, fg_color=BG_DEEP, corner_radius=0)
        self.col_right.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)

        self._build_left_col()
        self._build_middle_col()
        self._build_right_col()
        self._build_statusbar()

    def _build_topbar(self):
        self.top_bar = ctk.CTkFrame(self.root, fg_color=BG_PANEL, height=64, corner_radius=0)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)

        title_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=16, pady=8)

        if self.img_owl:
            lbl_ico = ctk.CTkLabel(title_frame, image=self.img_owl, text="")
            lbl_ico.pack(side="left", padx=(0, 10))

        name_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        name_frame.pack(side="left")
        
        title_row = ctk.CTkFrame(name_frame, fg_color="transparent")
        title_row.pack(anchor="w")
        
        ctk.CTkLabel(title_row, text="T Bot", fg_color="transparent",
                     text_color=WHITE, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(side="left")
                     
        self.pulse_badge = ctk.CTkLabel(title_row, text="● HAZIR", fg_color="transparent",
                                        text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"))
        self.pulse_badge.pack(side="left", padx=(10, 0), pady=(4, 0))

        self.lbl_subtitle = ctk.CTkLabel(name_frame, text="TÜGVA Otomasyon Sistemi — Münazara & Yaz Okulu", fg_color="transparent",
                                         text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=9))
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

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

        divider = ctk.CTkFrame(self.root, fg_color=BORDER, height=1, corner_radius=0)
        divider.pack(fill="x")

    def _build_left_col(self):
        stats_frame = ctk.CTkFrame(self.col_left, fg_color="transparent")
        stats_frame.pack(fill="x", padx=4, pady=(6, 6))

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        self.card_total = self._build_stat_card(stats_frame, 0, "TOPLAM", "0")
        self.card_done  = self._build_stat_card(stats_frame, 1, "TAMAMLANAN", "0")
        self.card_skip  = self._build_stat_card(stats_frame, 2, "ATLANAN", "0")

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
            columns=("Takim", "Detay", "Saat"))

        self.completed_tree.heading("Takim",  text="Takım / TC", anchor="w")
        self.completed_tree.heading("Detay",  text="Yarışmacılar", anchor="w")
        self.completed_tree.heading("Saat",   text="Saat",        anchor="w")

        self.completed_tree.column("Takim",  anchor="w", width=110, minwidth=80)
        self.completed_tree.column("Detay",  anchor="w", width=130, minwidth=100)
        self.completed_tree.column("Saat",   anchor="w", width=65,  minwidth=50)

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
                     
        div = ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0)
        div.pack(fill="x", padx=16, pady=2)

        val_lbl = ctk.CTkLabel(card, text=value, text_color=WHITE,
                               font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"))
        val_lbl.pack(pady=(4, 10))
        return val_lbl

    def _build_middle_col(self):
        # 1. Program Seçimi & Dosya Kartı
        card_top = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_top.pack(fill="x", padx=4, pady=(6, 4))

        p_row = ctk.CTkFrame(card_top, fg_color="transparent")
        p_row.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(p_row, text="🎯  Program:", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=(0, 8))

        self.seg_program = ctk.CTkSegmentedButton(
            p_row, values=["Türkiye Münazara Yarışması", "TÜGVA Yaz Okulu"],
            variable=self.var_program, command=self._on_program_change,
            selected_color=WHITE, selected_hover_color=ACCENT_HOVER,
            text_color="#000000", unselected_color=BG_ELEVATED, unselected_hover_color=BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        )
        self.seg_program.pack(side="right", fill="x", expand=True)

        # Dosya Seçim Satırı
        f_row = ctk.CTkFrame(card_top, fg_color="transparent")
        f_row.pack(fill="x", padx=12, pady=(4, 10))

        file_box = ctk.CTkFrame(f_row, fg_color=BG_ELEVATED, corner_radius=6)
        file_box.pack(side="left", fill="x", expand=True)

        self.lbl_file = ctk.CTkLabel(file_box,
                                     text=os.path.basename(self.file_path) if self.file_path else "Dosya seçilmedi…",
                                     text_color=TEXT_SUB, font=ctk.CTkFont(family="Segoe UI", size=10),
                                     anchor="w", padx=10, pady=7)
        self.lbl_file.pack(fill="x")

        browse_btn = ctk.CTkButton(f_row, text="Gözat", fg_color=BG_ELEVATED, text_color=TEXT_MAIN,
                                   hover_color=BORDER, command=self.browse_file, width=80, height=28,
                                   font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"))
        browse_btn.pack(side="right", padx=(8, 0))

        # 2. Münazara Ayarları Kartı (Bölge, Okul, Danışman Hoca)
        self.card_munazara = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        self.card_munazara.pack(fill="x", padx=4, pady=(4, 4))

        m_head = ctk.CTkFrame(self.card_munazara, fg_color="transparent")
        m_head.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(m_head, text="🏛️   Münazara Okul & Danışman Bilgileri", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left")

        # Bölge ve İl/İlçe Satırı
        row_reg = ctk.CTkFrame(self.card_munazara, fg_color="transparent")
        row_reg.pack(fill="x", padx=12, pady=(2, 4))

        self.bolge_options = [
            "5 - Güneydoğu Anadolu Bölgesi",
            "1 - Akdeniz Bölgesi",
            "2 - Ankara - İzmir",
            "3 - Doğu Anadolu Bölgesi",
            "4 - Ege Bölgesi",
            "6 - İç Anadolu Bölgesi",
            "7 - İstanbul",
            "8 - Karadeniz Bölgesi",
            "9 - Marmara Bölgesi"
        ]
        self.cb_bolge = ctk.CTkOptionMenu(row_reg, values=self.bolge_options,
                                          fg_color=BG_ELEVATED, button_color=BORDER,
                                          dropdown_fg_color=BG_PANEL, text_color=TEXT_MAIN,
                                          font=ctk.CTkFont(family="Segoe UI", size=10),
                                          width=200, height=26)
        self.cb_bolge.set(self.bolge_options[0])
        self.cb_bolge.pack(side="left", padx=(0, 6))

        self.entry_city = ctk.CTkEntry(row_reg, placeholder_text="İl (Örn: Diyarbakır)",
                                       fg_color=BG_ELEVATED, border_color=BORDER,
                                       font=ctk.CTkFont(family="Segoe UI", size=10), height=26, width=105)
        self.entry_city.insert(0, "Diyarbakır")
        self.entry_city.pack(side="left", padx=(0, 6), fill="x", expand=True)

        self.entry_district = ctk.CTkEntry(row_reg, placeholder_text="İlçe (Örn: Kayapınar)",
                                           fg_color=BG_ELEVATED, border_color=BORDER,
                                           font=ctk.CTkFont(family="Segoe UI", size=10), height=26, width=105)
        self.entry_district.insert(0, "Kayapınar")
        self.entry_district.pack(side="left", fill="x", expand=True)

        # Okul / Lise Satırı
        row_school = ctk.CTkFrame(self.card_munazara, fg_color="transparent")
        row_school.pack(fill="x", padx=12, pady=(2, 4))

        self.entry_school = ctk.CTkEntry(row_school, placeholder_text="Lise / Okul Adı (Boş bırakılırsa rastgele seçilir)",
                                         fg_color=BG_ELEVATED, border_color=BORDER,
                                         font=ctk.CTkFont(family="Segoe UI", size=10), height=26)
        self.entry_school.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.chk_school_exists = ctk.CTkCheckBox(row_school, text="Listede Var",
                                                 variable=self.var_school_exists,
                                                 fg_color=TEXT_MAIN, text_color=TEXT_SUB,
                                                 checkmark_color="#000000",
                                                 font=ctk.CTkFont(family="Segoe UI", size=9))
        self.chk_school_exists.pack(side="right")

        # Danışman Hoca Satırı
        row_t1 = ctk.CTkFrame(self.card_munazara, fg_color="transparent")
        row_t1.pack(fill="x", padx=12, pady=(2, 4))

        self.entry_teacher_name = ctk.CTkEntry(row_t1, placeholder_text="Danışman Ad Soyad",
                                              fg_color=BG_ELEVATED, border_color=BORDER,
                                              font=ctk.CTkFont(family="Segoe UI", size=10), height=26)
        self.entry_teacher_name.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.entry_teacher_tc = ctk.CTkEntry(row_t1, placeholder_text="Danışman TC No",
                                            fg_color=BG_ELEVATED, border_color=BORDER,
                                            font=ctk.CTkFont(family="Segoe UI", size=10), height=26, width=120)
        self.entry_teacher_tc.pack(side="left", padx=(0, 6))

        row_t2 = ctk.CTkFrame(self.card_munazara, fg_color="transparent")
        row_t2.pack(fill="x", padx=12, pady=(2, 8))

        self.entry_teacher_phone = ctk.CTkEntry(row_t2, placeholder_text="Danışman Tel (5xx-xxx-xxxx)",
                                               fg_color=BG_ELEVATED, border_color=BORDER,
                                               font=ctk.CTkFont(family="Segoe UI", size=10), height=26)
        self.entry_teacher_phone.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.entry_teacher_email = ctk.CTkEntry(row_t2, placeholder_text="Danışman E-posta",
                                               fg_color=BG_ELEVATED, border_color=BORDER,
                                               font=ctk.CTkFont(family="Segoe UI", size=10), height=26)
        self.entry_teacher_email.pack(side="left", fill="x", expand=True)

        # 3. reCAPTCHA Ayarları Kartı
        card_settings = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_settings.pack(fill="x", padx=4, pady=(4, 4))

        settings_header = ctk.CTkFrame(card_settings, fg_color="transparent")
        settings_header.pack(fill="x", padx=12, pady=(6, 2))
        ctk.CTkLabel(settings_header, text="⚙️   reCAPTCHA Çözücü", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left")

        self.chk_audio_captcha = ctk.CTkCheckBox(card_settings, text="Sesli Doğrulama Kullan (Ücretsiz reCAPTCHA)",
                                                  variable=self.var_audio_captcha,
                                                  fg_color=TEXT_MAIN, text_color=TEXT_MAIN,
                                                  checkmark_color="#000000",
                                                  font=ctk.CTkFont(family="Segoe UI", size=10))
        self.chk_audio_captcha.pack(anchor="w", padx=12, pady=(2, 3))

        self.chk_token_captcha = ctk.CTkCheckBox(card_settings, text="2captcha API Çözümü Kullan (config.py anahtarı)",
                                                  variable=self.var_token_captcha,
                                                  fg_color=TEXT_MAIN, text_color=TEXT_MAIN,
                                                  checkmark_color="#000000",
                                                  font=ctk.CTkFont(family="Segoe UI", size=10))
        self.chk_token_captcha.pack(anchor="w", padx=12, pady=(2, 6))

        # 4. Log Kartı
        card_log = ctk.CTkFrame(self.col_middle, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card_log.pack(fill="both", expand=True, padx=4, pady=(4, 6))

        log_header = ctk.CTkFrame(card_log, fg_color=BG_PANEL, corner_radius=0, height=36)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        ctk.CTkLabel(log_header, text="📋  İşlem Kayıtları (Log)", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=14, pady=6)
                     
        ctk.CTkButton(log_header, text="Temizle", text_color=TEXT_SUB, fg_color="transparent",
                      hover_color=BG_ELEVATED, command=self._clear_log, width=60, height=22,
                      font=ctk.CTkFont(family="Segoe UI", size=9)).pack(side="right", padx=14, pady=6)

        self.txt_log = ctk.CTkTextbox(card_log, fg_color=BG_DEEP, text_color=TEXT_SUB,
                                      font=("Cascadia Code", 9), corner_radius=6)
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)
        self.txt_log.configure(state="disabled")

        self.txt_log.tag_config("success", foreground=COLOR_SUCCESS)
        self.txt_log.tag_config("error",   foreground=COLOR_ERROR)
        self.txt_log.tag_config("info",    foreground=COLOR_INFO)
        self.txt_log.tag_config("muted",   foreground=COLOR_MUTED)
        self.txt_log.tag_config("accent",  foreground=COLOR_ACCENT)

    def _build_right_col(self):
        card = ctk.CTkFrame(self.col_right, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card.pack(fill="both", expand=True, padx=4, pady=(6, 6))

        header = ctk.CTkFrame(card, fg_color=BG_PANEL, corner_radius=0, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="📊  Yüklenen Veri Önizlemesi", text_color=TEXT_MAIN,
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")).pack(side="left", padx=12)

        self.lbl_row_count = ctk.CTkLabel(header, text="(0 Kayıt)", text_color=TEXT_SUB,
                                         font=ctk.CTkFont(family="Segoe UI", size=9))
        self.lbl_row_count.pack(side="left", padx=4)

        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right", padx=12, pady=6)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Tabloda ara...",
                                         fg_color=BG_DEEP, border_color=BORDER,
                                         width=150, height=26,
                                         font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_search.pack(side="right")
        self.entry_search.bind("<KeyRelease>", self.filter_preview_data)

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

        ctk.CTkLabel(bar, text="T Bot v3.5  •  TÜGVA Otomasyonu", text_color=TEXT_SUB,
                     font=ctk.CTkFont(family="Segoe UI", size=9), padx=14).pack(side="right", pady=3)

    def _on_program_change(self, value=None):
        prog = self.var_program.get()
        if "Münazara" in prog:
            self.card_munazara.pack(fill="x", padx=4, pady=(4, 4), after=self.col_middle.winfo_children()[0])
            self.lbl_subtitle.configure(text="Türkiye Münazara Yarışması Takım Başvuru Otomasyonu")
        else:
            self.card_munazara.pack_forget()
            self.lbl_subtitle.configure(text="TÜGVA Yaz Okulu Başvuru Otomasyonu")
        
        if self.file_path and os.path.exists(self.file_path):
            self.load_preview_data()
        self.load_completed_from_file()

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Tablo / Veri Dosyası Seç",
            filetypes=[("Excel / CSV Dosyaları", "*.xlsx *.xls *.csv"), ("Tüm Dosyalar", "*.*")])
        if path:
            self.file_path = path
            self.lbl_file.configure(text=os.path.basename(path))
            self.load_preview_data()

    def load_preview_data(self):
        if not self.file_path or not os.path.exists(self.file_path):
            return

        prog = self.var_program.get()

        if "Münazara" in prog:
            data = excel_munazara.load_munazara_data(self.file_path)
            if 'error' in data:
                self.log_message(f"⛔  Hata: {data['error']}", tag="error")
                return

            self.munazara_data = data
            teams = data['teams']

            # Danışman Hoca bilgilerini otomatik doldur
            t = data.get('teacher', {})
            if t.get('name') and not self.entry_teacher_name.get().strip():
                self.entry_teacher_name.delete(0, tk.END)
                self.entry_teacher_name.insert(0, t['name'])
            if t.get('tc') and not self.entry_teacher_tc.get().strip():
                self.entry_teacher_tc.delete(0, tk.END)
                self.entry_teacher_tc.insert(0, t['tc'])
            if t.get('phone') and not self.entry_teacher_phone.get().strip():
                self.entry_teacher_phone.delete(0, tk.END)
                self.entry_teacher_phone.insert(0, t['phone'])
            if t.get('email') and not self.entry_teacher_email.get().strip():
                self.entry_teacher_email.delete(0, tk.END)
                self.entry_teacher_email.insert(0, t['email'])

            cols = ["Takım Adı", "Okul / Lise", "1. Yarışmacı", "1. TC", "2. Yarışmacı", "2. TC", "Danışman"]
            self.preview_tree["columns"] = cols
            self.preview_tree.delete(*self.preview_tree.get_children())
            for col in cols:
                self.preview_tree.heading(col, text=col, anchor="w")
                if "Okul" in col:
                    w = 190
                elif "TC" in col or "Takım" in col:
                    w = 95
                else:
                    w = 125
                self.preview_tree.column(col, anchor="w", width=w, minwidth=70, stretch=True)

            t_name = self.entry_teacher_name.get().strip() or t.get('name') or "—"
            for i, tm in enumerate(teams):
                tag = "even" if i % 2 == 0 else "odd"
                tm_school = tm.get('school', '')
                tm_teacher = tm.get('teacher', {}).get('name') or t_name
                self.preview_tree.insert("", "end", values=[
                    tm['team_name'],
                    tm_school,
                    tm['p1']['name'], tm['p1']['tc'],
                    tm['p2']['name'], tm['p2']['tc'],
                    tm_teacher
                ], tags=(tag,))

            self.card_total.configure(text=str(len(teams)))
            self.lbl_row_count.configure(text=f"({len(teams)} Takım, {data['total_students']} Öğrenci)")

            # Atlanan (önceden tamamlanan) takım sayısı
            completed_file = 'completed_munazara.txt'
            completed_teams = set()
            if os.path.exists(completed_file):
                with open(completed_file, 'r', encoding='utf-8') as f:
                    completed_teams = {line.strip() for line in f if line.strip()}

            skip_count = 0
            for tm in teams:
                tracking_id = f"{tm['team_name']}_{tm['p1']['tc']}_{tm['p2']['tc']}"
                if tracking_id in completed_teams:
                    skip_count += 1
            self.card_skip.configure(text=str(skip_count))

            if data['warnings']:
                for w in data['warnings']:
                    self.log_message(f"⚠️  {w}", tag="info")

            self.log_message(f"⬛  Münazara tablosu yüklendi → {len(teams)} Takım ({data['total_students']} öğrenci)", tag="info")

        else:
            # Standart Yaz Okulu tablosu
            try:
                if self.file_path.lower().endswith(".csv"):
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        sep = ";" if ";" in f.readline() else ","
                    df = pd.read_csv(self.file_path, sep=sep, dtype=str).fillna("")
                else:
                    df = pd.read_excel(self.file_path, dtype=str).fillna("")

                self.df_preview = df
                cols = list(df.columns)
                self.preview_tree["columns"] = cols
                self.preview_tree.delete(*self.preview_tree.get_children())
                for col in cols:
                    self.preview_tree.heading(col, text=col, anchor="w")
                    w = max(90, min(180, len(col)*12))
                    self.preview_tree.column(col, anchor="w", width=w, minwidth=70, stretch=True)

                for i, (_, row) in enumerate(df.head(200).iterrows()):
                    tag = "even" if i % 2 == 0 else "odd"
                    self.preview_tree.insert("", "end", values=list(row), tags=(tag,))

                self.lbl_row_count.configure(text=f"({len(df)} satır, {len(cols)} sütun)")
                self.card_total.configure(text=str(len(df)))

                completed_tckns = set()
                if os.path.exists('completed.txt'):
                    with open('completed.txt', 'r', encoding='utf-8') as f:
                        completed_tckns = {line.strip() for line in f if line.strip()}
                
                tc_col = None
                for col in df.columns:
                    if col.strip().lower() in ['t.c.', 't.c. kimlik no', 't.c kimlik no', 'tc kimlik no','t.c',
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
                self.log_message(f"⬛  Önizleme yüklendi → {len(df)} kayıt", tag="info")

            except Exception as e:
                self.log_message(f"⛔  Önizleme hatası: {e}", tag="error")

    def filter_preview_data(self, event=None):
        query = self.entry_search.get().strip().lower()
        prog = self.var_program.get()

        if "Münazara" in prog and self.munazara_data:
            self.preview_tree.delete(*self.preview_tree.get_children())
            teams = self.munazara_data['teams']
            t_name = self.entry_teacher_name.get().strip()
            for i, tm in enumerate(teams):
                match = (query == "" or
                         query in tm['team_name'].lower() or
                         query in tm['p1']['name'].lower() or
                         query in tm['p1']['tc'].lower() or
                         query in tm['p2']['name'].lower() or
                         query in tm['p2']['tc'].lower())
                if match:
                    tag = "even" if i % 2 == 0 else "odd"
                    self.preview_tree.insert("", "end", values=[
                        tm['team_name'],
                        tm['p1']['name'], tm['p1']['tc'],
                        tm['p2']['name'], tm['p2']['tc'],
                        t_name
                    ], tags=(tag,))
        elif self.df_preview is not None:
            self.preview_tree.delete(*self.preview_tree.get_children())
            if query == "":
                filtered_df = self.df_preview.head(200)
            else:
                mask = self.df_preview.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)
                filtered_df = self.df_preview[mask].head(200)
                
            for i, (_, row) in enumerate(filtered_df.iterrows()):
                tag = "even" if i % 2 == 0 else "odd"
                self.preview_tree.insert("", "end", values=list(row), tags=(tag,))

    def load_completed_from_file(self):
        self.completed_tree.delete(*self.completed_tree.get_children())
        prog = self.var_program.get()
        target_file = 'completed_munazara.txt' if "Münazara" in prog else 'completed.txt'

        if not os.path.exists(target_file):
            self.card_done.configure(text="0")
            return

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    entry = line.strip()
                    if entry:
                        tag = "even" if i % 2 == 0 else "odd"
                        parts = entry.split('_') if '_' in entry else [entry, 'Önceki Oturum']
                        takim_part = parts[0]
                        detay_part = " & ".join(parts[1:]) if len(parts) > 1 else "Tamamlandı"
                        self.completed_tree.insert("", "end", values=(takim_part, detay_part, "—"), tags=(tag,))
            self._update_done_counter()
        except Exception as e:
            self.log_message(f"Tamamlananlar yüklenemedi: {e}", tag="error")

    def _clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state="disabled")

    def _clear_completed(self):
        prog = self.var_program.get()
        target_file = 'completed_munazara.txt' if "Münazara" in prog else 'completed.txt'

        if not messagebox.askyesno("Sıfırla", f"Tamamlanan başvuruları ({target_file}) sıfırlamak istediğinize emin misiniz?"):
            return
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write("")
            self.completed_tree.delete(*self.completed_tree.get_children())
            self._update_done_counter()
            self.load_preview_data()
            self.log_message("✅  Tamamlanan başvurular sıfırlandı.", tag="success")
        except Exception as e:
            self.log_message(f"⛔  Sıfırlama hatası: {e}", tag="error")

    def log_message(self, msg_str, tag=None):
        self.txt_log.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
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
                parts = raw.split(":")
                takim = parts[0]
                detay = parts[1] if len(parts) > 1 else ""
                n = len(self.completed_tree.get_children())
                tag2 = "even" if n % 2 == 0 else "odd"
                now_str = datetime.now().strftime("%H:%M")
                self.completed_tree.insert("", 0, values=(takim, detay, now_str), tags=(tag2,))
                self._update_done_counter()
            except: pass

    def _update_done_counter(self):
        n = len(self.completed_tree.get_children())
        self.card_done.configure(text=str(n))

    def start_bot(self):
        if self.is_running: return
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showwarning("Dosya Seç", "Lütfen önce bir veri tablosu seçin.")
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
            bot_munazara.STOP_MUNAZARA_BOT = True
            self.log_message("⏹  Durdurma isteği gönderildi…", tag="error")
            self.btn_stop.configure(state="disabled")

    def _bot_thread(self):
        try:
            use_audio = self.var_audio_captcha.get()
            use_token = self.var_token_captcha.get()
            prog = self.var_program.get()

            if "Münazara" in prog:
                # Seçili bölgenin numarasını al (örn "5 - Güneydoğu..." -> "5")
                b_str = self.cb_bolge.get().split('-')[0].strip()
                school_info = {
                    'bolge_val': b_str,
                    'city': self.entry_city.get().strip(),
                    'district': self.entry_district.get().strip(),
                    'school': self.entry_school.get().strip(),
                    'school_in_list': self.var_school_exists.get(),
                    'teacher': {
                        'name': self.entry_teacher_name.get().strip(),
                        'tc': self.entry_teacher_tc.get().strip(),
                        'phone': self.entry_teacher_phone.get().strip(),
                        'email': self.entry_teacher_email.get().strip(),
                    }
                }
                bot_munazara.run_munazara_bot(self.file_path, school_info,
                                              log_callback=self._safe_log,
                                              use_audio_captcha=use_audio,
                                              use_token_captcha=use_token)
            else:
                bot.run_bot(self.file_path, log_callback=self._safe_log,
                            use_audio_captcha=use_audio,
                            use_token_captcha=use_token)

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
            bot_munazara.STOP_MUNAZARA_BOT = True
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
