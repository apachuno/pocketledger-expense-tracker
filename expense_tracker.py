"""Simple desktop expense tracker built with Python's Tkinter and SQLite.

Run with: python3 expense_tracker.py
No third-party packages are required.
"""

import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"
CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills", "Education",
    "Entertainment", "Health", "Travel", "Other"
]

BG = "#f4f6fb"
CARD = "#ffffff"
INK = "#182230"
MUTED = "#667085"
ACCENT = "#3457d5"
GREEN = "#16835b"
RED = "#c0392b"
BORDER = "#e2e7f0"


class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PocketLedger — Expense Tracker")
        self.geometry("1060x700")
        self.minsize(900, 620)
        self.configure(bg=BG)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self._style()
        self._build_ui()
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spent_on TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                notes TEXT DEFAULT ''
            )
        """)
        self.conn.commit()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=INK, rowheight=32, borderwidth=0, font=("Arial", 10))
        style.configure("Treeview.Heading", background="#edf1fa", foreground=INK,
                        font=("Arial", 10, "bold"), relief="flat", padding=(8, 9))
        style.map("Treeview", background=[("selected", "#dce5ff")], foreground=[("selected", INK)])
        style.configure("TCombobox", padding=7)
        style.configure("TEntry", padding=8)
        style.configure("TButton", font=("Arial", 10), padding=(10, 8))
        style.configure("Primary.TButton", background=ACCENT, foreground="white", borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#2947b3")])
        style.configure("Danger.TButton", background="#fff0ef", foreground=RED, borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#ffe0dd")])

    def _build_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(22, 14))
        title_block = tk.Frame(header, bg=BG)
        title_block.pack(side="left", fill="x", expand=True)
        tk.Label(title_block, text="PocketLedger", bg=BG, fg=INK,
                 font=("Arial", 24, "bold")).pack(anchor="w")
        tk.Label(title_block, text="A simple, local-first way to track your spending.",
                 bg=BG, fg=MUTED, font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        tk.Label(header, text="●  SAVED ON THIS DEVICE", bg=BG, fg=GREEN,
                 font=("Arial", 9, "bold")).pack(side="right", anchor="n", pady=8)

        summary = tk.Frame(self, bg=BG)
        summary.pack(fill="x", padx=28, pady=(0, 16))
        self.total_var = tk.StringVar(value="₹0.00")
        self.month_var = tk.StringVar(value="₹0.00")
        self.count_var = tk.StringVar(value="0")
        self._summary_card(summary, "TOTAL SPENDING (FILTERED)", self.total_var, ACCENT).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._summary_card(summary, "SPENDING THIS MONTH", self.month_var, GREEN).pack(side="left", fill="x", expand=True, padx=5)
        self._summary_card(summary, "TRANSACTIONS (FILTERED)", self.count_var, "#8a4bd4").pack(side="left", fill="x", expand=True, padx=(10, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 22))
        left = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.configure(width=300)
        left.pack_propagate(False)
        tk.Label(left, text="Add an expense", bg=CARD, fg=INK,
                 font=("Arial", 15, "bold")).pack(anchor="w", padx=20, pady=(20, 3))
        tk.Label(left, text="Fields marked * are required.", bg=CARD, fg=MUTED,
                 font=("Arial", 9)).pack(anchor="w", padx=20, pady=(0, 15))

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.amount_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self._field(left, "Date * (YYYY-MM-DD)", self.date_var)
        self._field(left, "What did you spend on? *", self.title_var)
        tk.Label(left, text="Category *", bg=CARD, fg=INK, font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        category = ttk.Combobox(left, textvariable=self.category_var, values=CATEGORIES, state="readonly")
        category.pack(fill="x", padx=20)
        self._field(left, "Amount in ₹ *", self.amount_var)
        self._field(left, "Notes (optional)", self.notes_var)
        ttk.Button(left, text="＋  Add expense", style="Primary.TButton", command=self.add_expense).pack(fill="x", padx=20, pady=(18, 8))
        ttk.Button(left, text="Clear form", command=self.clear_form).pack(fill="x", padx=20)
        tk.Label(left, text="Tip: Your entries are stored in\nexpenses.db beside this app.",
                 bg=CARD, fg=MUTED, justify="left", font=("Arial", 9)).pack(anchor="w", padx=20, pady=(22, 15))

        right = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        top = tk.Frame(right, bg=CARD)
        top.pack(fill="x", padx=18, pady=(18, 12))
        tk.Label(top, text="Your expenses", bg=CARD, fg=INK, font=("Arial", 15, "bold")).pack(side="left")
        filter_row = tk.Frame(top, bg=CARD)
        filter_row.pack(side="right")
        tk.Label(filter_row, text="Category", bg=CARD, fg=MUTED, font=("Arial", 9)).pack(side="left", padx=(0, 6))
        self.filter_var = tk.StringVar(value="All")
        filter_box = ttk.Combobox(filter_row, textvariable=self.filter_var, values=["All"] + CATEGORIES,
                                  state="readonly", width=14)
        filter_box.pack(side="left")
        filter_box.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        ttk.Button(filter_row, text="Monthly chart", command=self.show_monthly_chart).pack(side="left", padx=(10, 5))
        ttk.Button(filter_row, text="Export CSV", command=self.export_csv).pack(side="left")

        table_frame = tk.Frame(right, bg=CARD)
        table_frame.pack(fill="both", expand=True, padx=18)
        columns = ("date", "title", "category", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("date", text="DATE")
        self.tree.heading("title", text="DESCRIPTION")
        self.tree.heading("category", text="CATEGORY")
        self.tree.heading("amount", text="AMOUNT")
        self.tree.column("date", width=105, minwidth=95, anchor="w")
        self.tree.column("title", width=190, minwidth=120, anchor="w")
        self.tree.column("category", width=125, minwidth=100, anchor="w")
        self.tree.column("amount", width=110, minwidth=95, anchor="e")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.show_details)

        bottom = tk.Frame(right, bg=CARD)
        bottom.pack(fill="x", padx=18, pady=14)
        self.status_var = tk.StringVar(value="Double-click an entry to view its notes.")
        tk.Label(bottom, textvariable=self.status_var, bg=CARD, fg=MUTED,
                 font=("Arial", 9)).pack(side="left", fill="x", expand=True)
        ttk.Button(bottom, text="Delete selected", style="Danger.TButton", command=self.delete_selected).pack(side="right")

    def _summary_card(self, parent, label, variable, accent):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1, padx=18, pady=14)
        tk.Label(card, text=label, bg=CARD, fg=MUTED, font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Label(card, textvariable=variable, bg=CARD, fg=accent, font=("Arial", 21, "bold")).pack(anchor="w", pady=(7, 0))
        return card

    def _field(self, parent, label, variable):
        tk.Label(parent, text=label, bg=CARD, fg=INK, font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.pack(fill="x", padx=20)
        return entry

    def add_expense(self):
        spent_on = self.date_var.get().strip()
        title = self.title_var.get().strip()
        category = self.category_var.get().strip()
        amount_text = self.amount_var.get().strip().replace(",", "")
        notes = self.notes_var.get().strip()
        try:
            date.fromisoformat(spent_on)
        except ValueError:
            messagebox.showerror("Check the date", "Enter a valid date in YYYY-MM-DD format, for example 2026-10-22.")
            return
        if not title:
            messagebox.showerror("Missing description", "Enter what the expense was for.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Check the amount", "Enter an amount greater than ₹0, such as 249 or 99.50.")
            return
        self.conn.execute("INSERT INTO expenses (spent_on, title, category, amount, notes) VALUES (?, ?, ?, ?, ?)",
                          (spent_on, title, category, amount, notes))
        self.conn.commit()
        self.clear_form(keep_date=True)
        self.refresh()
        self.status_var.set(f"Added: {title} — ₹{amount:,.2f}")

    def clear_form(self, keep_date=False):
        self.title_var.set("")
        self.amount_var.set("")
        self.notes_var.set("")
        self.category_var.set(CATEGORIES[0])
        if not keep_date:
            self.date_var.set(date.today().isoformat())

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        category = self.filter_var.get() if hasattr(self, "filter_var") else "All"
        if category and category != "All":
            rows = self.conn.execute("SELECT * FROM expenses WHERE category=? ORDER BY spent_on DESC, id DESC", (category,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM expenses ORDER BY spent_on DESC, id DESC").fetchall()
        for row in rows:
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["spent_on"], row["title"], row["category"], f"₹{row['amount']:,.2f}"))
        filtered_total = sum(float(row["amount"]) for row in rows)
        month_prefix = date.today().strftime("%Y-%m")
        month_total = self.conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(spent_on, 1, 7)=?", (month_prefix,)).fetchone()[0]
        self.total_var.set(f"₹{filtered_total:,.2f}")
        self.month_var.set(f"₹{month_total:,.2f}")
        self.count_var.set(str(len(rows)))
        self.status_var.set(f"Showing {len(rows)} expense{'s' if len(rows) != 1 else ''}. Double-click a row for notes.")

    def export_csv(self):
        """Export expenses to a CSV file that opens in Excel or Google Sheets."""
        category = self.filter_var.get()
        if category and category != "All":
            rows = self.conn.execute(
                "SELECT spent_on, title, category, amount, notes FROM expenses "
                "WHERE category=? ORDER BY spent_on DESC, id DESC", (category,)
            ).fetchall()
            default_name = f"pocketledger_{category.lower()}_expenses.csv"
        else:
            rows = self.conn.execute(
                "SELECT spent_on, title, category, amount, notes FROM expenses "
                "ORDER BY spent_on DESC, id DESC"
            ).fetchall()
            default_name = "pocketledger_expenses.csv"

        if not rows:
            messagebox.showinfo("Nothing to export", "There are no expenses to export for this selection.")
            return

        destination = filedialog.asksaveasfilename(
            title="Export expenses as CSV", defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not destination:
            return
        try:
            with open(destination, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "Description", "Category", "Amount (INR)", "Notes"])
                for row in rows:
                    writer.writerow([row["spent_on"], row["title"], row["category"],
                                     f"{float(row['amount']):.2f}", row["notes"] or ""])
        except OSError as exc:
            messagebox.showerror("Export failed", f"Could not save the CSV file.\n\n{exc}")
            return
        messagebox.showinfo("Export complete", f"Exported {len(rows)} expense(s) to:\n{destination}")

    def show_monthly_chart(self):
        """Show a simple bar chart of the last 12 months using Tkinter Canvas."""
        from datetime import datetime
        today = date.today()
        month_keys = []
        year, month = today.year, today.month
        for _ in range(12):
            month_keys.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month, year = 12, year - 1
        month_keys.reverse()
        totals_by_month = {
            row["month"]: float(row["total"])
            for row in self.conn.execute(
                "SELECT substr(spent_on, 1, 7) AS month, SUM(amount) AS total "
                "FROM expenses GROUP BY substr(spent_on, 1, 7)"
            ).fetchall()
        }
        values = [totals_by_month.get(key, 0.0) for key in month_keys]
        labels = [datetime.strptime(key, "%Y-%m").strftime("%b %y") for key in month_keys]

        window = tk.Toplevel(self)
        window.title("PocketLedger — Monthly spending")
        window.geometry("850x440")
        window.minsize(650, 360)
        window.configure(bg=BG)
        tk.Label(window, text="Monthly spending — last 12 months", bg=BG, fg=INK,
                 font=("Arial", 17, "bold")).pack(anchor="w", padx=22, pady=(18, 2))
        tk.Label(window, text="Bars show total expenses recorded in each calendar month.",
                 bg=BG, fg=MUTED, font=("Arial", 10)).pack(anchor="w", padx=22, pady=(0, 10))
        chart = tk.Canvas(window, bg=CARD, highlightthickness=1,
                          highlightbackground=BORDER, height=300)
        chart.pack(fill="both", expand=True, padx=22, pady=(0, 20))

        def draw_chart(_event=None):
            chart.delete("all")
            width, height = chart.winfo_width(), chart.winfo_height()
            if width < 100 or height < 100:
                return
            left, right, top, bottom = 66, 18, 24, 58
            plot_w, plot_h = width - left - right, height - top - bottom
            max_value = max(values) if values else 0
            scale_max = max_value * 1.15 if max_value > 0 else 1.0
            for i in range(5):
                fraction = i / 4
                y = top + plot_h - fraction * plot_h
                chart.create_line(left, y, width - right, y, fill="#e8ecf4")
                chart.create_text(left - 9, y, text=f"₹{scale_max * fraction:,.0f}",
                                  anchor="e", fill=MUTED, font=("Arial", 8))
            slot = plot_w / 12
            bar_w = max(5, slot * 0.58)
            for i, (label, value) in enumerate(zip(labels, values)):
                center = left + (i + 0.5) * slot
                bar_h = value / scale_max * plot_h if value > 0 else 0
                y0 = top + plot_h - bar_h
                if value > 0:
                    chart.create_rectangle(center - bar_w / 2, y0, center + bar_w / 2,
                                           top + plot_h, fill=ACCENT, outline="")
                    if slot >= 48:
                        chart.create_text(center, max(top + 8, y0 - 9), text=f"₹{value:,.0f}",
                                          fill=INK, font=("Arial", 8))
                chart.create_text(center, top + plot_h + 20, text=label,
                                  fill=MUTED, font=("Arial", 8), angle=45)
            chart.create_text(width - right, 8, text=f"12-month total: ₹{sum(values):,.2f}",
                              anchor="ne", fill=INK, font=("Arial", 9, "bold"))
        chart.bind("<Configure>", draw_chart)
        window.after(100, draw_chart)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select an expense", "Choose an expense from the list first.")
            return
        row = self.conn.execute("SELECT title, amount FROM expenses WHERE id=?", (int(selected[0]),)).fetchone()
        if row and messagebox.askyesno("Delete expense", f"Delete ‘{row['title']}’ (₹{row['amount']:,.2f})? This cannot be undone."):
            self.conn.execute("DELETE FROM expenses WHERE id=?", (int(selected[0]),))
            self.conn.commit()
            self.refresh()

    def show_details(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        row = self.conn.execute("SELECT * FROM expenses WHERE id=?", (int(selected[0]),)).fetchone()
        if row:
            details = f"Date: {row['spent_on']}\nDescription: {row['title']}\nCategory: {row['category']}\nAmount: ₹{row['amount']:,.2f}\n\nNotes: {row['notes'] or 'No notes added.'}"
            messagebox.showinfo("Expense details", details)

    def _on_close(self):
        self.conn.close()
        self.destroy()


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
