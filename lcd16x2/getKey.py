class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
    
    def __call__(self):
        charlist = []
        
        continueList = [chr(i) for i in range(0x30, 0x3A)]
        continueList.extend([chr(0x1B), chr(0x5B), chr(0x4F)])
        
        getNext = True
        while getNext:
            nextChar = self.impl()
            if not nextChar:
                getNext = False
            else:
                charlist.append(nextChar)
            
            if len(charlist) and charlist[0] != chr(27):
                getNext = False
            
            if charlist[-1] not in continueList:
                getNext = False
            
            if charlist == [chr(27), chr(27)]:
                getNext = False
        
        
        if (len(charlist) == 4) and (charlist[1] == '[') and (charlist[3] == '~'):
            if charlist[2] == '1':
                return 'home'
            if charlist[2] == '2':
                return 'insert'
            if charlist[2] == '3':
                return 'delete'
            if charlist[2] == '4':
                return 'end'
            if charlist[2] == '5':
                return 'page-up'
            if charlist[2] == '6':
                return 'page-down'
        
        
        
        if len(charlist) == 3:
            if charlist[1] == '[':
                if charlist[2] == 'A':
                    return 'u-arr'
                if charlist[2] == 'B':
                    return 'd-arr'
                if charlist[2] == 'C':
                    return 'r-arr'
                if charlist[2] == 'D':
                    return 'l-arr'
            
            elif charlist[1] == 'O':
                if charlist[2] == 'H':
                    return 'home'
                if charlist[2] == 'F':
                    return 'end'
        
        if len(charlist) == 2:
            if charlist == [chr(27), chr(27)]:
                return chr(27)
        
        if len(charlist) == 1:
            if charlist[0] is '\x7f':
                return 'bksp'
            elif charlist[0] is '\x03':
                return 'keyboard-interrupt'
            elif charlist[0] is '\x04':
                return 'end-of-file'
            else:
                return charlist[0]
        
        return ''



class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch



class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()



getKey = _Getch()
