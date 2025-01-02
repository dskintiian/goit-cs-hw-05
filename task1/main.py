from aiofile import async_open
from aioshutil import copyfile, SameFileError
import argparse
import asyncio
import os

from aiopath import AsyncPath

async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source-dir', default='src', required=False)
    parser.add_argument('-d', '--dest-dir', default='dst', required=False)

    args = parser.parse_args()

    src = AsyncPath(os.path.abspath(args.source_dir))
    dist = AsyncPath(os.path.abspath(args.dest_dir))

    await read_directory(src, dist)

async def read_directory(src: AsyncPath, dist: AsyncPath):
    try:
        async for item in src.iterdir():
            if await item.is_dir():
                await read_directory(item, dist)
            if await item.is_file():
                await copy_file(item, dist)
    except (FileNotFoundError, PermissionError) as e:
        await log_error(e)

async def copy_file(src: AsyncPath, dist: AsyncPath):
    name, ext = os.path.splitext(src.name)
    if ext == '':
        ext = '_no_extension'

    dist_path = AsyncPath(dist / ext)
    await dist_path.mkdir(exist_ok=True, parents=True)
    try:
        await copyfile(src, dist_path / src.name)
    except (SameFileError, PermissionError) as e:
        await log_error(e)

async def log_error(e):
    async with async_open('.error_log', 'a') as afp:
        await afp.write(str(e) + '\n')

if __name__ == '__main__':
    asyncio.run(main())