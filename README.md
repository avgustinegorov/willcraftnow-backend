# willcraftnow-backend

## Development Environment

> Please use python 3.6. The rest of the versions are not compatible.

1. Copy `.env.example` in `WillCraft/settings` directory, name it `.env` and place it in the same directory.

2. run `python manage.py migrate`.

3. run `python manage.py runscript deployment`.

4. run `python manage.py runserver`.

5. Start the frontend.

> IMPORTANT: Please note that the frontend will take an application `client_id` from the backend and use that for authentication. If you reset the database, please restart the development server on the frontend after.

> Since `client_id` is different everytime you reset the database, and the frontend is a static site generator which only calls the backend to save the `client_id` on generation, a reset of the frontend is required everytime you reset the backend or change the db.

# Data structure explaination

```
User
├── Assets (5/6 Kinds of assets) 1, 2, 3
    ├── Bank Accounts
    ├── Investment Accounts
    ├── Real Estate
    ├── Insurance
    ├── Company Shares
    ├── Residual
├── Entities (Two kinds of Entities) 4, 5
    ├── Charity
    ├── Person
├── Order (Will, LPA, and Schedule of Asset)
    ├── WILL
        ├── Allocation
        ├── Appointments
            - via entity_roles, only People should be allowed
        ├── Last Rites
        ├── Prayer Instructions
    ├── LPA
        ├── DoneePowers
            - via entity_roles, only People should be allowed
        ├── Restrictions on Donee Powers
    ├── SCHEDULE OF ASSETS
        ├── Assets
    ├── Invoice
```
