from flask import Flask
from pymongo import MongoClient
from flask_pymongo import pymongo
from flask import Flask, render_template, request, redirect, flash
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Zomato@restaurant'

app.config['MONGO_URI'] = 'mongodb+srv://abhishek:abhishekmasai@cluster0.y8lffxx.mongodb.net/restuarnt?retryWrites=true&w=majority'

# mongo = MongoClient(app.config['MONGO_URI'])
# db = pymongo(app).db

# Initialize PyMongo client
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo.get_database()
collection = db['your_collection_name']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/menu')
def menu():
    data = load_data_from_mongodb()
    return render_template('menu.html', menu=data)


@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        availability = request.form['availability']

        new_menu_item = {
            'id': get_next_menu_id(),
            'name': dish_name,
            'price': price,
            'availability': availability
        }

        collection.insert_one(new_menu_item)
        flash('Menu item added successfully!')
        return redirect('/menu')

    return render_template('add_menu.html')


@app.route('/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu_item(menu_id):
    menu_item = collection.find_one({'id': menu_id})

    if menu_item:
        if request.method == 'POST':
            dish_name = request.form['dish_name']
            price = float(request.form['price'])
            availability = request.form['availability']

            updated_menu_item = {
                'name': dish_name,
                'price': price,
                'availability': availability
            }

            collection.update_one({'id': menu_id}, {'$set': updated_menu_item})
            flash('Menu item updated successfully!')
            return redirect('/menu')

        return render_template('edit_menu.html', menu_item=menu_item)

    flash('Menu item not found!')
    return redirect('/menu')


@app.route('/menu/delete/<int:menu_id>', methods=['GET', 'POST'])
def delete_menu_item(menu_id):
    menu_item = collection.find_one({'id': menu_id})

    if menu_item:
        if request.method == 'POST':
            collection.delete_one({'id': menu_id})
            flash('Menu item deleted successfully!')
            return redirect('/menu')

        return render_template('delete_menu.html', menu_item=menu_item)

    flash('Menu item not found!')
    return redirect('/menu')


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        dish_ids = request.form.getlist('dish_ids')
        dish_order_status = request.form['status']

        valid_dish_ids = []
        for dish_id in dish_ids:
            dish = collection.find_one({'id': int(dish_id), 'availability': 'yes'})
            if dish:
                valid_dish_ids.append(int(dish_id))

        if len(valid_dish_ids) == len(dish_ids):
            order = {
                'order_id': get_next_order_id(),
                'customer_name': customer_name,
                'dish_ids': valid_dish_ids,
                'status': dish_order_status,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            db.orders.insert_one(order)
            flash('Order placed successfully!')
            return redirect('/orders')
        else:
            flash('Invalid dish ID(s) or item(s) not available!')
            return redirect('/orders')

    data = load_data_from_mongodb()
    orders = db.orders.find()
    return render_template('orders.html', menu=data, orders=orders)


@app.route('/orders/update/<int:order_id>', methods=['GET', 'POST'])
def update_order_status(order_id):
    order = db.orders.find_one({'order_id': order_id})

    if order:
        if request.method == 'POST':
            new_status = request.form['status']
            db.orders.update_one({'order_id': order_id}, {'$set': {'status': new_status}})
            flash('Order status updated successfully!')
            return redirect('/orders')

        return render_template('update_order.html', order=order)

    flash('Order not found!')
    return redirect('/orders')


@app.route('/review_orders')
def review_orders():
    orders = db.orders.find()
    return render_template('review_order.html', orders=orders)


@app.route('/exit')
def exit():
    return render_template('exit.html')


def load_data_from_mongodb():
    return list(collection.find())


def get_next_menu_id():
    menu = list(collection.find().sort('id', -1).limit(1))
    if menu:
        return menu[0]['id'] + 1
    return 1


def get_next_order_id():
    orders = list(db.orders.find().sort('order_id', -1).limit(1))
    if orders:
        return orders[0]['order_id'] + 1
    return 1


if __name__ == '__main__':
    app.run(debug=True)


