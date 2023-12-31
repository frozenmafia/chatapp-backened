from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String, TIMESTAMP, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    content = Column(String, nullable=False)

    # sender = relationship('User', foreign_keys=[sender_id], back_populates='messages_sent')
    # receiver = relationship('User', foreign_keys=[receiver_id], back_populates='messages_received')

    def __str__(self):
        return f"Message(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, type={self.type}, created_at={self.created_at}, content={self.content})"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    online = Column(Boolean, nullable=False, default=False)
    #
    # messages_sent = relationship('Message', foreign_keys=[Message.sender_id], back_populates='sender')
    # messages_received = relationship('Message', foreign_keys=[Message.receiver_id], back_populates='receiver')
    def __str__(self):
        return f"User(id={self.id}, email={self.email}, name={self.name}, created_at={self.created_at}, online={self.online})"




class UnreadMessageCount(Base):
    __tablename__ = "unread_message_counts"
    id = Column(Integer, primary_key=True, nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    count = Column(Integer, nullable=False, default=0)

    # sender = relationship('User', foreign_keys=[sender_id], back_populates='unread_message_counts_sent')
    # receiver = relationship('User', foreign_keys=[receiver_id], back_populates='unread_message_counts_received')

    # UniqueConstraint('sender_id', 'receiver_id')

    def __str__(self):
        return f"UnreadMessageCount(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, count={self.count})"
