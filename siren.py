from turtle import width
import PySimpleGUI as sg

layout = [[sg.Text('请选择模型', key='-MODEL_DISPLAY-'), sg.Button('选择模型文件', key='-MODEL-')],
          [sg.Text('请选择待分离音频', key='-INPUT_DISPLAY-'), sg.Button('选择模型文件', key='-INPUT-')],
          [sg.Text('请选择输出文件夹啊', key='-OUTPUT_DISPLAY-'), sg.Button('选择模型文件', key='-OUTPUT-')],
          [sg.Button('选择模型文件', key='-RUN-')]]

# Create the Window
window = sg.Window('Siren 音频分离')
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    elif event == '-MODEL-':
        text = window['-MODEL_DISPLAY-']
        model_path = sg.popup_get_file('请输入模型文件路径')
        text.update(value=model_path)
    elif event == '-INPUT-':
        text = window['-INPUT_DISPLAY-']
        model_path = sg.popup_get_file('请输入音频文件路径')
        text.update(value=model_path)
    elif event == '-OUTPUT-':
        text = window['-OUTPUT_DISPLAY-']
        model_path = sg.popup_get_file('你想输出到那个文件夹？')
        text.update(value=model_path)
    elif event == '-RUN-':
        print('RUNNING')


window.close()
