import pandas as pd
from datetime import datetime, timedelta
import time
import schedule
## Email Modules
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pyodbc

### Database parameters
server = '168.62.210.62'
database = 'Protobase'
username = 'PowerBI'
password = 'H82&2w0)j&21!'
con = pyodbc.connect(
    'DRIVER={​​​​​​SQL Server}​​​​​​;SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)


def dfs_list():
    con_file = open('Containers.sql', 'r')
    cont_data = pd.read_sql_query(con_file.read(), con)
    con_file.close()
    route_file = open('Routes.sql', 'r')
    route_data = pd.read_sql_query(route_file.read(), con)
    route_file.close()
    df_ls = [cont_data, route_data]
    return df_ls


def save_excel(dfs_list, workbookname):
    with pd.ExcelWriter(workbookname) as writer:
        for i, data in enumerate(dfs_list):
            data.to_excel(writer, 'sheet%s' % i, index=False)
        writer.save()


### Sending Email
class send_mail():
    def __init__(self):
        pass

    def send_mail_excel(self, to, subject, workbookname):
        msg = MIMEMultipart()
        msg['From'] = 'reports@protoenergy.com'

        msg['To'] = to
        msg['Subject'] = subject
        msg['Cc'] = "dmuturi@protoenergy.com,"
        content = '''\
                            <html>
                            <head> 
                                <p>Dear Amanda</p>
                                <p> Please find attached the weekly Containers and route summary report. 
                                The report compares last weeks sales (from: {​​​​​​}​​​​​​ to: {​​​​​​}​​​​​​) and last months sales for the same period.
                                </p>
                            </head>
                            <body>
                                <p>Kind Regards,</p>
                                <p>Muturi</p>
                            </body>
                            </html>
                            '''.format(datetime.strftime(datetime.now() - timedelta(8), '%Y-%m-%d'),
                                       datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d'))
        msg.attach(MIMEText(content, "html", 'utf-8'))
        ### Attaching the excel
        Attachment = MIMEApplication(open(workbookname, "rb").read(), _subtype='txt')
        Attachment.add_header('Content-Disposition', 'attachment', filename=workbookname)
        msg.attach(Attachment)
        ## Sending the mail
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login("reports@protoenergy.com", "abc.1234")
            smtp.send_message(msg)
        print('message sent successfully')

    def run():
        df_ls = dfs_list()
        workbook = 'ContainerAndRoutesSummary.xlsx'

    save_excel(df_ls, workbook)
    send_mail().send_mail_excel(
        to='amanda@protoenergy.com',
        subject='Weekly Container and route sales',
        workbookname=workbook)


if __name__ == '__main__':
    schedule.every().monday.at('09:30').do(run)
    while True:
        schedule.run_pending()
        time.sleep(2)
