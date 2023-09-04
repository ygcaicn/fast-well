import asyncio
import time
from app.core.auth.deps import get_current_active_superuser, get_current_active_user
from app.core.auth.utils.captcha import get_captcha, verify_captcha
from app.core.auth.utils.contrib import send_new_account_email

r = send_new_account_email(email_to="ygcaicn@gmail.com",
                           username="ygcaicn@gmail.com", password="123456")
print(r)
# async def main():
#     a = time.time()
#     for i in range(1000):
#         _, k = await get_captcha()
#         await verify_captcha(k, k)
#     print(time.time()-a)

# if __name__ == "__main__":
#     asyncio.run(main())
