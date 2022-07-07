class Person:
    namelist = []

    def __init__(self, surname, givenname, position, gender='male'):
        self.surname = surname
        self.givenname = givenname
        self.gender = gender
        self.name_with_initials = (
            f'{self.surname} {self.givenname.split()[0][0]}.\
{self.givenname.split()[1][0]}.'
        )
        if self.gender == 'male':
            self.address = (
                f'Уважаемый {self.givenname.split()[0]} \
{self.givenname.split()[1]}!'
            )
        elif self.gender == 'female':
            self.address = (
                f'Уважаемая {self.givenname.split()[0]} \
{self.givenname.split()[1]}!'
            )
        self.position = position
        self.namelist.append(self)


gurchenko = Person(
    'Гурченко', 'Владимир Алексеевич',
    'Начальнику управления строительства объектов краевой и \
муниципальной собственности'
)

dubov = Person('Дубову', 'Алексей Сергеевич', 'Первому заместителю министра')

krylova = Person(
    'Крыловой', 'Елена Юрьевна',
    'Начальнику отдела контроля и аудита финансового управления',
    gender='female')

lavrinovich = Person(
    'Лавриновичу', 'Игорь Евгеньевич',
    'Начальнику управления архитектуры и градостроительства'
)

magomaev = Person(
    'Магомаеву', 'Темирлан Магометзагитович', 'Заместителю министра'
)

maksimova = Person(
    'Максимовой', 'Наталья Яковлевна',
    'Заместителю министра - начальнику финансового управления', gender='female'
)

nazarenko = Person(
    'Назаренко', 'Алексей Сергеевич',
    'И.о. заместителя министра по экономическим вопросам'
)

selemenev = Person(
    'Селеменеву', 'Александр Иванович',
    'Заместителю министра - главному архитектору края'
)

minister = Person(
    'Сутурину', 'Олег Борисович',
    'Министру строительства Хабаровского края'
)

tarasevich = Person(
    'Тарасевич', 'Александра Анатольевна',
    'Заведующему сектором государственной службы и профилактики коррупционных \
и иных правонарушений', gender='female'
)

sz = Person(
    'Труфановой', 'Ярославна Егоровна',
    'Начальнику КГКУ "Служба заказчика Минстроя края"', gender='female'
)

shevchenko = Person(
    'Шевченко', 'Максим Александрович',
    'И.о. начальника управления экономики и развития строительной отрасли'
)
