personal-info =
    💎<b>Скидка:  {$discountPercentage}%
    🎁Бонусы:  {$bonusPoints} Rise coins
    🖇Реф. ссылка:</b> <code>{$link}</code>
    ❤️‍🔥<b>Спасибо что вы с нами!</b>❤️‍🔥

strategy-choose = 
    Вы выбрали - <b>{$name}</b>.
    Пожалуйста, введите количество аккаунтов...

strategy-accounts = 
    Вы ввели количество аккаунтов - <b>{$accounts}</b> шт.
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
    { $accounts_profit ->
      *[one] Количество аккаунтов - <b> {$accounts_profit} шт </b>🧾
    }
    ━━━━━━━━━━━━━━━━━━━━━━
    { $profit -> 
        [one] Отложенная прибыль - <b>{$profit} рубль </b>💎
        [few] Отложенная прибыль - <b>{$profit} рубля</b>💎
        [many] Отложенная прибыль - <b>{$profit} рублей</b>💎
        *[other] Отложенная прибыль - <b>{$profit} рублей</b>💎
    }</blockquote>

product-quantity =
    <blockquote>Всего доступно - <b>{$quantity}</b> шт.
    Введите не меньше - <b>{$min}</b> шт.</blockquote>

product-info =
    <blockquote>
    Вы выбрали - <b>{$name}</b>
    Количество - <b>{$quantity}</b> шт.
    { $bonus ->
        [one] Вы используете - <b>{$bonus} бонус</b>
        { "" }
        [few] Вы используете - <b>{$bonus} бонуса</b>
        { "" }
        [many] Вы используете - <b>{$bonus} бонусов</b>
        { "" }
        *[None]   { "" }
    }
    Нажмите <b>"Оплатить"</b> для продолжения
    </blockquote>

general-accounts-info =
    <code><b>Общая статистика</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего аккаунтов: <b>{$accounts}</b>
    Всего забанено: <b>{$total_bans}</b>
    VAC баны: <b>{$total_vac}</b>
    Community баны: <b>{$total_community}</b>
    Game баны: <b>{$total_game_ban}</b>
    Банов за последние 7 дней: <b>{$bans_in_last_week}</b>

    <b>Общая статистика инвентарей</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего предметов: <b>{$items}</b>
    Всего кейсов: <b>{$cases}</b>
    Общая цена: <b>{$prices} рублей</b></code>

personal-accounts-info =
    <code><b>Личная статистика</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего аккаунтов: <b>{$accounts}</b>
    Всего забанено: <b>{$total_bans}</b>
    VAC баны: <b>{$total_vac}</b>
    Community баны: <b>{$total_community}</b>
    Game баны: <b>{$total_game_ban}</b>
    Банов за последние 7 дней: <b>{$bans_in_last_week}</b>

    <b>Личная статистика инвентарей</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Всего предметов: <b>{$items}</b>
    Всего кейсов: <b>{$cases}</b>
    Общая цена: <b>{$prices} рублей</b></code>

error-quantity-add-accounts = Вы можете добавить не более $accounts_limit аккаунтов

success_add_accounts = Добавлено $accounts аккаунтов

get-accounts-dump = получать аккаунты подпись

error-accounts-dump = ошибка при нажатие на кнопку

remove-accounts-info = Отправьте файл с аккаунтами которые нужно удалить...

error-not-steam_ids_dump = Отправьте файл содержащий steamid/vanity_url/steam_urls

success-remove-accounts = Удалено $length_accounts аккаунтов

error-process-accounts-file = Ошибка при обработке

error-file-found = Файл или текст не найден!

process-accounts-file = Идет обработка...

add-accounts-info = Отправьте файл или сообщение с аккаунтами\nтекст не длинее 78 строк ...

personal-accounts-empty =
    У вас нет аккаунтов.
    Нажмите кнопку добавить аккаунты