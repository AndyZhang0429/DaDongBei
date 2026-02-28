import tkinter as tk
import pyaudio, wave
import threading
import os

music_player = pyaudio.PyAudio()
music_stream = None
music_file = None

save_settings = False
route_settings = os.path.join(os.environ['APPDATA'], "Dadongbei/settings.txt") if os.name == "nt" else "~/.config/Dadongbei/settings.txt" if os.name == "posix" else "~/Library/Application Support/Dadongbei/settings.txt" if os.name == "mac" else "settings.txt"

mixpercentage = 0.0
mixlist = ["!", "?", "是", "我", "的", "家", "乡"]
music_on = True

def encode(original : str):
    original = original.encode('utf-8')
    code = ""
    codelist = [" ", "北", "大北", "东北", "大大北", "大东北", "东大北", "东东北",
            "大大大北", "大大东北", "大东大北", "大东东北", "东大大北", "东大东北", "东东大北", "东东东北"]

    for b in original:
        code += codelist[(b&0xf0)>>4]
        code += codelist[b&0x0f]
    return code

def mixcode(code : str, percentage = 7.0, mixcharacters = ["!", "?", "是", "我", "的", "家", "乡"]):
    import random
    for i in range(int(len(code)*percentage)):
        j = random.randint(0, len(code))
        code = code[0:j] + random.choice(mixcharacters) + (code[j:] if j<len(code) else "")
    return code

def decode(code : str):
    buffer = ""
    double = False
    singlebytebuf = 0
    out = b""
    codelist = [" ", "北", "大北", "东北", "大大北", "大东北", "东大北", "东东北",
            "大大大北", "大大东北", "大东大北", "大东东北", "东大大北", "东大东北", "东东大北", "东东东北"]


    for c in code:
        if c not in [" ", "大", "东", "北"]:
            continue
        buffer += c
        if c == " " or c == "北":
            if double:
                singlebytebuf += codelist.index(buffer)
                out += bytes([singlebytebuf])
            else:
                singlebytebuf = codelist.index(buffer)<<4
            buffer = ""
            double = not double
    return out.decode('utf-8')

def get_setting_text():
    return f"({mixpercentage}, {mixlist}, {music_on})"

def load_settings():
    global mixpercentage, mixlist, music_on, save_settings
    try:
        with open(route_settings, "r") as f:
            mixpercentage, mixlist, music_on = eval(f.read())
            save_settings = True
    except FileNotFoundError:
        save_settings = False
    except SyntaxError:
        save_settings = False

load_settings()

main = tk.Tk()
main.title("大东北编码器")
main.minsize(200, 100)  # 设置窗口最小尺寸为600x400像素

menu_bar = tk.Menu(main, tearoff=0)
main.config(menu=menu_bar)

settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="设置", menu=settings_menu)

def show_mixpercentagepopup_settings_menu(*args):
    popupwindow_mixpercentagepopup_settings_menu = tk.Toplevel(main)
    popupwindow_mixpercentagepopup_settings_menu.geometry("500x400")
    popupwindow_mixpercentagepopup_settings_menu.title("编码百分比")

    slidebar_mixpercentagepopup_settings_menu = tk.Scale(popupwindow_mixpercentagepopup_settings_menu, from_=0.0, to=10.0, resolution=0.01, orient=tk.HORIZONTAL, label="编码混淆倍数")
    slidebar_mixpercentagepopup_settings_menu.pack(fill=tk.X, side=tk.TOP, expand=False)
    slidebar_mixpercentagepopup_settings_menu.set(mixpercentage)
    def update_mixpercentage(*args):
        global mixpercentage
        mixpercentage = slidebar_mixpercentagepopup_settings_menu.get()
    slidebar_mixpercentagepopup_settings_menu.bind("<ButtonRelease-1>", update_mixpercentage)

    items_mixpercentagepopup_settings_menu = tk.Listbox(popupwindow_mixpercentagepopup_settings_menu)
    items_mixpercentagepopup_settings_menu.pack(fill=tk.X, side=tk.TOP, expand=False)
    for item in mixlist:
        items_mixpercentagepopup_settings_menu.insert(tk.END, item)
    additementry_mixpercentagepopup_settings_menu = tk.Entry(popupwindow_mixpercentagepopup_settings_menu)
    additementry_mixpercentagepopup_settings_menu.pack(fill=tk.X, side=tk.TOP, expand=False)
    additembutton_mixpercentagepopup_settings_menu = tk.Button(popupwindow_mixpercentagepopup_settings_menu, text="添加", command=lambda: (mixlist.append(additementry_mixpercentagepopup_settings_menu.get()), items_mixpercentagepopup_settings_menu.insert(tk.END, mixlist[-1])))
    additembutton_mixpercentagepopup_settings_menu.pack(fill=tk.X, side=tk.TOP, expand=False)
    deleteitembutton_mixpercentagepopup_settings_menu = tk.Button(popupwindow_mixpercentagepopup_settings_menu, text="删除", command=lambda: (mixlist.pop(items_mixpercentagepopup_settings_menu.curselection()[0]), items_mixpercentagepopup_settings_menu.delete(items_mixpercentagepopup_settings_menu.curselection())))
    deleteitembutton_mixpercentagepopup_settings_menu.pack(fill=tk.X, side=tk.TOP, expand=False)

settings_menu.add_command(label="混淆", command=show_mixpercentagepopup_settings_menu)

# 播放音乐函数
def play_music():
    # 创建并启动音乐播放线程
    music_thread = threading.Thread(target=_play_music)
    music_thread.daemon = True  # 设置为守护线程，主程序退出时自动退出
    music_thread.start()

# 实际的音乐播放函数，在后台线程中运行
def _play_music():
    global music_stream, music_file, music_on
    music_on = True
    try:
        # 打开WAV文件
        music_file = wave.open("dadongbei.wav", "rb")
        
        # 创建音频流
        music_stream = music_player.open(
            format=music_player.get_format_from_width(music_file.getsampwidth()),
            channels=music_file.getnchannels(),
            rate=music_file.getframerate(),
            output=True
        )
        while music_on:
            data = music_file.readframes(1024)
            while data and music_on:
                music_stream.write(data)
                data = music_file.readframes(1024)
            music_file.rewind()
            
    except Exception as e:
        print(f"播放音乐时出错: {e}")
    finally:
        if music_stream:
            music_stream.stop_stream()
            music_stream.close()
        if music_file:
            music_file.close()

# 停止音乐函数
def stop_music():
    global music_on
    music_on = False

# 音乐设置弹窗函数
def show_musicpopup_settings_menu(*args):
    popupwindow_musicpopup_settings_menu = tk.Toplevel(main)
    popupwindow_musicpopup_settings_menu.geometry("200x100")
    popupwindow_musicpopup_settings_menu.resizable(False, False)
    popupwindow_musicpopup_settings_menu.title("音乐")
    
    # 音乐状态显示
    status_var = tk.StringVar(value="正在播放《大东北我的家乡》" if music_on else "音乐已关闭")
    status_label = tk.Label(popupwindow_musicpopup_settings_menu, textvariable=status_var)
    status_label.pack(fill=tk.X, side=tk.TOP, pady=10, padx=5)
    
    # 单个状态切换按钮
    def toggle_music():
        global music_on
        music_on = not music_on
        status_var.set("正在播放《大东北我的家乡》" if music_on else "音乐已关闭")
        
        if music_on:
            play_music()
        else:
            # 关闭音乐
            stop_music()
    
    toggle_button = tk.Button(popupwindow_musicpopup_settings_menu, text="切换状态", command=toggle_music)
    toggle_button.pack(fill=tk.X, side=tk.TOP, pady=10, padx=5)

settings_menu.add_command(label="音乐", command=show_musicpopup_settings_menu)

def show_otherpopup_settings_menu(*args):
    global save_settings
    popupwindow_otherpopup_settings_menu = tk.Toplevel(main)
    popupwindow_otherpopup_settings_menu.geometry("200x100")
    popupwindow_otherpopup_settings_menu.resizable(False, False)
    popupwindow_otherpopup_settings_menu.title("其他")
    checkvar = tk.BooleanVar(value=save_settings)
    checkifsave_otherpopup_settings_menu = tk.Checkbutton(popupwindow_otherpopup_settings_menu, text="保存设置", variable=checkvar)
    checkifsave_otherpopup_settings_menu.pack(fill=tk.X, side=tk.TOP, pady=10, padx=5)
    def update_settings():
        global save_settings
        save_settings = checkvar.get()
        if save_settings:
            os.makedirs(os.path.dirname(route_settings), exist_ok=True)
            with open(route_settings, "w") as f:
                f.write(get_setting_text())
        else:
            try:
                os.remove(route_settings)
            except FileNotFoundError:
                pass
    checkifsave_otherpopup_settings_menu.config(command=update_settings)

settings_menu.add_command(label="其他", command=show_otherpopup_settings_menu)


frame_main = tk.Frame(main)
frame_main.pack(fill=tk.BOTH, expand=True)
frame_main.columnconfigure(0, weight=1, minsize=50)
frame_main.columnconfigure(1, weight=1, minsize=50)
frame_main.rowconfigure(0, weight=1, minsize=50)

frame_encode = tk.Frame(frame_main)
frame_encode.grid(row=0, column=0, sticky="nsew")
frame_decode = tk.Frame(frame_main)
frame_decode.grid(row=0, column=1, sticky="nsew")

encode_button = tk.Button(frame_encode, text="编码", command=lambda: (decode_input.delete("1.0", "end"), decode_input.insert("1.0", mixcode(encode(encode_input.get("1.0", "end-1c")), mixpercentage, mixlist))), height=1)
encode_button.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=False)
decode_button = tk.Button(frame_decode, text="解码", command=lambda: (encode_input.delete("1.0", "end"), encode_input.insert("1.0", decode(decode_input.get("1.0", "end-1c")))), height=1)
decode_button.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=False)

encode_input = tk.Text(frame_encode)
encode_input.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
decode_input = tk.Text(frame_decode)
decode_input.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

if music_on:
    play_music()

main.mainloop()

if save_settings:
    os.makedirs(os.path.dirname(route_settings), exist_ok=True)
    with open(route_settings, "w") as f:
        f.write(get_setting_text())
else:
    try:
        os.remove(route_settings)
    except FileNotFoundError:
        pass