import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Помилка завантаження: {e}")
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word.lower(), 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    if search_words:
        search_words_set = set(word.lower() for word in search_words)
        words = [word for word in words if word.lower() in search_words_set]

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(counter_dict, top_n=10):
    top_items = sorted(counter_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*top_items) if top_items else ([], [])

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.title(f"Топ-{top_n} слів за частотою в тексті")
    plt.xlabel("Слова")
    plt.ylabel("Кількість")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"

    text = get_text(url)
    if text:
        search_words = ['love', 'marriage', 'family', 'pride', 'prejudice', 'darcy', 'elizabeth', 'bennet', 'sister', 'sisters']
        result = map_reduce(text, search_words)

        print("Підрахунок слів:", result)
        visualize_top_words(result, top_n=10)
    else:
        print("Помилка: не вдалося завантажити текст.")