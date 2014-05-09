betting_pool_web_app
====================

A flask web app that helps run a betting pool

What is this Webapp for ?
=========================
This is a simple webapp that was developed so that one can 
create a fun Betting pool (with virtual money ;) ).
The idea was to learn webapp development and develop a fun app.

The webapp was developed using Flask.
Flask is a micro webdevelopment framework for Python.
Since I think Python is a faily good programming language
masked as a scripting language, Flask looks like a good
candidate. (Another option I considered was Bottle).

Pre-requisites
==============
Since this uses Flask web development toolkit, please
install Flask on your system.
(Find how to install it at : http://flask.pocoo.org/docs/installation )

Configuration Files
===================
Configure your application using the config file picked up
from the environment variable BETTING_APP_CFG_FILE .
The sample config file to use is config/settings.cfg .

How to play the game
====================
The game basically has some users as admin and others who are not admins.
Each user has to first register with a username.
Once the user is registered, he can login to his page.
On his page, he will see that he has been allocated a sum of money to bet with.
He will also see a bunch of bets.
The user can simply put in the amount he wants to bet on each bet to enter the betting pool.
The maximum amount of money a user can bet is fixed, so the game is really betting with that amount, and once the results of the bets are out, the guy who makes the most money from the amount initially given to his is the winner!

If the user is one of the admins, he will be able to add a bet.
A bet has a name, and has upto four options.
Once a bet is added, all other users can start betting on it.


