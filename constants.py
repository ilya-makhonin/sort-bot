start_message = 'Привет приятель! Команда *IT Root* рада тебя видеть))\n\nВыбирай, и читай статьи. Можешь выбрать по ' \
                'автору, можешь по теме. Есть раздел с приглашенными участниками. Либо жми *"Я сам выберу! ' \
                'Покажите все статьи"* и выбирай сам!\n\n*Приятного чтения!*'

main_message = 'Выбирай, и читай статьи. Можешь выбрать по автору, можешь по теме. Есть раздел с приглашенными ' \
               'участниками. Либо жми *"Я сам выберу! Покажите все статьи"* и выбирай сам!\n\n*Приятного чтения!*'

help_mes = 'В этом боте собраны статьи с канала *IT Root*! Ты можешь искать статьи по автору, по теме, или нажать ' \
           '*Я сам выберу! Покажите все статьи* - чтобы получить список из всех статей, и выбрать самому. Также есть ' \
           'раздел с приглашенными участниками.\n\nСписки тем и статей как правило имеют несколько страниц, ' \
           'используй *Далее* и *Назад*, что бы листать список.\n\n*Приятного чтения!*'

helping_text = 'Список админских команд в боте:\n\n/global - глобальная рассылка (*/global <текст рассылки>*)' \
               '\n\n/downloadarticle - добавление своей статьи в БД ' \
               '(*/downloadarticle авторы|темы|название|ссылка* или *other|section|theme|name|link*)\n\n' \
               '/downloadtheme - добавление темы в БД (*/downloadtheme <название темы>*)\n\n/userscount - количество' \
               'пользователей\n\n/addcourse - добавить новый курс (*/addcourse название|ссылка_на_описание*)\n\n' \
               '/lastarticle - последняя загруженная статья'

hello_author_mes = 'Хорошо!\n\nВыбирай, чьи статьи ты хочешь читать: Naize, Valter или Fox'
hello_theme_mes = 'Вот все темы, на которые когда либо были написаны статьи. Выбирай, что душе угодно!'
hello_all_mes = 'Все статьи с канала IT Root. Выбирай и читай что хочешь!'
hello_other_mes = 'Ты выбрал раздел с приглашенными участниками!'
hello_courses_mes = 'Тут ты можешь посмотреть наши авторские курсы'


author_mes = 'Ты выбрал статьи {}'
theme_mes = 'Статьи по теме {}'
other_mes = 'Ты выбрал раздел {}'

first_level_back = 'Назад в меню'
back_to_author = 'Назад к списку авторов'
back_to_theme = 'Назад к списку тем'
back_to_other = 'Назад в раздел с приглашенными участниками'

download_incorrect = 'Не правильно введены данные. Шаблон - <b>авторы|темы|название|ссылка</b>'
other_incorrect = 'При проверке данных произошла ошибка:\n\nКорректность раздела: {}\n\nКорректность тем: {}'
stand_incorrect = 'При проверке данных произошла ошибка:\n\nКорректность авторов: {}\n\nКорректность тем: {}'
download_success = 'Статья успешно добавлена'
article_duplicate = 'Статья с таким названием уже существует! Используйте другое название'

main_menu = [
    'По авторам',
    'По темам',
    'Я сам выберу! Покажите все статьи',
    'Other. Гости, интервью, и многое другое',
    'Курсы по разработке'
]

state = {
    'st': 'starting',

    'at': 'author',
    'ac': 'author_choice',

    'th': 'theme',
    'tc': 'theme_choice',

    'al': 'all',

    'ot': 'other',
    'oc': 'other_choice',

    'cr': 'courses'
}
