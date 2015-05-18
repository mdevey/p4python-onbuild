import os
import sys
from P4 import P4,P4Exception

# Create the P4 instance
p4 = P4()                        

#  (debugging)
#  print environment variables
#
def print_p4_env(name, default="<unset>"):
    global p4
    value = p4.env( name ) or default
    print ("p4.env('" + name + "'): " + value)

#  (debugging)
#  generic print of most p4.run* results, if it fails use print(info)
#
def print_p4(info, title=None):
  for entry in info:
      if title:
          print(entry[title] + "\t[" + title + "]");           
      for key in entry:          # and display all key-value pairs
          if(title and title == key):
              continue
          print("\t" + key + " = " + str(entry[key]))

#  (debugging)
#  print a file
#
def print_file(path):
    print("printing: " + path)
    f = open(path, 'r')
    print f.read()
    f.close()

#  (debugging)
#  Show p4 login credentials
#
def print_login_credentials():
    global p4
    print_p4_env('P4CONFIG')
    print_p4_env('P4PORT', "<unset default perforce:1666>")
    print_p4_env('P4USER')
    print_p4_env('P4PASSWORD')

    if os.path.isfile(p4.ticket_file):
        print("p4.ticket_file: " + p4.ticket_file)       
        print_file(p4.ticket_file)
        print("p4.run_tickets()")
        info = p4.run_tickets()
        print_p4(info)
    elif p4.env('P4PASSWORD') is None:
        print("p4.ticket_file: " + p4.ticket_file + " [Does Not Exist]")
        print "bind mount in ", p4.ticket_file, "or pass in P4PASSWORD (config or environment)"
        print "Without a login, abilities are normally limited\n"

    if os.path.isfile(p4.p4config_file):
      print("p4.p4config_file: " + p4.p4config_file);
      print_file('/root/.p4config')

#
#  Example command usage, print a user list known to the server
#
def print_user_list(limit):
    global p4
    print("=======================================================")
    print("= No login required to see user list, bug or feature :)")
    print("=======================================================")
    info = p4.run_users()   # Run "p4 users" (returns a dict)
    users = len(info)
    if(users > limit):
        print(str(users) + " users returned, only printing the first " + str(limit))
    print_p4(info[0:limit], 'User');
    
    user = p4.env('P4USER')
    if user:
        print("And this person:")
        info = p4.run_users([user])
        print_p4(info, 'User')
#
#  Example command usage, print recent changelists
#
def print_recent_changes(limit):
    print("=====================================================")
    print("= Show recent changes (requires login authentication)")
    print("=====================================================")
    opts = ['-m', limit]
    info = p4.run_changes(opts)
    print_p4(info, 'change')

    user = p4.env('P4USER')
    if user:
        info = p4.run_changes(opts + ['-u', user])
        if len(info) > 0 :
            print("Most recent changelists by you...")
            print_p4(info, 'change')
        else:
            print("There were no changes by you...")

def main():
    global p4
    try:
        p4.connect()
       
        print_login_credentials()

        print_user_list(2)

        print_recent_changes(1)

        p4.disconnect()  
    except P4Exception:
        for e in p4.errors:
            print(e)

if __name__ == '__main__':
    main()
