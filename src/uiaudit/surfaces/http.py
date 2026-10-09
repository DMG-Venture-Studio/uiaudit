"""The HTTP surface: one route per operation, generated from the catalog; OpenAPI is committed."""

import json
import sys
from dataclasses import asdict

from uiaudit import boot
from uiaudit.catalog.index import Operation, on_surface
from uiaudit.kernel.envelope import Envelope

ENVELOPE_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": ["ok", "version"],
    "properties": {
        "ok": {"type": "boolean"},
        "data": {"type": "object"},
        "error": {"type": ["string", "null"]},
        "next_step": {"type": ["string", "null"]},
        "version": {"type": "integer"},
    },
}


def route(operation: Operation) -> str:
    """The path of one operation: `POST /<noun>/<verb>`."""
    return "/" + operation.name.replace(".", "/")


def listing() -> list[str]:
    """The routes this surface exposes, one per operation in the catalog."""
    return [route(operation) for operation in on_surface("http")]


def _path_item(operation: Operation) -> dict[str, object]:
    """One route's OpenAPI entry: the operation's name, summary, effect and grant, and the envelope back."""
    return {
        "post": {
            "operationId": operation.name,
            "summary": operation.summary,
            "x-effect": operation.effect,
            "x-grant": operation.grant,
            "responses": {
                "200": {
                    "description": "The envelope: data, or the error and the next step.",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Envelope"}}},
                }
            },
        }
    }


def openapi() -> dict[str, object]:
    """The OpenAPI 3.1 document for every operation on this surface, built from the catalog."""
    return {
        "openapi": "3.1.0",
        "info": {"title": "uiaudit", "version": "1"},
        "paths": {route(operation): _path_item(operation) for operation in on_surface("http")},
        "components": {"schemas": {"Envelope": ENVELOPE_SCHEMA}},
    }


def main(argv: list[str] | None = None) -> int:
    """Print what this surface exposes as an envelope; the transport itself is built per slice."""
    boot.build()
    arguments = sys.argv[1:] if argv is None else argv
    print(json.dumps(asdict(Envelope(ok=True, data={"routes": listing(), "arguments": arguments}))))
    return 0
