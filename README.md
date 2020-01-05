Portfolio Performance
=================

This application shows the evolution of a portfolio stock during the time. The values of the quotations are get from this [free api](https://www.worldtradingdata.com/). The charts are builded using the [chartjs library](https://www.chartjs.org).
   
## Building

It is needed the python3 library installed.

It is best to use the python `virtualenv` tool to build locally:

```sh
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py runserver
```

Then visit `http://localhost:8000` to view the app. 
