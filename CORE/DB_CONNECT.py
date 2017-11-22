#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from DB_TABLE import *


@DECO_SINGLETON()
class DB_CONNECT(object):
    def __init__(self,
                 # connection='sqlite:////Users/andyguo/Desktop/ssg.db',
                 connection='postgresql+psycopg2://postgres:More@TD_2017@core_db.more.com:5432/postgres',
                 echo=False,
                 isolation_level='READ COMMITTED'):
        self.connection = connection
        self.engine = create_engine(self.connection, echo=echo, isolation_level=isolation_level)
        self.smaker = sessionmaker(bind=self.engine)
        self.scope_smaker = scoped_session(sessionmaker(bind=self.engine))

    def create_db(self):
        DB_BASE.metadata.create_all(self.engine)

    def create_root_atom(self):
        first_session = None
        try:
            first_session = sess(new=true)
            if not first_session.query(ATOM).filter(ATOM.name == ROOT_ATOM_NAME).first():
                first_session.add(ATOM(name=ROOT_ATOM_NAME))
                first_session.commit()
        except:
            pass
        finally:
            first_session.close()

    def __call__(self, *args, **kwargs):
        if kwargs.get('new', False):
            return self.smaker()
        else:
            return self.scope_smaker()


sess = DB_CONNECT()

if __name__ == '__main__':
    engine = sess.engine
    sess.create_db()
    sess.create_root_atom()
    # smaker = sessionmaker(bind=engine)
    # session = DB_CONNECT.engine
    #
    # u1 = USER(name='guoxiaoao')
    # session().add(u1)
    #
    # v1 = VIEW()
    # session().add(v1)
    #
    # p1 = VIEW_PERMISSION(user_name=current_user)
    # v1.permissions.append(p1)
    #
    # session().commit()

    # d1 = DATA(name='A001C003_170212_R50X')
    # session().add(d1)
    # t1 = session().query(TAG).first()
    # d1.tags = [t1]
    # session().commit()

    # ss1 = SEARCH(search_param=str({'and': ['data;name;like;%C002%']}), search_target='tag')
    # sess().add(ss1)
    #
    # v1 = VIEW()
    # v1.searches.append(ss1)
    # sess().add(v1)
    #
    # sess().commit()

    u1 = USER(name='guoxiaoao')
    u2 = USER(name='test')

    sess().add_all([u1, u2])
    a1 = ATOM(name='aa')
    d1 = DATA(name='111', thumbnail=QImage('/Users/guoxiaoao/Desktop/Screen Shot 2017-11-16 at 17.27.56.png'))
    a1.datas.append(d1)
    a1.datas.append(d1)
    sess().add(a1)

    sess().commit()
    #
    # dd = sess().query(DATA).first()
    # print dd
    # dd_t = dd.thumbnail
    # print dd_t.size()

    # import sys
    # from PySide.QtCore import  *
    # from PySide.QtGui import *
    #
    # app = QApplication(sys.argv)
    # a = QLabel()
    # qq = QPixmap()
    # qq.convertFromImage(dd_t)
    # a.setPixmap(qq)
    # # mainWin = MainWindow()
    # a.show()
    # sys.exit(app.exec_())

    # a1 = sess().query(ATOM).get('63e60bde-ce6c-11e7-b362-0cc47a73af8f')
    # a2 = sess().query(ATOM).get('91db29d4-ce73-11e7-a656-f832e47271c1')
    #
    # ll = LINK(name='tt', parent=a1, target=a2)
    # sess().add(ll)
    # sess().commit()