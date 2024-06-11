import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime
from datetime import timedelta
import sys
import os
import threading
import json
import time

def resourcePath(filename):
  if hasattr(sys, "_MEIPASS"):
      return os.path.join(sys._MEIPASS, filename)
  return os.path.join(filename)

# カレンダーの作成
def create_calendar(year, month):
    # 既存のウィジェットをすべて削除
    for widget in calendar_frame.winfo_children():
        if not isinstance(widget, tk.Button):
            widget.destroy()

    # 月の表示
    month_label = tk.Label(calendar_frame, text=f"{year}-{month:02d}", font=("Helvetica", 12), bg=bg_color, fg=fg_color)
    month_label.grid(row=0, column=0, columnspan=7, sticky='nsew')

    # 曜日の表示
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, weekday in enumerate(weekdays):
        if 0 < i < 6:
            weekday_label = tk.Label(calendar_frame, text=weekday, bg=bg_color, fg=fg_color)
        else:
            weekday_label = tk.Label(calendar_frame, text=weekday, bg=bg_color, fg="red")
        weekday_label.grid(row=1, column=i)

    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    next_month_day = 1
    prev_month_day = calendar.monthrange(year, month-1 if month != 1 else 12)[1] - cal[0].count(0) + 1

    # 今日の日付を取得
    today = datetime.today().date()

    for i in range(6):  # 6週分の日付を表示
        if i >= len(cal):  # 追加した範囲チェック
            break
        for j in range(7):
            if cal[i][j] != 0:  # 当月の日付
                date = f"{year}-{month:02d}-{cal[i][j]:02d}"
                # その日が土曜日、日曜日、または今日であるかチェック
                if j == 0 or j == 6 or date == str(today):
                    date_label = tk.Label(calendar_frame, text=str(cal[i][j]), font=("Helvetica", 10), bg=bg_color, fg="red")
                else:
                    date_label = tk.Label(calendar_frame, text=str(cal[i][j]), font=("Helvetica", 10), bg=bg_color, fg=fg_color)

            else:  # 前月または次月の日付
                if i == 0:  # 前月の日付
                    if month == 1:
                        prev_month_year = year - 1
                        prev_month_month = 12
                    else:
                        prev_month_year = year
                        prev_month_month = month - 1
                    date = f"{prev_month_year}-{prev_month_month:02d}-{prev_month_day:02d}"
                    date_label = tk.Label(calendar_frame, text=str(prev_month_day), font=("Helvetica", 10), bg=bg_color, fg=next_month_color)
                    prev_month_day += 1
                else:  # 次月の日付
                    if month == 12:
                        next_month_year = year + 1
                        next_month_month = 1
                    else:
                        next_month_year = year
                        next_month_month = month + 1
                    date = f"{next_month_year}-{next_month_month:02d}-{next_month_day:02d}"
                    date_label = tk.Label(calendar_frame, text=str(next_month_day), font=("Helvetica", 10), bg=bg_color, fg=next_month_color)
                    next_month_day += 1
            date_label.grid(row=i*2+2, column=j, sticky='nsew')
            if date in memo_dict:
                text = memo_dict[date]
            else:
                text = ""
            memo_text = tk.Text(calendar_frame, height=4, width=10, font=("Helvetica", 8), bg=bg_color, fg=fg_color, insertbackground=fg_color, undo=True)
            memo_text.insert('1.0', text)
            memo_text.grid(row=i*2+3, column=j, sticky='nsew')
            memo_text.bind("<FocusIn>", lambda event, date=date: on_focus(event, date))
            memo_text.bind('<FocusOut>', lambda event: save_memo())

    # ウィンドウサイズに応じて表示サイズを切り替える
    calendar_frame.grid_rowconfigure(0, weight=0)
    for i in [3,5,7,9,11,13]:

        calendar_frame.grid_rowconfigure(i, weight=3)  # カレンダーの行
    for i in range(7):
        calendar_frame.grid_columnconfigure(i, weight=1)  # 各列

def on_focus(event, date=None):
    global last_focused
    last_focused = [event.widget, date]

# 前の月へ移動
def prev_month():
    global year, month, last_focused
    save_memo()

    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1

    create_calendar(year, month)

# 次の月へ移動
def next_month():
    global year, month
    save_memo()

    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    create_calendar(year, month)

# メモ作成関数
def create_memo():
    global free_memo_text

    # 既存のウィジェットを全て削除
    for widget in memo_frame.winfo_children():
        widget.destroy()

    # 自由メモ欄の追加
    free_memo_text = tk.Text(memo_frame, height=10, font=("Helvetica", 10), bg=bg_color, fg=fg_color, insertbackground=fg_color, undo=True)
    free_memo_text.grid(row=0, column=0, sticky='nsew')

    if "free_memo" in memo_dict:
        text = memo_dict["free_memo"]
    else:
        text = ""
    free_memo_text.insert('1.0', text)
    free_memo_text.bind("<FocusIn>", lambda event: on_focus(event))
    free_memo_text.bind('<FocusOut>', lambda event: save_memo())
    memo_frame.grid_columnconfigure(0, weight=1)
    memo_frame.grid_rowconfigure(0, weight=10)  # 月の表示の行

def toggle_free_memo():
    global calendar_frame, memo_frame, free_memo_text # グローバル変数として参照

    width = root.winfo_width()
    height = root.winfo_height()
    root.geometry(f"{width}x{height}")

    # ウィジェットが存在する場合、非表示にする
    if free_memo_text.winfo_exists():
        save_memo()

        for widget in root.winfo_children():
            widget.destroy()

        # ボタンフレームの作成
        button_frame = tk.Frame(root, bg=bg_color)
        button_frame.pack(fill='x', side='bottom')  # ボタンフレームをウィンドウの下部に配置

        prev_button = tk.Button(button_frame, text='<<', command=prev_month, bg=button_color, fg=fg_color)
        prev_button.pack(side='left')

        next_button = tk.Button(button_frame, text='>>', command=next_month, bg=button_color, fg=fg_color)
        next_button.pack(side='right')

        free_memo_label = tk.Button(button_frame, text="Toggle Memo", command=toggle_free_memo, bg=button_color, fg=fg_color)
        free_memo_label.pack(fill='x')

        pane = tk.PanedWindow(root, orient='vertical', bg=bg_color)
        pane.pack(fill='both', expand=True)

        # カレンダーフレームの作成
        calendar_frame = tk.Frame(pane, bg=bg_color)
        calendar_frame.pack(fill='both', expand=False)
        pane.add(calendar_frame)

        create_calendar(year, month)

    else:
        for widget in root.winfo_children():
            widget.destroy()

        # ボタンフレームの作成
        button_frame = tk.Frame(root, bg=bg_color)
        button_frame.pack(fill='x', side='bottom')  # ボタンフレームをウィンドウの下部に配置

        prev_button = tk.Button(button_frame, text='<<', command=prev_month, bg=button_color, fg=fg_color)
        prev_button.pack(side='left')

        next_button = tk.Button(button_frame, text='>>', command=next_month, bg=button_color, fg=fg_color)
        next_button.pack(side='right')

        free_memo_label = tk.Button(button_frame, text="Toggle Memo", command=toggle_free_memo, bg=button_color, fg=fg_color)
        free_memo_label.pack(fill='x')

        pane = tk.PanedWindow(root, orient='vertical', bg=bg_color)
        pane.pack(fill='both', expand=True)

        # カレンダーフレームの作成
        calendar_frame = tk.Frame(pane, bg=bg_color)
        pane.add(calendar_frame)

        # メモフレームの作成
        memo_frame = tk.Frame(pane, bg=bg_color)
        pane.add(memo_frame)

        create_calendar(year, month)
        create_memo()

# メモの保存
def save_memo():
    global last_focused
    widget, date = last_focused

    if widget is None and date is None:
        pass

    elif date is None:
        widget, date = last_focused
        memo = widget.get("1.0", tk.END).strip()
        memo_dict["free_memo"] = memo
        last_focused = [None,None]

    else:
        widget, date = last_focused
        memo = widget.get("1.0", tk.END).strip()
        memo_dict[date] = memo
        last_focused = [None,None]

    # ファイルにデータを保存
    with open(f"{work_path}/data.json", "w") as f:
        json.dump(memo_dict, f)

def save_and_close():
    save_memo()
    root.destroy()

def date_checker():
    today = datetime.today().date()
    while True:
        if today < datetime.today().date():
            today = datetime.today().date()
            create_calendar(year, month)

        time.sleep(60)

# ダークモードの色設定
bg_color = '#2d2d2d'
fg_color = '#ffffff'
today_color = '#ff0000'
button_color = '#4d4d4d'
next_month_color = '#808080'

# ウィンドウの作成
root = tk.Tk()
root.title('Calendar with Memo')
root.iconbitmap(default=resourcePath("icon.ico"))
root.geometry("400x600")

# ウィンドウの背景色を設定
root.configure(bg=bg_color)

# ボタンフレームの作成
button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(fill='x', side='bottom')  # ボタンフレームをウィンドウの下部に配置

prev_button = tk.Button(button_frame, text='<<', command=prev_month, bg=button_color, fg=fg_color)
prev_button.pack(side='left')

next_button = tk.Button(button_frame, text='>>', command=next_month, bg=button_color, fg=fg_color)
next_button.pack(side='right')

free_memo_label = tk.Button(button_frame, text="Toggle Memo", command=toggle_free_memo, bg=button_color, fg=fg_color)
free_memo_label.pack(fill='x')

pane = tk.PanedWindow(root, orient='vertical', bg=bg_color)
pane.pack(fill='both', expand=True)

# カレンダーフレームの作成
calendar_frame = tk.Frame(pane, bg=bg_color)
calendar_frame.pack(fill='both', expand=True)
pane.add(calendar_frame)

# メモフレームの作成
memo_frame = tk.Frame(pane, bg=bg_color)
pane.add(memo_frame)

work_path = os.path.dirname(sys.executable)

# メモの保存用辞書
try:
    with open(f"{work_path}/data.json", "r") as f:
        memo_dict = json.load(f)

    # 現在日時から一年前の日時を取得
    one_year_ago = datetime.today().date() - timedelta(days=365)
    for key in list(memo_dict.keys()):
        if key != "free_memo":
            if datetime.strptime(key, '%Y-%m-%d').date() < one_year_ago:
                # キーが一年前より前のものなら削除
                del memo_dict[key]
except Exception as e:
    memo_dict = {}

last_focused = [None,None]

root.protocol("WM_DELETE_WINDOW", save_and_close)

# 現在の年と月
year = datetime.today().year
month = datetime.today().month

# 初期表示
create_calendar(year, month)
create_memo()

thread = threading.Thread(target=date_checker, daemon=True)
thread.start()

root.mainloop()
