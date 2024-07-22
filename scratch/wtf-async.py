
# SuperFastPython.com
# example of running a blocking function call in asyncio in a new thread with return value
import time
import asyncio

class RestResponse:
    _wtf: int

    def __init__(self, wtf: int):
        self._wtf = wtf

class RestRequest:

    def call_endpoint(self, number: int, sync: bool) -> RestResponse:
        if sync:
            return self._send_request(number)
        else:
            return self._send_request_async(number)

    def _send_request(self, number: int) -> RestResponse:
        return RestResponse(number)

    async def _send_request(self, number: int) -> RestResponse:
        return RestResponse(number)

    def _execute(self, number: int) -> RestResponse:
        return RestResponse(number)

# blocking function
def blocking_task() -> RestResponse:
    # report a message
    print('task is running')
    # block
    time.sleep(2)
    # report a message
    print('task is done')
    # return a value
    return RestResponse(100)

# main coroutine
async def main() -> None:
    # create a coroutine for the blocking function call
    coro = asyncio.to_thread(blocking_task)
    # execute the call in a new thread and await the result
    result = await coro
    print(type(result))
    # report the result
    print(f'Got: {result}')

# start the asyncio program
asyncio.run(main())
