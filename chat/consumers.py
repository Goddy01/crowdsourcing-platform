from ably import AblyRealtime
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    ably = AblyRealtime(os.environ.get('ROOT_API_KEY'))
    await ably.connection.once_async('connected')
    print('Connected to Ably')


asyncio.run(main())