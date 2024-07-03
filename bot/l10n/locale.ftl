personal-info =
    💎<b>Скидка:  {$discountPercentage}%
    🎁Бонусы:  {$bonusPoints} Rise coins
    🖇Реф. ссылка:</b> <code>{$link}</code>
    ❤️‍🔥<b>Спасибо что вы с нами!</b>❤️‍🔥

strategy-choose = 
    Вы выбрали - <b>{$name}</b>.
    Пожалуйста, введите количество аккаунтов...

strategy-accounts = 
    Вы ввели количество аккаунтов - <b>{$accounts}</b> шт.🧾
    Пожалуйста, введите количество недель...

strategy-result =
    <blockquote>Вы выбрали - <b>{$name}</b>
    ━━━━━━━━━━━━━━━━━━━━━━
    { $weeks ->
        [one] Вы инвестируете - <b>{$weeks} неделю </b>〽️
        [few] Вы инвестируете - <b>{$weeks} недели</b>〽️
        [many] Вы инвестируете - <b>{$weeks} недель</b>〽️
        *[other] Вы инвестируете - <b>{$weeks} недель</b>〽️
    }
    ━━━━━━━━━━━━━━━━━━━━━━
    { $price -> 
        [one] Средняя цена дропа - <b>{$price} рубль</b>❗️
        [few] Средняя цена дропа - <b>{$price} рубля</b>❗️
        [many] Средняя цена дропа - <b>{$price} рублей</b>❗️
        *[other] Средняя цена дропа - <b>{$price} рубля</b>❗️
    }
    ━━━━━━━━━━━━━━━━━━━━━━
    { $account_price -> 
        [one] Цена аккаунта - <b>{$account_price} рубль </b>▫️
        [few] Цена аккаунта - <b>{$account_price} рубля</b>▫️
        [many] Цена аккаунта - <b>{$account_price} рублей</b>▫️
        *[other] Цена аккаунта - <b>{$account_price} рубля</b>▫️
    }
    ━━━━━━━━━━━━━━━━━━━━━━
    Количество аккаунтов - <b> {$accounts_profit} шт.   (  +  {$accounts_count}) </b>🧾
    ━━━━━━━━━━━━━━━━━━━━━━
    { $profit -> 
        [one] Отложенная прибыль - <b>{$profit} рубль </b>💎
        [few] Отложенная прибыль - <b>{$profit} рубля</b>💎
        [many] Отложенная прибыль - <b>{$profit} рублей</b>💎
        *[other] Отложенная прибыль - <b>{$profit} рублей</b>💎
    }</blockquote>

product-quantity =
    <blockquote>🔸Всего доступно - <b>{$quantity}</b> шт🔸
    ❗️Введите не меньше - <b>{$min}</b> шт❗️</blockquote>

product-info =
    <blockquote>
    Вы выбрали - <b>{$name}</b>
    Количество - <b>{$quantity}</b> шт🧾
    { $bonus ->
        [one] Вы используете - <b>{$bonus} бонус</b>🎁
        { "" }
        [few] Вы используете - <b>{$bonus} бонуса</b>🎁
        { "" }
        [many] Вы используете - <b>{$bonus} бонусов</b>🎁
        { "" }
        *[None]   { "" }
    }
    Нажмите <b>"🛍Оплатить🛍"</b> для продолжения
    </blockquote>

general-accounts-info =
    <code><b>🔰Общая статистика🔰</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего аккаунтов: <b>{$accounts}</b>🧾
    Всего забанено: <b>{$total_bans}</b>⛔️
    VAC баны: <b>{$total_vac}</b>🚫
    Community баны: <b>{$total_community}</b>🔕
    Game баны: <b>{$total_game_ban}</b>🔇
    📆Банов за последние 7 дней: <b>{$bans_in_last_week}</b>📆

    <b>🔰Общая статистика инвентарей🔰</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔫Всего предметов: <b>{$items}</b>🔫
    📦Всего кейсов: <b>{$cases}</b>📦
    💰Общая цена: <b>{$prices} рублей</b>💰</code>

personal-accounts-info =
    <code><b>🔰Личная статистика🔰</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего аккаунтов: <b>{$accounts}</b>🧾
    Всего забанено: <b>{$total_bans}</b>⛔️
    VAC баны: <b>{$total_vac}</b>🚫
    Community баны: <b>{$total_community}</b>🔕
    Game баны: <b>{$total_game_ban}</b>🔇
    📆Банов за последние 7 дней: <b>{$bans_in_last_week}</b>📆

    <b>🔰Личная статистика инвентарей🔰</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔫Всего предметов: <b>{$items}</b>🔫
    📦Всего кейсов: <b>{$cases}</b>📦
    💰Общая цена: <b>{$prices} рублей</b>💰</code>

error-quantity-add-accounts = 
    { $accounts_limit -> 
        [one] Вы можете добавить не более <b>{$accounts_limit} аккаунт</b>🧾
        [few] Вы можете добавить не более <b>{$accounts_limit} аккаунта</b>🧾
        [many] Вы можете добавить не более <b>{$accounts_limit} аккаунтов</b>🧾
        *[other] Вы можете добавить не более <b>{$accounts_limit} аккаунта</b>🧾
    }

success_add_accounts =
    { $accounts -> 
        [one] Добавлен  <b>{$accounts} аккаунт</b>🧾
        [few] Добавлено <b>{$accounts} аккаунта</b>🧾
        [many] Добавлено <b>{$accounts} аккаунтов</b>🧾
        *[other] Добавлено <b>{$accounts} аккаунта</b>🧾
    }

get-accounts-dump = 
    ваши аккаунты
    ❗️при нажатии кнопки <b>назад</b> файл удалится❗️

error-accounts-dump = 
    ❗️<b>ошибка</b> при нажатие на кнопку❗️

remove-accounts-info = 
    Отправьте файл с аккаунтами которые нужно удалить...

error-not-steam_ids_dump = 
    Отправьте файл содержащий 
    <b>steamid или ссылку на профиль/b>

success-remove-accounts =
    { $length_accounts -> 
        [one] Удалено  <b>{$length_accounts} аккаунт</b>🧾
        [few] Удалено <b>{$length_accounts} аккаунта</b>🧾
        [many] Удалено <b>{$length_accounts} аккаунтов</b>🧾
        *[other] Удалено <b>{$length_accounts} аккаунта</b>🧾
    }

error-process-accounts-file =
    ❗️<b>Ошибка при обработке</b>❗️

error-file-found =
    <b>❗️Файл или текст не найден❗️</b>

process-accounts-file =
    💭Идет обработка...💭

add-accounts-info =
    Отправьте файл или сообщение с аккаунтами🧾
    <b>текст не длинее 78 строк ...</b>

personal-accounts-empty =
    У вас нет аккаунтов
    Нажмите кнопку <b>📩добавить аккаунты📩</b>

bonus-quantity-max = 
    Введите количество не больше {$bonus}

error-user-havent-bonus = 
    ❗️У вас <b>нет</b> бонусов для использования❗️

payment-product = 
    тут будет оплата продукта какая то инфа
    Я пидорас (с) Лешка Колеватов
    я знаю, лешка 
    
    Минеев. Подписаться.

