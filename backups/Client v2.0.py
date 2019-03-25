import wx
import json
import _thread
import time
import socket


class ClientUI(wx.Frame):
    contacts = []
    sendType = 11 # 单发还是群发
    sendTo = 0
    meID = 4

    def __init__(self,c,parent=None,id=-1,title=''):
        self.logicClient=c

        wx.Frame.__init__(self,parent,id,title,size=(1024,600))
        self.panel = wx.Panel(self)

        self.panel_user = wx.Panel(self.panel)
        self.user_list = wx.ListBox(self.panel_user,style=wx.ALIGN_CENTER|wx.LB_SINGLE,size = (300,600))

        self.panel_content = wx.Panel(self.panel)
        self.content_text = wx.TextCtrl(self.panel_content,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2,size = (600,300))
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

        self.init()

    def init(self):
        self.user_list.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.user_list.Bind(wx.EVT_LISTBOX, self.OnClick_listSelect)
        self.send_button.Bind(wx.EVT_BUTTON, self.OnClick_sendButton) #绑定事件

    # 用户列表监听
    def OnClick_listSelect(self,event):
        selection = event.GetEventObject().GetSelection()
        self.sendType = self.contacts[selection]['type']
        self.sendTo = self.contacts[selection]['id']
        # 切换Replace()
        # self.OptionPanel = PanelB(self)
        # self.HBoxPanel.Hide(self.MPL)
        # self.HBoxPanel.Replace(self.MPL,self.OptionPanel) 
        # self.SetSizer(self.HBoxPanel)  
        # self.HBoxPanel.Layout()
        # self.ProcessPanelB()

    # 发送按钮
    def OnClick_sendButton(self,event):
        text = self.input_text.GetValue()
        text = text.strip('\n')
        if text and self.sendTo !=0:
            theTime = time.strftime("%H:%M:%S", time.localtime()) # 时间 %Y-%m-%d %H:%M:%S
            if self.logicClient.sendMsg(self.sendType,text,self.sendTo,{"time":theTime}):
                #将消息显示到窗口
                title = "我 " + theTime
                message = " " + text
                self.addMessage(title,message)
            else:    
                self.addMessage("系统消息：发送数据失败！","")

    # 联系人列表 datas:[{"id":3,"type":11or13,"name":"cyt"}]
    def refreshUserList(self,datas):
        self.contacts = datas
        if self.user_list.Items and len(self.user_list.Items):
            self.user_list.Items.Clear()

        # 除去自己
        for i,u in enumerate(self.contacts):
            if u['id'] == self.meID:
                self.contacts.pop(i)
                break
        # 插入系统用户
        self.contacts.insert(0,{"type":11, "id":0, "name":"系统管理员"})

        for sub in self.contacts:
            if sub['type'] == 11:
                content = " " + sub['name'] + "（PY：" + str(sub['id']) + "）"
            else:
                content = " 群：" + sub['name'] + "（PY：" + str(sub['id']) + "）"
            self.user_list.Append(content)
        self.user_list.SetString(0,"联系人列表")
        self.user_list.Refresh()

    # 用户列表相关
    def addUser(self,id,name):
        self.user_list.Append(name)

    def addMessage(self,title,text,type = 0):
        if type == 0:
            titleColor = wx.Colour(0,128,64)
        else:
            titleColor = wx.Colour(0,0,255)
        titleFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        textFont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.content_text.SetDefaultStyle(wx.TextAttr(titleColor,wx.NullColour,titleFont)) # 文本样式
        self.content_text.AppendText(title+'\n')

        self.content_text.SetDefaultStyle(wx.TextAttr(wx.BLACK,wx.NullColour,textFont))       
        self.content_text.AppendText(text+'\n')
        
        self.input_text.Clear()

    # 显示发送失败
    def sendFail(self,falg = 0):
        return 


class Client():
    title = 'Python聊天TCP'
    serverIP = '192.168.43.104'
    serverPort = 1367
    hostIP = '192.168.43.104'
    hostPort = 3784
    status = 0 # 1为在线 # 0为离线

    me = 4 #自己的id
    contacts = []

    # sendMsg(self,type,data,to,extra = {})函数 成功返回True，失败返回False
    def sendMsg(self,type,data,to,extra= {}):
        if not data:
            return False
        try:
            self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sendSock.connect((self.serverIP, self.serverPort))
            #格式化数据并发送
            msg = {"type":type, "from":self.me, "to":to, "data":data}
            json_string = json.dumps(dict(msg,**extra))
            self.sendSock.send(bytes(json_string, encoding = "utf8"))
            self.sendSock.close()
            return True
        except:
            self.sendSock.close()
            return False
        return False


    # 开一个线程接受一个用户的处理
    def receive(self,sock,addr):
        while True:
            try:
                data = sock.recv(1024).decode(encoding = "utf8")
                if not data:
                    break
                msg = json.loads(data)

                if msg['type'] == 2:
                    break
                elif msg['type'] == 4:
                    if msg['code'] == "contacts":
                        #获取联系人列表
                        self.contacts = msg['data']
                        self.ui.refreshUserList(self.contacts)
                elif msg['type'] == 12 or msg['type'] == 14:
                    data = msg['data']
                    for ms in data:
                        title = ms['fromName']+" "+ms['time']
                        message = " " + ms['msg']
                        self.ui.addMessage(title,message,1)
            except:
                self.ui.addMessage("系统消息：接受数据失败！","")
        sock.close()

    # 接受消息线程
    def receiveThread(self):
        try:
            self.receiveSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.receiveSock.bind((self.hostIP,self.hostPort))
            self.receiveSock.listen(5) #允许最大连接数为5
            self.buffersize = 1024

            while True:
                sock,addr = self.receiveSock.accept()
                t = _thread.start_new_thread(self.receive,(sock,addr))

        except:
            self.ui.addMessage("系统消息：","接受线程错误，请重启程序！")
        finally:
            self.receiveSock.close()

    # 同步消息
    def syncServer(self):
        while True:
            if self.status == 0:
                if self.sendMsg(1,"login",0,{"ip":self.hostIP,"port":self.hostPort}):
                    self.status = 1
                    clientUI.SetTitle(self.title + " - 已登录")
                    # 请求联系人列表
                    self.sendMsg(3,"contacts",0,{"code":"contacts"})
                else:
                    clientUI.SetTitle(self.title + " - 连接失败")
            elif self.status > 0:
                if not self.sendMsg(1,"hello",0) :
                    self.status = 0
                    clientUI.SetTitle(self.title + " - 连接失败")
            time.sleep(5)
        self.ui.addMessage("系统消息：同步线程（syncServer）异常退出！","")

    def startRun(self,ui):
        self.ui = ui
        _thread.start_new_thread(self.syncServer,()) #同步状态线程
        _thread.start_new_thread(self.receiveThread,()) # 接受消息线程
        


if __name__ == '__main__':
    app = wx.App(False)
    client = Client()
    clientUI = ClientUI(client,None,wx.ID_ANY, "客户端!")
    clientUI.Show(True)
    client.startRun(clientUI)
    app.MainLoop()





# code=1 客户端向服务端发送登录，问候信息
# code=2 
# code=3 客户端查询用户信息（例请求联系人列表code="contacts"）
# code=4 服务端返回结果(返回联系人列表code="contacts")
# code=5 客户端向服务端发送更改信息（ip，port等）
# code=11,13 客户端向服务端发送消息（单发，群发）
# code=12 服务端向客户端发送消息
