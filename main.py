from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_

from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users import User
from data.orders import Orders
from data.order_creation_form import OrdersCreationForm
from data.chat import Chat

from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '12qasdj6'

login_manager = LoginManager()
login_manager.init_app(app)


def get_second_user(chat_id: int) -> User:
    db_sess = db_session.create_session()
    chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()

    if current_user.id == chat.user1:
        user2 = db_sess.query(User).filter(User.id == chat.user2).first()
    else:
        user2 = db_sess.query(User).filter(User.id == chat.user1).first()
    return user2


def get_chats_list() -> list[dict]:
    db_sess = db_session.create_session()
    chats_preparing = db_sess.query(Chat).filter(
        or_(current_user.id == Chat.user1, current_user.id == Chat.user2)
    ).all()

    chats = []
    for i in chats_preparing:
        second_user = get_second_user(i.id)
        if i.get_last_message()['user_id'] == current_user.id:
            last_message_user = current_user.name
        else:
            last_message_user = second_user.name

        chats.append({
            "id": i.id,
            "name": second_user.name,
            "image": second_user.image,
            "last_message_user": last_message_user,
            "last_message": i.get_last_message()['message']
        })
    return chats


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template('main_page.html', title='TalentHarbor')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            speciality=form.speciality.data,
            email=form.email.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        f = request.files['file']
        if f:
            db_sess = db_session.create_session()
            user = db_sess.query(User).get(current_user.id)
            path = f'users_images/profile{current_user.id}.png'
            f.save(f"static/{path}")
            user.image = path
            db_sess.commit()
        return redirect('/profile')

    else:
        try:
            data = {
                "name": current_user.name,
                "surname": current_user.surname,
                "phone_number": current_user.phone_number,
                "email": current_user.email,
                "image": current_user.image
            }
        except AttributeError:
            data = {}

        rating = current_user.get_rating()
        return render_template('profile.html', title='Профиль', data=data, rating=rating)


@app.route("/orders")
@login_required
def orders():
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders, User).join(User, User.id == Orders.employer).all()
    return render_template("orders.html", title="Заказы", orders=orders)


@app.route("/create_order", methods=['GET', 'POST'])
@login_required
def create_order():
    form = OrdersCreationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        order = Orders()
        order.title = form.order_title.data
        order.description = form.description.data
        order.employer = current_user.id
        db_sess.add(order)
        db_sess.commit()
        return redirect('/orders')
    return render_template('create_order.html', title='Разместить заказ', form=form,
                           title2="Создать заказ")


@app.route("/order/<id>", methods=['GET', 'POST'])
@login_required
def order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id).first()
    if request.method == "POST":
        order.executor = current_user.id
        db_sess.commit()
        return redirect('/accepted_orders')

    data = {
        "title": order.title,
        "description": order.description
    }
    return render_template("accept_order.html", title="Откликнуться на заказ", data=data)


@app.route("/edit_order/<id>", methods=['GET', 'POST'])
@login_required
def edit_order(id):
    form = OrdersCreationForm()
    form.submit.label.text = 'Изменить'
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id).first()
    if not order:
        abort(404)
    if current_user.id == order.employer:
        if request.method == "GET":
            form.order_title.data = order.title
            form.description.data = order.description
        if form.validate_on_submit():
            order.title = form.order_title.data
            order.description = form.description.data
            db_sess.commit()
            return redirect('/orders')
    else:
        abort(404)
    return render_template("create_order.html", title="Редактировать заказ", form=form,
                           title2="Редактировать заказ")


@app.route("/delete_order/<id>")
@login_required
def delete_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id).first()
    if not order:
        abort(404)
    if current_user.id == order.employer:
        db_sess.delete(order)
        db_sess.commit()
        return redirect('/orders')
    else:
        abort(404)


@app.route("/accepted_orders")
@login_required
def accepted_orders():
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).filter(Orders.executor == current_user.id).all()

    formatted_orders = []
    for order in orders:
        employer_user = db_sess.query(User).filter(User.id == order.employer).first()
        employer_fullname = f"{employer_user.surname} {employer_user.name}"
        formatted_order = {
            "id": order.id,
            "title": order.title,
            "description": order.description,
            "executor": order.executor,
            "employer": employer_fullname
        }
        formatted_orders.append(formatted_order)
    return render_template("accepted_orders.html", title="Принятые заказы", orders=formatted_orders)


@app.route("/deny_order/<id>")
@login_required
def deny_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id).first()
    if not order:
        abort(404)
    if current_user.id == order.executor:
        order.executor = None
        db_sess.commit()
        return redirect("/orders")


@app.route("/chat", methods=['GET', 'POST', 'PUT'])
@login_required
def chat():
    db_sess = db_session.create_session()
    chat = db_sess.query(Chat).filter(Chat.id == current_user.last_chat).first()

    if request.method == "PUT":
        chat_id = int(request.form.get('chat_id'))
        chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()

        data = chat.get_messages()
        user2 = get_second_user(chat_id)
        data = chat.get_messages()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        user.last_chat = chat_id
        db_sess.commit()

        return jsonify({
            "messages": [{"user_id": msg['user_id'], "message": msg['message']} for msg in data],
            "user2": {
                "id": user2.id,
                "name": user2.name,
                "image": user2.image
            }
        })

    if not current_user.last_chat:
        chats = get_chats_list()
        return render_template("chat.html", title="Чат", data=None, user2=None, chats=chats)

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            chat.add_message(current_user.id, message)
            db_sess.commit()
        data = chat.get_messages()

        chats = get_chats_list()
        user2 = get_second_user(chat.id)

        return jsonify({
            "messages": [{"user_id": msg['user_id'], "message": msg['message']} for msg in data],
            "chats": chats,
            "user2": {
                "id": user2.id,
                "name": user2.name,
                "image": user2.image
            }
        })

    user2 = get_second_user(chat.id)
    data = chat.get_messages()
    chats = get_chats_list()

    return render_template("chat.html", title="Чат", data=data, user2=user2, chats=chats)


def main():
    db_session.global_init("db/freelance.db")
    app.run()


if __name__ == '__main__':
    main()
