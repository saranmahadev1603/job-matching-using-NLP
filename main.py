from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from uuid import uuid4
from core import percentageCalc,convertText
import sqlite3
import pyperclip
from mailer import sendEmail 
class GUI:

    def __init__(self) -> None:
        self.conn = sqlite3.connect("data.db")        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS applications(
                id TEXT PRIMARY KEY NOT NULL, 
                name TEXT, 
                email TEXT,                 
                jobid TEXT,
                match REAL
            ); 
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY NOT NULL, 
                jobname TEXT, 
                jobdesc TEXT                             
            ); 
        """)
        self.main()

    def sendSelectedEmails(self):
        jobname = self.conn.execute("SELECT jobname FROM jobs WHERE id='{}' ".format(self.mwjobId.get())).fetchall()
        for mail in self.applicantsEmail:
            sendEmail(mail, "You have been shortlisted for the job - {}".format(jobname[0][0]))

    def matchViewWindow(self):
        sw = Toplevel()
        sw.title("Sorted Candidates")
        sw.resizable(False, False)

        self.applicantsTree = ttk.Treeview(sw)
        self.applicantsTree['columns'] = ('Name', 'Email', 'Match')
        self.applicantsTree.column('#0', width=0, stretch=NO)
        self.applicantsTree.column('Name', anchor=CENTER)
        self.applicantsTree.column('Email', anchor=CENTER)
        self.applicantsTree.column('Match', anchor=CENTER)

        self.applicantsTree.heading('#0', text='', anchor=CENTER)
        self.applicantsTree.heading('Name', text='Name', anchor=CENTER)
        self.applicantsTree.heading('Email', text='Email', anchor=CENTER)
        self.applicantsTree.heading('Match', text='Match', anchor=CENTER)

        data = self.conn.execute("SELECT * FROM applications WHERE jobid='{}' ".format(self.mwjobId.get())).fetchall()
        matchpercent = float(self.mwjobPercentage.get())

        self.applicantsEmail = []

        count = 0
        for applicant in data:
            if float(applicant[4]*100) >= float(matchpercent):
                self.applicantsTree.insert(parent='', index=count, iid=count, text='', values=(applicant[1],  applicant[2], applicant[4]*100))
                self.applicantsEmail.append(applicant[2])
            count += 1
        
        self.applicantsTree.pack()

        selectedEmailBtn = Button(sw,text="Send Selected Email", width=40, command  = self.sendSelectedEmails )
        selectedEmailBtn.pack()

        sw.mainloop()

    def viewJob(self,event, jobId = None):
        item = self.jobs.selection()
        for i in item:
            if jobId == None:
                jobId = self.jobs.item(i, "values")[0]
            
            vjtl = Toplevel()
            vjtl.resizable(False, False)

            vjtl.title("{} ".format(jobId))
            
            data = self.conn.execute("SELECT jobname,jobdesc FROM jobs WHERE id = '{}'".format(jobId)).fetchone()

            jobTitle = Label(vjtl, text=data[0], font=('Times 16'))
            jobTitle.pack()
            
            jobDesc = Message(vjtl, text= data[1])
            jobDesc.pack()

            jobIdCopyBtn = Button(vjtl, text = "Copy ID", command= lambda: pyperclip.copy(jobId))
            jobIdCopyBtn.pack()
            
            vjtl.mainloop()

    def jobsWindow(self):
        jobsPanel = Toplevel()
        jobsPanel.resizable(False,False)

        self.jobs = ttk.Treeview(jobsPanel)
        self.jobs['columns'] = ('ID', 'Name')
        self.jobs.column('#0', width=0, stretch=NO)
        self.jobs.column('ID', anchor=CENTER)
        self.jobs.column('Name', anchor=CENTER)

        self.jobs.heading('#0', text='', anchor=CENTER)
        self.jobs.heading('ID', text='ID', anchor=CENTER)
        self.jobs.heading('Name', text='Name', anchor=CENTER)

        cursor = self.conn.execute("SELECT id,jobname from jobs")
        count = 0
        for row in cursor:
            self.jobs.insert(parent='', index=count, iid=count, text='', values=(row[0],  row[1]))
            count+=1
        jobsPanel.bind("<Double-1>", self.viewJob)
        self.jobs.pack()

        jobsPanel.mainloop()

    def addJob(self):
        try:
            self.conn.execute("""
                INSERT INTO jobs(id, jobname, jobdesc)
                VALUES ('{}','{}','{}');
            """.format(
                uuid4().hex, 
                self.jobNameEntry.get(),
                self.jobDescEntry.get(1.0,END)
            ))

            self.conn.commit()
            messagebox.showinfo(message="Data Inserted Successfully!")
        
        except Exception as e:
            messagebox.showerror(message=e, title="Database Error!")

    def managerWindow(self):
        if self.managerPasswordEntry.get() == "admin":
            mw = Toplevel()
            mw.title("Manager")
            mw.resizable(False, False)
            mw.geometry("400x400")

            jobName = Label(mw,  text = "Job Name")
            jobName.place(relx = 0.2, rely = 0.05)

            self.jobNameEntry = Entry(mw , width = 40)
            self.jobNameEntry.place(relx = 0.2, rely = 0.10)

            jobDesc = Label(mw, text = "Job Description")
            jobDesc.place(relx = 0.2, rely = 0.15)

            self.jobDescEntry = Text(mw, width=30, height=10)
            self.jobDescEntry.place(relx = 0.2, rely = 0.20)

            jobEntryBtn =  Button(mw,  text = "Submit", width=15, command=self.addJob)        
            jobEntryBtn.place(relx = 0.2, rely = 0.62)

            mwjobIdLabel = Label(mw, text="Job ID:")
            mwjobIdLabel.place(relx = 0.1, rely=0.75)

            self.mwjobId = Entry(mw, width=32)
            self.mwjobId.place(relx = 0.2, rely=0.75)

            mwjobPercentageLabel = Label(mw, text = "Match(%):")
            mwjobPercentageLabel.place(relx = 0.05, rely =0.81)

            self.mwjobPercentage = IntVar()
            mwjobPercentageMatch = Spinbox(mw, from_ = 0,  to = 100, textvariable= self.mwjobPercentage)
            mwjobPercentageMatch.place(relx = 0.2, rely =0.81)
            self.mwjobPercentage.set(70)

            jobcheckbtn = Button(mw, text = "Jobs",  width=10 , command=self.jobsWindow)
            jobcheckbtn.place(relx = 0.7, rely = 0.74)

            viewBtn = Button(mw, text = "View", width=15, command=self.matchViewWindow)
            viewBtn.place(relx = 0.2, rely=0.86)

            mw.mainloop()

    def submission(self):
        desc = self.conn.execute("SELECT jobdesc FROM jobs WHERE id = '{}'".format(self.jobidEntry.get())).fetchone()[0]
        convertedText = convertText(self.location.get())
                
        match = percentageCalc((desc, convertedText))        

        self.conn.execute("""
            INSERT INTO applications(id,name,email,jobid,match)
            VALUES ('{}','{}','{}','{}','{}')
        """.format(
            uuid4().hex, self.nameEntry.get(),  
            self.emailEntry.get(), self.jobidEntry.get(), match
            )
        )
        self.conn.commit()

    def main(self):
        root = Tk()
        root.title("Apply Job")
        root.resizable(False, False)
        root.geometry("500x600")

        welcome =  Label(root, text="Apply For Job", font=('Times 14'))
        welcome.place(relx = 0.4, rely = 0.05)

        jobidLabel = Label(root, text = "Job ID")
        jobidLabel.place(relx = 0.2, rely = 0.15)

        self.jobidEntry = Entry(root, width= 40)
        self.jobidEntry.place(relx =  0.2, rely = 0.2)

        jobcheckbtn = Button(root, text = "Jobs",  width=10 , command=self.jobsWindow)
        jobcheckbtn.place(relx = 0.7, rely = 0.19)

        namelabel = Label(root, text = "Name:")
        namelabel.place(relx =  0.2, rely = 0.25)

        self.nameEntry = Entry(root , width = 40)
        self.nameEntry.place(relx = 0.2, rely = 0.3)

        emailLabel = Label(root, text = "Email")
        emailLabel.place(relx = 0.2, rely = 0.35)

        self.emailEntry = Entry(root, width=40)
        self.emailEntry.place(relx =  0.2, rely = 0.4)

        self.location = StringVar()
        resumeBtn =  Button(root, text = ">Upload Resume<" , width= 30, command= lambda : self.location.set(askopenfilename()))
        resumeBtn.place(relx = 0.2, rely = 0.45)

        submitBtn =  Button(root, text = "Submit" , width= 30, command = self.submission)
        submitBtn.place(relx = 0.2, rely = 0.50)
        
        managerPasswordLabel = Label(root, text = "Manager Password")
        managerPasswordLabel.place(relx = 0.2,  rely = 0.6)

        self.managerPasswordEntry  = Entry(root, width=40, show="#")
        self.managerPasswordEntry.place(relx=0.2,  rely=0.65)

        managerBtn =  Button(root, text = "Submit" , width= 30, command = self.managerWindow)
        managerBtn.place(relx = 0.2, rely = 0.70)
        
        root.mainloop()
    
    

if __name__ == "__main__":
    GUI()