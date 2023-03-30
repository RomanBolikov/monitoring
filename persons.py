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


a = Person(
    'Антонову', 'Антон Антонович',
    'Начальнику управления безопасности'
)

d = Person('Демидову', 'Денис Дмитриевич', 'Заместителю начальника отдела')

y = Person(
    'Юрьевой', 'Юлия Юрьевна',
    'И.о. начальника управления экономики',
    gender='female'
)
