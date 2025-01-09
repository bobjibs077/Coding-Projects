from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter import filedialog as fd
import qrcode
import cv2

# Creating Main Window
window = Tk()
window.title('QR Code Generator and Detector')
window.iconbitmap('icon.ico')
window.geometry('500x480+440+180')
window.resizable(height=TRUE, width=TRUE)

# Creating Notebook
tab_control = ttk.Notebook(window)
first_tab = ttk.Frame(tab_control)
second_tab = ttk.Frame(tab_control)
tab_control.add(first_tab, text='Generator')
tab_control.add(second_tab, text='Detector')
tab_control.pack(expand=1, fill='both')

# Creating a Canvas
first_canvas = Canvas(first_tab, width=500, height=480)
first_canvas.pack()
second_canvas = Canvas(second_tab, width=500, height=480)
second_canvas.pack()

# Widgets - tab 1
image_label1 = Label(window)
first_canvas.create_window(250, 150, window=image_label1)

# TTK Label - QR code Data
qrdata_label = ttk.Label(window, text='QRcode Data')
data_entry = ttk.Entry(window, width=55)
first_canvas.create_window(70, 330, window=qrdata_label)
first_canvas.create_window(300, 330, window=data_entry)

# TTK Label - Filename
Filename_label = ttk.Label(window, text='Filename')
Filename_entry = ttk.Entry(window, width=55)
first_canvas.create_window(84, 360, window=Filename_label)
first_canvas.create_window(300, 360, window=Filename_entry)

# Buttons
reset_button = ttk.Button(window, text='Reset', state=DISABLED)
generate_button = ttk.Button(window, text='Generate QRcode', command=lambda: generate_qrcode())
first_canvas.create_window(300, 390, window=reset_button)
first_canvas.create_window(410, 390, window=generate_button)

# Widgets - tab 2
image_label2 = Label(window)
data_label = ttk.Label(window)
second_canvas.create_window(250, 150, window=image_label2)
second_canvas.create_window(250, 300, window=data_label)

# Generating the QR code
def generate_qrcode():
    qrcode_data = str(data_entry.get())
    qrcode_name = str(Filename_entry.get())
    if qrcode_name == '':
        showerror(
            title='Error',
            message=(
                "An error has occurred\n"
                "The following is the cause:\n"
                "-> Empty filename entry field\n"
                "Make sure the filename entry is filled when generating the QR code"
            )
        )
    else:
        if askyesno(
            title='Confirmation',
            message='Do you want to create a QR code with the provided information?'
        ):
            try:
                qr = qrcode.QRCode(version=1, box_size=6, border=4)
                qr.add_data(qrcode_data)
                qr.make(fit=True)
                name = qrcode_name + '.png'
                qr_img = qr.make_image(fill_color='black', back_color='white')
                qr_img.save(name)
                global qrcode_image
                qrcode_image = PhotoImage(file=name)
                image_label1.config(image=qrcode_image)
                reset_button.config(state=NORMAL, command=reset)
            except Exception as e:
                showerror(title='Error', message=f'Error occurred: {e}')

# Reset button
def reset():
    if askyesno(title='Reset', message='Are you sure you want to reset?'):
        image_label1.config(image='')
        reset_button.config(state=DISABLED)

# File path
def open_dialog():
    name = fd.askopenfilename()
    file_entry.delete(0, END)
    file_entry.insert(0, name)
    
# File Entry and Browse button
file_entry = ttk.Entry(window, width=60)
browse_button = ttk.Button(window, text='Browse', command=open_dialog)
second_canvas.create_window(200, 350, window=file_entry)
second_canvas.create_window(430, 350, window=browse_button)

# Detecting QR code
def detect_qrcode():
    image_file = file_entry.get()
    if image_file == '':
        showerror(title='Error', message='Please provide a QR code image file to detect')
    else:
        try:
            qr_img = cv2.imread(image_file)
            qr_detector = cv2.QRCodeDetector()
            global qrcode_image
            qrcode_image = PhotoImage(file=image_file)
            image_label2.config(image=qrcode_image)
            data, _, _ = qr_detector.detectAndDecode(qr_img)
            data_label.config(text=data)
        except Exception as e:
            showerror(
                title='Error',
                message=f'Error occurred while detecting data: {e}'
            )
            
# Detect Button
detect_button = ttk.Button(window, text='Detect QRcode', command=detect_qrcode)
second_canvas.create_window(65, 385, window=detect_button)

# Close Application
def close_window():
    if askyesno(title='Close Application', message='Are you sure you want to close the application?'):
        window.destroy()

window.protocol('WM_DELETE_WINDOW', close_window)
window.mainloop()
