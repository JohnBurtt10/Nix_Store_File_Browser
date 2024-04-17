def _send_layer(combination, zero_entropy_layer, layer, send_layer):
    _overhead = layer['overhead']
    _accounted_for_packages_file_size = layer['accounted_for_packages_file_size']
    stripped_packages = layer['packages']
    layer_info = {'combination': list(combination), 'overhead': _overhead, 'packages': list(
        stripped_packages), 'accounted_for_packages_file_size': _accounted_for_packages_file_size, 'zero_entropy_layer': zero_entropy_layer}
    send_layer(layer_info)


def send_layers(answer, is_creating_zero_entropy_layers, send_layer):
    for (combination, zero_entropy_layer, i) in answer:
        if is_creating_zero_entropy_layers != zero_entropy_layer:
            continue
        layer = answer[(combination, zero_entropy_layer, i)]
        _send_layer(combination, zero_entropy_layer, layer, send_layer)