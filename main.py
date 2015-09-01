"""
@Create: 2015/7/8
@author: Tang Yu-Jia    
"""
from PicPick import CPicPick

if __name__ == '__main__':
    doWork = CPicPick()
    doWork.InitParameter()
    if doWork.mode == 'Check':
        doWork.Check()
    else:
        doWork.PicPick()