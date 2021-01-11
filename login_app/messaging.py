from django.core.mail import send_mail

def email_password_reset(message_dict):
   contents = f"""
   Hi you, 
   Your token is: {message_dict['token']}
   1) Copy your token
   2) Please open the link in your browser: 'http://127.0.0.1:8000/accounts/set_new_password/'
   """
   send_mail(
      'Password Reset Token',
      contents,
      'sarigucki@gmail.com',
      [message_dict['email']],
      fail_silently=False
   )

def email_account_confirmation(message_dict):
   contents = f"""
   Hi welcome, 
   Thank you for signing up. 
   You can use your username: {message_dict['username']} and your password for logging in. 
   You can create a room or wait to be invited to a room.
   Make sure people in your kitchen know that you joined the app, so they can find and invite you.
   See you soon! 
   """
   send_mail(
      'Welcome',
      contents,
      'sarigucki@gmail.com',
      [message_dict['email']],
      fail_silently=False
   )