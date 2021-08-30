# currency-service

## Configuration

Add your environment variables to the docker-compose.yml file:

```yaml
version: '3.2'
services:
    app:
        build: .
        ports:
            - "5000:5000"
        environment:
            PYTHONDONTWRITEBYTECODE: 1
            FLASK_DEBUG: 1
            FREE_CURRENCY_API_BASE_URL: https://freecurrencyapi.net/api
            FREE_CURRENCY_API_API_KEY: xxxxxxx-xxxxxxxx-xxxxxx-xxxxxx 
        volumes:
            - .:/usr/src/app
```