import mysql_handler as localsql
import datetime, json

def strDateToPython(date):
    return datetime.datetime.strptime(date.replace('"', ""), '%Y-%m-%dT%H:%M:%S.%f')

def pythonToStrDate(d):
    return json.dumps(d.isoformat())

def verify_session(srid, ip):
    res = localsql.fetchone("SELECT * FROM sessions WHERE `sr:id` = %s", srid)
    if res['success'] and res['results']:
        
        if res['results'][2] == ip and strDateToPython(res['results'][4]) > datetime.datetime.now():
            # we're good, the user is cool
            
            localsql.execute("UPDATE sessions SET expiry = %s WHERE `sr:id` = %s", True, False, pythonToStrDate(datetime.datetime.now() + datetime.timedelta(days=1)), srid)
            
            return res['results'][0]
        
        else:
            # huh, has the session but expired or wrong ip? In both situations, let's just delete the session, hey?
            
            localsql.execute("DELETE FROM sessions WHERE `sr:id` = %s", True, False, srid)
            
            return False
        
    else:
        return str(res)

def get_user(method, value):
    res = localsql.fetchone("SELECT * FROM users WHERE " + method + " = %s", value)
    if res['success']:
        if res['results']:
            
            ret = localsql.fetchone("SELECT * FROM users_public WHERE `ur:id` = %s", res['results'][0])
            if ret['success'] and ret['results']:
                
                return {"ur:id": res['results'][0], "u:id": res['results'][1], "email": res['results'][2], "avatar": ret['results'][1], "credits": ret['results'][2], "creation": ret['results'][3]}
                
            else:
                return False
            
        else:
            return False
        
    else:
        return False