start_message = 'Привет приятель! Команда *IT Root* рада тебя видеть))\n\nВыбирай, и читай статьи. Можешь выбрать по ' \
                'автору, можешь по теме. Есть раздел с приглашенными участниками. Либо жми *Я сам выберу! ' \
                'Покажите все статьи* и выбирай сам!\n\n*Приятного чтения!*'

help_mes = 'В этом боте собраны статьи с канала *IT Root*. Ты можешь искать статьи по автору, по теме, или нажать ' \
           '*Я сам выберу! Покажите все статьи* - чтобы получить список из всех статей, и выбрать самому.\n\n' \
           'Списки тем и статей как правило имеют несколько страниц, используй *Далее* и *Назад*, что бы листать' \
           ' список\n\n*Приятного чтения!*'

helping_text = 'Список админских команд в боте:\n\n/global - глобальная рассылка (*/global <текст рассылки>*)' \
               '\n\n/downloadarticle - добавление своей статьи в БД ' \
               '(*/downloadarticle авторы|темы|название|ссылка*)\n\n' \
               '/downloadtheme - добавление темы в БД (*/downloadtheme <название темы>*)'

hello_author_mes = 'Хорошо!\n\nВыбирай, чьи статьи ты хочешь читать: Naize, Valter или Fox'
hello_theme_mes = 'Вот все темы, на которые когда либо были написаны статьи. Выбирай, что душе угодно!'
hello_all_mes = 'Все статьи с канала IT Root. Выбирай и читай что хочешь!'
hello_other_mes = 'Ты выбрал раздел с приглашенными участниками!'


author_mes = 'Ты выбрал статьи {}'
theme_mes = 'Статьи по теме {}'

first_level_back = 'Назад в меню'
back_to_author = 'Назад к списку авторов'
back_to_theme = 'Назад к списку тем'

download_incorrect = 'Не правильно введены данные. Шаблон - <b>авторы|темы|название|ссылка</b>'
author_error = 'Авторы не были найдены. Попробуйте ещё раз!'
theme_error = 'Темы не были найдены. Попробуйте ещё раз!'
download_success = 'Статья успешно добавлена'

main_menu = [
    'По авторам',
    'По темам',
    'Я сам выберу! Покажите все статьи',
    'Other. Гости, интервью, и многое другое'
]

other_section = [
    'Статьи наших гостей',
    first_level_back
]

state = {
    'st': 'starting',
    'at': 'author',
    'ac': 'author_choice',
    'th': 'theme',
    'tc': 'theme_choice',
    'al': 'all',
    'ot': 'other',
    'oc': 'other_choice'
}
