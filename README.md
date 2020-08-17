# Labs23-Test-API
This is a test API that takes a city id as input, takes historical housing data for that given city from a MongoDB of over 20,000 cities to train a fbprophet forecasting model, forecasts housing prices in the city for 2 years into the future, and populates the database with the forecast.

This API was built as a proof of concept for the Citrics.io team. This functionality was integrated into the existing Citrics API. The code for that can be viewed [here](https://github.com/steve122192/city-data-comparison-ds)