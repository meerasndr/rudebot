# stress_test.py
import asyncio, aiohttp, time, json
URL = "http://localhost:8000/chat"
TOTAL = 40
SPACING = 0.2  # seconds between launches

payload = {"messages": [{"role":"user","content":"ping"}]}

async def hit(session, idx):
    t0 = time.time()
    async with session.post(URL, json=payload) as r:
        code = r.status
        txt = await r.text()
        return (idx, code, time.time()-t0, txt)

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(TOTAL):
            tasks.append(asyncio.create_task(hit(session, i)))
            await asyncio.sleep(SPACING)
        results = await asyncio.gather(*tasks)
    ok = sum(1 for _,c,_,_ in results if c==200)
    rl = sum(1 for _,c,_,_ in results if c==429)
    print(f"OK: {ok}, 429: {rl}")
    # show a couple of samples
    for r in results[:5]:
        print(r[:3])

if __name__ == "__main__":
    asyncio.run(main())
