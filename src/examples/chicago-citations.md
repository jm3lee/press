---
title: Chicago Citation Examples
author: Brian Lee
id: chicago-citations
citation: chicago citations
---

Demonstrates Chicago-style citations using the `cite` global and the `link` filter.

## cite

Single source:

{{ cite("hull") }}

Multiple sources:

{{ cite("hull", "doe") }}

## link filter

{{ {"citation": {"author": "hull", "year": 2016, "page": 307}, "url": "/hull"} | link }}
