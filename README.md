# Freenom renew

Simple script to renew freenom domains. The usage is pretty simple:

```sh
pip install -r requirements.txt
python3 run.py <IP>
```

It will iterate over all of your domains to change the first entry to the given IP. This is the most convenient method for me, as I have just one A record with the desired IP on each domain, and then every other record is a CNAME pointing to that one (such as WWW).

Feel free to fork it or do a pull request if you want to extend its functionality.