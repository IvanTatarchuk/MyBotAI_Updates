
#!/usr/bin/env python3
import hashlib, sys

if __name__ == '__main__':
    data = sys.stdin.read().encode('utf-8')
    print(hashlib.sha256(data).hexdigest())
