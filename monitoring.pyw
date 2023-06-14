import tkinter as tk
from tkinter import ttk, filedialog as fd, font, messagebox as mb
from tkcalendar import DateEntry
from pathlib import Path
from websearch import Request
from subprocess import Popen
from doctypes import DOC_TYPES
import json
import persons
import form_doc
import re
import requests
import textwrap
import threading
from atomicinteger import AtomicInteger


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        f = font.nametofont('TkDefaultFont')
        f.configure(size=11)
        s = ttk.Style()
        s.configure('My.TButton', justify='center')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.initUI()
        self.date = None
        self.path = None
        self.opened_docs = AtomicInteger(0)
        config_path = Path(__file__).with_name('config.json')
        with config_path.open('r+') as config:
            data = json.load(config)
            existing_path = data.get('readerpath')
            if existing_path is not None:
                self.readerpath = Path(existing_path)
            else:
                mb.showinfo(
                    'Выбор программы', 'Выберите расположение программы для \
чтения файлов формата .pdf'
                )
                path = fd.askopenfilename(
                    defaultextension=".exe", initialdir='C:\\Program Files'
                )
                if path is not None:
                    self.readerpath = Path(path)
                else:
                    mb.showinfo('Выбор программы', 'Программа не выбрана!')
                    self.destroy()
                data['readerpath'] = path
                config.seek(0)
                json.dump(data, config)
                config.truncate()
        self.thread_count = AtomicInteger(0)
        self.prompt_date()

    # #########################################################################

    # всплывающее окно с запросом даты
    def prompt_date(self):

        # нельзя сменить дату, пока не завершены все загрузки
        if self.thread_count.value > 0:
            return mb.showwarning(
                'Ошибка',
                'Нельзя изменить дату, пока не завершены все загрузки'
            )

        # загрузка виджетов всплывающего окна
        self.prompt = tk.Toplevel()
        self.prompt.attributes('-topmost', 'true')
        x = self.winfo_x()
        y = self.winfo_y()
        self.prompt.geometry("250x150+%d+%d" % (x + 200, y + 100))
        self.prompt.protocol('WM_DELETE_WINDOW', lambda: self.destroy())

        label = ttk.Label(
            self.prompt, text='Выберите дату: \n', justify='center')
        label.pack(side='top', pady=10)

        self.npa_date_entry = DateEntry(self.prompt, date_pattern='dd.mm.y')
        self.npa_date_entry.pack(pady=(0, 10))
        self.npa_date_entry.delete(0, tk.END)

        choose_date = ttk.Button(
            self.prompt, text='Выбрать', command=self.choose_date
        )
        choose_date.pack(pady=(0, 10))

    # выбор даты по нажатию кнопки "Выбрать"
    def choose_date(self):
        self.deletedir()
        self.total_list = None
        self.date = self.npa_date_entry.get()
        self.docs = Request(self.date)
        self.total_list = self.docs.total_list()
        while self.total_list is None:
            if mb.askretrycancel(
                'Ошибка', 'Сервер недоступен, повторить запрос?'
            ):
                self.total_list = self.docs.total_list()
            else:
                self.prompt.destroy()
                return self.prompt_date()
        self.docs_num = len(self.total_list)
        if self.docs_num == 0:
            mb.showinfo(
                message=f'Документы за {self.date} не опубликованы!'
            )
            self.prompt.destroy()
            return self.prompt_date()
        else:
            self.next_btn['state'] = (
                'disabled' if self.docs_num == 1 else '!disabled'
            )
            self.cur_choice = 1
            self.prev_btn['state'] = 'disabled'
            config_path = Path(__file__).with_name('config.json')
            with config_path.open('r+') as config:
                data = json.load(config)
                existing_path = data.get('main_folder')
                if existing_path is not None:
                    self.path = Path(
                        existing_path, 'Monitoring', f'{self.date}'
                    )
                else:
                    mb.showinfo(
                        'Выбор расположения каталога',
                        'Выберите расположение каталога для сохранения \
файлов')
                    path = fd.askdirectory(
                        initialdir='C:\\Program Files'
                    )
                    if path is not None:
                        Path(path, 'Monitoring').mkdir(exist_ok=True)
                        self.path = Path(
                            path, 'Monitoring', f'{self.date}'
                        )
                    else:
                        mb.showinfo('Выбор каталога', 'Каталог не выбран!')
                        self.destroy()
                    data['main_folder'] = path
                    config.seek(0)
                    json.dump(data, config)
                    config.truncate()
            self.path.mkdir(exist_ok=True)
            self.prompt.destroy()
            self.total_label_text.set(
                f'Всего документов за {self.date}: {self.docs_num}'
            )
            self.show_doc()
    #########################################################################

    # основной интерфейс
    def initUI(self):
        mainframe = ttk.Frame(self)
        mainframe.pack(expand=True, fill='both')

        # всего документов
        self.total_label_text = tk.StringVar()
        total_label = ttk.Label(mainframe, textvariable=self.total_label_text)
        total_label.grid(
            row=0, column=0, columnspan=3, padx=10, pady=(10, 0), sticky=tk.W
        )

        # просмотрено документов
        self.opened_docs_label = ttk.Label(mainframe)
        self.opened_docs_label.grid(
            row=1, column=0, columnspan=3, padx=10, pady=(10, 0), sticky=tk.W
        )

        # кнопка "Другая дата"
        change_date = ttk.Button(
            mainframe, text='Другая дата', command=self.prompt_date,
            style='My.TButton'
        )
        change_date.grid(row=0, rowspan=2, column=2, padx=5, pady=(10, 0))

        # номер текущего документа
        self.current_label_text = tk.StringVar()
        current_label = ttk.Label(
            mainframe, textvariable=self.current_label_text)
        current_label.grid(
            row=2, column=0, columnspan=3, padx=10, pady=(10, 0), sticky=tk.W
        )

        # наименование текущего документа
        self.npa_title = tk.StringVar()
        npa_label = ttk.Label(mainframe, textvariable=self.npa_title)
        npa_label.grid(
            row=3, column=0, columnspan=3, padx=10, pady=(10, 0), sticky=tk.W
        )

        # кнопка "Загрузить PDF"
        self.load_pdf = ttk.Button(
            mainframe, text='              ', command=self.start_thread,
            style='My.TButton'
        )
        self.load_pdf.grid(row=4, column=0, padx=5, pady=(10, 15))

        # кнопка "Удалить PDF", меняется на "Сформировать документ" при выборе
        # галочки "Сформировать документ"
        self.delete_pdf = ttk.Button(
            mainframe, text='Удалить PDF', command=self.delete_pdf,
            state='disabled', style='My.TButton'
        )
        self.delete_pdf.grid(row=4, column=2, padx=5, pady=(10, 15))

        # галочка "Сформировать документ"
        self.form_var = tk.IntVar()
        self.form_chckbtn = ttk.Checkbutton(
            mainframe, text='Сформировать документ', state='disabled',
            variable=self.form_var, command=self.enable
        )
        self.form_chckbtn.grid(row=5, column=0, padx=5, pady=(10, 5))

        # ярлык текущих загрузок
        self.downloads = tk.StringVar()
        downloads_label = ttk.Label(
            mainframe, justify='center', textvariable=self.downloads
        )
        downloads_label.grid(row=6, column=0, padx=5)

        # окно выбора адресата
        namevar = tk.StringVar(
            value=[elem.name_with_initials for elem in persons.Person.namelist]
        )
        self.addr_listbox = tk.Listbox(
            mainframe, listvariable=namevar, bg='white', height=5,
            selectmode='extended', state='disabled'
        )
        self.addr_listbox.grid(
            row=5, column=2, rowspan=3, columnspan=2, padx=5, pady=10,
            sticky=tk.W
        )

        # кнопка "Сформировать документ"
        self.call_form_doc = ttk.Button(
            mainframe, text='Cформировать\nдокумент', command=self.send,
            style='My.TButton'
        )

        # кнопка "Предыдущий"
        self.prev_btn = ttk.Button(
            mainframe, text='Предыдущий\n(<Shift-Tab>)', command=self.prev_doc,
            state='disabled', style='My.TButton'
        )
        self.prev_btn.grid(row=9, column=0, padx=5, pady=(5, 15))
        self.bind('<Shift-Tab>', lambda e: self.prev_btn.invoke())

        # кнопка "Следующий"
        self.next_btn = ttk.Button(
            mainframe, text='Следующий\n(<Tab>)', command=self.next_doc,
            style='My.TButton'
        )
        self.next_btn.grid(row=9, column=2, padx=5, pady=(5, 15))
        self.bind('<Tab>', lambda e: self.next_btn.invoke())
    #######################################################################

    # описание классовых методов (функций) основного интерфейса

    # отображение текущего документа
    def show_doc(self):
        self.current_label_text.set(
            f'Документ {self.cur_choice} из {self.docs_num}:'
        )
        cur_doc = self.total_list[self.cur_choice - 1]
        text = cur_doc['complexName'].replace('\n', '')
        file_length = cur_doc['pdfFileLength'] // 1024
        self.npa_title.set(textwrap.fill(text))
        if self.call_form_doc.winfo_ismapped():
            self.call_form_doc.grid_forget()
            self.delete_pdf.grid(row=4, column=2, padx=5, pady=(10, 15))
        self.addr_listbox.selection_clear(0, tk.END)
        self.form_var.set(0)
        if cur_doc.get('pdf_loaded') is None or not cur_doc.get('pdf_loaded'):
            self.load_pdf.configure(
                state='!disabled', text=f'Загрузить PDF\n({file_length} Кб)'
            )
            self.delete_pdf['state'] = 'disabled'
            self.form_chckbtn['state'] = 'disabled'
        else:
            self.load_pdf.configure(
                state='disabled', text=f'Документ загружен\n({file_length} Кб)'
            )
            self.delete_pdf['state'] = '!disabled'
            self.form_chckbtn['state'] = '!disabled'

    # формирование реквизитов файла PDF
    def pdf_requisites(self, cur_doc):
        eonum = cur_doc['eoNumber']
        doc_num = re.search(r'№ \d+(-ФКЗ|-ФЗ|-р|/пр|н|-О|-П|-О-П|-О-О)?',
                            cur_doc['complexName']).group()
        for key, value in DOC_TYPES.items():
            if re.match(key, cur_doc['complexName']):
                doc_type = value
        if doc_num[-3] == '/':
            doc_num = doc_num[:-3]+'_пр'
        return (eonum, doc_type, doc_num)

    # старт нового потока (кнопка "Загрузить PDF")
    def start_thread(self):
        self.load_pdf.configure(state='disabled')
        threading.Thread(target=self.get_pdf, daemon=True).start()
        downloads = self.thread_count.increment_and_get()
        with threading.Lock():
            self.downloads.set("Загружается: " + str(downloads))

    # загрузка файла PDF
    def get_pdf(self):
        cur_number = self.cur_choice - 1
        cur_doc = self.total_list[cur_number]
        reqs = self.pdf_requisites(cur_doc)
        file_length = cur_doc['pdfFileLength'] // 1024
        savename = f'{reqs[1]} {reqs[2]}.pdf'
        pdf = open(Path(self.path, savename), 'wb')
        try:
            url = requests.get(
              f'http://publication.pravo.gov.ru/file/pdf/?eoNumber={reqs[0]}',
              timeout=(3, 15)
            )
        except (
            requests.exceptions.Timeout, requests.exceptions.ConnectionError
        ):
            pdf.close()
            self.thread_count.decrement_and_get()
            return mb.showerror(
                'Ошибка загрузки', 'Плохое соединение с сервером'
            )
        pdf.write(url.content)
        pdf.close()
        if cur_number == self.cur_choice - 1:
            self.load_pdf.configure(
                text=f'Документ загружен\n({file_length} Кб)', state='disabled'
            )
            self.delete_pdf['state'] = '!disabled'
            self.form_chckbtn['state'] = '!disabled'
        if self.total_list[cur_number].get('pdf_loaded') is None:
            self.opened_docs.increment_and_get()
            self.opened_docs_label.configure(
                text=f'Просмотрено документов: {self.opened_docs.value}'
            )
        self.total_list[cur_number]['pdf_loaded'] = True
        Popen(args=[self.readerpath, Path(self.path, savename)])
        downloads = self.thread_count.decrement_and_get()
        with threading.Lock():
            self.downloads.set("Загружается: " + str(downloads))

    # удаление файла PDF (кнопка "Удалить PDF")
    def delete_pdf(self):
        cur_number = self.cur_choice - 1
        cur_doc = self.total_list[cur_number]
        reqs = self.pdf_requisites(cur_doc)
        deletename = f'{reqs[1]} {reqs[2]}.pdf'
        deletepath = Path(self.path, deletename)
        deletepath.unlink(missing_ok=True)
        self.total_list[cur_number]['pdf_loaded'] = False
        file_length = cur_doc['pdfFileLength'] // 1024
        self.load_pdf.configure(
            state='!disabled', text=f'Загрузить PDF\n({file_length} Кб)'
        )
        self.delete_pdf['state'] = 'disabled'
        self.form_chckbtn['state'] = 'disabled'

    # включение возможности формирования документа
    # (галочка "Сформировать документ")
    def enable(self):
        if self.form_var.get() == 1:
            self.addr_listbox['state'] = 'normal'
            self.delete_pdf.grid_forget()
            self.call_form_doc.grid(row=4, column=2, padx=5, pady=(10, 15))
        elif self.form_var.get() == 0:
            self.addr_listbox.selection_clear(0, tk.END)
            self.addr_listbox['state'] = 'disabled'
            self.call_form_doc.grid_forget()
            self.delete_pdf.grid(row=4, column=2, padx=5, pady=(10, 15))

    # отображение предыдущего документа
    def prev_doc(self):
        self.cur_choice -= 1
        if self.cur_choice == 1:
            self.prev_btn['state'] = 'disabled'
        elif self.cur_choice == self.docs_num - 1:
            self.next_btn['state'] = '!disabled'
        self.show_doc()

    # отображение следующего документа
    def next_doc(self):
        self.cur_choice += 1
        if self.cur_choice == 2:
            self.prev_btn['state'] = '!disabled'
        if self.cur_choice == self.docs_num:
            self.next_btn['state'] = 'disabled'
        self.show_doc()

    # формирование файла служебной записки
    def send(self):
        if not self.addr_listbox.curselection():
            return mb.showerror('Ошибка', 'Выберите адресата')
        cur_number = self.cur_choice - 1
        cur_doc = self.total_list[cur_number]
        for key, value in DOC_TYPES.items():
            if re.match(key, cur_doc['complexName']):
                doc_type = value
        doc_date = re.search(r'\d{2}\.\d{2}\.\d{4}',
                             cur_doc['complexName']).group()
        doc_num = re.search(r'№ \d+(-ФКЗ|-ФЗ|-р|/пр|н|-О|-П|-О-П|-О-О)?',
                            cur_doc['complexName']).group()
        pages = str(cur_doc['pagesCount'])
        return form_doc.form_doc(
            addressees=[persons.Person.namelist[i] for i
                        in self.addr_listbox.curselection()],
            npa_type=doc_type,
            npa_title=cur_doc['complexName'].replace('\n', ''),
            npa_date=doc_date,
            npa_num=doc_num,
            publ_date=self.date,
            app_sheets=pages
        )

    # удаление пустого каталога при закрытии окна программы или смене даты
    def deletedir(self):
        try:
            if self.path and not any(self.path.iterdir()):
                self.path.rmdir()
        except FileNotFoundError:
            pass

    # выход из программы
    def quit(self):
        self.deletedir()
        self.destroy()


##############################################################################


def main():
    root = App()
    root.title('Мониторинг')
    root.iconbitmap(Path(r'c:\Prog\my_icon.ico'))
    root.resizable(False, False)
    root.mainloop()


if __name__ == '__main__':
    main()
