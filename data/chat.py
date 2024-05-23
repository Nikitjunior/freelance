import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from PIL import Image
from io import BytesIO


class Chat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user1 = sqlalchemy.Column(sqlalchemy.Integer)
    user2 = sqlalchemy.Column(sqlalchemy.Integer)
    messages = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self) -> str:
        return f"<Chat> {self.id} user1:{self.user1} user2:{self.user2}"

    def add_message(self, user_id: int, message: str):
        if self.messages:
            self.messages += f";&*!{user_id}:&*!{message}"
        else:
            self.messages += f"{user_id}:&*!{message}"

    def get_messages(self) -> list[dict]:
        raw_data = self.messages.split(";&*!")
        data = []
        for i in raw_data:
            i = i.split(":&*!")
            dialog = {}
            dialog['user_id'] = int(i[0])
            dialog['message'] = i[1]
            data.append(dialog)
        return data

    def get_last_message(self) -> dict:
        raw_data = self.messages.split(";&*!")[-1]
        data = raw_data.split(":&*!")
        return {"user_id": int(data[0]), "message": data[1]}
