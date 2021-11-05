import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter.constants import ANCHOR, CENTER
from PIL import Image, ImageTk
from Crypto.Cipher import AES
import binascii
import os


def define_layout(obj, cols=1, rows=1):
    def method(trg, col, row):
        for c in range(cols):
            trg.columnconfigure(c, weight=1)
        for r in range(rows):
            trg.rowconfigure(r, weight=1)

    if type(obj) == list:
        for trg in obj:
            method(trg, cols, rows)
    else:
        trg = obj
        method(trg, cols, rows)


class app:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('window')

        self.div1 = tk.Frame(self.window)
        self.div1.grid(row=0, column=0, sticky='we')
        self.div2 = tk.Frame(self.window)
        self.div2.grid(row=1, column=0, sticky='we')
        self.div3 = tk.Frame(self.window, width=400, height=300)
        self.div3.grid(row=2, column=0, sticky='nswe')

        self.key_title = tk.Label(self.div1, text='key:')
        self.key_title.grid(row=0, column=0, sticky='e')

        self.key_entry = ttk.Entry(self.div1)
        self.key_entry.config(width=100)
        self.key_entry.grid(row=0, column=1, sticky='w')

        self.bt1 = ttk.Button(self.div2, text='選圖', command=self.show_image)
        self.bt1.grid(row=0, column=0, sticky='we')

        self.bt2 = ttk.Button(self.div2, text='加密', command=self.encrypt)
        self.bt2.grid(row=0, column=1, sticky='we')

        self.bt3 = ttk.Button(self.div2, text='解密', command=self.decrypt)
        self.bt3.grid(row=0, column=2, sticky='we')

        self.image_area = tk.Label(self.div3, image='')

        define_layout(self.window, 1, 3)
        self.window.rowconfigure(0, weight=0)
        self.window.rowconfigure(1, weight=0)

        define_layout(self.div1, 2, 0)
        define_layout(self.div2, 3, 0)

    def show_image(self):
        path = filedialog.askopenfilename()
        if not path:
            print("nothing")
        else:
            print(path)
            self.img = Image.open(path)
            imgTK = ImageTk.PhotoImage(self.img)
            self.image_area.image = imgTK
            self.image_area.config(image=imgTK, anchor=CENTER)
            self.image_area.pack()

    def encrypt_init_(self):
        if self.img.mode != 'RGB':
            self.img = self.img.convert('RGB')

        self.img.save('temp.ppm')
        file = open('temp.ppm', 'rb')

        self.detail = file.read()

        temp_detail = self.detail
        index_list = []
        for num in range(3):
            index = temp_detail.find(10)
            index_list.append(index)
            temp_detail = temp_detail[index+1:]

        index = index_list[0] + (index_list[1] + 1) + (index_list[2] + 1) + 1

        self.format = self.detail[:index]
        self.pixel = self.detail[index:]
        print(self.format)

        self.key = os.urandom(16)
        self.key_entry.delete(0, 'end')
        self.key_entry.insert(0, binascii.hexlify(self.key).decode('utf-8'))
        print(self.key)
        print(binascii.hexlify(self.key))
        print(type(self.key))

        self.iv = b'1234567890123456'

        while len(self.pixel) % 16 != 0:
            pad = bytes([self.pixel[-1]])
            self.pixel = self.pixel + pad

    def encrypt(self):
        self.encrypt_init_()
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        f_out = open('output.ppm', 'wb')
        f_out.write(self.format)
        f_out.write(cipher.encrypt(self.pixel))
        f_out.close()

        temp = Image.open('output.ppm')
        path = filedialog.askdirectory()
        if not path:
            messagebox.showinfo("Cancel", "You cancel saving")
            return
        else:
            target_path = os.path.join(path, 'output_enc.png')
            temp.save(target_path)
            temp.close()
            self.img = Image.open(target_path)

        os.remove('temp.ppm')
        os.remove('output.ppm')

        imgTK = ImageTk.PhotoImage(self.img)
        self.image_area.image = imgTK
        self.image_area.config(image=imgTK, anchor=CENTER)
        self.image_area.pack()

    def decrypt_init(self):
        self.img.save('temp.ppm')
        file = open('temp.ppm', 'rb')

        self.detail = file.read()

        temp_detail = self.detail
        index_list = []
        for num in range(3):
            index = temp_detail.find(10)
            index_list.append(index)
            temp_detail = temp_detail[index+1:]

        index = index_list[0] + (index_list[1] + 1) + (index_list[2] + 1) + 1

        self.format = self.detail[:index]
        self.pixel = self.detail[index:]
        print(self.format)

        self.key = self.key_entry.get()
        if not self.key:
            messagebox.showerror('no key', 'please input your proper key')
            return
        elif len(self.key) != 32:
            messagebox.showerror("key length", "key length is wrong")
            return
        else:
            self.key = binascii.unhexlify(self.key)

        self.iv = b'1234567890123456'

        while len(self.pixel) % 16 != 0:
            pad = bytes([self.pixel[-1]])
            self.pixel = self.pixel + pad

    def decrypt(self):
        self.decrypt_init()
        decryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        f_out = open('output.ppm', 'wb')
        f_out.write(self.format)
        f_out.write(decryptor.decrypt(self.pixel))
        f_out.close()

        temp = Image.open('output.ppm')
        path = filedialog.askdirectory()
        if not path:
            messagebox.showinfo("Cancel", "You cancel saving")
            return
        else:
            target_path = os.path.join(path, 'output_dec.png')
            temp.save(target_path)
            temp.close()
            self.img = Image.open(target_path)

        os.remove('temp.ppm')
        os.remove('output.ppm')

        imgTK = ImageTk.PhotoImage(self.img)
        self.image_area.image = imgTK
        self.image_area.config(image=imgTK, anchor=CENTER)
        self.image_area.pack()

    def begin(self):
        self.window.mainloop()


window = app()
window.begin()
