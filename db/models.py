import hashlib
import time

from sqlalchemy import create_engine, func
from sqlalchemy.orm import relationship, backref, relation
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql




Base = declarative_base()

friends = Table(
    'friends', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True)
    )

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable = False)
    email = Column(String(70), nullable = False)
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())
    last_seen_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_removed = Column(Boolean, nullable = False, default = False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50))


    following = relation(
        "User",secondary = friends,
        primaryjoin = friends.c.user_id == id,
        secondaryjoin = friends.c.friend_id == id,
        backref = "followers")

    def as_dict(self):
        user = {
                'id': self.id,
                'email': self.email,
                'created_date': int(time.mktime(self.created_timestamp.timetuple())),
                'updated_date': int(time.mktime(self.last_seen_timestamp.timetuple())),
                'is_removed': self.is_removed,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
                }
        if len(self.avatars) > 0:
            user['avatar'] = {
                'id': self.avatars[-1].id,
                'url': self.avatars[-1].url,
                'is_silhouette': self.avatars[-1].is_silhouette,
                'created_date': int(time.mktime(self.avatars[-1].created_timestamp.timetuple()))
            }

        return user

class PushToken(Base):
    __tablename__ = 'push_tokens'

    client_types = ['IOS', 'ANDROID']

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(256))
    client_type = Column(mysql.ENUM(client_types), nullable = False, default=client_types[1])
    client_version = Column(String(10))
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())

    user = relationship('User', backref='push_tokens')

class AuthToken(Base):
    __tablename__ = 'auth_tokens'

    providers = ['FACEBOOK', 'GOOGLE', 'KAHOOTS']

    id = Column(Integer, primary_key=True)
    push_token_id = Column(Integer, ForeignKey('push_tokens.id'), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    token = Column(String(256), nullable = False, default = 0)
    expires_in_sec = Column(Integer, nullable = False, default = 3200)
    oauth_provider = Column(mysql.ENUM(providers))
    last_seen_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())

    push_token = relationship('PushToken', backref='auth_tokens')
    user = relationship('User', backref='auth_tokens')

class Avatar(Base):
    __tablename__ = 'avatars'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    remote_url = Column(String(256), nullable = False, default = 0)
    is_silhouette = Column(Boolean, nullable = False, default = False)
    url = Column(String(256), nullable = False, default = 0)
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())
    user = relationship('User', backref='avatars')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)

    title = Column(String(100), nullable = True)
    description = Column(String(300), nullable = True)
    image = Column(String(2083), nullable = True)
    url = Column(String(2083), nullable = True)
    host = Column(String(255), nullable = True)
    type = Column(String(40), nullable = True)
    site_name = Column(String(255), nullable = True)
    site_icon = Column(String(2083), nullable = True)
    hash = Column(String(255), nullable = True)
    charset = Column(String(20), nullable = True)
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())
    updated_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_published = Column(Boolean, nullable = False, default = False)
    user = relationship('User', backref='posts')

    def generate_sum(self):
        m = hashlib.md5()
        m.update(`self.title` + self.host)
        return m.hexdigest()


    def as_dict(self):
        post = {
                'id': self.id,
                'user_id': self.user_id,
                'title': self.title,
                'description': self.description,
                'image': self.image,
                'url': self.url,
                'host': self.host,
                'site_name': self.site_name,
                'site_icon': self.site_icon,
                'hash': self.hash,
                'charset': self.charset,
                'created_date': int(time.mktime(self.created_timestamp.timetuple())),
                'created_date': int(time.mktime(self.updated_timestamp.timetuple())),
                'is_published': self.is_published}
        return post

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable = False)
    comment = Column(Text, nullable = False)
    user = relationship('User')
    post = relationship('Post', backref='comments')
    created_timestamp = Column(DateTime(timezone=True), nullable = False, default=func.current_timestamp())

    def as_dict(self):
        comment = {
                'id': self.id,
                'user_id': self.user_id,
                'post_id': self.title,
                'comment': self.comment,
                'created_date': int(time.mktime(self.created_timestamp.timetuple()))
                }
        return comment