# Хөгжүүлэлтийн орчин бэлдэх, суулгах

* Шалгагчийг өөрийн компьютерт суулгаж тохируулах
    ** Virtual environment үүсгэх:

        $ mkvirtualenv -p /usr/bin/python3.8 my_env
 
    ** Virtual environment идэвхжүүлэх: 

        $ workon my_env

    ** Virtual environment-д төсөлд холбоотой пакет, framework суулгах: 

        $ pip3 install -r requirements.txt

    ** Хэрэв хийсвэр орчин идэвхгүй болгох бол дараах тушаал

        (my_env) $ deactivate

* Өгөгдлийн сан (postgre)
    ** postgre -г асаах

        $ systemctl start postgresql
 
    ** Өгөгдлийн санд нэвтрэх

        $ sudo -u postgres psql

    ** Database үүсгэх

        postgres=# CREATE DATABASE grader;

    ** Хэрэв Database устгах бол

        postgres=# DELETE DATABASE grader;
        
* Sandbox буюу isolate суулгах, тохируулах

    ** isolate build
    
        $ sudo apt install libcap-dev
        $ git clone https://github.com/ioi/isolate.git
        $ cd isolate
        $ make isolate 
        
    ** isolate хэрэглээ
    
        1. Тохируулгын файлыг хуулна
        
        sudo mkdir -p /usr/local/etc
        sudo cp -rfv default.cf /usr/local/etc/isolate
        
        2. Орчинг эхлүүлэх команд
        
        sudo ./isolate --init
        
        3. Sandbox-д ажлуулах програмыг хуулах
        
        sudo cp -rfv a.out /var/local/lib/isolate/0/box/
        
        4. Програмыг 1 секунт, 512МB-ийн хязгаарлалттайгаар ажиллуулах. 
           Тухайн програм хамгийн ихдээ 60 секунд унтаж болно.
           
        sudo ./isolate -t 1 -m 524288 -w 60 --run a.out

* django
    git remote add origin git@github.com:goldetime/django.git git push -u origin master
