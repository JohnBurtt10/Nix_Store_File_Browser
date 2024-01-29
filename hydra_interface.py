from flask import Flask, render_template, request, jsonify
from hydra_client import Hydra
import dependency_analyzer
from extract_earliest_latest_values import extract_earliest_latest_values
import json

#TODO:
# - Clear caches button

app = Flask(__name__)

#hydra config
hydra_url = "http://hydra.clearpath.ai/"
hydra = Hydra(url=hydra_url)

hydra.login(username="administrator", password="clearp@th")

# Create a route to handle the AJAX request
@app.route('/process', methods=['POST'])
def process():

    # client input
    selected_project = request.form.get('selected_project', '')
    selected_sort_key_1 = request.form.get('sort_key_1_select', '')
    selected_sort_key_2 = request.form.get('sort_key_2_select', '')
    selected_quantity = int(request.form.get('quantity', ''))
    minimum_entropy = int(request.form.get('minimum_entropy', ''))
    minimum_file_size = int(request.form.get('minimum_file_size', ''))
    
    projects = hydra.get_projects()
    jobsets = hydra.get_jobsets(project=selected_project)
    sort_keys = {'dependency_weight', 'entropy', 'file_size'}
    (store_path_entropy_dict,
    store_path_file_size_dict,
    reverse_dependencies_dict,
    dependency_store_path_dict,
    dependency_all_store_path_dict,
    #TODO: change how this info is passed maybe?
    store_path_jobsets_dict,
    earliest_jobset,
    latest_jobset) = dependency_analyzer.mike(project_name=selected_project, hydra=hydra)

    earliest_latest_values_dict = extract_earliest_latest_values(input_dict=reverse_dependencies_dict)

    top_n_values = dependency_analyzer.compute_top_n_information(store_path_entropy_dict, 
                              store_path_file_size_dict, 
                              earliest_latest_values_dict, 
                              dependency_store_path_dict,
                              dependency_all_store_path_dict,
                              store_path_jobsets_dict,
                              project_name=selected_project, 
                              hydra=hydra, 
                              latest_jobset=latest_jobset, 
                              sort_key1=selected_sort_key_1,
                              sort_key2=selected_sort_key_2,
                              n=selected_quantity,
                              #TODO fix names
                              minimum_entropy=minimum_entropy,
                              minimum_file_size=minimum_file_size,
                              print_dependency_weight=False)
        
    return render_template('index.html',
                            projects=projects,
                            sort_keys=sort_keys,
                            top_n_values=top_n_values,
                            selected_quantity=selected_quantity,
                            default_minimum_entropy=minimum_entropy,
                            default_minimum_file_size=minimum_file_size,
                            selected_sort_key_1=selected_sort_key_1,
                            selected_sort_key_2=selected_sort_key_2,
                            selected_project=selected_project,
                            earliest_jobset=earliest_jobset,
                            latest_jobset=latest_jobset,
                            jobsets=jobsets)


@app.route('/compare/<project_name>/<base_node>/<compare_node>')
def compare(project_name, base_node, compare_node):
    serialized_jobsets_array = request.args.get('jobsets')

    if serialized_jobsets_array:
        try:
            jobsets = json.loads(serialized_jobsets_array)
        except json.JSONDecodeError as e:
            return jsonify({'result': 'error', 'message': 'Invalid JSON in myArray parameter'})
    else:
        return jsonify({'result': 'error', 'message': 'myArray parameter not provided'})
    
    print(f"Comparing {base_node} and {compare_node} for project {project_name}")
    print(f"Received jobsets: {jobsets}")
    
    overlap_list, disjoint_list = dependency_analyzer.compare(hydra, base_node, compare_node)
    combined_list = dependency_analyzer.combine(project_name=project_name, hydra=hydra, jobsets=jobsets, list1=overlap_list, list2=disjoint_list)
    
    print("Comparison and combination completed successfully.")
    
    return jsonify(combined_list)

@app.route('/get_children/<parent_node>')
def get_children(parent_node):
    print(f"Getting children for parent node: {parent_node}")
    
    children = dependency_analyzer.get_children(hydra, parent_node)
    
    print(f"Children for {parent_node}: {children}")
    
    return jsonify(children)

@app.route('/')
def index():

    # hydra config
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)
    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()

    return render_template('index.html', projects=projects,
                            sort_keys = {'dependency_weight',
                                        'entropy', 'file_size'},
                                        top_n_values='',
                                        selected_quantity='100',
                                        selected_sort_key_1='entropy',
                                        selected_sort_key_2='file_size',
                                        minimum_entropy=0,
                                        minimum_file_size=0)

if __name__ == '__main__':
    app.run(debug=True)
