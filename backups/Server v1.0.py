# Server.py 服务器

import socket
import time
import _thread
import json
import pymysql
import wx


class Database():
    users = []

    def __init__(self):
        # 连接database
        conn = pymysql.connect(host="127.0.0.1", user="root",password="",database="python",charset="utf8")
        self.cursor = conn.cursor()

        # 初始化 users
        us = self.getUserList()
        for u in us:
            c = {}
            c['id'] = u['id']
            c['name'] = u['name']
            c['time'] = u['status']
            c['unread'] = 0 #未读消息
            self.users.append(c)

    def __del__(self):
        cursor.close()
        conn.close()

    # 添加消息
    def addMessage(self,source,target,time,message,status):
        sql = "INSERT into message(source,target,time,message,status) values('%d','%d',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'),'%s','%d')" %(source,target,time,message,status)
        self.cursor.execute(sql)

    # 根据id查询昵称
    """ def findName(self,id):
        sql = "SELECT nickname FROM user where id = %d" %(id)
        self.cursor.execute(sql)   
  
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return '未知' """

    # 获取用户列表
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
                return
    # 下线
    def offline(self,id):
        for us in self.users:
            if us['id'] == id:
                us['time'] = -1
                return



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
            if item['status'] >= 1:
                self.user_list.SetItemBackgroundColour(i+1,"#00EE00")
                
            elif item['status']<=0:
                self.user_list.SetItemBackgroundColour(i+1,"#8F8F8F")

    # 设置在线离线
    def setUserStatus(self,index,status):
        if status >= 1:
            self.user_list.SetItemBackgroundColour(index,"#00EE00")
                
        elif status<=0:
            self.user_list.SetItemBackgroundColour(index,"#8F8F8F")

    def addMessage(self,text):
        self.content_text.AppendText(text+'\n')



class Server():
    title = 'Python服务器'
    HostIP = '127.0.0.1' #主机地址
    HostPort = 1367 #端口号
    HostADDR = (HostIP, HostPort)
    MAXClient = 16

    database = Database()

    # 定时发送发送消息
    def sendThread(self):
        return

    # 发送消息
    def send(self,msg):
        msgTo = msg['to']
        fromName = self.database.findName(msg['from'])
        msg['fromName'] = fromName
        ip,port = self.database.findSock(msgTo)
        try:
            self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sendSock.connect((ip, port))

            msg['type'] = 12 # 12代表服务器向客户端发送消息
            json_string = json.dumps(msg)
            self.sendSock.send(bytes(json_string, encoding = "utf8"))
        except:
            # 显示发送失败
            serverUI.addMessage("向"+fromName+"发送信息失败！")
        finally:
            self.sendSock.close()

    # 发送处理
    def handleMessage(self,msg):
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fromName = self.database.findName(msg['from'])
        toName = self.database.findName(msg['to'])
        headInfo = fromName + ' ==> ' + toName + '  at '+theTime+' : ';
        serverUI.addMessage(headInfo+msg['data'])
        # 如果在线直接发送，否则添加未读消息
        if self.database.isOnline(msg['to']):
            msg['time'] = theTime
            self.send(msg)
            # 加入数据库
            self.database.addMessage(msg['from'],msg['to'],theTime,msg['data'],1)
        else:
            # 加入数据库
            self.database.addMessage(msg['from'],msg['to'],theTime,msg['data'],0)

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
                    if msg['data'] == "login" or self.database.users[index]['time'] < 0:
                        serverUI.addMessage('用户('+name+')已经上线!') #显示消息
                        serverUI.setUserStatus(index+1,10)
                        self.database.users[index]['ip'] = msg['ip']
                        self.database.users[index]['port'] = msg['port']
                    self.database.online(id) #修改数据状态
                    
                elif msg['type'] == 11:
                    self.handleMessage(msg) #消息处理
            except:
                break
        sock.close()
        
    # 接受消息线程
    def receiveThread(self):
        try:
            self.receiveSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.receiveSock.bind(self.HostADDR)
            self.receiveSock.listen(16) #允许最大连接数为16
            self.buffersize = 1024
            serverUI.addMessage('Server准备就绪,最大连接数=16,maxsize=1024')
            self.flag = True
        except:
            self.flag = False
            serverUI.addMessage('服务器创建接受线程失败')

        while True:
            sock,addr = self.receiveSock.accept()
            t = _thread.start_new_thread(self.receive,(sock,addr))
        
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
        #接受用户列表
        userlist=self.database.getUserList()
        if userlist == 0 or userlist == -1:
            return
        serverUI.setUserList(userlist)

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
    
    