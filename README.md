# IMP_Flask

IMP_Flask is meant to be the next and hopefully somewhat final successor of [Madmin](https://github.com/davidv1992/madmin). 
Its primary purpose is to manage inventory, but it also includes bindings for the Conscribo XML-API, a point-of-sale system and
support for simple ingredient-to-product processes.


The projects structure is derived from the [Flask-Large-Application-Example](https://github.com/Robpol86/Flask-Large-Application-Example).

## Features

* Fast transaction input.
* As-Correct-As-Possible inventory pricing.
* Price modifiers.
* Conscribo integration.
* Point-of-sale management.
* Missing/Extra inventory tracking and autocorrection.
* Ingredient-to-product processes.
* Tests are written for [pytest](http://pytest.org/).
* Any unhandled exceptions raised in views are emailed to you from your production instance. The email
  is styled to look similar to the exceptions shown in development environments, but without the interactive console.
* Message flashing is "powered by" [Bootstrap Growl](https://github.com/mouse0270/bootstrap-growl). 


## Directory Structure

```GAP
├─ imp_flask/         # All application code in this directory.
│  ├─ core/             # Shared/misc code goes in here as packages or modules.
│  ├─ models/
│  │  ├─ helpers.py     # Helpers related to database processes.
│  │  ├─ imps.py        # Holds several tables related to IMP objects.
│  │  └─ meta.py        # Holds several tables required for users etc.
│  │
│  ├─ static/
│  │  ├─ favicon.ico
│  │  ├─ js/
│  │  └─ css/
│  │
│  ├─ tasks/          # Input data processes.
│  │
│  ├─ templates/      # Base templates used/included throughout the app.
│  │  ├─ 404.html
│  │  └─ base.html
│  │
│  ├─ validators/          # json structures for apicalls
│  │
│  ├─ views/
│  │  ├─ view1/
│  │  │  ├─ templates/              # Templates only used by view1.
│  │  │  │  └─ view1_section1.html  # Naming convention: package_module.html
│  │  │  ├─ section1.py             # Each view module has its own blueprint.
│  │  │  └─ section2.py
│  │  │
│  │  ├─ view2/
│  │  └─ view3/
│  │
│  ├─ application.py  # Flask create_app() factory.
│  ├─ blueprints.py   # Define Flask blueprints and their URLs.
│  ├─ config.py       # All configs for Flask, Prod, Dev, etc.
│  ├─ extensions.py   # Instantiate SQLAlchemy, etc. Importable.
│  └─ middleware.py   # Error handlers, template filters, other misc code.
│
├─ tests/                   # Tests are structured similar to the application.
│  ├─ core/
│  │  └─ test_something.py
│  ├─ tasks/
│  └─ conftest.py
│
└─ manage.py          # Main entry-point into the Flask application.
```

## Design Choices

### Inventory

You will notice that a 'productbucket' is almost the same as a 'transaction'. This is because in some abstract view, inventory in a transaction is basically
just inventory of someone else. A selling and buying transaction is the same thing, but with a minus sign. To avoid confusion, a negative amount is always a loss
and a positive amount is always a gain.
