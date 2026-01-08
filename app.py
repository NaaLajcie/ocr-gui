import tkinter as tk
from tkinter import filedialog, messagebox
import cv2, pytesseract, os, hashlib
import pandas as pd
from glob import glob

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

FRAME_INTERVAL = 30
LANG = "pol+eng"

def ocr_image(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang=LANG)

def extract_video(video):
    cap = cv2.VideoCapture(video)
    frames = []
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        if i % FRAME_INTERVAL == 0:
            name = f"_frame_{i}.png"
            cv2.imwrite(name, frame)
            frames.append(name)
        i += 1
    cap.release()
    return frames

class App:
    def __init__(self, root):
        self.root = root
        root.title("OCR → Sheets")

        tk.Button(root, text="Wybierz pliki", command=self.load_files).pack(fill="x")
        self.text = tk.Text(root, height=15)
        self.text.pack(fill="both", expand=True)

        self.cols_entry = tk.Entry(root)
        self.cols_entry.insert(0, "Nazwa;Cena;Data")
        self.cols_entry.pack(fill="x")

        tk.Button(root, text="START OCR", command=self.process).pack(fill="x")

    def load_files(self):
        self.files = filedialog.askopenfilenames(filetypes=[("Media", "*.png *.jpg *.jpeg *.mp4")])
        self.text.insert("end", "\n".join(self.files) + "\n")

    def process(self):
        rows = []
        seen = set()

        for f in self.files:
            if f.lower().endswith(".mp4"):
                frames = extract_video(f)
                for fr in frames:
                    txt = ocr_image(fr).strip()
                    os.remove(fr)
                    if txt:
                        h = hashlib.md5(txt.encode()).hexdigest()
                        if h not in seen:
                            seen.add(h)
                            rows.append(txt)
            else:
                txt = ocr_image(f).strip()
                if txt:
                    h = hashlib.md5(txt.encode()).hexdigest()
                    if h not in seen:
                        seen.add(h)
                        rows.append(txt)

        cols = self.cols_entry.get().split(";")
        data = []
        for r in rows:
            parts = [p.strip() for p in r.split("\n") if p.strip()]
            row = parts[:len(cols)] + [""] * (len(cols)-len(parts))
            data.append(row)

        df = pd.DataFrame(data, columns=cols)
        df.to_csv("output.csv", index=False, encoding="utf-8")
        messagebox.showinfo("OK", "Zapisano output.csv")

root = tk.Tk()
App(root)
root.mainloop()
