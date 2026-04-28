python3 -c "
import memcache
mc = memcache.Client(['127.0.0.1:11211'])
mc.set('user:1', 'Dmitry', time=5)
mc.set('user:2', 'Admin', time=5)
mc.set('test:1', 'Data', time=5)
print('Ключи записаны')
print('user:1 =', mc.get('user:1'))
print('user:2 =', mc.get('user:2'))
print('test:1 =', mc.get('test:1'))
import time
time.sleep(6)
print('\\nЧерез 6 секунд:')
print('user:1 =', mc.get('user:1'))
print('user:2 =', mc.get('user:2'))
print('test:1 =', mc.get('test:1'))
"