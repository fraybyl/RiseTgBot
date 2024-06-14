personal-info =
    <b>Скидка:  {$discountPercentage}%
    Бонусы:  {$bonusPoints} Rise coins
    Реф. ссылка:</b> <code>{$link}</code>
    <b>Спасибо что вы с нами!</b>

strategy-choose = 
    Вы выбрали - <b>{$name}</b>.
    Пожалуйста, введите количество аккаунтов...

strategy-accounts = 
    Вы ввели количество аккаунтов - <b>{$accounts}</b>.
    Пожалуйста, введите количество недель...

strategy-result = 
    <blockquote>Вы выбрали - <b>{$name}</b>.
    Вы инвестируете - <b>{$weeks} недель </b>.
    Средняя цена дропа - <b>{$price} рублей</b>.
    Цена аккаунта - <b>{$account_price} рублей </b>.
    Количество аккаунтов - <b>{$accounts}</b>.
    Сохраненная прибыль - <b>{$profit}</b>.</blockquote>

product-quantity = 
    <blockquote>Всего доступно - <b>{$quantity}</b> штук.
    Введите не меньше - <b>{$min}</b> штук.</blockquote>

product-info = 
    <blockquote>
    Вы выбрали - <b>{$name}</b>
    Количество - <b>{$quantity}</b>
    { $bonus ->
        [one] Вы используете - <b>{$bonus} бонус</b>.
        { "" }
        [few] Вы используете - <b>{$bonus} бонуса</b>.
        { "" }
        [many] Вы используете - <b>{$bonus} бонусов</b>.
        { "" }
        *[None]   { "" }
    }
    Нажмите <b>"Оплатить"</b> для продолжение.
    </blockquote>

general-accounts-info = 
    <blockquote>
    Всего аккаунтов - <b>{$accounts}</b>
    Всего забанено - <b>{$total_bans}</b>
    VAC баны - <b>{$total_vac}</b>
    Community баны <b>{$total_community}</b>
    Всего банов за последние 7 дней <b>{$bans_in_last_week}</b>