import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from PIL import Image
from io import BytesIO


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    speciality = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    phone_number = sqlalchemy.Column(sqlalchemy.String, unique=True)
    image = sqlalchemy.Column(sqlalchemy.String, default='images/profile.png')
    rating = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"<User> {self.id}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.hashed_password, password)

    def add_rating(self, raiting: int):
        if self.rating:
            self.rating += f", {raiting}"
        else:
            self.rating = str(raiting)

    def get_rating(self) -> float:
        if self.rating:
            rating = list(map(int, self.rating.split(",")))
            print(rating)
            return round((sum(rating) / len(rating)), ndigits=1)
        return 0