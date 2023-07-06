import sqlite3
from flask import Flask, request, redirect, render_template, session, send_from_directory, abort
import os
import string
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import threading



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'djaflsfjljehrw7343682yg'
info = {}


def readfile(filename):
    f = open(filename)
    s = f.read()
    f.close()
    return s

def is_exist_username(user):
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    cur.execute("select username from users_info where username=?", (user,))
    x = cur.fetchone()
    conn.commit()
    if x == None:
        return False
    else:
        return True
    

def check_login(username, password):
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    tuple_of_users = cur.execute("select Username,Password,status from Users_info where Username=? and Password=?" , (username,password)).fetchall()
    conn.commit() 
    if tuple_of_users != [] :
        tuple_of_users =tuple_of_users[0]
        if tuple_of_users[2] == 'false':
            # error no active account
            return 'noactive'
        return 'active'
    else:
        # error no exist 
        return 'wrong'



def get_commodity():
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    commodity = cur.execute(
        "SELECT commodity_info.ID, commodity_info.name , commodity_info.src  , commodity_info.Price , commodity_info.category FROM commodity_info WHERE category='LAPTOP'").fetchall()
    conn.commit()
    return(commodity)


#@app.route('/')
#def login():
 #   return render_template('Login.html')
@app.route('/', methods=['GET', 'POST'])
def index():
    commodity = get_commodity()

    try:
        if session['logged_in'] == True:
            return render_template('Home.html', final_buy=False ,logged_in=True,no_login=False , commodity_best=commodity[0:4], commodity_latest=commodity[0:4])
    except:
        return render_template('Home.html', final_buy=False,logged_in=False,no_login=True , commodity_best=commodity[0:4], commodity_latest=commodity[0:4])


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':        
        username = request.form.get('user', '')
        password = request.form.get('password')
        check_user = check_login(username, password)
        if check_user == 'active':
            session['logged_in'] = True
            session['username'] = username

            commodity = get_commodity()

            return render_template('Home.html', final_buy=False ,logged_in=True,no_login=False, commodity_best=commodity[0:4], commodity_latest=commodity[0:4])
        # if username == 'admin' and password == 'admin12345':
        #     session['logged_in'] = True
        #     session['username'] = username
        #     return redirect('/admin')
        elif check_user == 'noactive':
            return render_template('Login.html' , show_err_noactive = True)
        elif check_user == 'wrong':
            return render_template('login.html', show_err = True)        
    else:
        return render_template('Login.html', show_err_noactive=False , show_err=False)
    # else:
        # show_err = False
 

    
@app.route('/laptop', methods=["GET"])
def laptop():

    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    laptops = commodity = cur.execute(
        "SELECT * FROM commodity_info WHERE category='LAPTOP'").fetchall()
    conn.commit()

    try:
        if session['logged_in'] == True:
            return render_template('Laptop.html', login_alrt_err=False ,logged_in=True,no_login=False, laptops=laptops)
    except:
        return render_template('Laptop.html', login_alrt_err=False ,logged_in=False ,no_login=True , laptops=laptops)

    


@app.route('/mobile', methods=["GET"])
def mobile():

    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    mobiles = cur.execute(
        "SELECT * FROM commodity_info WHERE category='MOBILE'").fetchall()
    conn.commit()

    try:
        if session['logged_in'] == True:
            return render_template('Mobile.html', login_alrt_err=False ,logged_in=True,no_login=False , mobiles=mobiles)
    except:
        return render_template('Mobile.html', login_alrt_err=False ,logged_in=False ,no_login=True , mobiles=mobiles)

    


@app.route('/otherProducts', methods=["GET"])
def otherProducts():

    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    otherProducts = commodity = cur.execute(
        "SELECT * FROM commodity_info WHERE category='Accessories'").fetchall()
    conn.commit()


    try:
        if session['logged_in'] == True:
            return render_template('OtherProducts.html', login_alrt_err=False ,logged_in=True,no_login=False , otherProducts=otherProducts)
    except:
        return render_template('OtherProducts.html', login_alrt_err=False , logged_in=False ,no_login=True, otherProducts=otherProducts)

    

@app.route('/signout')
def signout():
    session['logged_in'] = False
    return redirect('/login ')



def send_confirmation_email(email):
    
    # Verify link KEY
    s_link_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    
    t = threading.Thread(None, send_confirmation_email_multiThread, None, (email, s_link_key))
    t.start()
    
    return s_link_key


# To accept the link confirmation request
@app.route('/confirm', methods=['GET'])
def _check_confirm():
    s_link = request.args.get('link','')


    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    is_exist = cur.execute('select link from users_info where link=?',(s_link,)).fetchall()
    conn.commit()
    
    # Get All confirm links         
    
    if is_exist is not None:
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        is_exist = cur.execute('UPDATE users_info SET status=?  where link=?',("true",s_link)).fetchall()
        conn.commit()
        return render_template('confirm_email.html')
    abort (403)



def send_confirmation_email_multiThread(email, s_link_key):

    s_smtp_server = 'smtp.gmail.com'
    i_port = 465
    s_sender_email = 'mehdibordbar24@gmail.com'
    s_password = 'jrqbyeukketdzqdu'
    
    # The confirmation link
    s_link = 'http://localhost:5000/confirm?link=%s' % s_link_key
    
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "لینک تایید حساب کاربری"
    msg['From'] = s_sender_email
    msg['To'] = email
    
    s_text = "جهت تایید حساب کاربری خود در وبسایت نیها تکنولوژی بر روی لینک زیر کلیک کنید.\n{link}".format(link=s_link)
    
    s_text_mime = MIMEText(s_text, 'plain','utf-8')
    
    msg.attach(s_text_mime)

    # reference : https://www.mongard.ir/one_part/170/sending-email-python/
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(s_smtp_server, i_port, context=context) as server:            
        server.login(s_sender_email, s_password) 
        server.sendmail(s_sender_email, email, msg.as_string())
        server.quit()
        
        return s_link_key
    
    
@app.route('/addToCart')
def addToCart() :
    name = request.args.get('name', '')
    src = request.args.get('src', '')
    price = request.args.get('price', '')
    route = request.args.get('route', '')
    
    try:
        username = session['username']

    except:
        if route == 'mobile':
            conn = sqlite3.connect('data.sqlite')
            cur = conn.cursor()
            mobiles = cur.execute(
                "SELECT * FROM commodity_info WHERE category='MOBILE'").fetchall()
            conn.commit()

            return render_template('Mobile.html', addToCart_alert= False, mobiles=mobiles, login_alrt_err=True , logged_in=False,no_login=True)
        
        
        elif route == 'laptop' :
            conn = sqlite3.connect('data.sqlite')
            cur = conn.cursor()
            laptops = cur.execute(
                "SELECT * FROM commodity_info WHERE category='LAPTOP'").fetchall()
            conn.commit()

            return render_template('Laptop.html', addToCart_alert= False , laptops=laptops, login_alrt_err=True , logged_in=False,no_login=True)

        elif route == 'other' :         
            conn = sqlite3.connect('data.sqlite')
            cur = conn.cursor()
            otherProducts = cur.execute(
                "SELECT * FROM commodity_info WHERE category='Accessories'").fetchall()
            conn.commit()
            
            return render_template('OtherProducts.html', addToCart_alert= False, otherProducts=otherProducts , login_alrt_err=True ,logged_in=False,no_login=True)

        else :         
            commodity  = get_commodity()
            return render_template('Home.html', addToCart_alert= False,  commodity_best=commodity[0:4], commodity_latest=commodity[0:4] , login_alrt_err=True ,logged_in=False,no_login=True)
        

    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    cur.execute('insert into ordered_commodities (username,name,src,price) values(? , ? , ? , ? )',
        (username, name, src, price))
    conn.commit()


    if route == 'mobile':
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        mobiles = cur.execute(
            "SELECT * FROM commodity_info WHERE category='MOBILE'").fetchall()
        conn.commit()

        return render_template('Mobile.html', addToCart_alert= True, login_alrt_err=False, mobiles=mobiles , logged_in=True,no_login=False)
    
    
    elif route == 'laptop' :
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        laptops = cur.execute(
            "SELECT * FROM commodity_info WHERE category='LAPTOP'").fetchall()
        conn.commit()

        return render_template('Laptop.html', addToCart_alert= True, login_alrt_err=False , laptops=laptops , logged_in=True,no_login=False)


    elif route == 'other' :
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        otherProducts = cur.execute(
            "SELECT * FROM commodity_info WHERE category='Accessories'").fetchall()
        conn.commit()
 
        return render_template('OtherProducts.html', addToCart_alert= True, login_alrt_err=False, otherProducts=otherProducts , logged_in=True,no_login=False)


    else:         
        commodity = get_commodity()
        return render_template('Home.html', addToCart_alert= True, login_alrt_err=False, commodity_best=commodity[0:4], commodity_latest=commodity[0:4] , logged_in=True,no_login=False)


@app.route('/cart', methods=['GET', 'POST'])
def cart():

    username = session['username']
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    user_commodities = cur.execute("select * from ordered_commodities where Username=? " , (username,)).fetchall()
    conn.commit() 

    com_length = len(user_commodities)
    
    total_price = 0
    for com in user_commodities:
        total_price += int(com[4])


    if request.method == 'POST':
        Address = request.form.get('Address', '')
        Code = request.form.get('Code', '')
        Phonenumber = request.form.get('Phonenumber', '')

        if Address == '' or Code == '' or Phonenumber == '' :
            return render_template('Cart.html', empty_field=True , user_commodities=user_commodities , com_length = com_length , total_price = total_price)
        
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        cur.execute('insert into Info (Address,Code,Phonenumber) values(? , ? , ? )',
                    (Address, Code, Phonenumber,))
        cur.execute('delete from ordered_commodities where username=?',
                    (username,))
        conn.commit()
        
        commodity = get_commodity()
        return render_template('Home.html' ,final_buy=True ,logged_in=True,no_login=False , commodity_best=commodity[0:4], commodity_latest=commodity[0:4])
 
    else:
        return render_template('Cart.html', empty_field=False, user_commodities=user_commodities , com_length = com_length , total_price = total_price)

        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        repassword = request.form.get('repassword', '')
        email = request.form.get('email', '')

        if email == '' or username == '' or password == '' or repassword == '':
            return render_template('Signup.html', empty_field=True)
        if password != repassword:
            return render_template('Signup.html', no_same_password=True)
        if is_exist_username(username) == True or username == 'admin':
            return render_template('Signup.html', user_err=True)
        
        link = send_confirmation_email(email)
        conn = sqlite3.connect('data.sqlite')
        cur = conn.cursor()
        cur.execute('insert into users_info (username,password,email,status,link) values(? , ? , ? , "false" , ?)',
                    (username, password, email, link))
        conn.commit()
        
        return render_template('login.html', show_alrt=True)
    return render_template('Signup.html', user_err=False ,empty_field=False, no_same_password=False)

#if __name__ == "__main__":
app.run(debug=True)


