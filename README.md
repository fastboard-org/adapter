# Fastboard - Adapter
Microservice for apdating and redirecting requests from Fastboard to external services.

# Installing the project

This project was build with [poetry](https://python-poetry.org/docs/) to manage dependencies.

Having poetry installed, run this command to install the dependencies:

```
poetry install
```

## Dev

To add new dependencies, you can run:

```
poetry add <dependency>
```

**NOTE**: Don't forget to commit all changes to `poetry.lock` and `pyproject.toml`! 

To activate the virtual environment run:

```
poetry shell
```

Then, you can run the app using:

```
python src/main.py
```

If you don't want to set up environment variables in your system, you can create a file with the same format as `.env-example` and run the app with:

```
python src/main.py --env=your-env-file
```

You can exit the virtual environment by simply running:

```
exit
```

To run the formatter:

```
black [Options] path
```

To run the linter:

```
flakeheaven lint path
```

Or, you can run the formatter and linter with:

```
python lint.py
```


## Running locally

In addition to running it directly within poetry's virtual environment you can run the project with Docker:

* Create a `.env` file with the same environment variables as in `.env-example`

* Run `docker build -t fastboard-adapter .`

* Run `docker run -p PORT:PORT --env-file=.env fastboard-adapter`
