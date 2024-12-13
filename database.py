from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, json
from sqlalchemy import DateTime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "hhx2005426"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(40), nullable=False, unique=True)  # 账号,唯一，用手机号登录
    password_hash = db.Column(db.String(128), nullable=False)  # 密码
    username = db.Column(db.String(40), nullable=False, default="美妆新秀")  # 用户名称
    avatar = db.Column(db.String(255), default="/image/default_avatar.png")  # 用户头像
    permissions = db.Column(db.Integer, nullable=False, default=1)
    is_delete = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Sets the password field to the hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'username': self.username,
            'permissions': self.permissions,
            'avatar': self.avatar
        }


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(40), nullable=False)  # 产品类别：makeUp,clean,care
    product_name = db.Column(db.String(40), nullable=False)
    start_time = db.Column(db.String(255))
    end_time = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_list = db.Column(db.Text)  # 用于存储json字符串
    skin_list = db.Column(db.Text)
    product_introduce = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=3)
    publish_by = db.relationship('User', lazy=True)
    tests = db.relationship('Test', backref='product', lazy=True)
    userComment = db.relationship('UserComment', backref='comment_product', lazy=True)
    audit_by = db.Column(db.Integer)

    def add_image(self, image_url):
        if not self.image_list:
            self.image_list = json.dumps([image_url])
        else:
            self.image_list = json.dumps(json.loads(self.image_list) + [image_url])

    def get_images(self):
        return json.loads(self.image_list) if self.image_list else []

    def add_skin_type(self, skin_type):
        if not self.skin_list:
            self.skin_list = json.dumps([skin_type])
        else:
            self.skin_list = json.dumps(json.loads(self.skin_list) + [skin_type])

    def get_skin_type(self):
        return json.loads(self.skin_list) if self.skin_list else []

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'product_name': self.product_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'user_id': self.user_id,
            'image_list': self.get_images(),
            'skin_list': self.get_skin_type(),
            'product_introduce': self.product_introduce,
            'status': self.status,
            'publish_by': self.publish_by.to_dict(),
            'tests': [test.to_dict() for test in self.tests],
            'audit_by': self.audit_by,
            'userComment': [comment.to_dict() for comment in self.userComment]
        }


class JoinedTest(db.Model):
    __tablename__ = "joinedTest"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': self.product.to_dict(),
        }


class Test(db.Model):
    __tablename__ = "test"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    skin_type = db.Column(db.String(40), nullable=False)  # 产品类别：makeUp,clean,care中的一个
    tag = db.Column(db.String(40), nullable=False)
    image_list = db.Column(db.Text)  # 用于存储json字符串
    score = db.Column(db.Integer, nullable=False)
    feeling = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    publish_time = db.Column(DateTime, default=datetime.utcnow)  # 发布时间
    user = db.relationship('User', lazy=True)

    def add_image(self, image_url):
        if not self.image_list:
            self.image_list = json.dumps([image_url])
        else:
            self.image_list = json.dumps(json.loads(self.image_list) + [image_url])

    def get_images(self):
        return json.loads(self.image_list) if self.image_list else []

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'skin_type': self.skin_type,
            'tag': self.tag,
            'image_list': self.get_images(),
            'score': self.score,
            'feeling': self.feeling,
            'user_id': self.user_id,
            'publish_time': self.publish_time,
            'user': self.user.to_dict(),
        }


class UserComment(db.Model):
    __tablename__ = "userComment"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_list = db.Column(db.Text)  # 用于存储json字符串
    comment_text = db.Column(db.Text)
    publish_time = db.Column(DateTime, default=datetime.utcnow)  # 发布时间
    user = db.relationship('User', lazy=True)

    def add_image(self, image_url):
        if not self.image_list:
            self.image_list = json.dumps([image_url])
        else:
            self.image_list = json.dumps(json.loads(self.image_list) + [image_url])

    def get_images(self):
        return json.loads(self.image_list) if self.image_list else []

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'image_list': self.get_images(),
            'user_id': self.user_id,
            'comment_text': self.comment_text,
            'publish_time': self.publish_time,
            'user': self.user.to_dict(),
        }


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
