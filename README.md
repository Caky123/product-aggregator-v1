# product-aggregator
REST API JSON Python microservice which allows users to browse a product catalog and which automatically updates prices from the offer service.

Online microservice: https://product-aggregator-stable.onrender.com/docs
Attention: onrender free plan -> after 15 minutes of inactivity, the server is shut down and the database is cleared

Local run: docker-compose up --build
Local db check: docker exec -it db_postgres psql -U postgres
