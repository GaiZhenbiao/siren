from __future__ import print_function
from faulthandler import disable
import os
import sys
import PySimpleGUI as sg
from asteroid.models import BaseModel
import numpy as np
import librosa
import soundfile as sf
import argparse

import librosa.display


def parse_args():
    parser = argparse.ArgumentParser(
        description="Siren -高质量、高效的多人声音频分离软件。可以实现分离2个同时说话的人声，以及背景噪音。 ")
    parser.add_argument("--audio",
                        help="需要分离的音频文件的路径")
    parser.add_argument("--model",
                        help="模型文件路径")
    parser.add_argument("--out", default=None, help="分离后音频存储路径。默认输出到同目录")
    parser.add_argument("--nogui",action='store_true',help="设置后不使用图形界面")
    args = parser.parse_args()
    return args

def vocal_separate(audio_path):
    global out_path
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

def check_none(resource, message='请输入路径！'):
    if resource == '':
        sg.popup_auto_close(message)
        return False
    return True

args = parse_args()
outpath=''
if not args.nogui:
    layout = [[sg.Text('请选择模型', key='-MODEL_DISPLAY-'), sg.Button('选择模型文件', key='-MODEL-')],
            [sg.Text('请选择待分离音频', key='-INPUT_DISPLAY-'),
            sg.Button('选择音频', key='-INPUT-')],
            [sg.Text('请选择输出文件夹', key='-OUTPUT_DISPLAY-'),
            sg.Button('选择输出文件夹', key='-OUTPUT-')],
            [sg.Button('处理', key='-RUN-')]
            ]

    # Create the Window
    window = sg.Window('Siren -高效、高质量的多人声音频分离', layout,
                    resizable=True, finalize=True, icon="mermaid2.ico")
    window.TKroot.minsize(400, 160)
    user_data = {
        'model_path': '',
        'audio_path': '',
        'out_path': ''
    }
    # Event Loop to process "events" and get the "values" of the inputs
    cycle = 0
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        elif event == '-MODEL-':
            text = window['-MODEL_DISPLAY-']
            model_path = sg.popup_get_file('请输入模型文件路径')
            if check_none(model_path):
                user_data['model_path'] = model_path
                text.update(value=model_path)
        elif event == '-INPUT-':
            text = window['-INPUT_DISPLAY-']
            audio_path = sg.popup_get_file('请输入音频文件路径')
            if check_none(audio_path):
                user_data['audio_path'] = audio_path
                text.update(value=audio_path)
        elif event == '-OUTPUT-':
            text = window['-OUTPUT_DISPLAY-']
            out_path = sg.popup_get_folder('你想输出到那个文件夹？')
            if check_none(out_path):
                user_data['out_path'] = out_path
                text.update(value=out_path)
        elif event == '-RUN-':
            if check_none(user_data['model_path'], "请指定模型文件！") and check_none(user_data['audio_path'], "请指定音频文件！"):
                if user_data['out_path'] == '':
                    out_path = os.path.dirname(user_data['audio_path'])
                else:
                    out_path = user_data['out_path']
                button = window['-RUN-']
                button.update(text="处理中(Stage 1/2)……")
                button.update(disabled=True)
                cycle = 1
        if cycle != 0:
            if cycle == 1:
                model = BaseModel.from_pretrained(user_data['model_path'])
                model.separate(user_data['audio_path'],
                            resample=True, output_dir=out_path)
                button.update(text="处理中(Stage 2/2)……")
                cycle = 2
            if cycle == 2:
                vocal_separate(user_data['audio_path'])
                button.update(text="处理")
                button.update(disabled=False)
                cycle = 0
    window.close()
else:
    if args.out is not None:
        out_path = args.out
    else:
        out_path = os.path.dirname(args.audio)
    print("Stage 1/2...")
    model = BaseModel.from_pretrained(args.model)
    model.separate(args.audio,
                resample=True, output_dir=out_path)
    print("Stage 2/2...")
    vocal_separate(args.audio)
    print("done.")