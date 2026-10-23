import ast
import operator
import tkinter as tk

BG = "#14171c"
DISPLAY_BG = "#14171c"
KEY_BG = "#1e232b"
KEY_HOVER = "#2a313c"
OP_BG = "#2b3a55"
OP_HOVER = "#37496b"
EQ_BG = "#4a7bd0"
EQ_HOVER = "#5a8be0"
TEXT = "#e6e9ef"
MUTED = "#7d8794"

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def evaluate(expression):
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            return BIN_OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](walk(node.operand))
        raise ValueError("Invalid expression")

    cleaned = (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("%", "/100")
    )
    return walk(ast.parse(cleaned, mode="eval"))


class Calculator(tk.Tk):
    LAYOUT = [
        ["C", "⌫", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "+"],
        ["±", "0", ".", "="],
    ]
    OPERATORS = {"÷", "×", "−", "+"}

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.expr = ""
        self.just_evaluated = False

        self.history = tk.Label(
            self, text="", anchor="e", bg=DISPLAY_BG, fg=MUTED, font=("Segoe UI", 12)
        )
        self.history.grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=(16, 0))

        self.display = tk.Label(
            self, text="0", anchor="e", bg=DISPLAY_BG, fg=TEXT, font=("Segoe UI Semibold", 36)
        )
        self.display.grid(row=1, column=0, columnspan=4, sticky="ew", padx=16, pady=(0, 12))

        for r, row in enumerate(self.LAYOUT, start=2):
            for c, label in enumerate(row):
                self.make_button(label, r, c)

        for i in range(4):
            self.columnconfigure(i, weight=1, uniform="col")

        self.bind_keys()

    def make_button(self, label, row, col):
        if label == "=":
            bg, hover = EQ_BG, EQ_HOVER
        elif label in self.OPERATORS or label in {"C", "⌫", "%"}:
            bg, hover = OP_BG, OP_HOVER
        else:
            bg, hover = KEY_BG, KEY_HOVER

        btn = tk.Button(
            self,
            text=label,
            command=lambda: self.press(label),
            bg=bg,
            fg=TEXT,
            activebackground=hover,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 16),
            width=5,
            height=2,
            cursor="hand2",
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def bind_keys(self):
        for ch in "0123456789.%":
            self.bind(ch, lambda e, k=ch: self.press(k))
        self.bind("+", lambda e: self.press("+"))
        self.bind("-", lambda e: self.press("−"))
        self.bind("*", lambda e: self.press("×"))
        self.bind("/", lambda e: self.press("÷"))
        self.bind("<Return>", lambda e: self.press("="))
        self.bind("<KP_Enter>", lambda e: self.press("="))
        self.bind("<BackSpace>", lambda e: self.press("⌫"))
        self.bind("<Escape>", lambda e: self.press("C"))

    def press(self, key):
        if key == "C":
            self.expr = ""
            self.history.config(text="")
        elif key == "⌫":
            self.expr = self.expr[:-1]
        elif key == "±":
            self.expr = self.expr[1:] if self.expr.startswith("−") else "−" + self.expr
        elif key == "=":
            self.calculate()
            return
        else:
            if self.just_evaluated and key not in self.OPERATORS:
                self.expr = ""
            if key in self.OPERATORS and self.expr and self.expr[-1] in self.OPERATORS:
                self.expr = self.expr[:-1]
            self.expr += key
        self.just_evaluated = False
        self.refresh()

    def calculate(self):
        if not self.expr:
            return
        try:
            result = evaluate(self.expr)
            text = format(result, ".10g")
            self.history.config(text=self.expr + " =")
            self.expr = text.replace("-", "−")
        except ZeroDivisionError:
            self.history.config(text=self.expr + " =")
            self.expr = ""
            self.display.config(text="Can't divide by zero")
            self.just_evaluated = False
            return
        except Exception:
            self.display.config(text="Error")
            self.expr = ""
            return
        self.just_evaluated = True
        self.refresh()

    def refresh(self):
        shown = self.expr or "0"
        size = 36 if len(shown) <= 10 else 24 if len(shown) <= 16 else 16
        self.display.config(text=shown, font=("Segoe UI Semibold", size))


if __name__ == "__main__":
    Calculator().mainloop()
