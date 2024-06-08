from typing import List
from sqlalchemy import func
from sqlalchemy.future import select
from bot.database.models import async_session, User

async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        
        if not user:
            referred_by = None
            if referral_code:
                try:
                    referrer_id = int(referral_code)  # Преобразуем referral_code в int
                    referrer = await session.scalar(select(User).where(User.telegram_id == referrer_id))
                    if referrer:
                        referred_by = referrer.telegram_id
                    else:
                        print(f"Referral code {referral_code} does not exist")
                except ValueError:
                    print(f"Invalid referral code: {referral_code}")
            
            user = User(telegram_id=telegram_id, username=username, referred_by=referred_by)
            session.add(user)
            await session.commit()
        
        return user