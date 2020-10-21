from io import BytesIO

from open_box.email import Mail
from open_box.email import Msg


def send_email():
    from_ = 'no-reply@17zuoye.com'
    host = 'smtp.dc.17zuoye.net'

    with BytesIO() as f:
        s = b"""mongodb:
  database_url: mongodb://xxxxxxxxxxxxx
  database_name: yyyyyyyyyyy
elasticsearch:
  hosts: ["127.0.0.1:9200", "127.0.0.1:9201"]
mysql:
  host: mysql+pymysql://zzzzzzzzzzzz
    """
        f.write(s)
        f.seek(0)

        # 制定邮件信息
        msg = Msg()
        msg.set_sender(
            from_,
        ).set_receivers(  # 收件人
            'han1@example.com',
            'han2@example.com',
        ).set_cc(  # 抄送
            'han3@example.com',
            'han4@example.com',
        ).set_bcc(  # 秘密抄送
            'han5@example.com',
        ).set_subject(  # 主题
            '淦',
        ).set_body(  # 内容
            '来，一起淦！！！',
        ).add_attachment(  # 附件
            f,
            'conf.yaml',
        )

        # 发送邮件
        with Mail(host=host) as email:
            email.send(msg)


if __name__ == '__main__':
    send_email()
