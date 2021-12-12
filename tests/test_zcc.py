from pyzcc import ZccDevice


def test_zcc():
    device = ZccDevice(host='1.1.1.1', brand='zimi', product='zcc',
                       mac='abcdef123456', port=5003, available_tcps=3)

    assert device.host == '1.1.1.1'
    assert device.brand == 'zimi'
    assert device.product == 'zcc'
    assert device.mac == 'abcdef123456'
    assert device.port == 5003
    assert device.available_tcps == 3

    assert device.__str__() == 'zimi zcc at 1.1.1.1:5003. Device MAC:abcdef123456'
    assert device.__repr__() == 'ZccDevice(host:"1.1.1.1", brand:"zimi", product:"zcc", mac:"abcdef123456", port:"5003", available_tcps:"3")'
