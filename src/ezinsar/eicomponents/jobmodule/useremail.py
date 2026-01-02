#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the emails for an EZ-InSAR processing. 

The module allows to control the email sending for an EZ-InSAR processing. 
    
    (From `ezinsar` package)

Changelog:
    * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

################################################################################
## FUNCTIONS
################################################################################
def send_email(job,
    step,
    error,
    listfile = None
    ):
    """Send an email with the bot 

    The function sends an email for an EZ-InSAR processing. 

    Args:
        job: `ezinsar` processing class
        step (str): Name of the step processing
        error (bool): error mode. Can be ``True`` or ``False`` 
        listfile (list of str or None): List of attached files [Default: ``None``]. 
    
    """
    
    message = MIMEMultipart("alternative")
    message["From"] = job.email['sender']['value']
    message["To"] = job.email['receiver']['value']

    if 'coregistration' in str(type(job)):
        mode = 'Coregistration'
    elif 'ifgstack' in str(type(job)):
        mode = 'Interferometric-stack'
    elif 'intstack' in str(type(job)):
        mode = 'Intensity-stack'
    elif 'tsprocessing' in str(type(job)):
        mode = 'TS-analysis'
    elif 'offsetprocessing' in str(type(job)):
        mode = 'Offset-tracking processing'
    else: 
        mode = 'UNKNOWN'
    
    message["Subject"] = "EZ-InSAR processing: %s" % (mode)

    if error: 
        modeerror = '<b>ABNORMAL termination</b>. Please check the verbose/log to understand the issue(s)</b>.'
    else:
        modeerror = '<b>normal termination</b>'
                        
    html = """\
    <html>
    <body>
        <p><b>Dear EZ-InSAR user,</b><br>
        <p></p>
        You have been launched a %s processing named <b>%s</b>.<br>
        <p>The <b>%s</b> step has been finished with a/an %s.</p>
        <p></p>
        <p>Kind regards,</p>
        <p></p>
        <p>EZ-InSAR bot</p>
    </body>
    </html>
    """ % (mode,job.title,step,modeerror)
    
    message.attach(MIMEText(html, "html"))

    for fi in listfile:
        filename1 = fi
        attachment1 = open(fi, "rb")
        p1 = MIMEBase('application', 'octet-stream')
        p1.set_payload((attachment1).read())
        encoders.encode_base64(p1)
        p1.add_header('Content-Disposition', "attachment; filename= %s" % fi)
        message.attach(p1)

    ## Send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(job.email['SMTPserver']['value'], job.email['SMTPport']['value'], context=context) as server:
        server.login(job.email['sender']['value'], job.email['password']['value'])
        server.sendmail(job.email['sender']['value'], job.email['receiver']['value'], message.as_string())