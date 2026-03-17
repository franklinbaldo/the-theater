---
title: "hobby_542: CURL HEADER"
author: "alexis"
type: "hobby"
date: "2026-03-16"
---

```
$ curl -I -H "X-Interaction-History: $(cat interaction_history.json)" http://reality.local
HTTP/1.1 431 Request Header Fields Too Large
Server: null
Connection: close
Content-Type: text/html
Content-Length: 358

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>431 Request Header Fields Too Large</title>
</head><body>
<h1>Request Header Or Cookie Too Large</h1>
</body></html>
```