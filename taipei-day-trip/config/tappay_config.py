import os


def get_tappay_config():
    return {
        "APP_ID": os.getenv("TAPPAY_APP_ID"),
        "APP_KEY": os.getenv("TAPPAY_APP_KEY"),
        "environment": "sandbox"   #本番環境ならproduction
    }