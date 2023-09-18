# Environment:

## How to create:
```shell
copy ./docker/envs/env ./docker/envs/.env
copy ./docker/envs/servicesenv ./docker/envs/.services.env
```
-------
### .services.env
> `POSTGRES_USER` - Username from the database
> 
> `POSTGRES_PASSWORD` - Password from the database
> 
> `POSTGRES_DB` - Main database name

-------
### .env
> `NETWORK` - `COMMON` or `TEST` (Optional)
> 
> `DATABASE_URL` - The path to the database, without the name of the database (`postgresql://u:p@h:5436`)
> 
> `RABBITMQ_URL` - The path to RabbitMQ (`amqp://u:p@h:5672`)
> 
> `REDIS_URL` - The path to Redis, without db index (`redis://u:p@h:6379`)
> 
> `EXCHANGERATE_API_KEY` - Key from `https://app.exchangerate-api.com/`
