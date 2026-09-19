from datetime import datetime


def input_int(
    prompt: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Некорректный ввод. Введите целое число.")
            continue

        if minimum is not None and value < minimum:
            print(f"Значение должно быть не меньше {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Значение должно быть не больше {maximum}.")
            continue
        return value


def input_date(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Некорректная дата. Используйте формат ГГГГ-ММ-ДД.")
