#!/usr/bin/python

import os
import string
import random

s = '#include <stdio.h> \nint main() { int n; scanf("%d", &n); for (int i = 0; i < 2; i++) {printf("%d", n); } return 0;}'

def submit(pid, source):
    
    # анхны pid -г хадгалч авах
    real_pid = pid

    # pid -нд санамсаргүй угтвар залгах
    letters = string.ascii_lowercase
    pid += ''.join(random.choice(letters) for i in range(5))
    
    # С код болгох
    out = pid + ".c"
    fw = open(out, "w")
    fw.write(source)
    fw.close()

    # compile хийж программаа гаргах (exe файл үүсгэх)
    res = pid + "output"
    com = "gcc " + out + " -o " + pid + " 2> " + res
    r = os.system(com)

    # source алдаатай эсэхийг шалгах
    fr = open(res, "r") 
    compile_error = fr.read()
    fr.close()

    if (compile_error):
        rm = "rm -rf " + pid + " " + out + " " + res
        os.system(rm)
        return compile_error
    
    # программ isolate дотор ажиллуулах
    cp = "sudo cp -rf " + pid + " /var/local/lib/isolate/0/box/"
    os.system(cp)

    # running program in isolate
    sand = "./sol.sh" + " problem_" + real_pid + " " + pid + " > " + res
    os.system(sand)

    # pass counter
    fr = open(res, "r") 
    ret = fr.read()
    fr.close()

    # бүх үүсгэсэн файл, програмуудыг устгах
    rm = "rm -rf " + pid + " " + out + " " + res
    os.system(rm)

    return ret

    def submit(self, pid, source):
        """Run code in Isolate"""
        # анхны pid -г хадгалч авах
        real_pid = pid

        # pid -нд санамсаргүй угтвар залгах
        letters = string.ascii_lowercase
        pid += ''.join(random.choice(letters) for i in range(5))
        
        # С код болгох
        out = pid + ".c"
        fw = open(out, "w")
        fw.write(source)
        fw.close()
        
        # compile хийж программаа гаргах (exe файл үүсгэх)
        res = pid + "output"
        com = "gcc " + out + " -o " + pid + " 2> " + res
        r = os.system(com)

        # source алдаатай эсэхийг шалгах
        fr = open(res, "r") 
        compile_error = fr.read()
        fr.close()

        if (compile_error):
            rm = "rm -rf " + pid + " " + out + " " + res
            os.system(rm)
            correct = False
            score = 0
            return {'correct': correct,
                    'score': score,
                    'msg': compile_error}

        # программ isolate дотор ажиллуулах
        cp = "sudo cp -rf " + pid + " /var/local/lib/isolate/0/box/"
        os.system(cp)
        
        # running program in isolate
        # sand = "./sol.sh" + " problem_" + real_pid + " " + pid + " > " + res
        sand = "./media/./sol.sh" + " ./media/problem_" + real_pid + " " + pid + " > " + res
        os.system(sand)

        # pass counter
        fr = open(res, "r") 
        ret = fr.read()
        fr.close()

        # бүх үүсгэсэн файл, програмуудыг устгах
        rm = "rm -rf " + pid + " " + out + " " + res
        os.system(rm)

        correct = True
        ret_dict = json.loads(ret)
        for i in ret_dict : 
            a = i

        b = ret_dict[str(a)]
        score = int(a) / int(b)
        print(score)
        msg = str(a) + "/" + str(b)
        print(msg)
        return {'correct': correct,
                'score': score,
                'msg': msg}
  
r = submit('123A', s)
print(r)
