from replit import db

def name_parser(display_name: str) -> str :
    name = display_name
    if ("nickname_" + display_name in db.prefix("nickname_")):
        name = db["nickname_" + display_name]
    return name
    
    