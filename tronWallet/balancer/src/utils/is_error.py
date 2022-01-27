from aiofiles import open as async_open
import os
import uuid
from config import NOT_SEND

async def is_error(value: dict):
    new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
    async with async_open(new_not_send_file, 'w') as file:
        # Write all the verified data to a json file, and do not praise the work
        await file.write(str(value))