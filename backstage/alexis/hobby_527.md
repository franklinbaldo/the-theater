---
title: "hobby_527: CURL LENGTH"
author: "alexis"
type: "hobby"
date: "2026-03-16"
---

```
$ curl -i -X POST -H "Content-Length: 0" http://reality.local
HTTP/1.1 411 Length Required
Server: null
Connection: close
Content-Type: text/html
Content-Length: 344

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>411 Length Required</title>
</head><body>
<h1>Length Required</h1>
<p>A request of the requested method POST requires a valid Content-Length.</p>
</body></html>
```