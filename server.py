#!/usr/bin/env python3

# Copyright 2023 The chainmetareader Authors. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

import setting
from framework.exceptions import BusinessException
from route import test, user_route, address_route, system_route, tg_bot_route
from utils import lark_notice_util

app = FastAPI()


# 自定义异常处理器
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    dct = {
        'errorCode': exc.code,
        'errorMessage': exc.msg,
        'success': False
    }
    traceback.print_exc()
    return JSONResponse(status_code=200, content=dct)


# 异常处理器2：处理所有异常
async def catch_all_exception_handler(request, exc):
    await lark_notice_util.make_error_notice(traceback.format_exc())
    return JSONResponse(status_code=500, content={"errorMessage": "Internal Server Error"})


@app.middleware("http")
async def log_request(request, call_next):
    print(f"{request.method} {request.url} {request.query_params} {request.session}")
    response = await call_next(request)
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    # do something with body ...
    ret = Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
    try:
        body = json.loads(body, strict=False)
    except Exception:
        pass
    print(body)
    return ret


# 添加 ServerErrorMiddleware，传入全局异常处理器
app.add_middleware(ServerErrorMiddleware, handler=catch_all_exception_handler)
app.add_middleware(SessionMiddleware, secret_key=setting.cookie_key)
app.include_router(test.router, prefix="")
app.include_router(user_route.router, prefix="")
app.include_router(address_route.router, prefix="")
app.include_router(system_route.router, prefix="")

app.include_router(tg_bot_route.router, prefix="")


@app.get("/", response_class=PlainTextResponse)
async def app_check():
    return "ok"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
