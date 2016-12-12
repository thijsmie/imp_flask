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
│  │  ├─ navbar.html
│  │  └─ base.html
│  │
│  ├─ textemplates/          # Templates for latex renderere.
│  │  └─ document.tex
│  │
│  ├─ texstatic/          # Static files for latex renderer
│  │  └─ logo.svg
│  │
│  ├─ validators/          # JSON structures for apicalls
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
│  ├─ middleware.py   # Error handlers, template filters, other misc code.
│  ├─ paths.py        # Importable module to fetch app paths
│  └─ strings.json    # App-wide config of fieldnames in templates (both html and tex)
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

## Latex templating with jinja2

All invoices and other documents are rendered with [jinja2](http://jinja.pocoo.org/) with aggressive input escaping to prevent attacks using, for example, \usepackage{python}. It also allows 
users to include special characters in product names, eventnames and whatever else they want.

## Inventory management implementation choices

### Price Calculation

With IMP the way prices are calculated differs from madmin in a significant way. There is no separate entity for a product and its inventory. That way, there is no way to tell where a product came from once it is in the database
This makes sense in the way that if you have two bottles of cola, they are interchangeable. Of course, there is a sell-by date, but that kind of micromanagement is beyond the scope of this system and happens "on the floor".
It also makes pricing fairer. The price of an amount of a certain product is just the fraction of the total amount times the total value. This means that no rounding errors can get lost in the system and that if you buy
items on offer the price is reduced for all items you have, instead of it being a lottery for the parties who buy from you.

### Modifying Transactions

In madmin transactions were basically immutable. This caused many problems, since mistakes happen ([pebcak](https://en.wiktionary.org/wiki/PEBCAK)). Therefore IMP moves to the other end of the spectrum. A transaction is editable
in an easy way, invoices get resent and changes are pushed to Conscribo with the press of a button.

### Point of Sale

Maintaining everything on your own is a tremendous amount of work. Anything that the system can handle for you is nice. So why not let the people who sell stuff for you enter the sales directly? It keeps a nice backlog of
it so you have control over what goes into the database and what does not.

### Inventory Correction

Even if your documentation is perfect, your numbers are impeccable and your helpers are perfect humans, the total count of inventory you have at when you count it will never match up to what IMP says. Theft, spoiling, losses and
quantum fluctuations will mess it up 100% of the time. Correcting inventory by hand is a chore and can go wrong easily, so IMP does it for you. IMP will also remember previous corrections and will notice when you may have
found some inventory you lost before and will take that into account. Of course, this is also pushed to Conscribo.

### Future Proofing

VAT-based bookkeeping? Weird margins on products? Transport costs? Locked prices? Brewing your own beer? New vending machine? IoT-enabled vending machines? Automatic product orders? You name it.