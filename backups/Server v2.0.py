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
    # 获取组列表，给服务器用
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
    
    # 设置用户信息
    def setUser(self,info):
        return

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
    def __init__(self,parent=None,id=-1,title=''):
        wx.Frame.__init__(self,parent,id,title,size=(1024,600))
        self.panel = wx.Panel(self)

        self.panel_user = wx.Panel(self.panel)
        self.user_list = wx.ListBox(self.panel_user,style=wx.ALIGN_CENTER|wx.LB_SINGLE|wx.LB_OWNERDRAW|wx.LB_NO_SB,size = (260,600))

        self.panel_content = wx.Panel(self.panel)
        self.content_text = wx.TextCtrl(self.panel_content,style=wx.TE_MULTILINE|wx.TE_READONLY,size = (600,300))
        self.input_text = wx.TextCtrl(self.panel_content,style=wx.TE_MULTILINE,size = (600,100))
        self.ctrl_panel = wx.Panel(self.panel_content)
        self.send_button = wx.Button(self.ctrl_panel,label='发送')
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.content_text,proportion = 1,flag = wx.TOP , border=10)
        self.vbox.Add(self.input_text,proportion = 1,flag = wx.TOP , border=30)
        self.vbox.Add(self.ctrl_panel,proportion = 1,flag = wx.RIGHT|wx.TOP , border=20)
        self.panel_content.SetSizer(self.vbox)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.panel_user,proportion=1,flag=wx.LEFT,border=20)
        self.hbox.Add(self.panel_content,proportion=1,flag=wx.RIGHT,border=20)
        self.panel.SetSizer(self.hbox)

    # 用户列表相关
    def setUserList(self,users):
        self.user_list.Append("用户列表")
        self.user_list.SetItemBackgroundColour(0,"#FFFFFF")
        self.user_list.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        for i,item in enumerate(users):
            self.user_list.Append(item['name'])
            if item['time'] >= 1: # 此处time相当于status
                self.user_list.SetItemBackgroundColour(i+1,"#00EE00")
                
            elif item['time']<=0:
                self.user_list.SetItemBackgroundColour(i+1,"#8F8F8F")

    # 设置在线离线
    def setUserStatus(self,index,status):
        if status >= 1:
            self.user_list.SetItemBackgroundColour(index,"#00EE00")
                
        elif status<=0:
            self.user_list.SetItemBackgroundColour(index,"#8F8F8F")
        self.user_list.Refresh()

    def addMessage(self,text):
        self.content_text.AppendText(text+'\n')



class Server():
    title = 'Python服务器'
    HostIP = '192.168.43.104' #主机地址
    HostPort = 1367 #端口号
    HostADDR = (HostIP, HostPort)

    database = Database()


    # 发送数据(self,type,data,to,extra = {})函数 成功返回True，失败返回False
    def sendData(self,type,to,data,extra={}):
        if not data:
            return False
        ip,port = self.database.findSock(to)
        try:
            self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sendSock.connect((ip, port))
            #格式化数据并发送
            msg = {"type":type, "to":to, "data":data}
            json_string = json.dumps(dict(msg,**extra))
            self.sendSock.send(bytes(json_string, encoding = "utf8"))
            self.sendSock.close()
            return True
        except:
            # 显示发送失败
            #serverUI.addMessage("向"+fromName+"发送信息失败！")
            self.sendSock.close()
            return False
        return False

    # 处理消息
    def handleMessage(self,recvMsg):
        msgType = recvMsg['type']
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fromName = self.database.findName(recvMsg['from'])
        if msgType == 11: # 单发消息
            toName = self.database.findName(recvMsg['to'])
            headInfo = fromName + ' ==> ' + toName + '  at '+theTime+' : ';
            serverUI.addMessage(headInfo+recvMsg['data'])
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
            headInfo = fromName + ' ==> ' + toName + '  at '+theTime+' : ';
            serverUI.addMessage(headInfo+recvMsg['data'])
            # 循环处理
            users = self.database.getGroupMember(recvMsg['to'])
            users.remove(recvMsg['from'])
            for u in users:
                data = [{"from":recvMsg['from'], "fromName":fromName, "time":theTime, "msg":recvMsg['data']}]
                isSendFlag = 0
                if self.database.isOnline(u):
                    if self.sendData(14,u,data):
                        isSendFlag = 1
                # 加入数据库
                self.database.addMessage(recvMsg['from'],u,theTime,recvMsg['data'],isSendFlag)


    # 登录处理
    def loginHandle(self):
        return
    
    # 开一个线程接受一个用户的处理
    def receive(self,sock,addr):
        while True:
            try:
                data = sock.recv(1024).decode(encoding = "utf8")
                if not data:
                    break
                msg = json.loads(data)

                if msg['type'] == 1:
                    id = msg ['from']
                    name = self.database.findName(id)
                    index = self.database.findIndex(id)
                    if msg['data'] == "login" or self.database.users[index]['time'] <= 0:
                        serverUI.addMessage('用户('+name+')已经上线!') #显示消息
                        serverUI.setUserStatus(index+1,10)
                        self.database.users[index]['ip'] = msg['ip']
                        self.database.users[index]['port'] = msg['port']
                    self.database.online(id) #修改数据状态
                    
                elif msg['type'] == 3:
                    if msg['code'] == "contacts":
                        # 请求联系人列表
                        contacts = self.database.getContacts()
                        if self.sendData(4,msg['from'],contacts,{"code":"contacts"}):
                            serverUI.addMessage('发送失败!')
                elif msg['type'] == 11 or msg['type'] == 13:
                    self.handleMessage(msg) #消息处理
            except:
                break
        sock.close()
        
    # 接受消息线程
    def receiveThread(self):
        try:
            self.receiveSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.receiveSock.bind(self.HostADDR)
            self.receiveSock.listen(32) #允许最大连接数为16
            self.buffersize = 1024
            serverUI.addMessage('Server准备就绪,最大连接数=16,maxsize=1024')
  
        except:
            serverUI.addMessage('创建接受线程失败')

        try:
            while True:
                sock,addr = self.receiveSock.accept()
                t = _thread.start_new_thread(self.receive,(sock,addr))
        except:
            serverUI.addMessage('接收数据失败！')
        
        
    # 维持用户状态
    def refreshUserStatus(self):
        while True:
            for i,it in enumerate(self.database.users):
                if it['time'] == 0:
                    self.database.offline(it['id'])
                    serverUI.setUserStatus(i+1,0)
                    serverUI.addMessage('用户('+it['name']+')已下线')
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
    serverUI = ServerUI(None, wx.ID_ANY, "437聊天系统 - 服务端!")
    serverUI.Show(True)
    server = Server()
    server.startRun()
    app.MainLoop()
    
    
