import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime

assets = [
    {"Item ID": 1, "Item Name": "HP Elitebook 840 G8", "Item Type": "Laptop", "In-use": False, "Serial Number": 1,
     "Price": 750.00, "Location": "IT", "Date added": "01-01-2024"},
    {"Item ID": 2, "Item Name": "Zebra MC3300", "Item Type": "Scanner", "In-use": True, "Serial Number": 2,
     "Price": 500.00, "Location": "Pick", "Date added": "14-02-2020"},
    # Add more items as needed
]

def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

def refresh_list():
    asset_list.delete(0, tk.END)
    for item in assets:
        asset_list.insert(tk.END, f"{item['Item ID']}: {item['Item Name']} ({item['Item Type']})")

def add_item():
    new_item = {}
    new_item["Item ID"] = max(item["Item ID"] for item in assets) + 1 if assets else 1

    new_item["Item Name"] = simpledialog.askstring("Input", "Enter Item Name:")
    if not new_item["Item Name"]:
        messagebox.showerror("Error", "Item Name cannot be empty.")
        return

    new_item["Item Type"] = simpledialog.askstring("Input", "Enter Item Type:")
    if not new_item["Item Type"]:
        messagebox.showerror("Error", "Item Type cannot be empty.")
        return

    while True:
        date_added = simpledialog.askstring("Input", "Enter Date Added (DD-MM-YYYY):")
        if validate_date(date_added):
            new_item["Date added"] = date_added
            break
        else:
            messagebox.showerror("Error", "Invalid date format.")

    new_item["Serial Number"] = simpledialog.askinteger("Input", "Enter Serial Number:")
    new_item["Price"] = simpledialog.askfloat("Input", "Enter Price:")
    new_item["Location"] = simpledialog.askstring("Input", "Enter Location:")
    in_use = simpledialog.askstring("Input", "Is it in-use? (True/False):")
    new_item["In-use"] = in_use.lower() == "true"

    assets.append(new_item)
    messagebox.showinfo("Success", "Item added successfully!")
    refresh_list()

def view_item():
    selected = asset_list.curselection()
    if not selected:
        messagebox.showerror("Error", "No item selected.")
        return
    item = assets[selected[0]]
    details = "\n".join(f"{key}: {value}" for key, value in item.items())
    messagebox.showinfo("Item Details", details)

def delete_item():
    selected = asset_list.curselection()
    if not selected:
        messagebox.showerror("Error", "No item selected.")
        return
    assets.pop(selected[0])
    messagebox.showinfo("Success", "Item deleted successfully!")
    refresh_list()

def edit_item():
    selected = asset_list.curselection()
    if not selected:
        messagebox.showerror("Error", "No item selected.")
        return

    item = assets[selected[0]]

    for key in item:
        if key not in ["Item ID"]:  # Skip immutable fields
            new_value = simpledialog.askstring("Input", f"Enter new value for {key} (current: {item[key]}):")
            if new_value:
                if key == "Date added" and not validate_date(new_value):
                    messagebox.showerror("Error", "Invalid date format.")
                    continue
                elif key == "Price":
                    new_value = float(new_value)
                elif key == "Serial Number":
                    new_value = int(new_value)
                elif key == "In-use":
                    new_value = new_value.lower() == "true"

                item[key] = new_value

    messagebox.showinfo("Success", "Item updated successfully!")
    refresh_list()

# GUI Setup
root = tk.Tk()
root.title("Asset Management")

frame = tk.Frame(root)
frame.pack(pady=10)

asset_list = tk.Listbox(frame, width=50, height=15)
asset_list.pack(side=tk.LEFT, padx=10)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=asset_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
asset_list.config(yscrollcommand=scrollbar.set)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Item", command=add_item)
add_button.grid(row=0, column=0, padx=5)

view_button = tk.Button(button_frame, text="View Item", command=view_item)
view_button.grid(row=0, column=1, padx=5)

edit_button = tk.Button(button_frame, text="Edit Item", command=edit_item)
edit_button.grid(row=0, column=2, padx=5)

delete_button = tk.Button(button_frame, text="Delete Item", command=delete_item)
delete_button.grid(row=0, column=3, padx=5)

refresh_list()
root.mainloop()