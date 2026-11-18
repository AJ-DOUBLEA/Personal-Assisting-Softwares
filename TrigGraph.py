import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TrigGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Trigonometry Graph — Degrees")
        self.root.geometry("1100x760")
        self.root.minsize(850, 620)

        self.function = tk.StringVar(value="sin")
        self.amplitude = tk.IntVar(value=1)
        self.coefficient = tk.IntVar(value=1)
        self.intercept = tk.IntVar(value=0)

        controls = ttk.Frame(root, padding=12)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(controls, text="Function:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        function_menu = ttk.Combobox(
            controls,
            textvariable=self.function,
            values=("sin", "cos"),
            state="readonly",
            width=8,
        )
        function_menu.grid(row=0, column=1, sticky="w", padx=5)
        function_menu.bind("<<ComboboxSelected>>", self.update_graph)

        self.add_slider(controls, "Amplitude (a)", self.amplitude, 0, 10, 1)
        self.add_slider(controls, "Coefficient of x (b)", self.coefficient, 1, 10, 2)
        self.add_slider(
            controls, "Y-intercept / vertical shift (c)",
            self.intercept, -10, 10, 3
        )

        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.figure.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.12)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=12, pady=(0, 12)
        )

        self.update_graph()

    def add_slider(self, parent, label, variable, minimum, maximum, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=4)
        parent.columnconfigure(3, weight=1)

        ttk.Label(frame, text=label, width=34).pack(side=tk.LEFT, padx=(0, 8))
        slider = tk.Scale(
            frame,
            from_=minimum,
            to=maximum,
            orient=tk.HORIZONTAL,
            variable=variable,
            resolution=1,
            length=450,
            command=self.update_graph,
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        value_label = ttk.Label(frame, width=4, text=str(variable.get()))
        value_label.pack(side=tk.LEFT, padx=8)

        def refresh_label(*_):
            value_label.config(text=str(variable.get()))

        variable.trace_add("write", refresh_label)

    def update_graph(self, *_):
        # The x-axis is in degrees, so convert to radians only for NumPy's
        # trigonometric calculations.
        x = np.linspace(0, 360, 2401)
        a = self.amplitude.get()
        b = self.coefficient.get()
        c = self.intercept.get()
        function_name = self.function.get()

        angle_radians = np.deg2rad(b * x)
        if function_name == "sin":
            y = a * np.sin(angle_radians) + c
        else:
            y = a * np.cos(angle_radians) + c

        self.ax.clear()
        self.ax.plot(x, y, label=f"y = {a}{function_name}({b}x) + ({c})")
        self.ax.axhline(c, linestyle="--", linewidth=1, label=f"Midline y = {c}")
        self.ax.axhline(0, linewidth=0.8)
        self.ax.axvline(0, linewidth=0.8)

        # Find turning points analytically, then annotate their coordinates.
        # For sin: maxima when bx = 90 + 360k; minima when bx = 270 + 360k.
        # For cos: maxima when bx = 360k; minima when bx = 180 + 360k.
        if a > 0:
            if function_name == "sin":
                max_base, min_base = 90, 270
            else:
                max_base, min_base = 0, 180

            extrema = []
            for kind, base, y_value in (
                ("max", max_base, c + a),
                ("min", min_base, c - a),
            ):
                # Include every matching turning point in the 0°–360° window.
                k_min = int(np.ceil((0 * b - base) / 360))
                k_max = int(np.floor((360 * b - base) / 360))
                for k in range(k_min, k_max + 1):
                    x_value = (base + 360 * k) / b
                    if -1e-9 <= x_value <= 360 + 1e-9:
                        extrema.append((x_value, y_value, kind))

            # Draw markers and labels. Alternate label placement to reduce overlap.
            for index, (x_value, y_value, kind) in enumerate(extrema):
                self.ax.scatter([x_value], [y_value], s=30, zorder=4)
                vertical_offset = 12 if index % 2 == 0 else -18
                label = f"({self.format_number(x_value)}, {self.format_number(y_value)})"
                self.ax.annotate(
                    label,
                    (x_value, y_value),
                    textcoords="offset points",
                    xytext=(0, vertical_offset),
                    ha="center",
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8),
                )

        self.ax.set_xlim(0, 360)
        self.ax.set_xticks(np.arange(0, 361, 45))
        self.ax.set_xlabel("x (degrees)")
        self.ax.set_ylabel("y")
        self.ax.set_title("Sine / Cosine Graph with Maximum and Minimum Points")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")

        # Keep all points visible, including when the vertical shift is large.
        padding = max(1, a * 0.25)
        self.ax.set_ylim(c - a - padding, c + a + padding)
        self.canvas.draw_idle()

    @staticmethod
    def format_number(value):
        if abs(value - round(value)) < 1e-7:
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrigGraphApp(root)
    root.mainloop()
