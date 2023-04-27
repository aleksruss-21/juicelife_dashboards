from telegram_bot import bot, aleks_bot


async def telegram_daily(mg: list, tg_id: int) -> None:
    """Send telegram daily"""
    if mg[0] == "Invalid_Goal":
        await bot.send_message(
            tg_id,
            "⚠️ Введен неверный ID цели. Пожалуйста, удалите аккаунт и добавьте заново с верным ID цели (/start).",
            parse_mode="HTML",
        )
    elif mg[0] == "Error":
        await bot.send_message(tg_id, "⚠️ Произошла непредвиденная ошибка. ")
    else:
        for message in mg:
            await bot.send_message(tg_id, message, parse_mode="HTML")

    await aleks_bot.send_message(
        90785234,
        f"""
    <b>Juice.Direct | {tg_id} отправлено!</b>""",
        parse_mode="HTML",
    )
    session = await bot.get_session()
    session_tg = await aleks_bot.get_session()
    await session.close()
    await session_tg.close()
