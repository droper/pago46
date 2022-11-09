# pago46 Challenge

## Endpoints

### settleupp

Endpoint the returns a list of user objects with a GET that receives one parameter:

* `users`: a comma separated list of usernames.

The endpoint will return the user objects of users in the parameter..

If called without a payload, it will give back all the users objects.

With no names: `curl --location --request GET 'http://127.0.0.1:8000/settleup'`

With names: `curl --location --request GET 'http://127.0.0.1:8000/settleup?users=<user>,<user>'`

### add

Endpoint that creates a new user, the POST receives a parameter:

* `user`: The name of the user to create.

If called without a payload or with an existing user, it will give a None response.

Example: `curl --location --request POST 'http://127.0.0.1:8000/add' --form 'user="pipo"'`

### iou

Endpoint to create a new debt, is a POST request that receives four parameters:

* `lender`: Name of the lender user
* `borrower`: Name of the borrower user
* `amount`: Amount
* `expiration`: Expiration date

Example:

`curl --location --request POST 'http://127.0.0.1:8000/iou' \
--form 'lender="pipo"' \
--form 'borrower="pepe"' \
--form 'amount="20"' \
--form 'expiration="2022-11-22"'`

## Architecture and scaling

A proposed architecture to scale the app will need to comply with the following criteria:

* Availability
* Performance
* Security

The architecture would be:

* An API Gateway that redirects to the microservice and can authenticate the requests. 
* A microservice with the API code.
* A service for the GraphQL (like AWS AppSync) that redirects to the Microservice and the database.
* A cloud managed database with automatic backups.


