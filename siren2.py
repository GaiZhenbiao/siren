import os
import argparse
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox

import numpy as np
import soundfile as sf
import librosa
import librosa.display
from asteroid.models import BaseModel


def parse_args():
    parser = argparse.ArgumentParser(
        description="Siren -高质量、高效的多人声音频分离软件。可以实现分离2个同时说话的人声，以及背景噪音。 ")
    parser.add_argument("--audio",
                        help="需要分离的音频文件的路径")
    parser.add_argument("--model",
                        help="模型文件路径")
    parser.add_argument("--out", default=None, help="分离后音频存储路径。默认输出到同目录")
    parser.add_argument("--nogui", action='store_true', help="设置后不使用图形界面")
    args = parser.parse_args()
    return args


def seperate_vocal(model_path, audio_path, out_path):
    model = BaseModel.from_pretrained(model_path)
    model.separate(audio_path,
                   resample=True, output_dir=out_path)


def seperate_foreground_and_background(audio_path, out_path):
    y, sr = librosa.load(audio_path)
    S_full, phase = librosa.magphase(librosa.stft(y))
    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))
    S_filter = np.minimum(S_full, S_filter)
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)
    S_foreground = mask_v * S_full
    S_background = mask_i * S_full
    D_foreground = S_foreground * phase
    y_foreground = librosa.istft(D_foreground)
    D_background = S_background * phase
    y_background = librosa.istft(D_background)
    sf.write(f"{out_path}/background.wav", y_background, sr, subtype='PCM_24')
    sf.write(f"{out_path}/foreground.wav", y_foreground, sr, subtype='PCM_24')


MODEL_PATH = "resources/pretrained/ConvTasNet_Libri2Mix_sepnoisy_16k.bin"


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.audio_prompt = "未选择音频文件"
        self.outdir_prompt = "默认输出到音频文件同目录下"
        self.process_prompt = "处理"
        photo = tk.PhotoImage(file="resources/images/siren.png")

        self.audio_display = ttk.Label(master)
        self.select_audio_btn = ttk.Button(master, text="选择音频")
        self.outdir_display = ttk.Label(master)
        self.select_outdir_btn = ttk.Button(master, text="选择输出路径")
        self.process_btn = ttk.Button(master, text=self.process_prompt)
        self.image = ttk.Label(master, image=photo)

        self.image.grid(row=0, columnspan=2)
        self.audio_display.grid(row=1, column=0, sticky="w", padx=10)
        self.select_audio_btn.grid(row=1, column=1, sticky="e", padx=10)
        self.outdir_display.grid(row=2, column=0, sticky="w", padx=10)
        self.select_outdir_btn.grid(row=2, column=1, sticky="e", padx=10)
        self.process_btn.grid(row=3, column=1, sticky="s", padx=10, pady=10)

        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.rowconfigure(3, weight=1)

        # Create the application variable.
        self.audio_path = tk.StringVar()
        self.outdir_path = tk.StringVar()
        self.process_bthtext = tk.StringVar()
        # Set it to some value.
        self.audio_path.set(self.audio_prompt)
        self.outdir_path.set(self.outdir_prompt)
        self.process_bthtext.set(self.process_prompt)
        # Tell the entry widget to watch this variable.
        self.audio_display["textvariable"] = self.audio_path
        self.outdir_display["textvariable"] = self.outdir_path
        self.process_btn["textvariable"] = self.process_bthtext

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.select_audio_btn.bind("<Button-1>", self.select_audio)
        self.select_outdir_btn.bind("<Button-1>", self.select_dir)
        self.process_btn.bind("<Button-1>", self.process)

    def check_none(self, src, message='路径不存在！'):
        if not(os.path.isdir(src) or os.path.isfile(src)):
            tkinter.messagebox.showerror(title="路径错误", message=message)
            return False
        return True

    def select_audio(self, event):
        name = tkinter.filedialog.askopenfile()
        self.audio_path.set(name.name)
        self.outdir_path.set(os.path.dirname(name.name))

    def select_dir(self, event):
        name = tkinter.filedialog.askdirectory()
        self.outdir_path.set(name.name)

    def process(self, event):
        audio = self.audio_path.get()
        outdir = self.outdir_path.get()
        if self.check_none(audio, "未选择音频文件，或者文件路径错误") and self.check_none(outdir, "未选择输出路径，或者输出路径错误"):
            self.process_btn["state"] = tk.DISABLED
            self.process_bthtext.set("分离人声中(阶段 1/2)……")
            tk.Tk.update(self=self)
            seperate_vocal(
                MODEL_PATH, audio, outdir)
            self.process_bthtext.set("分离噪声中(阶段 2/2)……")
            tk.Tk.update(self=self)
            seperate_foreground_and_background(
                audio, outdir)
            self.process_bthtext.set(self.process_prompt)
            self.process_btn["state"] = tk.ACTIVE
            tk.Tk.update(self=self)


args = parse_args()
if not args.nogui:
    root = tk.Tk()
    root.iconbitmap("resources/images/mermaid.ico")
    root.title("Siren 高效多人声分离")
    root.minsize(300, 180)
    myapp = App(root)
    myapp.mainloop()
else:
    print("分离人声中(阶段 1/2)……")
    seperate_vocal(MODEL_PATH, args.audio, args.out)
    print("分离噪声中(阶段 2/2)……")
    seperate_foreground_and_background(args.audio, args.out)
    print("完成")
