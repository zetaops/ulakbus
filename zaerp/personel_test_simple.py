from tests.testengine import TestEngine


def test_personel_listele():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    assert {'personel_list': ['10', '11', '12']} == wf.current.jsonout


def test_personel_goruntule():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    assert {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sen'} == wf.current.jsonout


def test_personel_duzenle_degisiklik_yap():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    wf.set_current(
        jsonin={'personel_data': {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sensen'}})
    wf.run()
    assert {'sonuc': 'degisiklikleri onizle'} == wf.current.jsonout


def test_personel_duzenle_degisiklik_yapma():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()
    wf.run()
    wf.set_current(
        jsonin={'personel_data': {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sen'}})
    wf.run()
    assert {'sonuc': 'degisiklik yapilmadi'} == wf.current.jsonout


def test_degisiklikleri_onizle():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()

    # step 1 - Personel Listele
    wf.run()

    # step 2 - Personel Goruntule
    wf.run()

    # Step 3 - Personel Duzenle
    # Workflow'a verinin yeni halini veriyoruz
    wf.set_current(
        jsonin={'personel_data': {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sensen'}})
    wf.run()

    # Veri degistigi icin degisiklik onizle bekliyoruz
    assert {'sonuc': 'degisiklikleri onizle'} == wf.current.jsonout


def test_personel_kaydet():
    wf = TestEngine()
    wf.set_current(workflow_name='personel_duzenle')
    wf.load_or_create_workflow()

    # step 1 - Personel Listele
    wf.run()

    # step 2 - Personel Goruntule
    wf.run()

    # Step 3 - Personel Duzenle
    # Workflow'a verinin yeni halini veriyoruz
    wf.set_current(
        jsonin={'personel_data': {'personel_id': '10', 'personel_name': 'gamze', 'personel_lastname': 'sensen'}})
    wf.run()

    wf.run()
    wf.run()

    wf.run()
    assert {'sonuc': 'personel kaydedildi'} == wf.current.jsonout
