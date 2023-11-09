# Architecture

As I don't know if anyone will ever read this, I'll keep this very high level for now, where I feel it's necessary.

# Directories

`lute` is the app module.  Each subfolder under it is either a blueprint or a utility/service package:

* `backup`: the `/backup` routes and service
* `bing`: the `/bing` routes and service
... etc

Special things:

* `db`: database setup and migrations, and demo data management
* `dev_api`: special/dangerous routes used during testing only (not loaded if app ENV = prod)
* `models`: the Sqlalchemy models
* `parse`: parsing
* `utils`: utils

## About `models`

The classes in `lute.models` are Sqlalchemy classes.  Most of these have simple methods for things like finding, loading, etc.

Some DB models (e.g. `lute.models.language.Language`) are used throughout the application, as they're pretty much just data classes with little functionality.

### Term and Book domain models

There are two more useful domain models:

* `lute.term.model.Term`
* `lute.book.model.Book`

These are used more frequently in the code as they provide useful domain-level abstractions.  They both have corresponding `lute.X.model.Repository` objects that translate these models to and from the DB/Sqlalchemy models.

### Datatables

Lute shows some data as tabular data in datatables, which just use Sqlalchemy to query the db directly without models.  The `lute.utils.data_tables` module helps with that.

# Fifty-thousand-foot overview of architecture

Except for parsing and rendering, the model for Lute is pretty simple:

* a route in a blueprint's `routes` module receives an incoming requests
* the route delegates to some kind of `service` module in the blueprint
* the `service` deals with either DB or domain models as needed, and commits to the `lute.db` via usual Flask-Sqlalchemy methods.

## The models

* The user studies `lute.models.language.Language`
* The user creates `lute.book.model.Book` (domain object), which is saved as a `lute.models.Book` db object.  A `DbBook` has one or more `lute.models.book.Text` objects, which are the pages in the `Book`.
* The user reads the text in the `lute.read` routes, and creates `lute.term.model.Term` objects, which are saved in the database as `lute.models.term.Term` objects.

# App setup

* The main entry point is `lute.main` which initializes the db and app.
* `lute.main` calls `lute.config.app_config.AppConfig` to get the configuration from the `lute/config/config.yml`.  The config.yml file is pre-written for Docker, or the prod example is used.  `AppConfig` is used in several places in the code to re-read the config file.  Among other things, the config gives the name of the folder where the user's data will be stored; this is suppliedy by the library `PlatformDirs` if it's not configured.
* `lute.main` calls `lute.app_setup`, the app factory.  `app_setup`:
  * calls `lute.db.setup.main` to run db migrations and backups as needed.  Migrations are handled by `lute.db.setup.migrator`, using files in `lute/db/schema/`.
  * loads all of the blueprints into the app.
* `lute.main` hands the configured app off to waitress.

# Parsing and Rendering

* Parsers are defined in `lute.parse`, with a base `AbstractParser` subclassed by other parsers.  The parsers are loaded into a `lute.parse.registry` which is consulted at runtime to determine which parsers are supported in the current environment.
* Any time a page is requested or a new `Term` is created, the appropriate parser is found from the `parse.registry`.  The parser uses the `Language` to get a list of `ParsedTokens`.
* If rendering, the list of `ParsedTokens` is given to the `lute.read.render.renderable_calculator` to determine which tokens, and which parts of tokens, should actually be rendered.
* When rendered, the `lute/static/js/lute.js` file adds javascript event handlers for each of the word elements in the rendered HTML.  These handlers get/post back to various bluescript routes.