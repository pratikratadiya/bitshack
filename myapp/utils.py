import threading
from django.conf import settings

from django.core.mail import EmailMessage

class EmailThread(threading.Thread):
	def __init__(self,attachment,recipient):
		self.subject = 'Automated PDF report'
		self.recipient = recipient
		self.html_content = attachment
		threading.Thread.__init__(self)

	def run(self):
		msg = EmailMessage(self.subject, body='PFA Automated report generated',to=self.recipient)
		msg.content_subtype = "html"
		msg.attach('report_{}'.format(str(id))+'.pdf', self.html_content, "application/pdf")
		msg.send()

def send_html_email(attachment, recipient):
	EmailThread(attachment, recipient).start()