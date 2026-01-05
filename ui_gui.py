import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import os
from engine import ChatEngine  # Importa il motore di chat con logica di gioco

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📱 FakeChat Simulator")
        self.root.geometry("500x700")
        self.root.configure(bg="#ECE5DD")  # Sfondo stile WhatsApp

        # Stato del gioco e variabili GUI
        self.engine = None
        self.lock = threading.Lock()
        self.running = False
        self.selected_msg_idx = None
        self.message_labels = []

        self.show_menu()  # Mostra il menu iniziale

    # ==========================
    # NUOVA PARTITA
    # ==========================
    def new_game(self):
        self.engine = ChatEngine()
        self.engine.reset_state()
        self.start_game()

    # ==========================
    # CARICA PARTITA
    # ==========================
    def load_game(self):
        self.engine = ChatEngine()
        self.start_game()

    # ==========================
    # MENU INIZIALE
    # ==========================
    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title = tk.Label(self.root, text="📱 FakeChat Simulator",
                         font=("Helvetica", 20, "bold"), bg="#ECE5DD")
        title.pack(pady=40)

        tk.Button(self.root, text="🆕 Nuova Partita", font=("Helvetica", 14),
                  width=20, command=self.new_game).pack(pady=10)
        tk.Button(self.root, text="📖 Regole", font=("Helvetica", 14),
                  width=20, command=self.show_readme).pack(pady=10)
        tk.Button(self.root, text="💾 Carica Partita", font=("Helvetica", 14),
                  width=20, command=self.load_game).pack(pady=10)
        tk.Button(self.root, text="📊 Statistiche", font=("Helvetica", 14),
                  width=20, command=self.show_stats).pack(pady=10)

    # ==========================
    # MOSTRA README
    # ==========================
    def show_readme(self):
        readme_path = os.path.abspath("README.md")
        if not os.path.exists(readme_path):
            messagebox.showerror("Errore", "README.md non trovato!")
            return

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        readme_window = tk.Toplevel(self.root)
        readme_window.title("📖 Regole del Gioco")
        readme_window.geometry("600x600")
        readme_window.configure(bg="#ECE5DD")

        frame = tk.Frame(readme_window, bg="#ECE5DD")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame, bg="#ECE5DD", bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#ECE5DD")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_label = tk.Label(
            scroll_frame,
            text=content,
            justify="left",
            anchor="nw",
            bg="#ECE5DD",
            fg="#000000",
            font=("Helvetica", 12),
            wraplength=550
        )
        text_label.pack(fill=tk.BOTH, expand=True)

    # ==========================
    # AVVIO GIOCO
    # ==========================
    def start_game(self):
        self.running = True
        self.selected_msg_idx = None
        self.message_labels = []

        for widget in self.root.winfo_children():
            widget.destroy()

        self.frame_messages = tk.Frame(self.root, bg="#ECE5DD")
        self.frame_messages.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame_messages, bg="#ECE5DD", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame_messages, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#ECE5DD")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_reply = tk.Entry(self.root, font=("Helvetica", 12))
        self.entry_reply.pack(fill=tk.X, padx=10, pady=5)
        self.btn_send = tk.Button(self.root, text="Invia", command=self.send_reply)
        self.btn_send.pack(pady=5)

        self.btn_pause = tk.Button(self.root, text="⏸️ Pausa", command=self.pause_game)
        self.btn_pause.pack(side=tk.LEFT, padx=10, pady=5)
        self.btn_resume = tk.Button(self.root, text="▶️ Riprendi", command=self.resume_game)
        self.btn_resume.pack(side=tk.LEFT, padx=10, pady=5)
        self.btn_stats = tk.Button(self.root, text="📊 Statistiche", command=self.show_stats)
        self.btn_stats.pack(side=tk.RIGHT, padx=10, pady=5)

        threading.Thread(target=self.game_loop, daemon=True).start()

    # ==========================
    # LOOP GIOCO
    # ==========================
    def game_loop(self):
        while self.running:
            if self.engine.paused:
                time.sleep(0.5)
                continue
            with self.lock:
                if random.random() < 0.5:
                    self.engine.spawn_message()
                self.engine.tick()
                if self.engine.check_game_over():
                    self.running = False
                    self.engine.save_state()
                    messagebox.showinfo("Game Over","Hai ignorato troppi messaggi!\nPartita terminata.")
                    self.show_menu()
                    return
            self.refresh_messages()
            time.sleep(1)

    # ==========================
    # AGGIORNA MESSAGGI
    # ==========================
    def refresh_messages(self):
        for lbl in self.message_labels:
            lbl.destroy()
        self.message_labels = []

        for idx, msg in enumerate(self.engine.active_messages):
            bg_color = "#DCF8C6" if idx != self.selected_msg_idx else "#A8D5BA"
            fg_color = "#000000"
            anchor = "w" if msg["user"] != "Tu" else "e"

            lbl = tk.Label(
                self.scroll_frame,
                text=f"{msg['user']}: {msg['text']} ({msg['time_left']}s)",
                bg=bg_color,
                fg=fg_color,
                font=("Helvetica", 12),
                anchor=anchor,
                justify="left",
                padx=10, pady=5,
                wraplength=300,
                relief="ridge",
                bd=1
            )
            lbl.pack(fill=tk.X, pady=2, anchor=anchor)
            lbl.bind("<Button-1>", lambda e, i=idx: self.select_message(i))
            self.message_labels.append(lbl)

        self.canvas.yview_moveto(1.0)

    # ==========================
    # SELEZIONE MESSAGGIO
    # ==========================
    def select_message(self, idx):
        self.selected_msg_idx = idx
        self.refresh_messages()

    # ==========================
    # INVIO RISPOSTA
    # ==========================
    def send_reply(self):
        if self.selected_msg_idx is None:
            messagebox.showwarning("Attenzione","Seleziona un messaggio a cui rispondere!")
            return
        text = self.entry_reply.get().strip()
        if not text:
            messagebox.showwarning("Attenzione","Scrivi una risposta!")
            return
        with self.lock:
            ok, user = self.engine.answer_message(self.selected_msg_idx, text)
            if ok:
                self.entry_reply.delete(0, tk.END)
                self.selected_msg_idx = None
            self.engine.save_state()
        self.refresh_messages()

    # ==========================
    # PAUSA / RIPRESA
    # ==========================
    def pause_game(self):
        if self.engine:
            self.engine.paused = True
            messagebox.showinfo("Pausa","Gioco in pausa")

    def resume_game(self):
        if self.engine:
            self.engine.paused = False
            messagebox.showinfo("Ripreso","Gioco ripreso")

    # ==========================
    # STATISTICHE
    # ==========================
    def show_stats(self):
        if not self.engine:
            messagebox.showinfo("Statistiche","Nessuna partita in corso")
            return
        stats = self.engine.get_stats()
        msg = "\n".join([f"{u}: Rep {d['reputation']} | Ignorati {d['ignored']}" for u,d in stats.items()])
        msg += f"\n\nMessaggi ignorati totali: {self.engine.ignored_total}\nRisposte totali: {self.engine.total_answers}"
        messagebox.showinfo("Statistiche", msg)
