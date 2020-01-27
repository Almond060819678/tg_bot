from aiohttp import web, ClientSession
import asyncio
import json

from settings import TOKEN_ECHO


class Api(object):
    URL = 'https://api.telegram.org/bot%s/%s'

    def __init__(self, token):
        self._token = token

    async def _request(self, method, message):
        headers = {
            'Content-Type': 'application/json'
        }
        async with ClientSession() as session:
            async with session.post(self.URL % (self._token, method),
                                    data=json.dumps(message),
                                    headers=headers) as resp:
                try:
                    assert resp.status == 200
                except AssertionError:
                    pass

    async def send_message(self, chat_id, text):
        message = {
            'chat_id': chat_id,
            'text': text
        }
        await self._request('sendMessage', message)


class Conversation(Api):
    def __init__(self, token):
        super().__init__(token)

    async def _handler(self, message):
        pass

    async def handler(self, request):
        message = await request.json()
        asyncio.ensure_future(self._handler(message['message']))
        return web.Response(status=200)


class EchoConversation(Conversation):
    def __init__(self, token):
        super().__init__(token)

    async def _handler(self, message):
        await self.send_message(message['chat']['id'],
                                message['text'])


async def init_app():
    echo_bot = EchoConversation(TOKEN_ECHO)
    app = web.Application(middlewares=[])
    app.router.add_post('/api/v1/echo', echo_bot.handler)
    return app


if __name__ == '__main__':
    web.run_app(init_app())
