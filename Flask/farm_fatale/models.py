from typing import Optional
import datetime
import decimal

from sqlalchemy import CHAR, DECIMAL, DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = 'device'
    __table_args__ = (
        Index('device_id', 'device_id', unique=True),
    )

    device_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(CHAR(5), nullable=False)
    device_name: Mapped[str] = mapped_column(String(50), nullable=False)
    device_type: Mapped[str] = mapped_column(String(30), nullable=False)
    create_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String(255))

    device_status: Mapped[list['DeviceStatus']] = relationship('DeviceStatus', back_populates='device')
    manual_control: Mapped[list['ManualControl']] = relationship('ManualControl', back_populates='device')
    sensor: Mapped[list['Sensor']] = relationship('Sensor', back_populates='device')
    auto_control: Mapped[list['AutoControl']] = relationship('AutoControl', back_populates='device')


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('email_address', 'email_address', unique=True),
        Index('password', 'password', unique=True),
        Index('user_id', 'user_id', unique=True)
    )

    user_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email_address: Mapped[str] = mapped_column(String(320), nullable=False)
    user_tel: Mapped[str] = mapped_column(CHAR(11), nullable=False)
    admin_level: Mapped[int] = mapped_column(TINYINT(1), nullable=False)
    create_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    manual_control: Mapped[list['ManualControl']] = relationship('ManualControl', back_populates='user')
    admin_value: Mapped[list['AdminValue']] = relationship('AdminValue', back_populates='user')


class DeviceStatus(Base):
    __tablename__ = 'device_status'
    __table_args__ = (
        ForeignKeyConstraint(['device_seq'], ['device.device_seq'], name='device_status_ibfk_1'),
        Index('device_seq', 'device_seq')
    )

    status_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    device_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    device_active: Mapped[int] = mapped_column(TINYINT(1), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    device: Mapped['Device'] = relationship('Device', back_populates='device_status')


class ManualControl(Base):
    __tablename__ = 'manual_control'
    __table_args__ = (
        ForeignKeyConstraint(['device_seq'], ['device.device_seq'], name='manual_control_ibfk_2'),
        ForeignKeyConstraint(['user_seq'], ['user.user_seq'], name='manual_control_ibfk_1'),
        Index('device_seq', 'device_seq'),
        Index('user_seq', 'user_seq')
    )

    m_control_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    user_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    device_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    actuator_state: Mapped[int] = mapped_column(TINYINT(1), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    device: Mapped['Device'] = relationship('Device', back_populates='manual_control')
    user: Mapped['User'] = relationship('User', back_populates='manual_control')


class Sensor(Base):
    __tablename__ = 'sensor'
    __table_args__ = (
        ForeignKeyConstraint(['device_seq'], ['device.device_seq'], name='sensor_ibfk_1'),
        Index('device_seq', 'device_seq')
    )

    sensor_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    device_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    value_code: Mapped[str] = mapped_column(CHAR(4), nullable=False)
    unit_code: Mapped[Optional[str]] = mapped_column(CHAR(10))
    value_range: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))

    device: Mapped['Device'] = relationship('Device', back_populates='sensor')
    admin_value: Mapped[list['AdminValue']] = relationship('AdminValue', back_populates='sensor')
    auto_control: Mapped[list['AutoControl']] = relationship('AutoControl', back_populates='sensor')
    control: Mapped[list['Control']] = relationship('Control', back_populates='sensor')
    device_log: Mapped[list['DeviceLog']] = relationship('DeviceLog', back_populates='sensor')


class AdminValue(Base):
    __tablename__ = 'admin_value'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_seq'], ['sensor.sensor_seq'], name='admin_value_ibfk_2'),
        ForeignKeyConstraint(['user_seq'], ['user.user_seq'], name='admin_value_ibfk_1'),
        Index('sensor_seq', 'sensor_seq'),
        Index('user_seq', 'user_seq')
    )

    admin_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    user_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    sensor_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    min: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    max: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    sensor: Mapped['Sensor'] = relationship('Sensor', back_populates='admin_value')
    user: Mapped['User'] = relationship('User', back_populates='admin_value')


class AutoControl(Base):
    __tablename__ = 'auto_control'
    __table_args__ = (
        ForeignKeyConstraint(['device_seq'], ['device.device_seq'], name='auto_control_ibfk_2'),
        ForeignKeyConstraint(['sensor_seq'], ['sensor.sensor_seq'], name='auto_control_ibfk_1'),
        Index('device_seq', 'device_seq'),
        Index('sensor_seq', 'sensor_seq')
    )

    a_control_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    device_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    actuator_state: Mapped[int] = mapped_column(TINYINT(1), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    sensor_seq: Mapped[Optional[int]] = mapped_column(INTEGER(11))

    device: Mapped['Device'] = relationship('Device', back_populates='auto_control')
    sensor: Mapped[Optional['Sensor']] = relationship('Sensor', back_populates='auto_control')


class Control(Base):
    __tablename__ = 'control'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_seq'], ['sensor.sensor_seq'], name='control_ibfk_1'),
        Index('sensor_seq', 'sensor_seq')
    )

    control_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    sensor_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    control_mode: Mapped[int] = mapped_column(TINYINT(1), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    sensor: Mapped['Sensor'] = relationship('Sensor', back_populates='control')


class DeviceLog(Base):
    __tablename__ = 'device_log'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_seq'], ['sensor.sensor_seq'], name='device_log_ibfk_1'),
        Index('sensor_seq', 'sensor_seq')
    )

    log_seq: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    sensor_seq: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    device_value: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    min: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    max: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    sensor: Mapped['Sensor'] = relationship('Sensor', back_populates='device_log')
