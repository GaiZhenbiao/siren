from faulthandler import disable
import PySimpleGUI as sg
from asteroid.models import BaseModel


def check_none(resource, message='请输入路径！'):
    if resource == '':
        sg.popup_auto_close(message)
        return False
    return True


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
                out_path = None
            else:
                out_path = user_data['out_path']
            button = window['-RUN-']
            button.update(text="处理中……")
            button.update(disabled=True)
            model = BaseModel.from_pretrained(user_data['model_path'])
            model.separate(user_data['audio_path'],
                           resample=True, output_dir=out_path)
            button.update(text="处理")
            button.update(disabled=False)


window.close()
