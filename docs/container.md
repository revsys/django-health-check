# Container (Docker/Podman)

Django HealthCheck can be integrated into various container orchestration systems by defining health checks that utilize the `manage.py health_check` command. Below are examples for Containerfile/Dockerfile, Docker Compose, and Kubernetes.

> [!TIP]
> Utilizing the health check command is usually superior to simple HTTP checks, as Django's `ALLOWED_HOSTS` settings and other middleware may interfere with HTTP-based health checks.

## Subsets

You may want to limit the checks performed by the health check command to a subset of all available checks.
E.G. you might want to skip checks that are monitoring external services like databases, caches, or task queues.

You can define subsets in your Django settings:

```python
# settings.py
HEALTH_CHECK = {
    "SUBSETS": {
        "container": [
            "MemoryUsage",
            "DiskUsage",
        ],
    }
}
```

... and then run the health check command with the `--subset` option:

```shell
python manage.py health_check --subset=container
```

## Configuration Examples

### Container Image

```Dockerfile
# Containerfile / Dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python manage.py health_check --subset=container || exit 1
```

### Compose

```yaml
# compose.yml / docker-compose.yml
services:
  web:
    # ... your service definition ...
    healthcheck:
      test: ["CMD", "python", "manage.py", "health_check", "--subset", "container"]
      interval: 60s
      timeout: 10s
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-django-app
spec:
  template:
    spec:
      containers:
        - name: django-container
          image: my-django-image:latest
          livenessProbe:
            exec:
                command:
                - python
                - manage.py
                - health_check
            periodSeconds: 60
            timeoutSeconds: 10
```
