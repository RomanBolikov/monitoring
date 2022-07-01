import tkinter as tk
from tkinter import ttk, font, messagebox as mb
from tkcalendar import DateEntry
from pathlib import Path
from websearch import Request
from PyPDF2 import PdfFileReader
import persons
import form_doc
import requests
import subprocess
import textwrap


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        f = font.nametofont('TkDefaultFont')
        f.configure(size=11)
        s = ttk.Style()
        s. configure('My.TButton', justify='center')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.initUI()
        self.date = None
        self.path = None
        self.opened_docs = 0
        self.prompt_date()

    # #########################################################################

    # всплывающее окно с запросом даты
    def prompt_date(self):

        def choose_date():
            self.deletedir()
            self.date = npa_date_entry.get()
            self.docs = Request(self.date)
            while self.docs.total_list is None:
                if mb.askretrycancel(
                    'Ошибка', 'Сервер недоступен, повторить запрос?'
                ):
                    self.docs = Request(self.date)
                else:
                    return self.destroy()
            self.docs_num = len(self.docs.total_list)
            if self.docs_num == 0:
                mb.showinfo(
                    message=f'Документы за {self.date} не опубликованы!'
                )
                prompt.destroy()
                self.prompt_date()
            else:
                self.next_btn['state'] = (
                    'disabled' if self.docs_num == 1 else '!disabled'
                )
                self.cur_choice = 1
                self.prev_btn['state'] = 'disabled'
                self.path = Path(
                    Path.home(), 'Desktop', 'Monitoring', f'{self.date}')
                prompt.destroy()
                self.total_label_text.set(
                    f'Всего документов за {self.date}: {self.docs_num}'
                )
                self.show_doc()

        # описание виджетов всплывающего окна
        prompt = tk.Toplevel()
        prompt.attributes('-topmost', 'true')
        x = self.winfo_x()
        y = self.winfo_y()
        prompt.geometry("250x150+%d+%d" % (x + 200, y + 100))
        prompt.protocol('WM_DELETE_WINDOW', lambda: self.destroy())

        label = ttk.Label(prompt, text='Выберите дату: \n', justify='center')
        label.pack(side='top', pady=10)

        npa_date_entry = DateEntry(prompt, date_pattern='dd.mm.y')
        npa_date_entry.pack(pady=(0, 10))
        npa_date_entry.delete(0, tk.END)

        choose_date = ttk.Button(
            prompt, text='Выбрать', command=choose_date
        )
        choose_date.pack(pady=(0, 10))
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
            mainframe, text='Загрузить PDF', command=self.get_pdf,
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

        # ярлык и поле листов приложения
        append_label = ttk.Label(
            mainframe, text='Листов\nприложения:', justify='center'
        )
        append_label.grid(row=6, column=0, padx=5)
        self.appendix = tk.StringVar()
        self.appendix_entry = ttk.Entry(
            mainframe, state='disabled', width=4, textvariable=self.appendix
        )
        self.appendix_entry.grid(row=7, column=0, padx=5, pady=(5, 0))

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
        cur_doc = self.docs.total_list[self.cur_choice - 1]
        text = cur_doc['ComplexName'].replace('\n', '')
        self.npa_title.set(textwrap.fill(text))
        self.load_pdf['state'] = '!disabled'
        self.delete_pdf['state'] = 'disabled'
        self.form_var.set(0)
        self.form_chckbtn['state'] = 'disabled'
        self.appendix_entry.delete(0, tk.END)
        self.appendix_entry['state'] = 'disabled'
        if self.call_form_doc.winfo_ismapped():
            self.call_form_doc.grid_forget()
            self.delete_pdf.grid(row=4, column=2, padx=5, pady=(10, 15))
        self.addr_listbox.selection_clear(0, tk.END)

    # формирование реквизитов файла PDF
    def pdf_requisites(self, cur_doc):
        eonum = cur_doc['EoNumber']
        doc_num = cur_doc['Number']
        if cur_doc['DocumentTypeName'] == 'Федеральный закон':
            doc_type = 'ФЗ'
        elif cur_doc['DocumentTypeName'] == 'Указ':
            doc_type = 'Указ'
        elif cur_doc['DocumentTypeName'] == 'Постановление':
            if cur_doc['SignatoryAuthorityName'] == 'Правительство Российской \
Федерации':
                doc_type = 'ППРФ'
            else:
                doc_type = 'Пост. КС РФ'
        elif cur_doc['DocumentTypeName'] == 'Распоряжение':
            doc_type = 'РПРФ'
        elif cur_doc['DocumentTypeName'] == 'Определение':
            if cur_doc['SignatoryAuthorityName'] == 'Правительство Российской \
Федерации':
                doc_type = 'РПРФ'
            else:
                doc_type = 'Опр. КС РФ'
        else:
            doc_type = 'Приказ Минстроя'
            doc_num = doc_num[:-3]+'_пр'
        return (eonum, doc_type, doc_num)

    # загрузка файла PDF (кнопка "Загрузить PDF")
    def get_pdf(self):
        reqs = self.pdf_requisites(self.docs.total_list[self.cur_choice - 1])
        self.path.mkdir(exist_ok=True)
        savename = f'{reqs[1]} {reqs[2]}.pdf'
        pdf = open(Path(self.path, savename), 'wb')
        try:
            url = requests.get(
                f'http://publication.pravo.gov.ru/File/GetFile/{reqs[0]}\
?type=pdf', timeout=(3, 15)
            )
        except (
            requests.exceptions.Timeout, requests.exceptions.ConnectionError
        ):
            pdf.close()
            return mb.showerror(
                'Ошибка загрузки', 'Плохое соединение с сервером'
            )
        pdf.write(url.content)
        pdf.close()
        self.load_pdf['state'] = 'disabled'
        self.delete_pdf['state'] = '!disabled'
        self.form_chckbtn['state'] = '!disabled'
        subprocess.Popen([Path(self.path, savename)], shell=True)
        self.opened_docs += 1
        self.opened_docs_label.configure(
            text=f'Просмотрено документов: {self.opened_docs}'
        )

    # удаление файла PDF (кнопка "Удалить PDF")
    def delete_pdf(self):
        reqs = self.pdf_requisites(self.docs.total_list[self.cur_choice - 1])
        deletename = f'{reqs[1]} {reqs[2]}.pdf'
        deletepath = Path(self.path, deletename)
        deletepath.unlink(missing_ok=True)
        self.load_pdf['state'] = '!disabled'
        self.delete_pdf['state'] = 'disabled'
        self.form_chckbtn['state'] = 'disabled'
        self.appendix_entry['state'] = 'disabled'

    # включение возможности формирования документа
    # (галочка "Сформировать документ")
    def enable(self):
        if self.form_var.get() == 1:
            self.addr_listbox['state'] = 'normal'
            self.appendix_entry['state'] = '!disabled'
            reqs = self.pdf_requisites(
                self.docs.total_list[self.cur_choice - 1]
            )
            openname = f'{reqs[1]} {reqs[2]}.pdf'
            openpath = Path(self.path, openname)
            with open(openpath, 'rb') as file_in:
                pdf = PdfFileReader(file_in)
                pages = str(pdf.getNumPages())
                self.appendix_entry.insert(0, pages)
                file_in.close()
            self.delete_pdf.grid_forget()
            self.call_form_doc.grid(row=4, column=2, padx=5, pady=(10, 15))
        elif self.form_var.get() == 0:
            self.addr_listbox['state'] = 'disabled'
            self.appendix_entry.delete(0, tk.END)
            self.appendix_entry['state'] = 'disabled'
            self.call_form_doc.grid_forget()
            self.delete_pdf.grid(row=4, column=2, padx=5, pady=(10, 15))

    # отображение следующего документа
    def prev_doc(self):
        self.cur_choice -= 1
        if self.cur_choice == 1:
            self.prev_btn['state'] = 'disabled'
        elif self.cur_choice == self.docs_num - 1:
            self.next_btn['state'] = '!disabled'
        self.show_doc()

    # отображение предыдущего документа
    def next_doc(self):
        self.cur_choice += 1
        if self.cur_choice == 2:
            self.prev_btn['state'] = '!disabled'
        elif self.cur_choice == self.docs_num:
            self.next_btn['state'] = 'disabled'
        self.show_doc()

    # формирование файла служебной записки
    def send(self):
        if not self.addr_listbox.curselection():
            return mb.showerror('Ошибка', 'Выберите адресата')
        if self.appendix.get() == '':
            return mb.showerror(
                'Ошибка', 'Укажите количество листов приложения'
            )
        cur_doc = self.docs.total_list[self.cur_choice - 1]
        if cur_doc['DocumentTypeName'] == 'Федеральный закон':
            doc_type = 'Федеральный закон'
        elif cur_doc['DocumentTypeName'] == 'Указ':
            doc_type = 'Указ Президента Российской Федерации'
        elif (cur_doc['DocumentTypeName'] == 'Постановление'
                and cur_doc['SignatoryAuthorityName'] == 'Правительство \
Российской Федерации'):
            doc_type = 'постановление Правительства Российской Федерации'
        elif cur_doc['DocumentTypeName'] == 'Распоряжение':
            doc_type = 'распоряжение Правительства Российской Федерации'
        elif cur_doc['SignatoryAuthorityName'] == 'Конституционный Суд \
Российской Федерации':
            if cur_doc['DocumentTypeName'] == 'Постановление':
                doc_type = 'Постановление Конституционного Суда Российской \
Федерации'
            else:
                doc_type = 'Определение Конституционного Суда Российской \
Федерации'
        else:
            doc_type = 'приказ Министерства строительства и \
жилищно-коммунального хозяйства Российской Федерации'
        doc_title = cur_doc['Name']
        doc_date = cur_doc['DocumentDate']
        doc_date_frmtd = f'{doc_date[8:10]}.{doc_date[5:7]}.{doc_date[:4]}'
        doc_num = cur_doc['Number']

        return form_doc.form_doc(
            addressees=[persons.Person.namelist[i] for i
                        in self.addr_listbox.curselection()],
            npa_type=doc_type,
            npa_title=doc_title,
            npa_date=doc_date_frmtd,
            npa_num=doc_num,
            publ_date=self.date,
            app_sheets=self.appendix.get()
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
