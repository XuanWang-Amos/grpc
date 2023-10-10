import asyncio


class ExampleAwaitable:
    def __await__(self):
        async def result():
            return 42

        return result().__await__()


print(f"{asyncio.iscoroutine(ExampleAwaitable())=}")
print(f"{asyncio.iscoroutine([ExampleAwaitable()])=}")

async def coro_wrapper(awaitable):
    return await awaitable

async def amain():
    await asyncio.wait([asyncio.create_task(coro_wrapper(ExampleAwaitable()))])
    await asyncio.wait([ExampleAwaitable()])
    print("waited!")


asyncio.run(amain())