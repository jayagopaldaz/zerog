import requests
import shutil

#r = requests.get(settings.STATICMAP_URL.format(**data), stream=True)
#if r.status_code == 200:
#    with open(path, 'wb') as f:
#        r.raw.decode_content = True
#        shutil.copyfileobj(r.raw, f)        

r = requests.get(settings.STATICMAP_URL.format(**data), stream=True)
if r.status_code == 200:
    with open(path, 'wb') as f:
        for chunk in r:
            f.write(chunk)

#r = requests.get(settings.STATICMAP_URL.format(**data), stream=True)
#if r.status_code == 200:
#    with open(path, 'wb') as f:
#        for chunk in r.iter_content(1024):
#            f.write(chunk)