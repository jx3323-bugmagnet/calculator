"""Simple desktop calculator. Run with: python calculator.py"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class Calculator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Calculator")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.expression = ""
        self.just_evaluated = False

        self.display_var = tk.StringVar(value="0")

        self._build_ui()
        self._bind_keys()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure(
            "Display.TLabel",
            background="#111111",
            foreground="#f5f5f5",
            font=("Segoe UI", 22),
            padding=12,
            anchor="e",
        )
        style.configure(
            "Calc.TButton",
            font=("Segoe UI", 14),
            padding=10,
        )

        display = ttk.Label(frame, textvariable=self.display_var, style="Display.TLabel")
        display.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        buttons = [
            ("C", 1, 0, self.clear),
            ("⌫", 1, 1, self.backspace),
            ("%", 1, 2, lambda: self.input("%")),
            ("/", 1, 3, lambda: self.input("/")),
            ("7", 2, 0, lambda: self.input("7")),
            ("8", 2, 1, lambda: self.input("8")),
            ("9", 2, 2, lambda: self.input("9")),
            ("*", 2, 3, lambda: self.input("*")),
            ("4", 3, 0, lambda: self.input("4")),
            ("5", 3, 1, lambda: self.input("5")),
            ("6", 3, 2, lambda: self.input("6")),
            ("-", 3, 3, lambda: self.input("-")),
            ("1", 4, 0, lambda: self.input("1")),
            ("2", 4, 1, lambda: self.input("2")),
            ("3", 4, 2, lambda: self.input("3")),
            ("+", 4, 3, lambda: self.input("+")),
            ("0", 5, 0, lambda: self.input("0")),
            (".", 5, 1, lambda: self.input(".")),
            ("=", 5, 2, self.evaluate),
        ]

        for text, row, col, command in buttons:
            button = ttk.Button(frame, text=text, style="Calc.TButton", command=command)
            if text == "=":
                button.grid(row=row, column=col, columnspan=2, sticky="nsew", padx=3, pady=3)
            else:
                button.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)

        for i in range(6):
            frame.rowconfigure(i, weight=1)
        for i in range(4):
            frame.columnconfigure(i, weight=1, minsize=70)

    def _bind_keys(self) -> None:
        self.root.bind("<Return>", lambda _event: self.evaluate())
        self.root.bind("<KP_Enter>", lambda _event: self.evaluate())
        self.root.bind("<Escape>", lambda _event: self.clear())
        self.root.bind("<BackSpace>", lambda _event: self.backspace())
        for char in "0123456789.+-*/%":
            self.root.bind(char, lambda event, c=char: self.input(c))

    def input(self, value: str) -> None:
        operators = set("+-*/%")

        if self.just_evaluated:
            if value in operators:
                self.just_evaluated = False
            else:
                self.expression = ""
                self.just_evaluated = False

        if value == "." and self._current_number_has_decimal():
            return

        if value in operators:
            if not self.expression:
                if value == "-":
                    self.expression = "-"
                    self._refresh_display()
                return
            if self.expression[-1] in operators:
                self.expression = self.expression[:-1] + value
                self._refresh_display()
                return

        self.expression += value
        self._refresh_display()

    def _current_number_has_decimal(self) -> bool:
        last_number = ""
        for char in reversed(self.expression):
            if char in "+-*/%":
                break
            last_number = char + last_number
        return "." in last_number

    def clear(self) -> None:
        self.expression = ""
        self.just_evaluated = False
        self.display_var.set("0")

    def backspace(self) -> None:
        self.expression = self.expression[:-1]
        self.just_evaluated = False
        self._refresh_display()

    def evaluate(self) -> None:
        if not self.expression:
            return

        expr = self.expression
        if expr[-1] in "+-*/%":
            expr = expr[:-1]

        try:
            result = self._safe_eval(expr)
        except ZeroDivisionError:
            self.display_var.set("Cannot divide by 0")
            self.expression = ""
            self.just_evaluated = True
            return
        except Exception:
            self.display_var.set("Error")
            self.expression = ""
            self.just_evaluated = True
            return

        if result == int(result):
            result = int(result)

        self.expression = str(result)
        self.just_evaluated = True
        self.display_var.set(self.expression)

    def _safe_eval(self, expr: str) -> float:
        tokens: list[str] = []
        number = ""
        for char in expr:
            if char.isdigit() or char == ".":
                number += char
            elif char in "+-*/%":
                if number:
                    tokens.append(number)
                    number = ""
                tokens.append(char)
            else:
                raise ValueError("Invalid character")
        if number:
            tokens.append(number)

        if tokens and tokens[0] == "-":
            tokens[:2] = [f"-{tokens[1]}"] if len(tokens) > 1 else tokens

        values: list[float] = []
        ops: list[str] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in "+-*/%":
                ops.append(token)
            else:
                values.append(float(token))
            i += 1

        if not values or len(ops) != len(values) - 1:
            raise ValueError("Invalid expression")

        i = 0
        while i < len(ops):
            if ops[i] in "*/%":
                left = values[i]
                right = values[i + 1]
                if ops[i] == "*":
                    result = left * right
                elif ops[i] == "/":
                    if right == 0:
                        raise ZeroDivisionError
                    result = left / right
                else:
                    if right == 0:
                        raise ZeroDivisionError
                    result = left % right
                values[i : i + 2] = [result]
                ops.pop(i)
            else:
                i += 1

        result = values[0]
        for op, value in zip(ops, values[1:]):
            if op == "+":
                result += value
            else:
                result -= value
        return result

    def _refresh_display(self) -> None:
        self.display_var.set(self.expression or "0")


def main() -> None:
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
