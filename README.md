# social network test
One should clone the project and after creating the virtual env, entering it and cd-ing to the projet root install the requirements with

	$ pip install -r requirements.txt
To run tests one should do all the migrations since the tests are functional tests, including going to the DB.

	$ cd social_network
	$ ./manage.py migrate
At this point one should create some environment variables that I use for the api keys and for the secret key setting

	$ export EMAIL_API_KEY=<your-api-key-for-emails-validation>
	$ export GEO_API_KEY=<your-api-key-for-ip-geo-location>
	$ export HOLIDAY_API_KEY=<your-api-key-for-holidays>
	$ export SECRET_KEY=<some secret key>
Then one can run the tests with

	$ ./manage.py test
I used here sqlite3 for DB, since it's the easiest to start with, for production I would go with the recommended DB which is postgresql.
I used requests for the 3rd party API's since it's a bit easier to work with in comparison with aiohttp. for a real world scenario I would choose aiohttp to make async, that way it won't block when calling the 3rd party API.
For the requirement of using JWT for authentication and authorization I used djangorestframework-simpleJWT since it's the recommended package by DRF, so I used it
