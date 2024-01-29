from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Sample data for demonstration
node_data = {
    'Beverages': ['Water', 'Coffee', 'Tea'],
    'Tea': ['Black Tea', 'White Tea', 'Green Tea'],
    'Green Tea': ['Sencha', 'Gyokuro', 'Matcha', 'Pi Lo Chun']
}

@app.route('/get_children/<parent_node>')
def get_children(parent_node):
    print(f"parent node: {parent_node}")
    children = node_data.get(parent_node, [])
    print(f"children: {children}")
    return jsonify(children)

@app.route('/')
def index():
    print(f"here?")

    return render_template('tree.html')

if __name__ == '__main__':
    app.run(debug=True)