# Server.py 服务器

import socket
import time
import _thread
import json
import pymysql
import wx


class Database():
    users = []
    groups = []

    def __init__(self):
        # 连接database
        self.conn = pymysql.connect(host="127.0.0.1", user="root",password="",database="python",charset="utf8")
        self.cursor = self.conn.cursor()

        # 初始化 users
        us = self.getUserList()
        for u in us:
            c = {}
            c['id'] = u['id']
            c['name'] = u['name']
            c['time'] = u['status']
            c['unread'] = 0 #未读消息
            self.users.append(c)

        # 初始化 groups
        self.groups = self.getGroupList()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    # 添加消息
    def addMessage(self,source,target,time,message,status):
        sql = "INSERT into message(source,target,time,message,status) values('%d','%d',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'),'%s','%d')" %(source,target,time,message,status)
        self.cursor.execute(sql)

    # 获取用户列表，给服务器用
    def getUserList(self):
        sql = "SELECT * FROM user"
        try:
            self.cursor.execute(sql)
            a = self.cursor.fetchall()
            if not a:
                return 0
            result=[]
            for b in a:
                c = {}
                c['id']= b[0]
                c['name']= b[1]
                c['status']= b[2]
                c['ip']= b[3]
                c['port']= b[4]
                result.append(c)
            return result
        except:
            return -1
    # 获取群列表，给服务器用
    def getGroupList(self):
        try:
            # 获取组
            sql = "SELECT * FROM `group`"
            self.cursor.execute(sql)
            a = self.cursor.fetchall()
            group=[]
            for b in a:
                c = {}
                c['type']=13 # 11为用户，13为群
                c['id']= b[0]
                c['name']= b[1]
                c['member'] = []

                sql = "SELECT memberID FROM `group_member` where id = %d" %(c['id'])
                self.cursor.execute(sql)
                o=self.cursor.fetchall()
                for p in o:
                    c['member'].append(p[0])

                group.append(c)
            return group
        except:
            return []
    # 获取contacts列表,给客户端用
    def getContacts(self):
        try:
            sql = "SELECT * FROM user"
            self.cursor.execute(sql)
            a = self.cursor.fetchall()
            if not a:
                return 0
            user=[]
            for b in a:
                c = {}
                c['type']=11 # 11为用户，13为群
                c['id']= b[0]
                c['name']= b[1]
                user.append(c)

            # 获取组
            sql = "SELECT * FROM `group`"
            self.cursor.execute(sql)
            a = self.cursor.fetchall()
            if not a:
                return 0
            group=[]
            for b in a:
                c = {}
                c['type']=13 # 11为用户，13为群
                c['id']= b[0]
                c['name']= b[1]
                c['member'] = []
                group.append(c)

            return user + group
        except:
            return []
    # 获取未读列表
    def getUnreadMessage(self,id):
        sql = "SELECT * FROM `message` WHERE target = '%d' AND status = 0" %(id)
        try:
            self.cursor.execute(sql)
            a = self.cursor.fetchall()
        
            result=[]
            for b in a:
                c = {}
                c['from']= b[1]
                c['fromName'] = self.findName(b[1])
                c['time']= b[3].strftime("%Y-%m-%d %H:%M:%S")
                c['msg']= b[4]
                result.append(c)
            return result
        except:
            return False

    # 根据id查询位置
    def findIndex(self,id):
        for i,us in enumerate(self.users):
            if us['id'] == id:
                return i
        return -1
    # 根据id查询name
    def findName(self,id):
        for us in self.users:
            if us['id'] == id:
                return us['name']
        return ""
    # 根据id查询IP,port
    def findSock(self,id):
        for us in self.users:
            if us['id'] == id:
                return us['ip'],us['port']
    #是否在线
    def isOnline(self,id):   
        for us in self.users:
            if us['id']==id:
                if us['time'] > 0:
                    return True
                else:
                    us['unread'] +=1
                    return False
        return False    
    # 上线
    def online(self,id):
        for us in self.users:
            if us['id'] == id:
                us['time'] = 10
                # 修改数据库的status字段，我就暂时先不改了
                return True
        return False
    # 下线
    def offline(self,id):
        for us in self.users:
            if us['id'] == id:
                us['time'] = -1
                return True
        return False
    # 根据id查询group name
    def findGroupName(self,id):
        for us in self.groups:
            if us['id'] == id:
                return us['name']
        return  ""
    # 根据id获取group member
    def getGroupMember(self,id):
        for us in self.groups:
            if us['id'] == id:
                return us['member'].copy()
        return []


class ServerUI(wx.Frame):
    def __init__(self, parent=None, id=-1, title =''):
        wx.Frame.__init__(self,parent,id,title,size=(1024,600))
       
        swindow = wx.SplitterWindow(parent= self, id= -1, style= wx.SP_LIVE_UPDATE)
        
        # 左面板
        left = wx.Panel(swindow)
        leftbox = wx.BoxSizer(wx.VERTICAL)
        left.SetSizer(leftbox)

        list_tab = wx.StaticText(left, -1, label = " 用户列表:", style = wx.ST_ELLIPSIZE_END)
        list_tab.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.user_list = wx.ListBox(left,style = wx.LB_SINGLE | wx.LB_OWNERDRAW)
        
        leftbox.Add(list_tab,0,flag = wx.TOP | wx.LEFT, border = 15)
        leftbox.Add(self.user_list,1,flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border = 15)

        # 右面板
        right = wx.Panel(swindow)
        rightbox = wx.BoxSizer(wx.VERTICAL)
        right.SetSizer(rightbox)

        log_tab = wx.StaticText(right, -1, label = " 日志消息:", style = wx.ST_ELLIPSIZE_END)
        log_tab.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.content_text = wx.TextCtrl(right,style=wx.TE_MULTILINE| wx.TE_READONLY| wx.TE_RICH2)
        
        rightbox.Add(log_tab,0,flag = wx.TOP | wx.LEFT, border = 15)        
        rightbox.Add(self.content_text,proportion = 1,flag = wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM , border=15)
        
        swindow.SplitVertically(left, right, 100)
        swindow.SetMinimumPaneSize(260) 

    # 用户列表
    def setUserList(self,users):
        self.user_list.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
        for i,item in enumerate(users):
            self.user_list.Append(item['name'] + "（" + str(item['id']) +"）")
            if item['time'] >= 1: # 此处time相当于status
                self.user_list.SetItemBackgroundColour(i,"#A0E030") 
            elif item['time']<=0:
                self.user_list.SetItemBackgroundColour(i,"#D0D0D0")

    # 设置在线离线
    def setUserStatus(self,index,status):
        if status >= 1:
            self.user_list.SetItemBackgroundColour(index,"#00A030")  
        elif status<=0:
            self.user_list.SetItemBackgroundColour(index,"#D0D0D0")
        self.user_list.Refresh()

    def showLog(self, text, type = 0):
        if type == 1:
            titleColor = wx.Colour(0,160,48)
        elif type == 2:
            titleColor = wx.Colour(255,128,0)
        elif type == 3:
            titleColor = wx.Colour(255,64,0)
        else:
            titleColor = wx.Colour(0,0,0)

        self.content_text.SetDefaultStyle(wx.TextAttr(titleColor,wx.NullColour))
        self.content_text.AppendText(text +'\n')

## -----------------------------


class Server():
    title = 'Python服务器'
    HostIP = '127.0.0.1' #主机地址
    HostPort = 1367 #端口号

    database = Database()


    # 发送数据(self,type,data,to,extra = {})函数 成功返回True，失败返回False
    def sendData(self,type,to,data,extra={}):
        if not data:
            return False
        if to == -1:
            msg = {"type":type, "to":to, "data":data}
            json_string = json.dumps(msg)
            extra["sock"].send(bytes(json_string, encoding = "utf8"))
            return True
            
        else:    
            ip,port = self.database.findSock(to)
            try:
                sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sendSock.connect((ip, port))
                #格式化数据并发送
                msg = {"type":type, "to":to, "data":data}
                json_string = json.dumps(dict(msg,**extra))
                sendSock.send(bytes(json_string, encoding = "utf8"))
                sendSock.close()
                return True
            except:
                sendSock.close()
                return False

    # 处理消息
    def handleMessage(self,recvMsg):
        msgType = recvMsg['type']
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fromName = self.database.findName(recvMsg['from'])

        if msgType == 11: # 单发消息
            toName = self.database.findName(recvMsg['to'])
            headInfo = fromName + ' => ' + toName + '  at '+theTime+' : ';
            serverUI.showLog(headInfo + recvMsg['data'])
            # 如果在线直接发送，否则添加未读消息
            data = [{"from":recvMsg['from'], "fromName":fromName, "time":theTime, "msg":recvMsg['data']}]
            isSendFlag = 0
            if self.database.isOnline(recvMsg['to']):
                if self.sendData(12,recvMsg['to'],data):
                    isSendFlag = 1
            # 加入数据库
            self.database.addMessage(recvMsg['from'],recvMsg['to'],theTime,recvMsg['data'],isSendFlag)
        
        elif msgType == 13: # 群发消息
            toName = self.database.findGroupName(recvMsg['to'])
            headInfo = fromName + ' =>> ' + toName + '  at '+theTime+' : ';
            serverUI.showLog(headInfo+recvMsg['data'])
            # 循环处理
            users = self.database.getGroupMember(recvMsg['to'])
            users.remove(recvMsg['from'])
            for u in users:
                data = [{"from":recvMsg['to'], "fromName":fromName, "time":theTime, "msg":recvMsg['data']}] # 此处to是目的地
                isSendFlag = 0
                if self.database.isOnline(u):
                    if self.sendData(14,u,data):
                        isSendFlag = 1
                # 群发消息不加入数据库
                #self.database.addMessage(recvMsg['from'],u,theTime,recvMsg['data'],isSendFlag)

    # 处理登录
    def loginHandle(self,msg,sock):  
        id = msg ['from']
        index = self.database.findIndex(id)
        if index < 0 :
            data = "none"
            self.sendData(2, -1, data, {"sock":sock})

        isLogin = self.database.users[index]['time'] > 0
        
        
        if msg['data'] == "hello" and isLogin:
            self.database.online(id) #修改数据状态
            return

        name = self.database.findName(id)
        if isLogin:
            serverUI.showLog('用户（'+name+'）重新上线!', 1)
        else:
            serverUI.showLog('用户（'+name+'）已经上线!', 1)
        serverUI.setUserStatus(index,10) # 更新用户状态
        self.database.users[index]['ip'] = msg['ip']
        self.database.users[index]['port'] = msg['port']
        self.database.online(id) #修改数据状态

        # 发送联系人列表
        contacts = self.database.getContacts()
        if not self.sendData(4,msg['from'],contacts,{"code":"contacts"}):
            serverUI.showLog('发送联系人列表失败!', 3)

        time.sleep(1)
        if msg['data'] == "login":
            msgs = self.database.getUnreadMessage(id)
            self.sendData(12, id, msgs)

    # 接受sock处理
    def receive(self,sock,addr):
        try:
            while True:
                data = sock.recv(1024).decode(encoding = "utf8")
                if not data:
                    break
                msg = json.loads(data)

                if msg['type'] == 1: # 登录
                    self.loginHandle(msg,sock)
                    
                elif msg['type'] == 3: #请求信息
                    if msg['data'] == "contacts": # 请求联系人列表
                        contacts = self.database.getContacts()
                        if self.sendData(4,msg['from'],contacts,{"code":"contacts"}):
                            serverUI.showLog('发送联系人列表失败!', 3)

                elif msg['type'] == 11 or msg['type'] == 13:
                    self.handleMessage(msg) #消息处理
        except:
            serverUI.showLog('客户端关闭了连接!', 3)
            pass
        finally:
            sock.close()
            return
        
    # 接受消息线程
    def receiveThread(self):
        try:
            self.receiveSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.receiveSock.bind((self.HostIP, self.HostPort))
            self.receiveSock.listen(32) #允许最大连接数为16
            self.buffersize = 1024
            serverUI.showLog("Server准备就绪,IP=" +self.HostIP + " Port=" + str(self.HostPort) +" listen=32 maxsize=1024", 2)
        except:
            serverUI.showLog('创建接收socket失败!', 3)
            return False
        
        while True:
            try:
                sock,addr = self.receiveSock.accept()
                t = _thread.start_new_thread(self.receive,(sock,addr))
            except:
                serverUI.showLog('接收数据失败！', 3)
                sock.close()

    # 维持用户状态
    def refreshUserStatus(self):
        while True:
            for i,it in enumerate(self.database.users):
                if it['time'] == 0:
                    self.database.offline(it['id'])
                    serverUI.setUserStatus(i,0)
                    serverUI.showLog('用户('+it['name']+')已下线', 2)
                elif it['time'] > 0:
                    it['time'] -= 1
            time.sleep(1)
            
    #开始运行
    def startRun(self):
        # 刷新user列表
        serverUI.setUserList(self.database.users)

        # 维持线程
        _thread.start_new_thread(self.refreshUserStatus,())

        # 接收线程
        _thread.start_new_thread(self.receiveThread,())


if __name__ == '__main__':
    app = wx.App(False)
    serverUI = ServerUI(None, wx.ID_ANY, "TCP系统 - 服务端")
    serverUI.Show(True)
    server = Server()
    server.startRun()
    app.MainLoop()
    
    