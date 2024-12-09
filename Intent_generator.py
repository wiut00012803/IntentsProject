import csv
import os
import random
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import re
import json
import datetime

def introduce_typo(word, typo_probability):
    articles = ['a', 'an', 'the', 'и', 'в', 'во', 'не', 'на', 'но', 'что', 'он', 'как', 'так', 'из', 'за', 'от']
    if word.lower() in articles:
        return word
    if random.random() < typo_probability / 100 and len(word) > 0:
        index = random.randint(0, len(word) - 1)
        letter = word[index]
        if letter.isalpha():
            replacement = get_nearest_letter(letter)
            word = word[:index] + replacement + word[index + 1:]
    return word

def get_nearest_letter(letter):
    keyboard_layout = {
        'a': ['q', 'w', 's', 'z'], 'b': ['v', 'g', 'h', 'n'], 'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c', 'x'], 'e': ['w', 'r', 'd', 's'], 'f': ['d', 'r', 't', 'g', 'v', 'c'],
        'g': ['f', 't', 'y', 'h', 'b', 'v'], 'h': ['g', 'y', 'u', 'j', 'n', 'b'], 'i': ['u', 'o', 'k', 'j'],
        'j': ['h', 'u', 'i', 'k', 'm', 'n'], 'k': ['j', 'i', 'o', 'l', 'm'], 'l': ['k', 'o', 'p'],
        'm': ['n', 'j', 'k'], 'n': ['b', 'h', 'j', 'm'], 'o': ['i', 'p', 'k', 'l'],
        'p': ['o', 'l'], 'q': ['w', 'a'], 'r': ['e', 't', 'd', 'f'], 's': ['a', 'w', 'e', 'd', 'x', 'z'],
        't': ['r', 'y', 'g', 'f'], 'u': ['y', 'i', 'j', 'h'], 'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'a', 's', 'e'], 'x': ['z', 's', 'd', 'c'], 'y': ['t', 'u', 'h', 'g'], 'z': ['a', 's', 'x'],
        'й': ['ц', 'ф'], 'ц': ['й', 'у', 'к'], 'у': ['ц', 'к', 'е'], 'к': ['у', 'е', 'н'],
        'е': ['у', 'н', 'г'], 'н': ['к', 'е', 'г', 'ш'], 'г': ['е', 'н', 'ш', 'щ'],
        'ш': ['г', 'щ', 'з'], 'щ': ['ш', 'з', 'х'], 'з': ['щ', 'х', 'ъ'], 'х': ['з', 'ъ'],
        'ъ': ['х'], 'ф': ['й', 'ы'], 'ы': ['ф', 'в', 'а'], 'в': ['ы', 'а', 'п'],
        'а': ['в', 'п', 'с'], 'п': ['а', 'с', 'р'], 'р': ['п', 'о', 'л'], 'о': ['р', 'л', 'д'],
        'л': ['о', 'д', 'ж'], 'д': ['л', 'ж', 'э'], 'ж': ['д', 'э'], 'э': ['ж'],
        'я': ['ч', 'с'], 'ч': ['я', 'с', 'м'], 'с': ['ч', 'м', 'и'], 'м': ['ч', 'с', 'и'],
        'и': ['с', 'м', 'т'], 'т': ['и', 'ь'], 'ь': ['т', 'б'], 'б': ['ь', 'ю'], 'ю': ['б']
    }
    lower_letter = letter.lower()
    if lower_letter in keyboard_layout:
        replacement = random.choice(keyboard_layout[lower_letter])
        return replacement.upper() if letter.isupper() else replacement
    else:
        return letter

def randomize_phrase_order(phrase, linked_phrases):
    linked_phrases = [lp.strip() for lp in linked_phrases if lp.strip()]
    punctuation = re.findall(r"[^\w\s'`]", phrase, re.UNICODE)
    phrase_clean = re.sub(r"[^\w\s'`]", '', phrase)
    tokens = phrase_clean.split()
    i = 0
    words = []
    while i < len(tokens):
        matched = False
        for lp in linked_phrases:
            lp_words = lp.split()
            if tokens[i:i + len(lp_words)] == lp_words:
                words.append(' '.join(lp_words))
                i += len(lp_words)
                matched = True
                break
        if not matched:
            words.append(tokens[i])
            i += 1
    random.shuffle(words)
    result_phrase = ' '.join(words)
    if punctuation:
        result_phrase += ''.join(punctuation)
    return result_phrase

def generate_phrases(base_phrases, typo_probability, count, stop_event, progress_callback, linked_phrases):
    phrases = set()
    attempts = 0
    max_attempts = count * 10
    while len(phrases) < count and not stop_event.is_set() and attempts < max_attempts:
        attempts += 1
        phrase = random.choice(base_phrases)
        randomized_phrase = randomize_phrase_order(phrase, linked_phrases)
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ'`-]+|[^\w\s'`]", randomized_phrase, re.UNICODE)
        new_words = [
            introduce_typo(word, typo_probability) if re.match(r"[a-zA-Zа-яА-ЯёЁ'`-]+$", word, re.UNICODE) else word for
            word in words]
        new_phrase = ''.join([word if re.match(r"[^\w\s'`]", word) else ' ' + word for word in new_words]).strip()
        new_phrase = re.sub(r'\s+([^\w\s])', r'\1', new_phrase)
        if new_phrase not in phrases:
            phrases.add(new_phrase)
            progress_callback(len(phrases), count)
    return list(phrases)

def create_intents_csv(phrases, csv_path, intent_value):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerows([(phrase, intent_value) for phrase in phrases])
    messagebox.showinfo("Успех", f"CSV файл '{csv_path}' создан успешно.\nСгенерировано {len(phrases)} интентов.")

def generate_and_save():
    try:
        count = int(count_entry.get())
        typo_probability = float(typo_probability_entry.get())
        base_phrases = base_phrases_text.get("1.0", "end").strip().split('\n')
        intent_value = intent_entry.get().strip()
        linked_phrases = linked_phrases_text.get("1.0", "end").strip().split('\n')
        linked_phrases = [lp for lp in linked_phrases if lp]
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{intent_value}.csv",
                                                filetypes=[("CSV files", "*.csv")])
        if not csv_path or not os.path.isdir(os.path.dirname(csv_path)):
            messagebox.showerror("Ошибка", "Неверный путь к файлу.")
            return
        stop_event = threading.Event()

        def update_progress(current, total):
            progress_bar.set(current / total)

        def generate_and_save_intents():
            show_progress_bar(True)
            phrases = generate_phrases(base_phrases, typo_probability, count, stop_event, update_progress,
                                       linked_phrases)
            create_intents_csv(phrases, csv_path, intent_value)
            save_history_entry({
                'timestamp': datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
                'count': count,
                'typo_probability': typo_probability,
                'intent_value': intent_value,
                'base_phrases': base_phrases,
                'linked_phrases': linked_phrases
            })
            show_progress_bar(False)

        threading.Thread(target=generate_and_save_intents).start()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def save_history_entry(entry):
    history_file = 'history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    history.append(entry)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def load_history_entry(entry):
    count_entry.delete(0, 'end')
    count_entry.insert(0, str(entry.get('count', '')))
    typo_probability_entry.delete(0, 'end')
    typo_probability_entry.insert(0, str(entry.get('typo_probability', '')))
    intent_entry.delete(0, 'end')
    intent_entry.insert(0, entry.get('intent_value', ''))
    base_phrases_text.delete('1.0', 'end')
    base_phrases_text.insert('end', '\n'.join(entry.get('base_phrases', [])))
    linked_phrases_text.delete('1.0', 'end')
    linked_phrases_text.insert('end', '\n'.join(entry.get('linked_phrases', [])))

def open_history_window():
    history_file = 'history.json'
    if not os.path.exists(history_file):
        messagebox.showinfo("История пуста", "Нет сохраненных записей истории.")
        return
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    history_window = ctk.CTkToplevel(root)
    history_window.title("История")
    history_window.geometry("800x600")
    history_window.lift()
    history_window.grab_set()

    # Основной фрейм для размещения элементов
    history_main_frame = ctk.CTkFrame(history_window)
    history_main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Фрейм для списка истории
    history_list_frame = ctk.CTkFrame(history_main_frame)
    history_list_frame.pack(side='left', fill='y', padx=(0, 10), pady=10)

    # Список истории
    history_listbox = tk.Listbox(history_list_frame, width=40)
    history_listbox.pack(side='left', fill='y')
    scrollbar = tk.Scrollbar(history_list_frame, orient="vertical")
    scrollbar.config(command=history_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    history_listbox.config(yscrollcommand=scrollbar.set)

    # Фрейм для деталей выбранной записи
    history_detail_frame = ctk.CTkFrame(history_main_frame)
    history_detail_frame.pack(side='right', fill='both', expand=True, pady=10)

    # Текстовое поле для отображения деталей
    history_detail_text = ctk.CTkTextbox(history_detail_frame)
    history_detail_text.pack(fill='both', expand=True)

    # Заполнение списка истории
    for idx, entry in enumerate(history):
        timestamp = entry.get('timestamp', 'Unknown time')
        intent_value = entry.get('intent_value', '')
        display_text = f"{timestamp} - {intent_value}"
        history_listbox.insert('end', display_text)

    # Функция обновления деталей при выборе записи
    def on_history_select(event):
        selected_indices = history_listbox.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        entry = history[index]
        history_detail_text.delete("1.0", "end")
        history_detail_text.insert('end', f"Время: {entry.get('timestamp', '')}\n")
        history_detail_text.insert('end', f"Название интента: {entry.get('intent_value', '')}\n")
        history_detail_text.insert('end', f"Количество интентов: {entry.get('count', '')}\n")
        history_detail_text.insert('end', f"Вероятность опечатки: {entry.get('typo_probability', '')}%\n")
        history_detail_text.insert('end', "Базовые фразы:\n")
        for phrase in entry.get('base_phrases', []):
            history_detail_text.insert('end', f"- {phrase}\n")
        history_detail_text.insert('end', "Связанные слова:\n")
        for phrase in entry.get('linked_phrases', []):
            history_detail_text.insert('end', f"- {phrase}\n")

    history_listbox.bind('<<ListboxSelect>>', on_history_select)

    # Кнопки загрузки и удаления
    buttons_frame = ctk.CTkFrame(history_window)
    buttons_frame.pack(pady=10)

    def load_selected_entry():
        selected_indices = history_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Выберите запись", "Пожалуйста, выберите запись из истории.")
            return
        index = selected_indices[0]
        entry = history[index]
        load_history_entry(entry)
        history_window.destroy()

    def delete_selected_entry():
        selected_indices = history_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Выберите запись", "Пожалуйста, выберите запись для удаления.")
            return
        index = selected_indices[0]
        del history[index]
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        history_listbox.delete(index)
        history_detail_text.delete("1.0", "end")
        messagebox.showinfo("Удалено", "Запись успешно удалена.")

    load_button = ctk.CTkButton(buttons_frame, text="Загрузить выбранную запись", command=load_selected_entry)
    load_button.grid(row=0, column=0, padx=10)
    delete_button = ctk.CTkButton(buttons_frame, text="Удалить выбранную запись", command=delete_selected_entry)
    delete_button.grid(row=0, column=1, padx=10)

def load_and_extract_base_phrases():
    try:
        csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not csv_path or not os.path.isfile(csv_path):
            messagebox.showerror("Ошибка", "Неверный путь к файлу.")
            return

        phrases = []
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if row:
                    phrases.append(row[0])

        base_phrases = extract_base_phrases(phrases)

        base_phrases_text.delete("1.0", "end")
        for phrase in base_phrases:
            base_phrases_text.insert("end", phrase + "\n")

        messagebox.showinfo("Успех", "База фраз восстановлена из CSV файла.")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def extract_base_phrases(phrases):
    phrase_groups = {}
    for phrase in phrases:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ'`-]+", phrase, re.UNICODE)
        normalized = ' '.join(sorted([word.lower() for word in words]))
        if normalized not in phrase_groups:
            phrase_groups[normalized] = phrase
    return list(phrase_groups.values())

def show_progress_bar(visible):
    if visible:
        progress_bar.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
    else:
        progress_bar.grid_remove()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Генератор интентов")
root.geometry("800x600")

main_frame = ctk.CTkFrame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure([2, 3], weight=1)
main_frame.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(main_frame, text="Количество интентов:").grid(row=0, column=0, padx=10, pady=10,
                                                           sticky="w")
count_entry = ctk.CTkEntry(main_frame)
count_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(main_frame, text="Вероятность опечатки %:").grid(row=1, column=0, padx=10, pady=10,
                                                              sticky="w")
typo_probability_entry = ctk.CTkEntry(main_frame)
typo_probability_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
typo_probability_entry.insert(0, "0")

ctk.CTkLabel(main_frame, text="База (одна фраза на строку):").grid(row=2, column=0, padx=10,
                                                                   pady=10, sticky="nw")
base_phrases_text = ctk.CTkTextbox(main_frame)
base_phrases_text.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(main_frame, text="Связанные слова (одна фраза на строку):").grid(row=3, column=0,
                                                                              padx=10, pady=10,
                                                                              sticky="nw")
linked_phrases_text = ctk.CTkTextbox(main_frame)
linked_phrases_text.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(main_frame, text="Название интента:").grid(row=4, column=0, padx=10, pady=10,
                                                        sticky="w")
intent_entry = ctk.CTkEntry(main_frame)
intent_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

generate_button = ctk.CTkButton(main_frame, text="Сгенерировать и сохранить", command=generate_and_save, fg_color="green")
generate_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

load_button = ctk.CTkButton(main_frame, text="Загрузить CSV и восстановить базу", command=load_and_extract_base_phrases)
load_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

history_button = ctk.CTkButton(main_frame, text="Просмотр истории", command=open_history_window)
history_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

progress_bar = ctk.CTkProgressBar(main_frame)
progress_bar.set(0)

show_progress_bar(False)

root.mainloop()
