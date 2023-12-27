import typing

import httpx
import pydantic
from shortuuid import decode

from faqmy_backend.conf import settings


class Document(pydantic.BaseModel):
    id: str
    name: str | None = None
    content: str


class BotSDK:
    def __init__(self, index_name: str):
        self.index_name = index_name
        self._client = httpx.AsyncClient(timeout=60)

    @property
    def upload_url(self) -> str:
        return self.index_url_prefix + "/upload"

    @property
    def scrape_url(self) -> str:
        return self.url_prefix + "/scan"

    @property
    def index_uuid(self) -> str:
        return "st_" + str(decode(self.index_name.removeprefix("st_")))

    @property
    def url_prefix(self) -> str:
        return f"{self.index_url_prefix}/documents"

    @property
    def index_url_prefix(self) -> str:
        return f"{settings.bot.url.rstrip('/')}/i/{self.index_uuid}"

    async def make_query(
        self, method: str, suffix: str = "", params: dict | None = None
    ) -> dict:
        async with httpx.AsyncClient(timeout=60) as client:
            url = self.url_prefix + suffix
            kwargs = {}
            if params:
                kwargs.update(json=params)
            resp = await getattr(client, method.lower())(url, **kwargs)
            return resp.json()

    async def post_json(
        self, url: str | None = None, params: dict[str, str] | None = None
    ) -> dict | str:
        return await self.make_query("post", params=params)

    async def ask(self, question: str) -> str:
        return str(
            await self.make_query(
                "post", "/ask", params={"question": question}
            )
        )

    async def scan(self, url: str) -> list[Document]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.scrape_url, json={"url": url})
            return self.parse_cards(resp.json())

    async def upload(self, uploaded_file) -> list[Document]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url=self.upload_url,
                files={
                    "file": (
                        uploaded_file.filename,
                        await uploaded_file.read(),
                        uploaded_file.content_type,
                    )
                },
            )
            return self.parse_cards(resp.json())

    def parse_cards(self, list_of_docs) -> list[Document]:
        return [
            Document(id=row["id"], name=row["name"], content=row["content"])
            for row in list_of_docs
        ]

    async def create_document(self, name: str, content: str) -> str:
        return (
            await self.post_json(params={"name": name, "content": content})
        )["id"]

    async def delete_document(self, doc_id: str):
        return await self.make_query(
            "get", suffix="/" + str(doc_id) + "/delete"
        )

    async def get_document(self, doc_id: str):
        return await self.make_query("get", suffix="/" + str(doc_id))
