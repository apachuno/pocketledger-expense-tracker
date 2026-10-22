# PocketLedger — Expense Tracker GUI

A beginner-friendly desktop expense tracker built with **Python, Tkinter, and SQLite**. It needs no third-party Python packages.

## Features

- Add expenses with date, description, category, amount, and optional notes
- Store entries in a local SQLite database (`expenses.db`)
- See total spending for the current filter, current-month spending, and transaction count
- Filter the table by category
- Double-click an entry to view its details and notes
- Delete an entry with a confirmation prompt
- Validate dates and amounts before saving

## Requirements

- Python 3.10 or newer recommended
- Tkinter (usually included with Python; some Linux distributions package it separately)

## Run it

Open Terminal in this folder and run:

```bash
python3 expense_tracker.py
```

A desktop window should open. Add an expense using the form on the left. Your data is saved automatically in `expenses.db` beside the Python file and is still there when you reopen the app.

## Try a sample entry

- Date: today's date in `YYYY-MM-DD` format
- Description: `Lunch`
- Category: `Food`
- Amount: `180`
- Notes: `Lunch near campus`

## GitHub project description

> A desktop expense tracker built with Python Tkinter and SQLite. Supports adding, filtering, viewing, and deleting expenses, with spending summaries and input validation.

## Next improvements to build

- Export transactions to CSV
- Monthly spending chart
- Edit existing expenses
- Set category budgets

## Privacy

The app stores data locally in the SQLite database. It does not upload expenses to a server.

## New features

- **Export CSV:** Click `Export CSV` to save all expenses, or only the currently selected category, to a `.csv` file. The file can be opened in Excel or Google Sheets.
- **Monthly spending chart:** Click `Monthly chart` to view totals for the last 12 calendar months. The chart is drawn with Tkinter's Canvas, so no charting package is needed.

Both features use Python's standard library; no additional packages are required.
