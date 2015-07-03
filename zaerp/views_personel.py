TEST_PERSONEL = {
    'personel_id': '10',
    'personel_name': 'gamze',
    'personel_lastname': 'sen',
    'personel_list': ['10', '11', '12'],
    'devam_et':'evet'
}


def personel_listele(current):
    current['jsonout'] = {'personel_list': ['10', '11', '12']}


def personel_goruntule(current):
    current['jsonout'] = {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sen'}


def personel_duzenle(current):
    personel_data = current.jsonin['personel_data']
    if personel_data['personel_lastname'] == 'sensen':
        current['jsonout'] = {'sonuc': 'degisiklikleri onizle'}
    else:
        current['jsonout'] = {'sonuc': 'degisiklik yapilmadi'}


# def degisiklikleri_onizle(current):
#
#     next_data = current.jsonin['next']
#     #assert next_data['val'] == 'cancel'
#     if next_data['val'] == 'cancel':
#         current['jsonout'] = {'sonuc': 'geri don'}
#     if next_data['val'] == 'save':
#         current['jsonout'] = {'sonuc': 'kaydedidi'}
#     else:
#         #current['task'].data['next']= False
#         current['jsonout'] = {'personel_data': {'personel_id': 'id', 'personel_name': 'name', 'personel_lastname': 'lastname'}}

def degisiklikleri_onizle(current):
    current['jsonout'] = {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sensen'}

def personel_kaydet(current):
     current['jsonout'] = {'sonuc': 'personel kaydedildi'}
