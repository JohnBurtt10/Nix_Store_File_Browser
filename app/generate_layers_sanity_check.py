from app import hydra_client, valid_container_data, generate_layers


def generate_layers_sanity_check():

    # hydra config
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = hydra_client.Hydra(url=hydra_url)

    def update_progress(task, progress):
        pass

    def report_error(error):
        pass

    def send_layer(layer):
        pass

    def update_layer_progress(progress):
        pass

    minimum_layer_recursive_file_size = 40
    maximum_layer_recursive_file_size = 1600
    start_date = "2003-01-20T00:00:00.000Z"
    end_date = "2023-08-18T00:00:00.000Z"
    session_id = 0

    container_data = generate_layers.generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress,
                                                     minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, start_date, end_date, session_id)

    
    sanity_check_passed = container_data == valid_container_data.valid_container_data 

    return sanity_check_passed