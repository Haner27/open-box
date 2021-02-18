from io import BytesIO

from open_box.email import Mail
from open_box.email import Msg


def send_email():
    from_ = '<from>'
    host = '<host>'

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

        # define msg object
        msg = Msg()
        msg.set_sender(
            from_,
        ).set_receivers(  # receivers
            'han1@example.com',
            'han2@example.com',
        ).set_cc(  # receivers with
            'han3@example.com',
            'han4@example.com',
        ).set_bcc(  # receivers with secret
            'han5@example.com',
        ).set_subject(  # subject
            'good',
        ).set_body(  # body
            'i am haner27！！！',
        ).add_attachment(  # attachment
            f,
            'conf.yaml',
        )

        # send email
        with Mail(host=host) as email:
            email.send(msg)


if __name__ == '__main__':
    send_email()
