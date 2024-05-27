import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Applications(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "applications"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sender = sqlalchemy.Column(sqlalchemy.Integer)
    recipient = sqlalchemy.Column(sqlalchemy.Integer)
    order = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.String)
