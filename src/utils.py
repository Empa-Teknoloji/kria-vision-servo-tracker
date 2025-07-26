#!/usr/bin/env python3
import os
import sys

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import tty
    import termios
    
    def getch():
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        except (termios.error, OSError):
            # Fallback for environments where termios doesn't work (like IDEs)
            return input()[:1] if input else ''
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except (termios.error, OSError):
                pass
        return ch