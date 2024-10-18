# QA_task_dogs
# 10 Основных Проблем в Коде
# Нет обработки ошибок HTTP-запросов
(критичность: высокая) Запросы к API (Dog API и Я.Диск) выполняются без проверки статуса ответа, что может привести к аварийному завершению при любой ошибке (например, сетевой сбой).

# Хардкод токенов доступа 
(критичность: высокая) Токены для доступа к API Я.Диска захардкожены в коде, что создает серьезные риски безопасности и не подходит для production.

# Нет обработки исключений 
(критичность: высокая) Ошибки выполнения (например, HTTP-запросов или операции с файлом) не перехватываются, что может привести к завершению работы программы при любой проблеме.

# Неудобная и непонятная именование функции "u" 
(критичность: высокая) Название u не несет никакой смысловой нагрузки, что ухудшает читаемость и поддержку кода.

# Неоптимальное использование объектов 
(критичность: высокая) Экземпляр класса YaUploader создается каждый раз при вызове функции u. Лучше передавать его как параметр функции или инициализировать один раз.

# Неиспользуемые ответы от запросов 
(критичность: средняя) В методах create_folder и upload_photos_to_yd отсутствует логика проверки ответа, что делает их менее надежными.

# Повторение кода в get_urls 
(критичность: средняя) Существуют повторяющиеся запросы для основной породы и подпород. Можно улучшить структуру, чтобы избежать дублирования.

# Хардкод папок и имен 
(критичность: средняя) Название папки 'test_folder' жестко задано в коде, и это делает приложение негибким. Желательно передавать такие параметры явно.

# Использование случайной породы в тесте 
(критичность: низкая) В тесте используется случайная порода, что делает тест нестабильным и труднопредсказуемым.

# Нет разделения ответственности 
(критичность: низкая) Функция u отвечает за много разных задач (получение изображений, создание папок, загрузка файлов), что нарушает принцип единственной ответственности.


# Вот основные изменения, внесенные в код:

Обработка ошибок HTTP-запросов и исключений: Добавила проверки статуса ответа и выбрасывание исключений для повышения надежности.
Улучшение читаемости кода: Переименовала функцию u в upload_dog_images, чтобы лучше отражать её назначение.
Хранение токена: Токен теперь передается как параметр конструктора, вместо хардкода.
Избавление от дублирования кода: Упростила функцию get_urls, устранив повторения.
Разделение ответственности: Функция upload_dog_images теперь более сфокусирована на одной задаче.
