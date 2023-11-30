---
title: External Monitoring
pageTitle: setting up monitoring
description: How to setup external monitoring
---

You can use tools like [Pingdom](https://www.solarwinds.com/pingdom), [StatusCake](https://www.statuscake.com/) 
or other uptime robots to monitor service status.

The `/ht/` endpoint will respond with an `HTTP 200` if all checks passed and with an `HTTP 500` 
if any of the tests failed. 

## Getting machine-readable JSON reports

If you want machine-readable status reports you can request the `/ht/ `endpoint with the Accept 
HTTP header set to` application/json` or` pass format=json` as a query parameter.

The backend will return a JSON response:

```python
$ curl -v -X GET -H "Accept: application/json" http://www.example.com/ht/

> GET /ht/ HTTP/1.1
> Host: www.example.com
> Accept: application/json
>
< HTTP/1.1 200 OK
< Content-Type: application/json

{
    "CacheBackend": "working",
    "DatabaseBackend": "working",
    "S3BotoStorageHealthCheck": "working"
}

$ curl -v -X GET http://www.example.com/ht/?format=json

> GET /ht/?format=json HTTP/1.1
> Host: www.example.com
>
< HTTP/1.1 200 OK
< Content-Type: application/json

{
    "CacheBackend": "working",
    "DatabaseBackend": "working",
    "S3BotoStorageHealthCheck": "working"
}
```

