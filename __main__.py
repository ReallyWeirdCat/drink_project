import os, time, datetime, json
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer

import config
from storage import Database

hostName   = config.hostname
serverPort = config.port
__location__ = os.getcwd()

DB = Database("test_db", "default_db_template")

class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
    
        user_ip = self.client_address[0]
        user = None
        if DB.exists("users", user_ip):
        
            user = DB.get("users", user_ip)
            
            current_visits = user["visits"]
            cooldown = user["visit_cooldown"]
            
            if time.time() > cooldown:
            
                user["visit_cooldown"]=time.time()+60
                user["visits"]+=1
            
                DB.set("users", user_ip, val=user)
            
        else:
        
            DB.set("users", user_ip, val={
                    "name": "User",
                    "visits": 1,
                    "visit_cooldown": time.time()+60,
                    "cheers": []
                }
            )
    
        request = self.path.split("/")
    
        #main page
        if request[1] == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            with open(os.path.join(__location__, "html", "index.html"), encoding="utf-8") as f:
                data = f.read()
            
            self.wfile.write(bytes(data, "utf-8"))
            return
        elif request[1] == "about":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            with open(os.path.join(__location__, "html", "about.html"), encoding="utf-8") as f:
                data = f.read()
            
            self.wfile.write(bytes(data, "utf-8"))
            return
        elif request[1] == "api":
        
            args = request[2:]
            if args[0] == "getreason":
            
                dt = datetime.datetime.now()
                month = str(dt.month)
                day = str(dt.day)
                
                answer = {
                    "title": "Повода нет",
                    "description": "Извините, кажется мы не успели добавить повод на текущий день.",
                    "cheers": None,
                    
                    "OK": True
                }
                
                if DB.exists("data", "drink_reasons", "month", month, day):
                
                    answer = DB.get("data", "drink_reasons", "month", month, day)
                
                answer["visits"]=user["visits"]
                answer["liked"] = [str(month), str(day)] in DB.get("users", user_ip, "cheers")
                answer["OK"]=True
                json_object = json.dumps(answer)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers(
                )
                self.wfile.write(bytes(json_object, "utf-8"))
            elif args[0] == "like":
            
                user = DB.get("users", user_ip)
                
                dt = datetime.datetime.now()
                month = str(dt.month)
                day = str(dt.day)
                
                if DB.exists("data", "drink_reasons", "month", month, day):
                
                    day_obj = DB.get("data", "drink_reasons", "month", month, day)
                    month_day = [month, day]
                    
                    if month_day in user["cheers"]:
                        user["cheers"].remove(month_day)
                        day_obj["cheers"]-=1
                    else:
                        user["cheers"].append(month_day)
                        day_obj["cheers"]+=1
                        
                    DB.set("data", "drink_reasons", "month", month, day, val=day_obj)
                    DB.set("users", user_ip, val=user)
                    
                    answer = {"OK": True}
                    json_object = json.dumps(answer)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json_object, "utf-8"))
                
                else:
                
                    answer = {
                    "OK": False,
                    "description": "interaction unavailable"
                    }
                    json_object = json.dumps(answer)
                    
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json_object, "utf-8"))
            
            else:
                answer = {
                    "OK": False,
                    "Description": "Bad request",
                }
                json_object = json.dumps(answer)
                
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers(
                )
                self.wfile.write(bytes(json_object, "utf-8"))
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            with open(os.path.join(__location__, "html", "404.html"), encoding="utf-8") as f:
                data = f.read()
            
            self.wfile.write(bytes(data, "utf-8"))
            
            
            
        DB.commit()   


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")