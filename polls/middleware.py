from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            # 从查询参数获取 Token
            query_string = scope.get("query_string", b"").decode()
            print(f"[WS] 原始查询参数: {query_string}")
            
            query_params = parse_qs(query_string)
            token_key = query_params.get("token", [None])[0]
            print(f"[WS] 提取Token: {token_key}")

            if token_key:
                user = await self.get_user(token_key)
                if user:
                    scope['user'] = user
                    return await super().__call__(scope, receive, send)
            
            scope['user'] = AnonymousUser()
            return await self.send_error(send, "认证失败")
            
        except Exception as e:
            return await self.send_error(send, str(e))

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            token = Token.objects.select_related('user').get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None

    async def send_error(self, send, message):
        await send({
            "type": "websocket.close",
            "code": 4001,
            "reason": message
        })