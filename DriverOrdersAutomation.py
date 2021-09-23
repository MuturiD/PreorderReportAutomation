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


class SendMail():
    def __init__(self):
        self.server = 'proto-os.database.windows.net'
        self.database = 'Protocore'
        self.username = 'Protocore'
        self.password = 'Base64_encoding'
        self.con = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        self.cursor = self.con.cursor()

    def read_sql(self):
        qry = ''' EXEC DriverOrderListing '''
        data = self.cursor.execute(qry)
        cols = [i[0] for i in data.description]
        res = [dict(zip(cols, row)) for row in data.fetchall()]
        return res

    def create_excel(self, workbookname):
        data = pd.DataFrame.from_dict(self.read_sql())
        ### Formating the dataframe to an excel Table
        cols = [{"header": col} for col in data.columns]
        (max_row, max_col) = data.shape
        writer = pd.ExcelWriter(f'{workbookname}.xlsx', engine='xlsxwriter')
        data.to_excel(writer, sheet_name='Report', startrow=1, header=False, index=False)
        worksheet = writer.sheets['Report']
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': cols})
        worksheet.set_column(0, max_col - 1, 12)
        writer.save()

    def send_mail_excel(self, to, subject, workbookname):
        msg = MIMEMultipart()
        msg['From'] = 'reports@protoenergy.com'
        msg['To'] = to
        msg['Subject'] = subject
        msg['Cc'] = "dmuturi@protoenergy.com,"
        content = '''\
                            <html>
                            <head> 
                                <p>Hey,</p>
                                <p> Find Attached the Drivers orders as of {}. 
                                </p>
                            </head>
                            <body>
                                <p>Thanks</p>
                            </body>
                            </html>
                            '''.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'))
        msg.attach(MIMEText(content, "html", 'utf-8'))
        ### Attaching the excel
        Attachment = MIMEApplication(open(f'{workbookname}.xlsx', "rb").read(), _subtype='txt')
        Attachment.add_header('Content-Disposition', 'attachment', filename=f'{workbookname}.xlsx')
        msg.attach(Attachment)
        ## Sending the mail
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login("reports@protoenergy.com", "abc.1234")
            smtp.send_message(msg)
        print('message sent successfully')

def run() -> object:
    # df_ls = SendMail()
    workbook = 'DriversOrders'
    SendMail().create_excel(workbook)
    SendMail().send_mail_excel(
        to='iwaihiga@protoenergy.com,mkitio@protoenergy.com,vmuthithi@protoenergy.com',
        subject='Hourly Drivers Orders',
        workbookname=workbook)


## Test Zone
if __name__ == '__main__':
    schedule.every().hour.at(":00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(3)