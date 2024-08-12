import ast
import asyncio
import platform
import json
import sys
from typing import Literal
from urllib.parse import urlencode

import pygame


JS_CODE = """
async function makeRequest() {
  const fetch_args = {
    method: <|REQUEST_TYPE|>, // <|ARG|> format used for Python string.replace() 
    headers: <|HEADERS|>
    };

  const response = await fetch(<|URL|>, fetch_args);

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

async function callMakeRequest() {
  try {
    const data = await makeRequest();
    window.response = JSON.stringify(data);
    //console.log('Data:', data);
  } catch (error) {
    console.error('Error:', error);
  }
}

callMakeRequest()
"""


class RequestHandler:
    def __init__(self):
        self._is_web: bool = sys.platform in ("emscripten", "wasi")
        self._js_code: str = JS_CODE
        self._request_task: asyncio.Task = None
        if self._is_web:
            self._window = platform.window
        else:
            import httpx

            self._httpx_client = httpx.AsyncClient()

    async def _make_request(
        self,
        request_type: Literal["POST", "GET"],
        url: str,
        headers: dict,
        params: dict,
        body: dict | None,
    ):
        if self._is_web:
            self._window.eval(
                self._js_code.replace("<|URL|>", f"'{url}'")
                .replace("<|REQUEST_TYPE|>", f'"{request_type}"')
                .replace("<|HEADERS|>", json.dumps(headers))
                .replace("<|BODY|>", json.dumps(body) if body else "null")
            )
        else:
            kwargs = {
                "method": request_type,
                "url": url,
                "headers": headers,
                "params": params,
            }
            if body:
                kwargs["json"] = body

            try:
                response = await self._httpx_client.request(**kwargs)
                self._httpx_response = response.json()
            except Exception as e:
                self._httpx_response = {"error": str(e)}

    def response(self) -> dict:
        if self._request_task and self._request_task.done():
            if self._is_web:
                if response := self._window.response:
                    return response
                    return json.dumps(ast.literal_eval(str(response)), indent=4)
            else:
                return self._httpx_response

    async def post(
        self, url: str, headers: dict = {''}, params: dict = {''}, body: dict = None
    ):
        self._request_task = asyncio.create_task(
            self._make_request("POST", url, headers, params, body)
        )

    async def get(self, url: str, headers: dict = {}, params: dict = {}):
        self._request_task = asyncio.create_task(
            self._make_request("GET", url, headers, params, None)
        )
