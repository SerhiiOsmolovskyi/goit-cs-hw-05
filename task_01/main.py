import argparse
import asyncio
import logging
import shutil
from pathlib import Path
from collections import defaultdict

# Налаштовуємо логування
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("file_sorter_errors.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Словник для зберігання статистики
file_stats = defaultdict(int)


async def copy_file(file_path: Path, output_folder: Path):
    """
    Копіює файл у підпапку, що відповідає його розширенню.
    """
    try:
        extension = file_path.suffix.lower().lstrip(".") or "no_extension"
        target_dir = output_folder / extension
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy2, file_path, target_path)

        # Оновлюємо статистику
        file_stats[extension] += 1

    except Exception as e:
        logging.error(f"Помилка при копіюванні файлу {file_path}: {e}")


async def read_folder(source_folder: Path, output_folder: Path):
    """
    Рекурсивно читає всі файли та копіює їх у відповідні папки.
    """
    tasks = []
    try:
        for file_path in source_folder.rglob("*"):
            if file_path.is_file():
                tasks.append(copy_file(file_path, output_folder))
    except Exception as e:
        logging.error(f"Помилка при читанні папки {source_folder}: {e}")

    await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source", help="Шлях до вихідної папки")
    parser.add_argument("output", help="Шлях до папки призначення")
    args = parser.parse_args()

    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(f"Вихідна папка {source_folder} не існує або не є директорією.")
        return

    asyncio.run(read_folder(source_folder, output_folder))

    # Підсумки сортування
    total_files = sum(file_stats.values())
    print(f"\n✅ Сортування завершено! Всього файлів: {total_files}")
    for ext, count in sorted(file_stats.items()):
        print(f"  {ext}: {count} шт.")


if __name__ == "__main__":
    main()
