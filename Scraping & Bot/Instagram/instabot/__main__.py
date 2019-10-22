from instabot import InstaBot
import sys

def main():
    bot = InstaBot.load_config()
    if not (getattr(bot, "login") and getattr(bot, "password")):
        return print('You must inform your login and password in the config file')
    if getattr(bot, "unfollow"):
        bot.unfollow_profiles()
    else:
        bot.start()

if __name__ == '__main__':
    main()
