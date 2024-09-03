import mysql.connector as sqltor
from tabulate import tabulate
import csv
from datetime import datetime
import sys
#imported necessary modules required for the program

try:
    f=open("transactions.csv","r",newline="")
except:
    f=open("transactions.csv","w",newline="")
#Creates a csv file (if it doesn't exist) to store transactions

f=open("transactions.csv", "r",newline="")  
r=csv.reader(f)
L=[]
for i in r:
    L+=[i]
header=["Date and Time","Username","Amount","Description","Recipient"]
if header not in L:
    f=open("transactions.csv","w",newline="")
    df=csv.writer(f)
    df.writerow(header)
    f.close()
else:
    f.close()
#Adds required header (if it doesn't exist) to the csv file        
                  
_pswd=input('mysql Password:')
try:       #IF DATABASE BANK EXISTS
    mycon=sqltor.connect(host="localhost",user="root",passwd=_pswd ,database="bank",charset="utf8")
    print("Succesfully connected to Database")
    cursor=mycon.cursor(buffered=True)
except:     #IF DATABASE BANK DOES NOT EXIST
    mycon=sqltor.connect(host="localhost",user="root",passwd=_pswd ,charset="utf8")
    cursor=mycon.cursor(buffered=True)
    cursor.execute("create database bank")
    mycon.commit()
    cursor.execute("use bank")
    mycon.commit()
    print("Successfully Connected to Database")
#Established connection with the database "bank"

cursor.execute('create table if not exists UserDetails (Name varchar(30), UserName varchar(25) primary key,DateOfBirth date, Gender char(10), Age int, Password varchar(30) not null ,Balance int)')
#Creates table UserDetails to store user data

def SignUp(): #Function defined to register a user who is using the system for the first time
    import datetime
    global UserName
    Name=input("Enter your name:")
    date1=input("Enter date of birth in YYYY-MM-DD format:")
    year, month, day = map(int, date1.split('-'))
    DateOfBirth=datetime.date(year,month,day)
    Gender=input("Gender(M/F/Others):")
    Age=int(input("Enter age:"))
    Balance=0 #Person with new account starts with an account balance of 0

    UserName=input("Enter a username:")
    cursor.execute("Select UserName from UserDetails")
    checkUserName=cursor.fetchall()
    for i in checkUserName: #Following code ensures that username is unique and isnt already in use
        while True:
            if i==(UserName,):       
                UserName=input("Username already exists,Try again:")
            else:       
                break       
        
    Password=input("Enter a password:")
    st1="Insert into UserDetails values(%s,%s,%s,%s,%s,%s,%s)"
    val1=(Name,UserName,DateOfBirth,Gender,Age,Password,Balance)
    cursor.execute(st1,val1)
    mycon.commit()
    print("Sign Up complete!")
    print("")
    print("Welcome", Name)
    return UserName

def Add(): #Function defined to deposit money to a User's account
    rU=UserName
    i=int(input("Enter Amount to be deposited:"))
    if i>0: #checking if entered value is negative  
        st2="Update UserDetails set Balance=Balance+%s where UserName=%s" 
        val2=(i,rU)
        cursor.execute(st2,val2)
        mycon.commit()
        print("Money Successfully deposited!")
        print("")
    
        now = datetime.now() #Inputing transaction to csv file
        dandt=now.strftime("%d/%m/%Y %H:%M:%S")
        val=(dandt,rU,i,"deposited","------")
        with open("transactions.csv","a",newline="") as f:
            df=csv.writer(f)
            df.writerow(val)
          
    else:
        print("Invalid amount")
        print("")     



def Withdraw(): #Function defined to withdraw money from a User's account
    rU=UserName
    i=int(input("Enter Amount to be withdrawn:"))
    st9="Select Balance from UserDetails where UserName=%s"
    val9=(rU,)
    cursor.execute(st9,val9)
    chb=cursor.fetchone()
    if chb[0]==0: #Following code checks wether the User's account balance is 0
        print("Account balance is 0, No more money can be withdrawn")
        print("")

    else:
        poorcheck="select Balance from UserDetails where username=%s"
        val=(rU,)
        cursor.execute(poorcheck,val)
        p=cursor.fetchall()
        for cash in p:  #Following code checks if you're trying to withdraw more money than you have in the account
            while True:
                if cash[0]<i:
                    ask=input("Insufficient balance, Would you like to continue?(YES/NO):")
                    if ask=="YES":
                        i=int(input("Enter Amount:"))
                    else:
                        break
                else:
                    ask="YES"
                    break
        if i>0:   #checking if negative amount is entered     
            if ask=="YES": 
                st3="Update UserDetails set Balance=Balance-%s where UserName=%s"
                val3=(i,rU)
                cursor.execute(st3,val3)
                mycon.commit()
                print("Money Successfully withdrawn!")
                print("")

                now = datetime.now() #Inputing transaction to csv file
                dandt=now.strftime("%d/%m/%Y %H:%M:%S")
                val=(dandt,rU,i,"withdrew","------")
                with open("transactions.csv","a",newline="") as f:
                    df=csv.writer(f)
                    df.writerow(val)

            else:
                print("Withdraw Unsuccesful") 
                print("")
        else:
            print("Invalid amount")
            print("")   
        

def CheckBalance(): #Function defined to check a User's account balance
    rU=UserName
    st4="Select Balance from UserDetails where UserName=%s"
    val4=(rU,)
    cursor.execute(st4,val4)
    b=cursor.fetchone()
    print("Your Balance is",b[0])
    print("")

def CheckUserDetails(): #Function defined to check a User's account details
    rU=UserName
    st5="Select * from UserDetails where UserName=%s"
    val5=(rU,)
    cursor.execute(st5,val5)
    cud=cursor.fetchall()
    print("Your details:")
    print(tabulate(cud,headers=["Name","UserName","DOB","Gender","Age","Password","Balance"]))
    print("")

def Login(): #Function defined for an existing User to interact with the database
    global UserName
    u=input("Enter Username:")
    p=input("Enter Password:")
    st6="Select UserName from UserDetails"
    cursor.execute(st6)
    uf=cursor.fetchall()
    while True: #Following set of codes checks wether the username exists in the database
        if (u,) not in uf:
            u=input("Incorrect Username, Try again:")
        else:
            break    
    st7="Select Password from UserDetails where UserName=%s"
    val7=(u,)
    cursor.execute(st7,val7)
    up=cursor.fetchone()
    while True: #Following set of codes checks wether the password entered matches the one in the database
        if up!=(p,):
            p=input("Incorrect Password, Try again:")
        else:
            break    

    st8="Select Name from UserDetails where UserName=%s"
    cursor.execute(st8,val7)
    Name=cursor.fetchone()
    print("")
    print("Welcome",Name[0])
    print("")
    UserName=u
    return UserName

def TransferMoney(): #Function to send money to another User
    rU=UserName
    stpoorcheck="select Balance from userdetails where username=%s"
    val=(rU,)
    cursor.execute(stpoorcheck,val)
    bal=cursor.fetchall()
    for i in bal: #To check if person has 0 account balance
        if i[0]==0:
            print("Account balance is 0, cannot transfer money")
        else:
            x=input("Enter username of User to send money to:")
            st6="Select UserName from UserDetails"
            cursor.execute(st6)
            uf=cursor.fetchall()
            if (x,) in uf: #To check if given username of user is real
                    am=int(input("Enter amount to be transferred:"))
                    while True:
                        if i[0]<am: #To check if entered amount is more than account balance
                            ask=input("You have Insufficient balance,would you like to continue?(YES/NO):")
                            if ask=="YES":
                                am=int(input("Enter amount:"))
                            else:
                                break
                        else:
                            ask="YES"
                            break
                    if am>0:#To check if entered amount is valid
                        if ask=="YES":
                            st10="Update UserDetails set Balance=Balance-%s where UserName=%s"
                            val10=(am,rU)
                            cursor.execute(st10,val10)
                            mycon.commit()
                            st11="Update UserDetails set Balance=Balance+%s where UserName=%s"
                            val11=(am,x)
                            cursor.execute(st11,val11)
                            mycon.commit()
                            print("Successfully Transferred")
                            print("")

                            now = datetime.now() #Inputing transaction to csv file
                            dandt=now.strftime("%d/%m/%Y %H:%M:%S")
                            val=(dandt,rU,am,"transferred",x)
                            with open("transactions.csv","a",newline="") as f:
                                df=csv.writer(f)
                                df.writerow(val)
                
                        else:
                            print("Transfer unsuccessful")
                            print("")    
                    else:
                        print("Invalid amount")
                        print("")
            else:
                print("User not found")
                print("")

def DeleteAccount(): #Function to delete account of the User
    rU=UserName
    confirm=input("Are you sure you want to delete your account ?(YES/NO):") #Confirmation
    if confirm=="YES":
        confirm2=input("Confirm password to continue:") #2nd level of confirmation
        st7="Select Password from UserDetails where UserName=%s"
        val7=(rU,)
        cursor.execute(st7,val7)
        up=cursor.fetchone()
        if up!=(confirm2,):
                print("Incorrect Password, Account deletion unsuccessful")
                print("")
        else:
                st12=("Delete from UserDetails where UserName=%s")
                val12=(rU,)
                cursor.execute(st12,val12)
                mycon.commit()
                sys.exit("Your account has been deleted")
    else:
        print("Account deletion cancelled")
        print("")
                
print("")
print("Hello!")
print("1.Login")
print("2.Sign Up")
print(" ")
x=int(input("Enter option:"))
if x==1:
    Login()
    while True:
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Check Balance")
        print("4. Check User Details")
        print("5. Transfer money")
        print("6. Delete Account")
        print("7. Quit")
        y=int(input("Enter Option:"))
        print("")
        if y==1:
            Add()
        elif y==2:
            Withdraw()
        elif y==3:
            CheckBalance()
        elif y==4:
            CheckUserDetails()
        elif y==5:
            TransferMoney()
        elif y==6:
            DeleteAccount()
        elif y==7:
            print("Thank You for choosing PROJECT BANK! See you soon!")
            break
        else:
            print("Invalid Option")
    
        
elif x==2:
    SignUp()
    while True:
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Check Balance")
        print("4. Check User Details")
        print("5. Transfer money")
        print("6. Delete account")
        print("7. Quit")
        y=int(input("Enter Option:"))
        print("")
        if y==1:
            Add()
        elif y==2:
            Withdraw()
        elif y==3:
            CheckBalance()
        elif y==4:
            CheckUserDetails()
        elif y==5:
            TransferMoney()
        elif y==6:
            DeleteAccount()
        elif y==7:
            print("Thank You for choosing PROJECT BANK! See you soon!")
            break
        else:
            print("Invalid Option")

else:
    print("Invalid Option")
    
        




