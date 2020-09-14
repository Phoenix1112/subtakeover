# insall

```
git clone https://github.com/Phoenix1112/yeni_takeover.git
cd yeni_takeover
pip3 install -r requirements.txt
```

# usage

eğer slack hook adresi ile birlikte kullanılacaksa, takeover.py dosyasını bir editor ile açıp "self.posting_webhook=" adlı değişkene
slack web hook adresinizi giriniz ve dosyayı kayıt ediniz. Aşağıdaki komut terminalde çıktı vermez. Bu yöntem cron ile birlikte çalışacak şekilde ayarlanmıştır.

```
python3 takeover.py --list subdomains.txt -t 100
```

yukarıdaki komuta ek olarak --output parametresini kullanabilirsiniz. Böylece hem slack kanalınıza takeover bilgisi gönderilir hem de output dosyasına
yazdırılır. Eğer Terminalden Çıktı almak istiyorsanız --print parametresi kullanılabilir.

```
python3 takeover.py --list subdomains.txt -t 100 --print
```

yukarıdaki komutta --print parametresi kullanılarak takeover bilgisinin terminalde görünmesini sağlamış olduk. Eğer web hook adresiniz kayıtlı ise hem 
slack kanalınıza hemde terminalde sonucları gösterir. eğer web hook yoksa sadece ekranda çıktıyı gösterir. Ayrıca stdin den subdomainler --stdin parametresi
ile kullanabilirsiniz.

```
cat subdomains.txt | python3 takeover.py --stdin --thread 100 --output output.txt --print
```


You can use this program with crontab. For example, you can start the program automatically every 5 hours and control the takeover on subdomains.txt.

open crontab:

```
crontab -e
```
Scroll down to the bottom line of the page and edit and paste the command below. For this you need to save your slack hook address in the takeover.py file.

```
0 */5 * * * cd /path/subtakeover && /usr/bin/python3 /root/subtakeover/takeover.py --list /path/subdomains.txt --thread 50
```
