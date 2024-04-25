from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users import User
from data.orders import Orders
from data.order_creation_form import OrdersCreationForm

from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '12qasdj6'

login_manager = LoginManager()
login_manager.init_app(app)


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

        db_sess = db_session.create_session()
        user_id = current_user.id
        user = db_sess.query(User).get(user_id)
        user.image_data = f.read()
        db_sess.commit()

        return redirect('/profile')
    else:
        try:
            if current_user.image_data:
                image = Image.open(BytesIO(current_user.image_data))
                image.save('static/images/res.png')
            data = {
                "name": current_user.name,
                "surname": current_user.surname,
                "phone_number": current_user.phone_number,
                "email": current_user.email,
            }
        except AttributeError:
            data = {}
        return render_template('profile.html', title='Профиль', data=data)


@app.route("/orders")
@login_required
def orders():
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders, User).join(User, User.id == Orders.employer)
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
    return render_template('create_order.html', title='Разместить заказ', form=form)


@app.route("/order/<id>", methods=['GET', 'POST'])
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


def main():
    db_session.global_init("db/freelance.db")
    app.run()


if __name__ == '__main__':
    main()
