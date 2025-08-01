---
title: Link Filter Examples
author: Brian Lee
id: link-filters
citation: link filters
---

Press provides custom Jinja filters for formatting links. Each filter accepts a metadata dictionary with at least `citation` and `url`.

## linktitle
{{"quickstart"|linktitle}}

## linkcap
{{"quickstart"|linkcap}}

## linkicon
{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | linkicon }}

## link_icon_title
{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | link_icon_title }}

## link
{{"quickstart"|link}}
