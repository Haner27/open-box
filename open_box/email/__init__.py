import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Msg:
    BASE_MSG_OPTIONS = ('From', 'To', 'Subject')
    RECEIVERS_OPTIONS = ('To', 'Cc', 'Bcc')

    def __init__(self):
        self.__msg = MIMEMultipart()

    @property
    def content(self):
        return self.__msg.as_string()

    @property
    def from_(self):
        if 'From' not in self.__msg:
            return None
        return self.__msg['From']

    @property
    def all_receivers(self):
        recvs = set()
        for k in self.RECEIVERS_OPTIONS:
            if k in self.__msg:
                val = self.__msg[k]
                for receiver in val.split(';'):
                    recvs.add(receiver)
        return list(recvs)

    def set_sender(self, sender):
        self.__msg['From'] = sender
        return self

    def set_receivers(self, *receivers):
        self.__msg['To'] = ';'.join(set(receivers))
        return self

    def set_subject(self, subject):
        self.__msg['Subject'] = Header(subject, 'utf-8')
        return self

    def set_cc(self, *cc):
        self.__msg['Cc'] = ';'.join(set(cc))
        return self

    def set_bcc(self, *bcc):
        self.__msg['Bcc'] = ';'.join(set(bcc))
        return self

    def set_body(self, body):
        self.__msg.attach(MIMEText(body, 'plain', 'utf-8'))
        return self

    def set_html_body(self, html):
        self.__msg.attach(MIMEText(html, 'html', 'utf-8'))
        return self

    def add_attachment(self, io, attachment_name):
        att = MIMEApplication(io.getvalue())
        att.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        self.__msg.attach(att)
        io.seek(0)
        return self

    def validate(self):
        for k in self.BASE_MSG_OPTIONS:
            if k not in self.__msg:
                return False, f'msg lack [{k}] option'
        return True, None


class Mail:
    def __init__(self, host, usr=None, pwd=None):
        self.__host = host  # 邮件服务
        self.__usr = usr
        self.__pwd = pwd
        self.__smtp = None

    def send(self, msg):
        code, err = msg.validate()
        if not code:
            raise Exception(err)

        self.__smtp.sendmail(
            msg.from_,
            msg.all_receivers,
            msg.content,
        )

    def __enter__(self):
        self.__smtp = smtplib.SMTP()
        self.__smtp.connect(self.__host)
        if self.__usr and self.__pwd:
            self.__smtp.login(self.__usr, self.__pwd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == smtplib.SMTPException:
            raise exc_val
        self.__smtp.close()
