from pathlib import Path
import docx
import subprocess


def form_doc(
        addressees, npa_type, npa_title, npa_date, npa_num, publ_date,
        app_sheets
):
    NPA_DATA = {
        'Федеральный конституционный закон': {
            'title_text': f'О Федеральном конституционном законе от {npa_date} \
№ {npa_num}',
            'case1': 'опубликован', 'case2': 'указанного Федерального \
конституционного закона',
            'short_type': 'ФКЗ'
        },
        'Федеральный закон': {
            'title_text': f'О Федеральном законе от {npa_date} № {npa_num}',
            'case1': 'опубликован', 'case2': 'указанного Федерального закона',
            'short_type': 'ФЗ'
        },
        'Указ Президента Российской Федерации': {
            'title_text': f'''Об Указе Президента Российской Федерации от \
{npa_date} № {npa_num}''',
            'case1': 'опубликован', 'case2': 'Указа', 'short_type': 'Указ'
        },
        'постановление Правительства Российской Федерации': {
            'title_text': f'''О постановлении Правительства Российской \
Федерации от {npa_date} № {npa_num}''', 'case1': 'опубликовано',
            'case2': 'указанного постановления', 'short_type': 'ППРФ'
        },
        'распоряжение Правительства Российской Федерации': {
            'title_text': f'''О распоряжении Правительства Российской \
Федерации от {npa_date} № {npa_num}''', 'case1': 'опубликовано',
            'case2': 'указанного распоряжения', 'short_type': 'РПРФ'
        },
        'Постановление Конституционного Суда Российской Федерации': {
            'title_text': f'''О Постановлении Конституционного Суда \
Российской Федерации от {npa_date} № {npa_num}''', 'case1': 'опубликовано',
            'case2': 'указанного Постановления', 'short_type': 'Пост. КС РФ'
        },
        'Определение Конституционного Суда Российской Федерации': {
            'title_text': f'''Об Определении Конституционного Суда Российской \
Федерации от {npa_date} № {npa_num}''', 'case1': 'опубликовано',
            'case2': 'указанного Определения', 'short_type': 'Опр. КС РФ'
        },
        '''приказ Министерства строительства и жилищно-коммунального хозяйства \
Российской Федерации''': {
            'title_text':
            f'О приказе Минстроя России от {npa_date} № {npa_num}',
            'case1': 'опубликован', 'case2': 'приказа',
            'short_type': 'приказ Минстроя'
        },
        'приказ Министерства финансов Российской Федерации': {
            'title_text':
            f'О приказе Минфина России от {npa_date} № {npa_num}',
            'case1': 'опубликован', 'case2': 'приказа',
            'short_type': 'приказ Минфина'
        }
    }
    current_npa_type = NPA_DATA[npa_type]
    doc = docx.Document(Path('C:/Боликов Р.А/Шаблоны/doc_template.docx'))
    table = doc.tables[0]
    address = table.cell(0, 2)
    title = table.cell(1, 0)
    exclamation = doc.paragraphs[1]
    first_para = doc.paragraphs[3]
    second_para = doc.paragraphs[4]
    appendix = doc.paragraphs[5]
    address.paragraphs[0].text = addressees[0].position
    address.paragraphs[1].text = addressees[0].name_with_initials
    for i in range(1, len(addressees)):
        address.add_paragraph(addressees[i].position)
        address.add_paragraph(addressees[i].name_with_initials)
    for para in address.paragraphs:
        para.style = 'addr_style'
    title.paragraphs[1].text = current_npa_type['title_text']
    title.paragraphs[1].style = 'title_style'
    if len(addressees) == 1:
        exclamation.text = addressees[0].address
    else:
        exclamation.text = 'Уважаемые коллеги!'
    first_para.text = f'Сообщаю, что {publ_date} на официальном \
Интернет-портале правовой информации pravo.gov.ru \
{current_npa_type["case1"]} {npa_type} от {npa_date} № {npa_num} \
"{npa_title}".'
    second_para.text = f'Направляю копию {current_npa_type["case2"]} для \
сведения и учета в работе.'
    appendix.text = f'Приложение: на {app_sheets} л. в 1 экз.'
    if npa_type == 'приказ Министерства строительства и жилищно-коммунального \
хозяйства Российской Федерации':
        savename = (
            f'{", ".join([elem.name_with_initials for elem in addressees])} \
{current_npa_type["short_type"]} {npa_num[:-3]}_пр.docx'
        )
    else:
        savename = (
            f'{", ".join([elem.name_with_initials for elem in addressees])} \
{current_npa_type["short_type"]} {npa_num}.docx'
        )
    doc.save(Path('C:/Боликов Р.А/Внутренние документы/Коллегам', savename))
    subprocess.Popen(
        [Path('C:/Боликов Р.А/Внутренние документы/Коллегам', savename)],
        shell=True
    )
