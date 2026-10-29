"""
Crime Record Management System
College DSA project using Python, Tkinter, Singly Linked List, Queue, Searching,
Sorting, and CSV file storage.

All records included in the first run are fictional demo data.
Run: python main.py
"""

import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crime_records.csv")
FIELDS = ["case_id", "crime_type", "location", "date_reported", "suspect_name", "status", "description"]


class CrimeRecord:
    """One crime record."""
    def __init__(self, case_id, crime_type, location, date_reported,
                 suspect_name, status, description=""):
        self.case_id = case_id.strip().upper()
        self.crime_type = crime_type.strip()
        self.location = location.strip()
        self.date_reported = date_reported.strip()
        self.suspect_name = suspect_name.strip()
        self.status = status.strip()
        self.description = description.strip()

    def to_dict(self):
        return {field: getattr(self, field) for field in FIELDS}


class Node:
    """Node in a singly linked list."""
    def __init__(self, record):
        self.record = record
        self.next = None


class CrimeLinkedList:
    """Stores records in a singly linked list."""
    def __init__(self):
        self.head = None
        self.size = 0

    def add(self, record):
        if self.find(record.case_id):
            raise ValueError("A record with this Case ID already exists.")
        node = Node(record)
        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node
        self.size += 1

    def find(self, case_id):
        current = self.head
        target = case_id.strip().upper()
        while current:
            if current.record.case_id == target:
                return current.record
            current = current.next
        return None

    def delete(self, case_id):
        target = case_id.strip().upper()
        current = self.head
        previous = None
        while current:
            if current.record.case_id == target:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                self.size -= 1
                return current.record
            previous = current
            current = current.next
        return None

    def update(self, case_id, updated_record):
        current = self.head
        target = case_id.strip().upper()
        while current:
            if current.record.case_id == target:
                updated_record.case_id = target
                current.record = updated_record
                return True
            current = current.next
        return False

    def all_records(self):
        records = []
        current = self.head
        while current:
            records.append(current.record)
            current = current.next
        return records

    def clear(self):
        self.head = None
        self.size = 0


class CaseQueue:
    """FIFO queue of case IDs waiting for review."""
    def __init__(self):
        self.items = []

    def enqueue(self, case_id):
        if case_id not in self.items:
            self.items.append(case_id)

    def dequeue(self):
        if not self.items:
            return None
        return self.items.pop(0)

    def peek(self):
        return self.items[0] if self.items else None

    def contains(self, case_id):
        return case_id in self.items


class CrimeRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crime Record Management System | DSA Project")
        self.root.geometry("1240x760")
        self.root.minsize(1000, 650)
        self.records = CrimeLinkedList()
        self.review_queue = CaseQueue()
        self.selected_case_id = None

        self._configure_style()
        self._build_ui()
        self._load_csv()
        self._refresh_table()
        self._update_stats()

    def _configure_style(self):
        self.root.configure(bg="#eef2f7")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TButton", padding=6, font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 19, "bold"),
                        foreground="#ffffff", background="#17324d")
        style.configure("Subheader.TLabel", font=("Segoe UI", 9),
                        foreground="#dce7f2", background="#17324d")
        style.configure("Stat.TLabel", font=("Segoe UI", 10, "bold"),
                        foreground="#17324d", background="#ffffff")

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17324d", padx=20, pady=15)
        header.pack(fill="x")
        ttk.Label(header, text="CRIME RECORD MANAGEMENT SYSTEM",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Python + DSA | Singly Linked List | FIFO Case Queue | CSV Storage",
                  style="Subheader.TLabel").pack(anchor="w", pady=(4, 0))

        stats = tk.Frame(self.root, bg="#eef2f7", padx=14, pady=10)
        stats.pack(fill="x")
        self.total_var = tk.StringVar(value="Total cases: 0")
        self.pending_var = tk.StringVar(value="Under investigation: 0")
        self.solved_var = tk.StringVar(value="Solved: 0")
        self.queue_var = tk.StringVar(value="Review queue: 0")
        for var in (self.total_var, self.pending_var, self.solved_var, self.queue_var):
            card = tk.Label(stats, textvariable=var, bg="#ffffff", fg="#17324d",
                            padx=16, pady=12, font=("Segoe UI", 10, "bold"),
                            relief="groove", bd=1)
            card.pack(side="left", fill="x", expand=True, padx=4)

        body = tk.Frame(self.root, bg="#eef2f7", padx=14, pady=4)
        body.pack(fill="both", expand=True)

        form = tk.LabelFrame(body, text="Crime Record Details", bg="#ffffff",
                             fg="#17324d", padx=12, pady=10,
                             font=("Segoe UI", 10, "bold"))
        form.pack(side="left", fill="y", padx=(0, 12))
        form.configure(width=300)
        form.pack_propagate(False)

        self.vars = {key: tk.StringVar() for key in FIELDS}
        labels = [
            ("case_id", "Case ID *"),
            ("crime_type", "Crime Type *"),
            ("location", "Location *"),
            ("date_reported", "Date (YYYY-MM-DD) *"),
            ("suspect_name", "Suspect / Person of Interest"),
            ("status", "Case Status *"),
        ]
        for row, (key, label) in enumerate(labels):
            tk.Label(form, text=label, bg="#ffffff", fg="#26384a",
                     font=("Segoe UI", 9)).grid(row=row * 2, column=0, sticky="w", pady=(7, 2))
            if key == "status":
                widget = ttk.Combobox(form, textvariable=self.vars[key],
                                      values=["Under Investigation", "Solved", "Closed", "Pending"],
                                      state="readonly", width=27)
                widget.set("Under Investigation")
            else:
                widget = ttk.Entry(form, textvariable=self.vars[key], width=30)
            widget.grid(row=row * 2 + 1, column=0, sticky="ew")

        tk.Label(form, text="Description / Notes", bg="#ffffff", fg="#26384a",
                 font=("Segoe UI", 9)).grid(row=12, column=0, sticky="w", pady=(7, 2))
        self.description = tk.Text(form, height=4, width=28, wrap="word",
                                   font=("Segoe UI", 9))
        self.description.grid(row=13, column=0, sticky="ew")

        buttons = tk.Frame(form, bg="#ffffff")
        buttons.grid(row=14, column=0, sticky="ew", pady=(12, 4))
        ttk.Button(buttons, text="Add Record", command=self.add_record).grid(row=0, column=0, padx=2, pady=3, sticky="ew")
        ttk.Button(buttons, text="Update Selected", command=self.update_record).grid(row=0, column=1, padx=2, pady=3, sticky="ew")
        ttk.Button(buttons, text="Delete Selected", command=self.delete_record).grid(row=1, column=0, padx=2, pady=3, sticky="ew")
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).grid(row=1, column=1, padx=2, pady=3, sticky="ew")
        ttk.Button(buttons, text="Add to Review Queue", command=self.queue_selected).grid(row=2, column=0, columnspan=2, padx=2, pady=3, sticky="ew")
        ttk.Button(buttons, text="Process Next Case", command=self.process_queue).grid(row=3, column=0, columnspan=2, padx=2, pady=3, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        right = tk.Frame(body, bg="#ffffff", padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True)
        top = tk.Frame(right, bg="#ffffff")
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="Records", bg="#ffffff", fg="#17324d",
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=23).pack(side="left", padx=(14, 4))
        ttk.Button(top, text="Search Case ID", command=self.search_case).pack(side="left", padx=3)
        ttk.Button(top, text="Show All", command=self.show_all).pack(side="left", padx=3)

        controls = tk.Frame(right, bg="#ffffff")
        controls.pack(fill="x", pady=(0, 8))
        tk.Label(controls, text="Filter:", bg="#ffffff").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        filter_box = ttk.Combobox(controls, textvariable=self.filter_var,
                                  values=["All", "Under Investigation", "Solved", "Closed", "Pending"],
                                  state="readonly", width=22)
        filter_box.pack(side="left", padx=5)
        filter_box.bind("<<ComboboxSelected>>", lambda _e: self._refresh_table())
        tk.Label(controls, text="Sort by:", bg="#ffffff").pack(side="left", padx=(12, 0))
        self.sort_var = tk.StringVar(value="Case ID")
        sort_box = ttk.Combobox(controls, textvariable=self.sort_var,
                                values=["Case ID", "Date", "Crime Type"],
                                state="readonly", width=12)
        sort_box.pack(side="left", padx=5)
        ttk.Button(controls, text="Sort", command=self._refresh_table).pack(side="left", padx=3)

        table_frame = tk.Frame(right, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)
        columns = ("case_id", "crime_type", "location", "date_reported", "suspect_name", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "case_id": ("Case ID", 85), "crime_type": ("Crime Type", 115),
            "location": ("Location", 125), "date_reported": ("Date", 100),
            "suspect_name": ("Suspect / POI", 135), "status": ("Status", 155)
        }
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=70, anchor="w")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(right, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        footer = tk.Label(self.root,
                          text="Educational demo only • Use fictional data • Restrict access to sensitive real-world records",
                          bg="#17324d", fg="#ffffff", pady=7, font=("Segoe UI", 9))
        footer.pack(fill="x")

    def _load_csv(self):
        if not os.path.exists(DATA_FILE):
            # Seed the first launch with fictional examples.
            examples = [
                CrimeRecord("CR101", "Theft", "Demo Market", "2026-10-20", "Demo Person A",
                            "Under Investigation", "Fictional sample record"),
                CrimeRecord("CR102", "Cybercrime", "Online", "2026-10-21", "Demo Person B",
                            "Pending", "Fictional sample record"),
                CrimeRecord("CR103", "Vandalism", "Demo Park", "2026-10-22", "Unknown",
                            "Solved", "Fictional sample record"),
            ]
            for record in examples:
                self.records.add(record)
            self._save_csv()
            return

        try:
            with open(DATA_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if all(field in row for field in FIELDS):
                        try:
                            self.records.add(CrimeRecord(**{field: row.get(field, "") or "" for field in FIELDS}))
                        except ValueError:
                            # Skip duplicate IDs in a malformed CSV.
                            continue
        except (OSError, csv.Error) as exc:
            messagebox.showerror("CSV Error", f"Could not load records:\n{exc}")

    def _save_csv(self):
        try:
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                for record in self.records.all_records():
                    writer.writerow(record.to_dict())
        except OSError as exc:
            messagebox.showerror("Save Error", f"Could not save records:\n{exc}")

    def _get_form_record(self):
        values = {key: var.get().strip() for key, var in self.vars.items()}
        values["description"] = self.description.get("1.0", "end").strip()
        required = ["case_id", "crime_type", "location", "date_reported", "status"]
        missing = [field for field in required if not values[field]]
        if missing:
            raise ValueError("Please fill all required fields marked with *.")
        try:
            date.fromisoformat(values["date_reported"])
        except ValueError:
            raise ValueError("Date must be valid and use YYYY-MM-DD format.")
        return CrimeRecord(**values)

    def add_record(self):
        try:
            record = self._get_form_record()
            self.records.add(record)
            self._save_csv()
            self._refresh_table()
            self._update_stats()
            self.clear_form()
            messagebox.showinfo("Success", "Crime record added and saved.")
        except ValueError as exc:
            messagebox.showwarning("Check Details", str(exc))

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Select a record in the table first.")
            return
        old_id = selected[0]
        try:
            record = self._get_form_record()
            # Keep the selected ID fixed so an update cannot accidentally create a duplicate.
            record.case_id = old_id
            self.records.update(old_id, record)
            self._save_csv()
            self._refresh_table()
            self._update_stats()
            self.clear_form()
            messagebox.showinfo("Updated", f"Record {old_id} updated.")
        except ValueError as exc:
            messagebox.showwarning("Check Details", str(exc))

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Select a record in the table first.")
            return
        case_id = selected[0]
        if not messagebox.askyesno("Confirm Delete", f"Delete case {case_id}?"):
            return
        deleted = self.records.delete(case_id)
        if deleted:
            self.review_queue.items = [item for item in self.review_queue.items if item != case_id]
            self._save_csv()
            self._refresh_table()
            self._update_stats()
            self.clear_form()
            messagebox.showinfo("Deleted", f"Record {case_id} deleted.")

    def search_case(self):
        case_id = self.search_var.get().strip().upper()
        if not case_id:
            messagebox.showwarning("Search", "Enter a Case ID to search.")
            return
        record = self.records.find(case_id)
        self._refresh_table(records=[record] if record else [])
        if record:
            self._populate_form(record)
        else:
            messagebox.showinfo("Not Found", f"No record found for {case_id}.")

    def show_all(self):
        self.search_var.set("")
        self.filter_var.set("All")
        self._refresh_table()

    def _refresh_table(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if records is None:
            records = self.records.all_records()
            selected_filter = self.filter_var.get()
            if selected_filter != "All":
                records = [r for r in records if r.status == selected_filter]
            sort_key = self.sort_var.get()
            if sort_key == "Date":
                records.sort(key=lambda r: r.date_reported)
            elif sort_key == "Crime Type":
                records.sort(key=lambda r: r.crime_type.lower())
            else:
                records.sort(key=lambda r: r.case_id)
        for record in records:
            self.tree.insert("", "end", iid=record.case_id, values=(
                record.case_id, record.crime_type, record.location,
                record.date_reported, record.suspect_name, record.status
            ))

    def _on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        record = self.records.find(selected[0])
        if record:
            self._populate_form(record)

    def _populate_form(self, record):
        self.selected_case_id = record.case_id
        for key in FIELDS:
            if key != "description":
                self.vars[key].set(getattr(record, key))
        self.description.delete("1.0", "end")
        self.description.insert("1.0", record.description)

    def clear_form(self):
        self.selected_case_id = None
        for key, var in self.vars.items():
            var.set("Under Investigation" if key == "status" else "")
        self.description.delete("1.0", "end")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def queue_selected(self):
        selected = self.tree.selection()
        case_id = selected[0] if selected else self.search_var.get().strip().upper()
        if not case_id or not self.records.find(case_id):
            messagebox.showwarning("Review Queue", "Select an existing case first.")
            return
        if self.review_queue.contains(case_id):
            messagebox.showinfo("Review Queue", f"{case_id} is already in the queue.")
            return
        self.review_queue.enqueue(case_id)
        self._update_stats()
        messagebox.showinfo("Review Queue", f"{case_id} added to the end of the review queue.")

    def process_queue(self):
        case_id = self.review_queue.dequeue()
        if case_id is None:
            messagebox.showinfo("Review Queue", "The review queue is empty.")
            return
        self._update_stats()
        messagebox.showinfo("Next Case", f"Next case for review: {case_id}\n\nFIFO: first in, first out.")

    def _update_stats(self):
        records = self.records.all_records()
        self.total_var.set(f"Total cases: {len(records)}")
        self.pending_var.set(f"Under investigation: {sum(r.status == 'Under Investigation' for r in records)}")
        self.solved_var.set(f"Solved: {sum(r.status == 'Solved' for r in records)}")
        self.queue_var.set(f"Review queue: {len(self.review_queue.items)}")


def main():
    root = tk.Tk()
    CrimeRecordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
