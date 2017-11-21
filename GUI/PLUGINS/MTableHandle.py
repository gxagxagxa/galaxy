from GUI.QT import *
from CORE.DB_CONNECT import *


class MTable(object):
    _nameRegExp = QRegExp("^([a-z0-9\-]+)$")

    @classmethod
    def getORMFromName(cls, name, attr='label'):
        table = cls.tableObj()
        session = sess()
        orm = session.query(table).filter(getattr(table, attr, None) == name).first()
        return orm

    @classmethod
    def getORMFromSgId(cls, sg_id):
        table = cls.tableObj()
        session = sess()
        orm = session.query(table).filter(getattr(table, 'sg_id', None) == sg_id).first()
        return orm

    @classmethod
    def getORMListFromParent(cls, parentORM, onlyUser=False):
        if not parentORM: return []
        session = sess()
        ormList = getattr(parentORM, cls._attr_from_parent, None)
        ormList = [orm for orm in ormList if orm.active]
        return ormList

    @classmethod
    def getORMListFromProject(cls, projectORM, onlyUser=False):
        table = cls.tableObj()
        session = sess()
        ormList = session.query(table).filter(table.project == projectORM).all()
        ormList = [orm for orm in ormList if orm.active]
        return ormList

    @classmethod
    def getORMListFromGlobal(cls, onlyUser=False):
        table = cls.tableObj()
        session = sess()
        ormList = session.query(table).all()
        ormList = [orm for orm in ormList if orm.active]
        return ormList

    @classmethod
    def tableName(cls):
        return cls.__name__[len('M'):].upper()

    @classmethod
    def tableObj(cls):
        return globals()[cls.tableName()]

    @classmethod
    def validateName(cls, name):
        nameValidator = QRegExpValidator(cls._nameRegExp)
        result, _, _ = nameValidator.validate(name, 0)
        return bool(result == QValidator.Acceptable)

    @classmethod
    def validateExist(cls, name, parentORM, attr='name'):
        session = sess()
        table = globals()[cls.tableName()]
        ORMs = session.query(table).filter(and_(getattr(table, attr, None) == name, table.parent == parentORM)).all()
        return bool(ORMs)

    @classmethod
    def inject(cls, *args, **kwargs):
        session = sess()
        table = globals()[cls.tableName()]
        orm = table(*args, **kwargs)
        session.add(orm)
        session.commit()
        return orm

    @classmethod
    def update(cls, orm, **kwargs):
        session = sess()
        for attr, value in kwargs.iteritems():
            print attr, value
            setattr(orm, attr, value)
        session.commit()
        return orm

    @classmethod
    def delete(cls, orm):
        session = sess()
        session.delete(orm)
        session.commit()

    @classmethod
    def active(cls, orm, flag):
        session = sess()
        orm.active = flag
        session.commit()
        return orm


class MAtom(MTable):
    _nameRegExp = QRegExp("^([a-z0-9\-]_\.+)$")

    @classmethod
    def canDelete(cls, orm):
        children = orm.sub_atoms.all()
        if len(children) >= 1:
            return False
        else:
            return True


class MData(MTable):
    _nameRegExp = QRegExp("^([a-z0-9\-]_\.+)$")

    @classmethod
    def canDelete(cls, orm):
        return True
