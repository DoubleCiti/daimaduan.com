from mailthon import email
from mailthon.middleware import TLS, Auth
from mailthon.postman import Postman

from daimaduan.bootstrap import celery


SENDER = 'noreply.daimaduan@gmail.com'


@celery.task
def send_email(config, user_email, subject, content):
    envelope = email(sender=SENDER,
                     receivers=[user_email],
                     subject=subject,
                     content=content)

    postman = Postman(host=config['host'],
                      port=int(config['port']),
                      middlewares=[TLS(force=True),
                                   Auth(username=config['username'], password=config['password'])])

    postman.send(envelope)
