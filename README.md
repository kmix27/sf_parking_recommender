### Who hates parking in San Francisco?  

If you didn't raise your hand you either don't live here or you don't have a car.  I have lived in several neighborhoods that have been an absolute nightmare to park in.  A statement that rings true for pretty much everyone in the city.  For my Metis passion project I set out to build a recommender system to handle the omnipresent question of "Where should I park in San Francisco?".  It's still in it's early stages of development, so the code can be a little rough at times, but it does work, and I welcome you to try it out.  

To get it up and running you'll need to follow these steps in order, future iterations won't be quite so complex I promise:  

1. Clone or download this repo.
2. Unzip the data: cleaned.zip
3. Get your [Google maps Javascript API key](https://developers.google.com/maps/documentation/javascript/)
4. At the bottom of app_web/templates/index2.html you'll find {{YOUR API KEY HERE}} replace that with your key.
5. Check out the requirements.txt and make sure they're satisfied.
6. In a fresh terminal run  ```python run_app_api.py``` to start up the API service.
7. In a new terminal tab run ```python run_app_web.py``` to start the web app.
8. Navigate to http://127.0.0.1:9001/ in a browser.

Maybe a month after I originally presented this the fine ML researchers at google came out with this [fantastic article](https://research.googleblog.com/2017/02/using-machine-learning-to-predict.html).  They really blew me out of the water with that one.  I'm very excited that it's a problem that is being worked on, and only a little bit jealous of the MUCH stronger ground truth the google team has to work with.  Looking for parking isn't only a hassle, it causes tons of congestion and unnecessary emissions,  and I really hope that it's something more people will consider working on.  


