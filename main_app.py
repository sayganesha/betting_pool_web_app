# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

###############################################################################
# App related methods
###############################################################################
def get_user(username):
	"""Returns (user_id, username) for given user"""
	db = get_db()
    	cur = db.execute('select user_id, name from users where name="%s"' % \
			 username)
    	entries = cur.fetchone()
	if not entries or len(entries) == 0:
		return ('', '')

	return (entries[0], entries[1])

def add_user(username):
	"""Adds a new user"""
	db = get_db()
    	cur = db.execute('insert into users(name) values("%s")' % \
			 username)
    	db.commit()

def add_bet_info(betname, bet_options):
	"""Adds a new bet with its options"""
	db = get_db()
	# First add a new bet
    	cur = db.execute('insert into bet_info(name, desc, pic) '\
			 'values("%s", "", "")' % betname)

	# Get back the bet_id
	cur = db.execute('select bet_id from bet_info where name="%s"'\
			 % betname)
	row = cur.fetchone()
	bet_id = row['bet_id']

	for bet_option in bet_options:
		if bet_option:
			db.execute('insert into bet_options(bet_id, name)'\
				  ' values("%s", "%s")' % (bet_id, bet_option))
    	db.commit()

def get_bet_options(bet_id):
    """
    Returns a dict
    key: (bet_opt_id, bet_opt_name, total_bets_on_this_option)
    value: List of (user_name amount_user_bet_on_this_option) strings
    """

    db = get_db()
    
    # Get all the bet_opt_ids for given bet
    cur = db.execute('select bet_opt_id, name '\
                     'from bet_options where bet_id=%s' % bet_id)
    all_bet_options = cur.fetchall()

    bet_options_table = {}
    for bet_option in all_bet_options:
        bet_opt_id = bet_option['bet_opt_id']

        # Get all users who bet on this option
        stmt = 'select user_id, name from users '\
               'where user_id in '\
               '(select user_id from user_bets where bet_opt_id=%s)' \
               % bet_opt_id
        cur = db.execute(stmt)
        all_users = cur.fetchall()

        user_info_list = []
        total_amount = 0
        for user in all_users:
            # Find out the amount each user bet on this bet option
            stmt = 'select amount from user_bets '\
                   'where user_id=%s and bet_opt_id=%s' \
                   % (user[0] , bet_opt_id)
            cur = db.execute(stmt)
            bet_amt_row = cur.fetchone()

            user_info_list.append(user[1] + ' ($ %s)' % bet_amt_row['amount'])
            total_amount += int(bet_amt_row['amount'])

        # Form the key
        table_key = (bet_opt_id, bet_option['name'], str(total_amount))
        # Add the betting option information in the table
        bet_options_table[table_key] = user_info_list

    return bet_options_table

def setup_env():
    """
    Initializes the application
    """
    global app
    app.config.from_object(__name__)

    # Load default config and override config from an environment variable
    app.config.from_envvar('BETTING_APP_CFG_FILE')

    connect_db();

###############################################################################
# Routes : Handles routes (or urls)
###############################################################################

@app.route('/addbet', methods=['GET', 'POST'])
def addbet():
    """
    Adds a new betting item.
    Note that only admins are allowed to add a new bet
    """
    if request.method == 'POST':
	# Register the user if not already there
	username = session['username']
	if username != app.config['ADMIN_USERNAME']:
		return 'Unauthorized user'
	add_bet_info(request.form['betname'],
		     (request.form['opt_1'], request.form['opt_2'],
		     request.form['opt_3'], request.form['opt_4']))

	return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p>The bet will called : <input type=text name=betname>
            <p>Most chickens will bet on:
                <input type=text size=50 maxlength=50 name=opt_1>
            <p>The rebel will go with:
                <input type=text size=50 maxlength=50 name=opt_2>
            <p>Insane people will bet on:
                <input type=text size=50 maxlength=50 name=opt_3>
            <p>Fun (and dumb) peeps will choose me:
                <input type=text size=50 maxlength=50 name=opt_4>
            <p><input type=submit value='Yo brother, add my bet!'>
        </form>
    '''

@app.route('/addusertobet', methods=['GET', 'POST'])
def addusertobet():
    """
    Adds a user to bet, removes any of his previous bets for this bet
    """
    user_id = request.form['user_id']
    bet_id = request.form['bet_id']
    bet_opt_id = request.form['bet_opt_id']
    amount = request.form['amount']
    
    # Check if amount is integer
    try:
        int(amount)
    except:
        # dont add the bet amount as it is illegal
        # TODO : Can improve by giving an error message.
        return redirect(url_for('index'))
        
    db = get_db()
    # each user has only MAX_SPEND_AMT, check if user is not overspending
    cur = db.execute('select sum(amount) from user_bets where user_id="%s" '\
                    'and bet_opt_id !=%s' % (user_id, bet_opt_id))
    amt_rows = cur.fetchone()
    if amt_rows[0]:
        amt_remaining = 0
        if (int(amt_rows[0]) + int(amount)) > app.config['MAX_SPEND_AMT']:
            amt_remaining = app.config['MAX_SPEND_AMT'] - (int(amt_rows[0]))
            return 'You have only %s $ to spend (you entered %s $)!!<br/>'\
                   '<a href="/">%s</a>!' %\
                   (amt_remaining, amount, app.config['OVERSPEND_MSG'])

    # Delete any previous bets user had
    cur = db.execute('delete from user_bets '\
                     'where user_id="%s" and '\
                     'bet_opt_id in '\
                     '(select bet_opt_id from bet_options where bet_id="%s")'\
                     % (user_id, bet_id))
 
    # Now add his new bet 
    cur = db.execute('insert into user_bets(user_id, bet_opt_id, amount)'\
                     ' values("%s", "%s", "%s")' \
                     % (user_id, bet_opt_id, amount))

    # First remove all bets this user has for this bet
    db.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'username' in session:
	db = get_db()
	cur = db.execute('select * from bet_info')
	bets = cur.fetchall()
        return render_template('main.html',
			       name = session['username'],
			       user_id = session['user_id'],
			       all_bets = bets,
			       get_bet_options_cb = get_bet_options)
    return 'Welcome to the %s Betting Pool !!<br/>'\
	   '<a href="/login">Login</a> and start betting or'\
           '<br/><a href="/register">Register</a> yourself for ULTIMATE fun!!' % \
	   app.config['BETTING_POOL_NAME']

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
	# Register the user if not already there
	username = request.form['username']
	user_id, name = get_user(username)
	if user_id or not username:
	    return 'User name "%s" already exists' % username
	else:
	    add_user(username)

	return redirect(url_for('login'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Register>
        </form>
        '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
	# Register the user if not already there
	username = request.form['username']
	user_id, name = get_user(username)
	if not user_id:
		return ('Invalid login name: %s, <br/>'\
			'Go back to <a href="/login">Login</a> '\
			'or <br/> <a href="/register">Register</a> Page' % username)

        session['username'] = username
        session['user_id'] = user_id
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
	setup_env()
	app.run()
