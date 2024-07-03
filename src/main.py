import asyncio
import pathlib

from aiohttp import ClientSession

OUTPUT_FOLDER_NAME = "result"


async def fetch(url: str, session: ClientSession, year: int) -> dict:
    async with session.get(url) as response:
        html_body = await response.read()
        return {"Body": html_body, "Year": year}


async def fetch_with_sem(
    url: str, session: ClientSession, year: int, sem: asyncio.Semaphore
) -> fetch:
    async with sem:
        return await fetch(url, session, year)


async def main(start_year: int = 2021, years_ago: int = 5) -> list:
    tasks = []
    sem = asyncio.Semaphore(10)
    async with ClientSession() as session:
        for i in range(years_ago):
            year = start_year - i
            url = f"https://www.boxofficemojo.com/year/{year}/"
            print(f"Year: {year}")
            tasks.append(
                asyncio.create_task(fetch_with_sem(url=url, session=session, year=year, sem=sem))
            )
        return await asyncio.gather(*tasks)


results = asyncio.run(main())

output_dir = pathlib.Path().resolve() / OUTPUT_FOLDER_NAME
output_dir.mkdir(parents=True, exist_ok=True)

for result in results:
    current_year = result.get("Year")
    html_data = result.get("Body")

    output_file = output_dir / f"{current_year}.html"
    output_file.write_text(html_data.decode())
