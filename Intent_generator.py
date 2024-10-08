import csv
import os
import random
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import re


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
        'w': ['q', 'a', 's', 'e'], 'x': ['z', 's', 'd', 'c'], 'y': ['t', 'u', 'h', 'g'],
        'z': ['a', 's', 'x'],
        'й': ['ц', 'ф'], 'ц': ['й', 'у', 'ы'], 'у': ['ц', 'к', 'в'], 'к': ['у', 'е', 'а'],
        'е': ['к', 'н', 'п'], 'н': ['е', 'г', 'р'], 'г': ['н', 'ш', 'о'], 'ш': ['г', 'щ', 'л'],
        'щ': ['ш', 'з', 'д'], 'з': ['щ', 'х', 'ж'], 'х': ['з', 'ъ', 'ж'], 'ъ': ['х', 'э'],
        'ф': ['й', 'ы'], 'ы': ['ф', 'в', 'ц'], 'в': ['ы', 'а', 'с'], 'а': ['в', 'п', 'с'],
        'п': ['а', 'с', 'р'], 'р': ['п', 'с', 'о'], 'о': ['р', 'л', 'д'], 'л': ['о', 'д', 'ж'],
        'д': ['л', 'ж', 'э'], 'ж': ['л', 'д', 'э'], 'э': ['д', 'ж'], 'я': ['ч', 'с'],
        'ч': ['я', 'с', 'м'], 'с': ['я', 'ч', 'м', 'и'], 'м': ['ч', 'с', 'и'], 'и': ['с', 'м', 'т'],
        'т': ['и', 'ь'], 'ь': ['т', 'б'], 'б': ['ь', 'ю'], 'ю': ['б']
    }
    lower_letter = letter.lower()
    if lower_letter in keyboard_layout:
        replacement = random.choice(keyboard_layout[lower_letter])
        return replacement.upper() if letter.isupper() else replacement
    else:
        return letter


def randomize_phrase_order(phrase, linked_phrases):
    linked_phrases = [lp.strip() for lp in linked_phrases if lp.strip()]
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ'-]+|[^\w\s]", phrase, re.UNICODE)
    words = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if re.match(r"[a-zA-Zа-яА-ЯёЁ'-]+", token, re.UNICODE):
            matched = False
            for lp in linked_phrases:
                lp_words = lp.split()
                if tokens[i:i + len(lp_words)] == lp_words:
                    words.append(' '.join(lp_words))
                    i += len(lp_words)
                    matched = True
                    break
            if not matched:
                words.append(token)
                i += 1
        else:
            words.append(token)
            i += 1
    words_only = [word for word in words if re.match(r"[a-zA-Zа-яА-ЯёЁ'-]+", word, re.UNICODE)]
    words_to_shuffle = [word for word in words_only if ' ' not in word]
    if len(words_to_shuffle) > 1:
        random.shuffle(words_to_shuffle)
    shuffled_words = iter(words_to_shuffle)
    result = []
    for word in words:
        if re.match(r"[a-zA-Zа-яА-ЯёЁ'-]+", word, re.UNICODE):
            if ' ' in word or word not in words_to_shuffle:
                result.append(word)
            else:
                result.append(next(shuffled_words))
        else:
            result.append(word)
    return ' '.join(result)


def generate_phrases(base_phrases, typo_probability, count, stop_event, progress_callback, linked_phrases):
    phrases = set()
    attempts = 0
    max_attempts = count * 10
    while len(phrases) < count and not stop_event.is_set() and attempts < max_attempts:
        attempts += 1
        phrase = random.choice(base_phrases)
        randomized_phrase = randomize_phrase_order(phrase, linked_phrases)
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ'-]+|[^\w\s]", randomized_phrase, re.UNICODE)
        new_words = [
            introduce_typo(word, typo_probability) if re.match(r"[a-zA-Zа-яА-ЯёЁ'-]+", word, re.UNICODE) else word for
            word in words]
        new_phrase = ''.join([word if re.match(r"[^\w\s]", word) else ' ' + word for word in new_words]).strip()
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
            show_progress_bar(False)

        threading.Thread(target=generate_and_save_intents).start()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def show_progress_bar(visible):
    if visible:
        progress_bar.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
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

progress_bar = ctk.CTkProgressBar(main_frame)
progress_bar.set(0)

generate_button = ctk.CTkButton(main_frame, text="Сгенерировать и сохранить", command=generate_and_save)
generate_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

show_progress_bar(False)

root.mainloop()
