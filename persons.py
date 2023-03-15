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

lavrinovich = Person(
    'Лавриновичу', 'Игорь Евгеньевич',
    'Начальнику управления архитектуры и градостроительства'
)

lee = Person(
    'Ли', 'Наталья Валентиновна',
    'Заместителю министра по экономическим вопросам', gender='female'
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
    'Начальнику управления жилищного строительства'
)

selemenev = Person(
    'Селеменеву', 'Александр Иванович',
    'Заместителю министра - главному архитектору края'
)

minister = Person(
    'Дубову', 'Алексей Сергеевич',
    'И.о. министра строительства Хабаровского края'
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

yusupova = Person(
    'Юсуповой', 'Анна Хайдаровна',
    'И.о. начальника управления экономики и развития строительной отрасли',
    gender='female'
)
