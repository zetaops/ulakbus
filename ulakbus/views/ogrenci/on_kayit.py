class YerlestirmeBilgisiForm(JsonForm):
    class Meta:
        include = ["giris_puan_turu", "giris_puani"]

    ileri_buton = form.Button("İleri", cmd="save")

class YerlestirmeBilgisi(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def yerlestirme_bilgisi_form(self):
        self.form_out(YerlestirmeBilgisiForm(self.object, current = self.current))

class OnKayitForm(JsonForm):
    class Meta:
        include = ["kan_grubu","baba_aylik_kazanc","baba_ogrenim_durumu","baba_meslek",
        "anne_ogrenim_durumu","anne_meslek","anne_aylik_kazanc","masraf_sponsor","emeklilik_durumu",
        "kiz_kardes_sayisi","erkek_kardes_sayisi","ogrenim_goren_kardes_sayisi","burs_kredi_no",
        "aile_tel","aile_gsm","aile_adres","ozur_durumu","ozur_oran"]
    kaydet_buton = form.Button("Kaydet", cmd="onkayit_kaydet")
    
class OnKayit(CrudView):
    class Meta:
        model = "Ogrenci"

    def onkayit_form(self):
        self.form_out(OnKayitForm(self.object, current = self.current))