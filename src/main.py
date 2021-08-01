from aiohttp import ClientSession
import asyncio
import pathlib

async def fetch(url, session, year):
	async with session.get(url) as response:
		html_body = await response.read()
		return {'Body': html_body, 'Year': year}


async def fetch_with_sem(url, session, year, sem):
	async with sem:
		return await fetch(url, session, year)

async def main(start_year=2020, years_ago=40):	
	tasks = []
	sem = asyncio.Semaphore(10)
	async with ClientSession() as session:
		for i in range(0, years_ago):
			year = start_year - i
			url = f'https://www.boxofficemojo.com/year/{year}/'
			print(f'Year: {year}')
			tasks.append(
				asyncio.create_task(
					fetch_with_sem(url, session, year, sem)))
		page_content = await  asyncio.gather(*tasks)
		return page_content

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
results = asyncio.run(main())

file_name = 'Results'
output_dir = pathlib.Path().resolve() / file_name
output_dir.mkdir(parents=True, exist_ok=True)

for result in results:
	current_year = result.get('Year')
	html_data = result.get('Body')

	output_file = output_dir / f'{current_year}.html' 
	output_file.write_text(html_data.decode())