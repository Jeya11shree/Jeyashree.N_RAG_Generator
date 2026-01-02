from src import vectorstore
import inspect

print('Available methods in vectorstore:')
for name, obj in inspect.getmembers(vectorstore):
    if callable(obj) and not name.startswith('_'):
        print(f'  - {name}()')
