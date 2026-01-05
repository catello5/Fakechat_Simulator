import tkinter as tk  # Libreria grafica Tkinter
from ui_gui import ChatGUI  # Importa la classe GUI del gioco

# ==============================
# PUNTO DI INGRESSO DEL PROGRAMMA
# ==============================
if __name__ == "__main__":
    # Crea la finestra principale
    root = tk.Tk()

    # Inizializza la GUI del gioco all'interno della finestra root
    ChatGUI(root)

    # Avvia il loop principale di Tkinter
    # Questo mantiene aperta la finestra e gestisce eventi (click, input, ecc.)
    root.mainloop()
