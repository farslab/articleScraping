# articleScraping


def Scrape 

Scrape fonksiyonu bütün web scraping işlemlerini içeren uygulama fonksiyonudur.BeautifulSoup kullanılarak yapılan web scraping sonucunda oluşturulmuş publication objeleri MongoDB clienti kullanılarak oluşturulmuş database'e kaydedilir. CRUD işlemlerinin tamamı bu fonksiyon içinde gerçekleşir.


class PublicationListView

Uygulama anasayfasında listelenen publication objelerini getirmek için Django içinde ListView class'ından yararlanılarak oluşturulmuştur. Bu class üzerinden bütün publication objeleri sayfaya getirilerek bir listeye aktarılmış ve anasayfada gösterilmiştir. 
Bu class içinde super fonksiyona override edilen get_queryset fonksiyonu ile filtreleme objeleri gönderildiyse dikkate alınarak sayfaya gönderilen obje setinin şekillendirilmesi sağlanmıştır. Home.html sayfasındaki filtreleme kutucukları kullanılarak yapılan bütün filtrelemeler get_queryset fonksiyonu içinde işlenerek sayfaya response döndürmektedir.

Elasticsearch
Elasticsearch yapısı databaselerde aramaları optimize etmek ve ölçeklenebilir databaseler oluşturmak için kullanılmaktadır. Projemizde performans amacıyla kullandıgımız elasticsearch yapısı get_queryset fonksiyonu içinde listview class ı ile birlikte calısmaktadır. Home.html içindeki filter formlar kullanılarak gönderilen GET requestleri get_queryset fonksiyonu tarafından alınarak elasticsearch filtresine gönderilmiştir. Elasticsearch indexlerinde yapılan arama sonucunda dönen cevaplar Django object management kullanılarak sayfaya gönderilmiştir. Filtreleme işlemi bu şekilde tamamlanmıştır.

