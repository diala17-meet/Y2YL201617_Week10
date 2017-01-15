from flask import Flask
from flask import session as login_session
from model import *

app = Flask(__name__)
engine = create_engine('sqlite:///fizzBuzz.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

@app.route('/')
def showInventory():
	inventory = session.query(Product).all()
	htmlString = ""
	for item in inventory:
		htmlString += "<p>" + item.name + "</p>" + "<p>" + item.description + "</p>" + "<p>" + item.price + "</br></br>" 
	return htmlString

def hello_world():
	return 'hello world!'
	
@app.route('/')
@app.route('/inventory')
def inventory():
	item = session.query(Product).all()
	return render_template("inventory.html", item = items)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		if email is None or password is None:
			flash('Missing Arguments')
			redirect(url_for('login'))
	if verify_password(email, password):
		customer = session.query(Customer).filter_by(email=email).one()
		flash('login Successful, welcome, %s' % customer.name)
		login_session['name'] = customer.name
		login_session['email'] = email
		login_session['id'] = customer.id
		return redirect(url_for('inventory'))
	else:
		flash('Incorrect username/password combination')
		return redirect(url_for('login'))

def verify_password(email, password):
	customer = session.query(Customer).filter_by(email = email).first()
	if not customer or not customer.verify_password(password):
		return False
	g.customer = customer
	return True	

@app.route('/newCustomer', methods = ['GET','POST'])
def newCustomer():
	return "To be implemented"

@app.route("/product/<int:product_id>")
def product(product_id):
	product = session.query(Product).filter_by(id=product_id).one()
	return render_template('product.html', product=product)

@app.route("/product/<int:product_id>/addToCart", methods = ['POST'])
def addToCart(product_id):
	if 'id' not in login_session:
		flash("you must be logged in to perform this action")
		return redirect(url_for('login'))
		quantity = request.form['quantity']
		product = session.query(product).filter_by(id=product_id).one()
		shoppingCart = session.query(shoppingCart).filter_by(customer_id=login_sessin['id']).one()
		if product.name in [item.prodct.name for item in shoppingCart.products]:
			assoc = session.query(shoppingCartassociation).filter_by(shoppingCart=shoppingCart) \
				.filter_by(product=product).one()
			assoc.quantity = int(assoc.quantity)+ int(quantity)
			flash("successfuly added to shopping Cart")
			return redirect(url_for('shoppingCart'))
		else:
			a = shoppingCartAssociation(product=product, quantity=quantity)
			shoppingCart.products.append(a)
			session.add_all([a, product, shoppingCart])
			session.commit()
			flash("Successfully added to shopping Cart")
			return redirect(url_for('shoppingCart'))

@app.route("/shoppingCart")
def shoppingCart():
	if 'id' not in login_session:
		flash("you must be logged in to perform this action")
		return redirect(url_for('login'))
	shoppingCart = session.query(shoppingCart).filter_by(customer_id=login_session['id']).one()
	return render_template('shoppingCart.html', shoppingCart=shoppingCart)

@app.route("/removeFromCart/<int:product_id>", methods = ['POST'])
def removeFromCart(product_id):
	if 'id' not in login_session:
		flash("you must be logged in to perform this action")
		return redirect(url_for('login'))
	shoppingCart = session.query(ShoppingCart).filter_by(customer_id=login_session['id']).one()
	association = session.query(ShoppingCartAssociation).filter_by(shoppingCart=shoppingCart).filter_by(product_id=product_id).one()
	session.delete(association)
	session.commit()
	flash("Item deleted succesfully")
	return redirect(url_for('shoppingCart'))
    
@app.route("/updateQuantity/<int:product_id>", methods = ['POST'])
def updateQuantity(product_id):
	return "To be implemented"

@app.route("/checkout", methods = ['GET', 'POST'])
def checkout():
	return "To be implmented"

@app.route("/confirmation/<confirmation>")
def confirmation(confirmation):
	return "To be implemented"

@app.route('/logout', methods = ['POST'])
def logout():
	return "To be implmented"

if __name__ == '__main__':
    app.run(debug=True)
