# Top AUSOPEN Girls

This is a sample project that fetches data from Twitter API every 60 seconds for each AusOpen Women Top Seeds predefined in a JSON file and then exposes the result in a WebService.

It uses Apache Kafka as streaming platform and Python Faust as Stream Processing library.


## Run this project

To run this project, create a virtual environment from the Pipenv file located at the root and activate it.

You need to have a Kafka cluster running in your machine, on the default port.

Then, you can just simply run: 'faust -A players_app worker -l info' and after the first sync, consume the endpoint at 'http://localhost:6066/players/{twitter_username}"

## Requirements
Pipenv installed in your system.
An Apache Kafka installation.
Twitter API credentials.

All dependencies are found in the Pipenv file.
