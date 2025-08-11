
#!/usr/bin/env python3
import json, sys
idx = json.load(open('index.json'))
q = ' '.join(sys.argv[1:]).lower()
print([d for d in idx['docs'] if q in d.get('text','').lower()])
