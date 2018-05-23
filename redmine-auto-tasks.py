#!/usr/bin/python
# -*- coding: utf-8 -*-
# self.name = "redmine-auto-tasks.py"
# self.author = "kyo1412@gmail.com"
# self.released = "2018-05-23"
# self.Server = redmine.org

import os
import base64
from redminelib import Redmine
import sys
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date

os.environ["NLS_LANG"] = ".UTF8"

def mail_remind_date():

	# Create list to save email and list issue
	buff_email=[]
	buff_issue=[]

	# Search all issue find issue where Remind Date is today

	for issue in redmine_connect.issue.all():

		# Check issue have Remind Date or Remind Date is exist
		if issue.custom_fields.get(1).value is not None:

			remind_date = issue.custom_fields.get(1).value

			# Check Remind Date is today
			if remind_date==date.today():

				# Assignee is exist
				if issue.assigned_to is None:

					# Create the first items on list
					if len(buff_email)==0:

						email=redmine_connect.user.get(issue.author.id).mail
						buff_email.extend([email])

						tmp = [issue.id]
						buff_issue.extend([tmp])

					else:
						check_exist = 0
						count_email=0

						# Check email is exist in buff_email
						while count_email<len(buff_email):

							email=redmine_connect.user.get(issue.author.id).mail

							if email==buff_email[count_email]:
								buff_issue[count_email].extend([issue.id])
								check_exist = 1
								count_email = len(buff_email)
								break
							else:
								check_exist = 0
								count_email += 1

						# Add new items to  buff_email
						if check_exist == 0:

							email=redmine_connect.user.get(issue.author.id).mail
							buff_email.extend([email])

							tmp = [issue.id]
							buff_issue.extend([tmp])

				else:

					# Issues have assignee
					if len(buff_email)==0:

						email=redmine_connect.user.get(issue.assigned_to.id).mail
						buff_email.extend([email])

						tmp = [issue.id]
						buff_issue.extend([tmp])
						#buff_issue[0].extend([issue.id])

					else:

						check_exist = 0
						count_email=0

						# Check email is exist in buff_email
						while count_email<len(buff_email):

							email=redmine_connect.user.get(issue.assigned_to.id).mail

							if email==buff_email[count_email]:

								buff_issue[count_email].extend([issue.id])
								check_exist = 1
								count_email = len(buff_email)
								break

							else:
								check_exist = 0
								count_email += 1

						# Add new items to  buff_email
						if check_exist == 0:

							email=redmine_connect.user.get(issue.assigned_to.id).mail
							buff_email.extend([email])

							tmp = [issue.id]
							buff_issue.extend([tmp])


	# Create email content
	count = 0
	while count<len(buff_email):

		recive_email = buff_email[count]
		subject = u"Nhắc nhở: Các Issues cần xử lý trong ngày hôm nay"
		content = u"""\
			Kính gửi anh/chị! <br/>
			Anh/Chị đã thiết lập Remind Date để hệ thống nhắc việc trong ngày hôm nay<br/>
			Các Issue cần xử lý:
			<br />
			"""

		# Add links issue to email content
		for tm_issue in buff_issue[count]:
			tmp = u"<a href=\"http://redmine.org/issues/"
			tmp += str(tm_issue)
			tmp += u"\">"
			tmp += redmine_connect.issue.get(tm_issue).subject
			tmp += u"</a> <br />"
			content += tmp

		content += u"<br /> <br /> Đây là email tự động, Mọi góp ý xin gửi về cho kyo1412@gmail.com"
		send_mail(recive_email, subject, content)
		count += 1


def send_mail(addr_to, subject, content):

	# Construct email
	# msg = MIMEMultipart('alternative') # Su dung khi dung ca text va html
	msg = MIMEText(content.encode('utf-8'), 'html', 'UTF-8')
	msg['Content-Type'] = "text/html; charset=utf-8"
	msg['To'] = addr_to
	msg['From'] = addr_from
	msg['Subject'] = subject

	try:
		# Send the message via an SMTP server
		mail_connect = smtplib.SMTP(base64.b64decode(smtp_server), 587)
		mail_connect.set_debuglevel(True)
		mail_connect.ehlo() # identify ourselves, prompting server for supported features

		### If we can encrypt this session, do it ###
		if mail_connect.has_extn('STARTTLS'):
			mail_connect.starttls()
			mail_connect.ehlo() # re-identify ourselves over TLS connection

		mail_connect.login(base64.b64decode(smtp_user), base64.b64decode(smtp_pass))
		try:
			mail_connect.sendmail(addr_from, addr_to, msg.as_string())
		finally:
			mail_connect.quit()
	except Exception, exc:
		sys.exit( "mail failed; %s" % str(exc) ) # give a error message

def auto_close_resolved_issue():
	# Auto close all issues which were resolved in lastweek
	for issue in redmine_connect.issue.all():
		if issue.status.name == "Resolved" and (date.today()-issue.updated_on.date()).days >= 7:
			issue.status_id=5
			issue.notes="Hệ thống tự động close issue \n Nếu issue chưa thực sự hoàn tất vui lòng reopen để tiếp tục thực hiện"
			issue.save()


#################################################################################################################
###########################################      Main funcion     ###############################################
#################################################################################################################
if __name__ == "__main__":
	keyauthen = <Your Redmine Key Authentication>
	server = <Your Redmine Server>
	redmine_connect = Redmine(server, key=keyauthen)

	# Define email addresses to use
	addr_from = <Your Email>
	# Define SMTP email server details
	smtp_server = <Your Email Server>
	smtp_user   = <Your Email Account>
	smtp_pass   = <Your Password>
	mail_remind_date()
	auto_close_resolved_issue()
